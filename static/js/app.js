/**
 * Main application logic for NeuroVisual
 * Handles audio input, API communication, and user feedback
 */

// Global state
let visualizationRenderer;
let currentAudioFeatures = {};
let currentVizParams = {};
let isProcessing = false;
let audioContext;
let microphone;
let audioAnalyser;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Initialize visualization renderer
    visualizationRenderer = new VisualizationRenderer('visualizationCanvas');
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('NeuroVisual initialized');
}

function setupEventListeners() {
    // Upload audio button
    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('audioFileInput').click();
    });
    
    document.getElementById('audioFileInput').addEventListener('change', handleAudioUpload);
    
    // Microphone button
    document.getElementById('micBtn').addEventListener('click', toggleMicrophone);
    
    // Feedback buttons
    document.getElementById('feedbackPositive').addEventListener('click', () => {
        submitFeedback(1);
    });
    
    document.getElementById('feedbackNegative').addEventListener('click', () => {
        submitFeedback(-1);
    });
    
    // Reset button
    document.getElementById('resetBtn').addEventListener('click', resetLearning);
}

async function handleAudioUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showStatus('Processing audio file...', 'info');
    
    const formData = new FormData();
    formData.append('audio', file);
    
    try {
        const response = await fetch('/api/upload_audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentAudioFeatures = data.features;
            currentVizParams = data.viz_params;
            
            // Update displays
            updateAudioFeaturesDisplay(currentAudioFeatures);
            updateVizParamsDisplay(currentVizParams);
            
            // Update visualization
            visualizationRenderer.updateParams(currentVizParams);
            visualizationRenderer.start();
            
            // Hide overlay
            document.getElementById('vizOverlay').classList.add('hidden');
            
            showStatus('Audio processed! Visualization started.', 'success');
            
            // Play the audio file for synchronization
            playAudioFile(file);
        } else {
            showStatus('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error uploading audio:', error);
        showStatus('Error uploading audio', 'error');
    }
}

function playAudioFile(file) {
    // Create audio element to play the file
    const audio = new Audio();
    audio.src = URL.createObjectURL(file);
    audio.play().catch(e => console.log('Audio playback error:', e));
}

async function toggleMicrophone() {
    const micBtn = document.getElementById('micBtn');
    
    if (!audioContext) {
        // Start microphone
        try {
            showStatus('Requesting microphone access...', 'info');
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Set up audio context
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            microphone = audioContext.createMediaStreamSource(stream);
            audioAnalyser = audioContext.createAnalyser();
            audioAnalyser.fftSize = 2048;
            
            microphone.connect(audioAnalyser);
            
            // Start processing
            processMicrophoneAudio();
            
            micBtn.textContent = '⏹️ Stop Microphone';
            micBtn.classList.add('active');
            
            // Hide overlay
            document.getElementById('vizOverlay').classList.add('hidden');
            
            showStatus('Microphone active! Visualization running.', 'success');
        } catch (error) {
            console.error('Error accessing microphone:', error);
            showStatus('Error: Could not access microphone', 'error');
        }
    } else {
        // Stop microphone
        if (microphone) {
            microphone.disconnect();
            audioContext.close();
            audioContext = null;
            microphone = null;
            audioAnalyser = null;
        }
        
        visualizationRenderer.stop();
        micBtn.textContent = '🎤 Use Microphone';
        micBtn.classList.remove('active');
        
        showStatus('Microphone stopped', 'info');
    }
}

function processMicrophoneAudio() {
    if (!audioAnalyser) return;
    
    // Get audio data
    const bufferLength = audioAnalyser.frequencyBinCount;
    const dataArray = new Float32Array(bufferLength);
    audioAnalyser.getFloatTimeDomainData(dataArray);
    
    // Extract basic features from audio data
    const features = extractSimpleFeatures(dataArray);
    currentAudioFeatures = features;
    
    // Get visualization params from server periodically
    if (!isProcessing && Math.random() < 0.1) { // Request every ~10 frames
        updateVisualizationFromFeatures(features);
    }
    
    // Update displays
    updateAudioFeaturesDisplay(features);
    
    // Continue processing
    if (audioContext) {
        requestAnimationFrame(processMicrophoneAudio);
    }
}

function extractSimpleFeatures(audioData) {
    // Calculate simple features from audio data
    let sum = 0;
    let sumSquares = 0;
    let zeroCrossings = 0;
    
    for (let i = 0; i < audioData.length; i++) {
        sum += Math.abs(audioData[i]);
        sumSquares += audioData[i] * audioData[i];
        
        if (i > 0 && audioData[i] * audioData[i-1] < 0) {
            zeroCrossings++;
        }
    }
    
    const energy = Math.sqrt(sumSquares / audioData.length);
    const zcr = zeroCrossings / audioData.length;
    
    return {
        energy: energy * 10, // Scale up
        energy_std: energy * 0.5,
        zero_crossing_rate: zcr,
        tempo: 120, // Default
        spectral_centroid: 2000 + energy * 2000
    };
}

async function updateVisualizationFromFeatures(features) {
    isProcessing = true;
    
    try {
        // This would send features to server for RL processing
        // For now, use local parameters
        const response = await fetch('/api/visualization');
        const data = await response.json();
        
        if (data.success) {
            currentVizParams = data.params;
            visualizationRenderer.updateParams(currentVizParams);
            visualizationRenderer.start();
            updateVizParamsDisplay(currentVizParams);
        }
    } catch (error) {
        console.error('Error updating visualization:', error);
    }
    
    isProcessing = false;
}

async function submitFeedback(feedback) {
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                feedback: feedback,
                state: {
                    audio_features: currentAudioFeatures,
                    viz_params: currentVizParams
                }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const feedbackText = feedback === 1 ? '👍 Feedback recorded: Soothing' : '👎 Feedback recorded: Overstimulating';
            showStatus(feedbackText, 'success');
            
            // The system learns from this feedback
            console.log('Learning updated based on feedback');
        } else {
            showStatus('Error submitting feedback', 'error');
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
        showStatus('Error submitting feedback', 'error');
    }
}

async function resetLearning() {
    if (!confirm('Are you sure you want to reset all learned preferences?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/reset', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('Learning reset successfully', 'success');
        } else {
            showStatus('Error resetting learning', 'error');
        }
    } catch (error) {
        console.error('Error resetting:', error);
        showStatus('Error resetting learning', 'error');
    }
}

function updateAudioFeaturesDisplay(features) {
    const container = document.getElementById('audioFeatures');
    
    let html = '';
    for (const [key, value] of Object.entries(features)) {
        const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
        html += `<p><span class="feature-label">${key}:</span> ${displayValue}</p>`;
    }
    
    container.innerHTML = html;
}

function updateVizParamsDisplay(params) {
    const container = document.getElementById('vizParams');
    
    let html = '';
    for (const [key, value] of Object.entries(params)) {
        const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
        html += `<p><span class="param-label">${key}:</span> ${displayValue}</p>`;
    }
    
    container.innerHTML = html;
}

function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('feedbackStatus');
    statusElement.textContent = message;
    statusElement.className = `feedback-status ${type}`;
    
    // Clear after 5 seconds
    setTimeout(() => {
        statusElement.textContent = '';
        statusElement.className = 'feedback-status';
    }, 5000);
}
