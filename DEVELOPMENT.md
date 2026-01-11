# Development Guide

## Running in Development Mode

To enable debug mode during development, set the `FLASK_DEBUG` environment variable:

```bash
# Linux/Mac
export FLASK_DEBUG=true
python app.py

# Windows (Command Prompt)
set FLASK_DEBUG=true
python app.py

# Windows (PowerShell)
$env:FLASK_DEBUG="true"
python app.py
```

## Running Tests

Run all tests:
```bash
python -m unittest test_neurovisual -v
```

Run specific test class:
```bash
python -m unittest test_neurovisual.TestAudioProcessor -v
```

## Project Structure

```
NeuroVisual/
├── app.py                      # Flask application entry point
├── audio_processor.py          # Audio feature extraction
├── visualization_engine.py     # Visual parameter generation
├── rl_agent.py                # Reinforcement learning agent
├── test_neurovisual.py        # Unit tests
├── requirements.txt           # Python dependencies
├── templates/
│   └── index.html            # Web interface HTML
├── static/
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       ├── app.js           # Frontend logic
│       └── visualization.js # Canvas rendering
└── uploads/                  # Audio file uploads (created at runtime)
```

## API Endpoints

### POST /api/upload_audio
Upload an audio file for processing.
- **Body**: multipart/form-data with 'audio' file
- **Response**: `{success: true, features: {...}, viz_params: {...}}`

### POST /api/process_realtime
Process real-time audio data.
- **Body**: `{audio_data: [...]}`
- **Response**: `{success: true, viz_params: {...}}`

### POST /api/feedback
Submit user feedback.
- **Body**: `{feedback: 1 or -1, state: {...}}`
- **Response**: `{success: true, message: "..."}`

### GET /api/visualization
Get current visualization parameters.
- **Response**: `{success: true, params: {...}}`

### POST /api/reset
Reset learning and preferences.
- **Response**: `{success: true, message: "..."}`

## Adding New Audio Features

1. Update `AudioProcessor.extract_features()` in `audio_processor.py`
2. Add feature mapping in `VisualizationEngine.generate_params_from_audio()`
3. Update `RLAgent` sensitivity multipliers if needed
4. Add tests for new features

## Customizing Visualizations

Edit `static/js/visualization.js` to modify:
- Pattern rendering in `drawCalmingPatterns()`
- Color schemes in `hslToRgb()`
- Animation behavior in `animate()`

## Safety Guidelines

When making changes, ensure:
- Flash intensity stays very low (max 0.1)
- Contrast stays moderate (max 0.5-0.7)
- Motion speed stays reasonable (max 0.7)
- Default parameters are always safe/comfortable
- All parameters have hard limits
