"""
Unit tests for NeuroVisual components
"""
import unittest
import numpy as np
import os
import json
from audio_processor import AudioProcessor
from visualization_engine import VisualizationEngine
from rl_agent import RLAgent


class TestAudioProcessor(unittest.TestCase):
    """Test audio processing functionality"""
    
    def setUp(self):
        self.processor = AudioProcessor()
    
    def test_default_features(self):
        """Test that default features are returned correctly"""
        features = self.processor._get_default_features()
        
        self.assertIn('tempo', features)
        self.assertIn('energy', features)
        self.assertIn('spectral_centroid', features)
        self.assertEqual(features['tempo'], 120.0)
    
    def test_extract_features_from_array_empty(self):
        """Test feature extraction with empty array"""
        features = self.processor.extract_features_from_array([])
        
        # Should return default features
        self.assertIn('tempo', features)
        self.assertIn('energy', features)
    
    def test_extract_features_from_array_short(self):
        """Test feature extraction with short audio array"""
        # Create short audio array (less than n_fft)
        short_audio = [0.1] * 100
        features = self.processor.extract_features_from_array(short_audio)
        
        # Should return default features
        self.assertIn('tempo', features)
        self.assertEqual(features['tempo'], 120.0)
    
    def test_extract_features_from_array_valid(self):
        """Test feature extraction with valid audio array"""
        # Create longer audio array
        audio_data = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/22050)).tolist()
        features = self.processor.extract_features_from_array(audio_data)
        
        # Check that features are extracted
        self.assertIn('energy', features)
        self.assertIn('spectral_centroid', features)
        self.assertIn('zero_crossing_rate', features)
        self.assertGreater(features['energy'], 0)


class TestVisualizationEngine(unittest.TestCase):
    """Test visualization engine functionality"""
    
    def setUp(self):
        self.engine = VisualizationEngine()
    
    def test_safe_defaults(self):
        """Test that safe default parameters are provided"""
        defaults = self.engine.get_safe_defaults()
        
        self.assertIn('color_hue', defaults)
        self.assertIn('motion_speed', defaults)
        self.assertIn('flash_intensity', defaults)
        
        # Check safe values
        self.assertEqual(defaults['flash_intensity'], 0.0)
        self.assertLessEqual(defaults['contrast'], 0.5)
        self.assertLessEqual(defaults['motion_speed'], 0.7)
    
    def test_generate_params_from_audio(self):
        """Test parameter generation from audio features"""
        audio_features = {
            'tempo': 120.0,
            'energy': 0.6,
            'spectral_centroid': 2500.0,
            'spectral_bandwidth': 2000.0,
            'zero_crossing_rate': 0.15,
            'chroma_mean': 0.5
        }
        
        sensitivity_multipliers = {
            'energy_sensitivity': 0.5,
            'tempo_sensitivity': 0.5,
            'contrast_sensitivity': 0.5,
            'flash_tolerance': 0.0
        }
        
        params = self.engine.generate_params_from_audio(
            audio_features, 
            sensitivity_multipliers
        )
        
        # Check that all parameters are present
        self.assertIn('color_hue', params)
        self.assertIn('motion_speed', params)
        self.assertIn('pattern_complexity', params)
        
        # Check that values are within safe bounds
        self.assertGreaterEqual(params['motion_speed'], 0.1)
        self.assertLessEqual(params['motion_speed'], 0.7)
        self.assertGreaterEqual(params['contrast'], 0.1)
        self.assertLessEqual(params['contrast'], 0.5)
    
    def test_flash_intensity_safety(self):
        """Test that flash intensity is properly controlled"""
        audio_features = {
            'energy': 0.9,  # High energy
            'tempo': 140.0
        }
        
        # Low flash tolerance - should not flash
        sensitivity_low = {
            'energy_sensitivity': 0.5,
            'tempo_sensitivity': 0.5,
            'contrast_sensitivity': 0.5,
            'flash_tolerance': 0.0
        }
        
        params = self.engine.generate_params_from_audio(
            audio_features,
            sensitivity_low
        )
        
        self.assertEqual(params['flash_intensity'], 0.0)
        
        # High flash tolerance with high energy - minimal flash allowed
        sensitivity_high = {
            'energy_sensitivity': 0.5,
            'tempo_sensitivity': 0.5,
            'contrast_sensitivity': 0.5,
            'flash_tolerance': 0.8
        }
        
        params = self.engine.generate_params_from_audio(
            audio_features,
            sensitivity_high
        )
        
        self.assertLessEqual(params['flash_intensity'], 0.1)


class TestRLAgent(unittest.TestCase):
    """Test reinforcement learning agent functionality"""
    
    def setUp(self):
        self.agent = RLAgent()
        # Clean up any existing preferences file
        if os.path.exists('user_preferences.json'):
            os.remove('user_preferences.json')
    
    def tearDown(self):
        # Clean up test preferences file
        if os.path.exists('user_preferences.json'):
            os.remove('user_preferences.json')
    
    def test_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent.sensitivity_multipliers)
        self.assertIn('energy_sensitivity', self.agent.sensitivity_multipliers)
        self.assertEqual(self.agent.sensitivity_multipliers['flash_tolerance'], 0.0)
    
    def test_get_visualization_params(self):
        """Test visualization parameter generation"""
        audio_features = {
            'tempo': 120.0,
            'energy': 0.5,
            'spectral_centroid': 2000.0
        }
        
        params = self.agent.get_visualization_params(audio_features)
        
        self.assertIn('color_hue', params)
        self.assertIn('motion_speed', params)
        self.assertIn('pattern_complexity', params)
    
    def test_positive_feedback(self):
        """Test learning from positive feedback"""
        audio_features = {
            'tempo': 130.0,
            'energy': 0.7,
            'spectral_centroid': 2500.0
        }
        
        viz_params = self.agent.get_visualization_params(audio_features)
        
        initial_energy_sensitivity = self.agent.sensitivity_multipliers['energy_sensitivity']
        
        # Provide positive feedback
        self.agent.update_from_feedback(
            {
                'audio_features': audio_features,
                'viz_params': viz_params
            },
            1  # Soothing
        )
        
        # Sensitivity should increase slightly for high energy
        self.assertGreaterEqual(
            self.agent.sensitivity_multipliers['energy_sensitivity'],
            initial_energy_sensitivity
        )
    
    def test_negative_feedback(self):
        """Test learning from negative feedback"""
        audio_features = {
            'tempo': 140.0,
            'energy': 0.8,
            'spectral_centroid': 3000.0
        }
        
        viz_params = self.agent.get_visualization_params(audio_features)
        
        initial_energy_sensitivity = self.agent.sensitivity_multipliers['energy_sensitivity']
        
        # Provide negative feedback
        self.agent.update_from_feedback(
            {
                'audio_features': audio_features,
                'viz_params': viz_params
            },
            -1  # Overstimulating
        )
        
        # Sensitivity should decrease
        self.assertLess(
            self.agent.sensitivity_multipliers['energy_sensitivity'],
            initial_energy_sensitivity
        )
    
    def test_sensitivity_bounds(self):
        """Test that sensitivities stay within safe bounds"""
        audio_features = {
            'tempo': 180.0,
            'energy': 1.0,
            'spectral_centroid': 4000.0
        }
        
        viz_params = self.agent.get_visualization_params(audio_features)
        
        # Give many negative feedbacks
        for _ in range(20):
            self.agent.update_from_feedback(
                {
                    'audio_features': audio_features,
                    'viz_params': viz_params
                },
                -1
            )
        
        # Check that all sensitivities are within bounds
        self.assertGreaterEqual(
            self.agent.sensitivity_multipliers['energy_sensitivity'],
            0.1
        )
        self.assertLessEqual(
            self.agent.sensitivity_multipliers['energy_sensitivity'],
            0.9
        )
        self.assertGreaterEqual(
            self.agent.sensitivity_multipliers['flash_tolerance'],
            0.0
        )
        self.assertLessEqual(
            self.agent.sensitivity_multipliers['flash_tolerance'],
            0.3
        )
    
    def test_save_and_load_preferences(self):
        """Test preference persistence"""
        # Modify sensitivities
        self.agent.sensitivity_multipliers['energy_sensitivity'] = 0.7
        self.agent.sensitivity_multipliers['tempo_sensitivity'] = 0.3
        self.agent._save_preferences()
        
        # Create new agent and check if it loads preferences
        new_agent = RLAgent()
        
        self.assertEqual(
            new_agent.sensitivity_multipliers['energy_sensitivity'],
            0.7
        )
        self.assertEqual(
            new_agent.sensitivity_multipliers['tempo_sensitivity'],
            0.3
        )
    
    def test_reset(self):
        """Test agent reset functionality"""
        # Modify agent state
        audio_features = {'tempo': 120.0, 'energy': 0.5}
        viz_params = self.agent.get_visualization_params(audio_features)
        
        self.agent.update_from_feedback(
            {'audio_features': audio_features, 'viz_params': viz_params},
            1
        )
        
        # Reset
        self.agent.reset()
        
        # Check that sensitivities are back to defaults
        self.assertEqual(
            self.agent.sensitivity_multipliers['energy_sensitivity'],
            0.5
        )
        self.assertEqual(len(self.agent.feedback_history), 0)


if __name__ == '__main__':
    unittest.main()
