"""
Visualization engine for generating audio-reactive visual parameters
"""
import numpy as np


class VisualizationEngine:
    """
    Generates visualization parameters that are safe and customizable
    for neurodivergent users
    """
    
    def __init__(self):
        """Initialize visualization engine with safe defaults"""
        self.default_params = {
            'color_hue': 200,  # Blue-ish (calming)
            'color_saturation': 0.5,  # Medium saturation
            'color_brightness': 0.7,  # Comfortable brightness
            'pattern_complexity': 0.3,  # Low complexity
            'motion_speed': 0.4,  # Slow motion
            'pattern_size': 0.6,  # Medium size
            'contrast': 0.4,  # Low contrast
            'flash_intensity': 0.0,  # No flashing
            'rotation_speed': 0.2,  # Slow rotation
        }
    
    def generate_params_from_audio(self, audio_features, sensitivity_multipliers):
        """
        Generate visualization parameters from audio features
        
        Args:
            audio_features: Dictionary of extracted audio features
            sensitivity_multipliers: Dictionary of learned sensitivity values
            
        Returns:
            Dictionary of visualization parameters
        """
        params = self.default_params.copy()
        
        # Map audio features to visual parameters with learned sensitivities
        
        # Energy -> motion speed and brightness (with safety limits)
        energy = audio_features.get('energy', 0.5)
        energy_mult = sensitivity_multipliers.get('energy_sensitivity', 0.5)
        params['motion_speed'] = np.clip(0.2 + energy * energy_mult * 0.6, 0.1, 0.7)
        params['color_brightness'] = np.clip(0.5 + energy * 0.3, 0.4, 0.8)
        
        # Spectral centroid -> color hue (frequency to color mapping)
        centroid = audio_features.get('spectral_centroid', 2000.0)
        # Map frequency range to hue (blue to red spectrum, avoiding harsh colors)
        normalized_centroid = np.clip((centroid - 1000) / 4000, 0, 1)
        params['color_hue'] = int(200 + normalized_centroid * 100)  # 200-300 range (blue-green)
        
        # Tempo -> pattern complexity and rotation speed
        tempo = audio_features.get('tempo', 120.0)
        tempo_mult = sensitivity_multipliers.get('tempo_sensitivity', 0.5)
        normalized_tempo = np.clip((tempo - 60) / 120, 0, 1)
        params['pattern_complexity'] = np.clip(0.2 + normalized_tempo * tempo_mult * 0.4, 0.1, 0.6)
        params['rotation_speed'] = np.clip(0.1 + normalized_tempo * tempo_mult * 0.3, 0.05, 0.4)
        
        # Spectral bandwidth -> pattern size
        bandwidth = audio_features.get('spectral_bandwidth', 2000.0)
        normalized_bandwidth = np.clip(bandwidth / 4000, 0, 1)
        params['pattern_size'] = np.clip(0.4 + normalized_bandwidth * 0.3, 0.3, 0.8)
        
        # Zero crossing rate -> contrast (but keep it low for comfort)
        zcr = audio_features.get('zero_crossing_rate', 0.1)
        contrast_mult = sensitivity_multipliers.get('contrast_sensitivity', 0.5)
        params['contrast'] = np.clip(0.2 + zcr * contrast_mult * 0.4, 0.1, 0.5)
        
        # Saturation based on chroma (but keep moderate)
        chroma = audio_features.get('chroma_mean', 0.5)
        params['color_saturation'] = np.clip(0.3 + chroma * 0.4, 0.2, 0.7)
        
        # Flash intensity - keep very low or zero for safety
        # Only allow minimal flash for very energetic music if user has shown tolerance
        flash_tolerance = sensitivity_multipliers.get('flash_tolerance', 0.0)
        if flash_tolerance > 0.7 and energy > 0.8:
            params['flash_intensity'] = 0.1  # Very minimal
        else:
            params['flash_intensity'] = 0.0
        
        return params
    
    def get_safe_defaults(self):
        """Return safe default parameters"""
        return self.default_params.copy()
