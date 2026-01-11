"""
NeuroVisual - Flask application for audio-reactive visualizations with RL
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from audio_processor import AudioProcessor
from visualization_engine import VisualizationEngine
from rl_agent import RLAgent

app = Flask(__name__)
CORS(app)

# Initialize components
audio_processor = AudioProcessor()
viz_engine = VisualizationEngine()
rl_agent = RLAgent()

# Create upload directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')


@app.route('/api/upload_audio', methods=['POST'])
def upload_audio():
    """Handle audio file upload and process it"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'current_audio.wav')
        audio_file.save(filepath)
        
        # Extract audio features
        features = audio_processor.extract_features(filepath)
        
        # Get visualization parameters from RL agent
        viz_params = rl_agent.get_visualization_params(features)
        
        return jsonify({
            'success': True,
            'features': features,
            'viz_params': viz_params
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process_realtime', methods=['POST'])
def process_realtime():
    """Process real-time audio features and generate visualization parameters"""
    try:
        data = request.get_json()
        audio_data = data.get('audio_data', [])
        
        # Extract features from audio data
        features = audio_processor.extract_features_from_array(audio_data)
        
        # Get visualization parameters
        viz_params = rl_agent.get_visualization_params(features)
        
        return jsonify({
            'success': True,
            'viz_params': viz_params
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Handle user feedback for reinforcement learning"""
    try:
        data = request.get_json()
        feedback = data.get('feedback')  # 1 for soothing (👍), -1 for overstimulating (👎)
        current_state = data.get('state', {})
        
        # Update RL agent with feedback
        rl_agent.update_from_feedback(current_state, feedback)
        
        return jsonify({
            'success': True,
            'message': 'Feedback received and learning updated'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visualization', methods=['GET'])
def get_visualization():
    """Get current visualization parameters"""
    try:
        # Get current state
        current_params = rl_agent.get_current_params()
        
        return jsonify({
            'success': True,
            'params': current_params
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_learning():
    """Reset the RL agent (for testing/debugging)"""
    try:
        rl_agent.reset()
        return jsonify({
            'success': True,
            'message': 'RL agent reset successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Debug mode should only be enabled in development
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
