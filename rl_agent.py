"""
Reinforcement Learning agent for learning user comfort preferences
"""
import numpy as np
import json
import os
from visualization_engine import VisualizationEngine


class RLAgent:
    """
    Human-in-the-loop RL agent that learns sensory-safe visual parameters
    based on user feedback (👍 soothing / 👎 overstimulating)
    """
    
    def __init__(self, learning_rate=0.1, exploration_rate=0.2):
        """
        Initialize RL agent
        
        Args:
            learning_rate: Rate at which to update preferences
            exploration_rate: Rate of exploration vs exploitation
        """
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        
        # Sensitivity multipliers for different parameters
        # These are learned over time based on user feedback
        self.sensitivity_multipliers = {
            'energy_sensitivity': 0.5,  # How much energy affects motion
            'tempo_sensitivity': 0.5,   # How much tempo affects complexity
            'contrast_sensitivity': 0.5, # How much contrast is allowed
            'flash_tolerance': 0.0,      # Tolerance for flashing (start at 0)
            'brightness_preference': 0.7, # Preferred brightness level
            'saturation_preference': 0.5, # Preferred color saturation
        }
        
        # Track feedback history for learning
        self.feedback_history = []
        
        # Current state
        self.current_audio_features = {}
        self.current_viz_params = {}
        
        # Visualization engine
        self.viz_engine = VisualizationEngine()
        
        # Load saved preferences if they exist
        self.preferences_file = 'user_preferences.json'
        self._load_preferences()
    
    def get_visualization_params(self, audio_features):
        """
        Generate visualization parameters based on audio and learned preferences
        
        Args:
            audio_features: Dictionary of audio features
            
        Returns:
            Dictionary of visualization parameters
        """
        self.current_audio_features = audio_features
        
        # Generate parameters using learned sensitivities
        viz_params = self.viz_engine.generate_params_from_audio(
            audio_features, 
            self.sensitivity_multipliers
        )
        
        # Add some exploration for learning
        if np.random.random() < self.exploration_rate:
            viz_params = self._explore_parameters(viz_params)
        
        self.current_viz_params = viz_params
        return viz_params
    
    def update_from_feedback(self, state, feedback):
        """
        Update learning based on user feedback
        
        Args:
            state: Dictionary containing audio features and viz params
            feedback: 1 for soothing (👍), -1 for overstimulating (👎)
        """
        # Record feedback
        self.feedback_history.append({
            'audio_features': state.get('audio_features', self.current_audio_features),
            'viz_params': state.get('viz_params', self.current_viz_params),
            'feedback': feedback,
        })
        
        # Update sensitivity multipliers based on feedback
        audio_features = state.get('audio_features', self.current_audio_features)
        viz_params = state.get('viz_params', self.current_viz_params)
        
        if feedback == 1:  # Soothing - reinforce current settings
            self._reinforce_positive(audio_features, viz_params)
        else:  # Overstimulating - reduce sensitivity
            self._reduce_overstimulation(audio_features, viz_params)
        
        # Save updated preferences
        self._save_preferences()
        
        # Reduce exploration as we learn more
        if len(self.feedback_history) > 20:
            self.exploration_rate = max(0.05, self.exploration_rate * 0.99)
    
    def _reinforce_positive(self, audio_features, viz_params):
        """Reinforce settings that user found soothing"""
        # Gradually increase tolerance for current parameter levels
        energy = audio_features.get('energy', 0.5)
        tempo = audio_features.get('tempo', 120.0)
        
        # If user liked higher energy/tempo, slightly increase sensitivity
        if energy > 0.6:
            self.sensitivity_multipliers['energy_sensitivity'] += self.learning_rate * 0.1
        if tempo > 100:
            self.sensitivity_multipliers['tempo_sensitivity'] += self.learning_rate * 0.1
        
        # Learn brightness and saturation preferences
        brightness = viz_params.get('color_brightness', 0.7)
        saturation = viz_params.get('color_saturation', 0.5)
        
        # Move preferences toward liked values
        self.sensitivity_multipliers['brightness_preference'] += \
            self.learning_rate * (brightness - self.sensitivity_multipliers['brightness_preference'])
        self.sensitivity_multipliers['saturation_preference'] += \
            self.learning_rate * (saturation - self.sensitivity_multipliers['saturation_preference'])
        
        # Clip values to safe ranges
        self._clip_sensitivities()
    
    def _reduce_overstimulation(self, audio_features, viz_params):
        """Reduce parameters that caused overstimulation"""
        energy = audio_features.get('energy', 0.5)
        tempo = audio_features.get('tempo', 120.0)
        
        # Reduce sensitivity to energy and tempo
        if energy > 0.5:
            self.sensitivity_multipliers['energy_sensitivity'] -= self.learning_rate * 0.2
        if tempo > 100:
            self.sensitivity_multipliers['tempo_sensitivity'] -= self.learning_rate * 0.2
        
        # Reduce contrast and flash tolerance
        contrast = viz_params.get('contrast', 0.4)
        if contrast > 0.3:
            self.sensitivity_multipliers['contrast_sensitivity'] -= self.learning_rate * 0.3
        
        self.sensitivity_multipliers['flash_tolerance'] -= self.learning_rate * 0.5
        
        # Move toward calmer brightness/saturation
        self.sensitivity_multipliers['brightness_preference'] -= self.learning_rate * 0.1
        self.sensitivity_multipliers['saturation_preference'] -= self.learning_rate * 0.1
        
        # Clip values to safe ranges
        self._clip_sensitivities()
    
    def _clip_sensitivities(self):
        """Ensure all sensitivities stay within safe bounds"""
        self.sensitivity_multipliers['energy_sensitivity'] = \
            np.clip(self.sensitivity_multipliers['energy_sensitivity'], 0.1, 0.9)
        self.sensitivity_multipliers['tempo_sensitivity'] = \
            np.clip(self.sensitivity_multipliers['tempo_sensitivity'], 0.1, 0.9)
        self.sensitivity_multipliers['contrast_sensitivity'] = \
            np.clip(self.sensitivity_multipliers['contrast_sensitivity'], 0.1, 0.7)
        self.sensitivity_multipliers['flash_tolerance'] = \
            np.clip(self.sensitivity_multipliers['flash_tolerance'], 0.0, 0.3)
        self.sensitivity_multipliers['brightness_preference'] = \
            np.clip(self.sensitivity_multipliers['brightness_preference'], 0.3, 0.9)
        self.sensitivity_multipliers['saturation_preference'] = \
            np.clip(self.sensitivity_multipliers['saturation_preference'], 0.2, 0.8)
    
    def _explore_parameters(self, viz_params):
        """Add small random variations for exploration"""
        explored_params = viz_params.copy()
        
        # Add small random noise to parameters (within safe bounds)
        for key in ['motion_speed', 'pattern_complexity', 'rotation_speed']:
            if key in explored_params:
                noise = np.random.uniform(-0.1, 0.1)
                explored_params[key] = np.clip(explored_params[key] + noise, 0.1, 0.7)
        
        return explored_params
    
    def get_current_params(self):
        """Get current visualization parameters"""
        return self.current_viz_params
    
    def reset(self):
        """Reset learning (for testing)"""
        self.sensitivity_multipliers = {
            'energy_sensitivity': 0.5,
            'tempo_sensitivity': 0.5,
            'contrast_sensitivity': 0.5,
            'flash_tolerance': 0.0,
            'brightness_preference': 0.7,
            'saturation_preference': 0.5,
        }
        self.feedback_history = []
        self.exploration_rate = 0.2
        self._save_preferences()
    
    def _save_preferences(self):
        """Save learned preferences to file"""
        try:
            data = {
                'sensitivity_multipliers': self.sensitivity_multipliers,
                'exploration_rate': self.exploration_rate,
                'feedback_count': len(self.feedback_history)
            }
            with open(self.preferences_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def _load_preferences(self):
        """Load saved preferences from file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    data = json.load(f)
                    self.sensitivity_multipliers = data.get('sensitivity_multipliers', self.sensitivity_multipliers)
                    self.exploration_rate = data.get('exploration_rate', self.exploration_rate)
                print(f"Loaded preferences from {self.preferences_file}")
        except Exception as e:
            print(f"Error loading preferences: {e}")
