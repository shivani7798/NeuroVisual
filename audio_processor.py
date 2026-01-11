"""
Audio processing module for extracting music features in real-time
"""
import numpy as np
import librosa
import soundfile as sf


class AudioProcessor:
    """Extracts audio features for visualization generation"""
    
    def __init__(self, sr=22050):
        """
        Initialize audio processor
        
        Args:
            sr: Sample rate for audio processing
        """
        self.sr = sr
        self.hop_length = 512
        self.n_fft = 2048
        
    def extract_features(self, audio_path):
        """
        Extract comprehensive audio features from file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary of extracted features
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sr)
            
            # Extract various features
            features = {}
            
            # Tempo and beat
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            
            # Energy/RMS
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
            features['energy'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
            features['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)
            features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=self.hop_length)
            features['spectral_bandwidth'] = float(np.mean(spectral_bandwidth))
            
            # Zero crossing rate (indicator of percussiveness)
            zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            features['zero_crossing_rate'] = float(np.mean(zcr))
            
            # MFCC (timbre)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            features['mfcc_mean'] = float(np.mean(mfccs))
            features['mfcc_std'] = float(np.std(mfccs))
            
            # Chroma features (pitch content)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)
            features['chroma_mean'] = float(np.mean(chroma))
            
            # Dynamics - loudness variation
            features['dynamic_range'] = float(np.max(rms) - np.min(rms))
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return self._get_default_features()
    
    def extract_features_from_array(self, audio_data):
        """
        Extract features from raw audio array (for real-time processing)
        
        Args:
            audio_data: List or array of audio samples
            
        Returns:
            Dictionary of extracted features
        """
        try:
            if not audio_data or len(audio_data) == 0:
                return self._get_default_features()
            
            y = np.array(audio_data, dtype=np.float32)
            
            # Ensure we have enough samples
            if len(y) < self.n_fft:
                return self._get_default_features()
            
            # Extract features
            features = {}
            
            # Energy/RMS
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
            features['energy'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=self.sr, hop_length=self.hop_length)
            features['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=self.sr, hop_length=self.hop_length)
            features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            features['zero_crossing_rate'] = float(np.mean(zcr))
            
            # Tempo estimate (if we have enough data)
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=self.sr)
                features['tempo'] = float(tempo)
            except:
                features['tempo'] = 120.0  # Default
            
            return features
            
        except Exception as e:
            print(f"Error extracting features from array: {e}")
            return self._get_default_features()
    
    def _get_default_features(self):
        """Return default features when extraction fails"""
        return {
            'tempo': 120.0,
            'energy': 0.5,
            'energy_std': 0.1,
            'spectral_centroid': 2000.0,
            'spectral_rolloff': 4000.0,
            'spectral_bandwidth': 2000.0,
            'zero_crossing_rate': 0.1,
            'mfcc_mean': 0.0,
            'mfcc_std': 1.0,
            'chroma_mean': 0.5,
            'dynamic_range': 0.5
        }
