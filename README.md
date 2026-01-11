# 🎵 NeuroVisual

**Personalized Audio-Reactive Visualizations for Neurodivergent Users**

NeuroVisual is a Flask-based, human-in-the-loop reinforcement learning system that generates real-time, audio-reactive visualizations designed for neurodivergent users. The system extracts live music features and adaptively adjusts visual parameters using user comfort feedback (👍 soothing / 👎 overstimulating) as a reward signal, learning sensory-safe, personalized visual patterns over time.

## ✨ Features

- **Real-Time Audio Processing**: Extracts music features including tempo, energy, spectral characteristics, and more
- **Adaptive Visualizations**: Generates calming, audio-reactive visual patterns that respond to music
- **Human-in-the-Loop Learning**: Uses reinforcement learning to adapt to individual user preferences
- **Sensory-Safe Design**: Prioritizes comfort with controlled brightness, contrast, and motion
- **User Feedback System**: Simple 👍/👎 feedback mechanism to guide learning
- **Personalized Experience**: Learns and saves individual user preferences over time
- **Multiple Audio Inputs**: Supports both audio file uploads and real-time microphone input

## 🏗️ Architecture

### Core Components

1. **Audio Processor** (`audio_processor.py`)
   - Extracts comprehensive audio features using librosa
   - Features: tempo, energy, spectral centroid, MFCC, chroma, zero-crossing rate
   - Supports both file-based and real-time stream processing

2. **Visualization Engine** (`visualization_engine.py`)
   - Maps audio features to visual parameters
   - Generates safe, comfortable visualization settings
   - Respects learned sensitivity multipliers

3. **RL Agent** (`rl_agent.py`)
   - Implements human-in-the-loop reinforcement learning
   - Learns from binary feedback (soothing vs. overstimulating)
   - Adaptively adjusts sensitivity multipliers
   - Persists learned preferences to disk

4. **Flask Web Application** (`app.py`)
   - RESTful API endpoints for audio processing and feedback
   - Serves interactive web interface
   - Coordinates all system components

5. **Web Interface** (`templates/`, `static/`)
   - Interactive canvas-based visualization renderer
   - Audio upload and microphone input controls
   - Feedback buttons and real-time parameter display

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser with Web Audio API support

### Setup

1. Clone the repository:
```bash
git clone https://github.com/shivani7798/NeuroVisual.git
cd NeuroVisual
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Starting the Application

1. Run the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

### Using NeuroVisual

1. **Choose Audio Input**:
   - Click "📁 Upload Audio" to use an audio file (MP3, WAV, etc.)
   - Click "🎤 Use Microphone" for real-time audio input

2. **Watch the Visualization**:
   - The visualization will adapt in real-time to the audio features
   - Patterns, colors, and motion are all audio-reactive

3. **Provide Feedback**:
   - Click 👍 "Soothing" when the visualization feels comfortable
   - Click 👎 "Overstimulating" when it feels overwhelming
   - The system learns from your feedback to personalize future visualizations

4. **Monitor Learning**:
   - View current audio features in the "Current Audio Features" panel
   - Track visualization parameters in the "Visualization Parameters" panel
   - Your preferences are automatically saved and persist across sessions

5. **Reset if Needed**:
   - Click "🔄 Reset Learning" to clear learned preferences and start fresh

## 🧠 How It Works

### Reinforcement Learning Process

1. **Audio Analysis**: System extracts features from audio input
2. **Parameter Generation**: RL agent generates visualization parameters based on:
   - Current audio features
   - Learned sensitivity multipliers
   - Exploration factor for learning

3. **Visualization**: Canvas renders audio-reactive patterns with generated parameters
4. **User Feedback**: User indicates comfort level (👍 or 👎)
5. **Learning Update**: RL agent adjusts sensitivity multipliers:
   - Positive feedback: Reinforces current parameter ranges
   - Negative feedback: Reduces sensitivity to stimulation factors
   
6. **Persistence**: Learned preferences saved to `user_preferences.json`

### Safety Features

- **Default Safe Parameters**: System starts with conservative, calming defaults
- **Bounded Adjustments**: All parameters have strict safety limits
- **Flash Protection**: Flash intensity starts at 0 and requires explicit tolerance
- **Gradual Learning**: Changes happen incrementally over time
- **Exploration Control**: Exploration rate decreases as system learns

## 📊 API Endpoints

- `POST /api/upload_audio` - Upload and process audio file
- `POST /api/process_realtime` - Process real-time audio data
- `POST /api/feedback` - Submit user feedback (1 for soothing, -1 for overstimulating)
- `GET /api/visualization` - Get current visualization parameters
- `POST /api/reset` - Reset learning and preferences

## 🎨 Visualization Parameters

The system controls these visual aspects:

- **Color Hue**: Base color of the visualization (blue-green spectrum for calmness)
- **Color Saturation**: Intensity of colors (moderate for comfort)
- **Color Brightness**: Overall brightness (adjustable based on preference)
- **Pattern Complexity**: Number of visual elements (low to medium)
- **Motion Speed**: Animation speed (slow to moderate)
- **Pattern Size**: Size of visual elements
- **Contrast**: Visual contrast level (kept low for comfort)
- **Flash Intensity**: Flashing effects (disabled by default)
- **Rotation Speed**: Pattern rotation rate (slow)

## 🔧 Configuration

### Audio Processing Settings

Edit `audio_processor.py` to adjust:
- Sample rate: `sr=22050`
- Hop length: `hop_length=512`
- FFT size: `n_fft=2048`

### Learning Parameters

Edit `rl_agent.py` to adjust:
- Learning rate: `learning_rate=0.1`
- Initial exploration rate: `exploration_rate=0.2`

## 🤝 Contributing

Contributions are welcome! This project is designed to help neurodivergent users, so please keep accessibility and sensory comfort as top priorities.

## 📝 License

See LICENSE file for details.

## 🌟 Acknowledgments

Built with consideration for neurodivergent sensory needs and preferences. The system prioritizes user comfort and personalization through adaptive learning.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.