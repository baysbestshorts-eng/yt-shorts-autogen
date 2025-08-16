"""
Voice changing and audio processing module
"""

import os
import logging
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile

from utils import ensure_directory

class VoiceChanger:
    """Audio processing and voice effects for YouTube Shorts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.enabled = config.get('enabled', True)
        self.effects = config.get('effects', {})
        self.output_format = config.get('output_format', 'wav')
        
        # Output directory
        self.output_dir = Path('output/audio_processed')
        ensure_directory(str(self.output_dir))
        
        # Check for required libraries
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required audio processing libraries are available"""
        try:
            import librosa
            import soundfile as sf
            from pydub import AudioSegment
            self.libraries_available = True
            self.logger.info("Audio processing libraries available")
        except ImportError as e:
            self.logger.warning(f"Some audio libraries not available: {e}")
            self.libraries_available = False
    
    def process_audio(self, audio_file_path: str) -> str:
        """
        Process audio file with voice effects
        
        Args:
            audio_file_path: Path to input audio file
            
        Returns:
            str: Path to processed audio file
        """
        if not self.enabled:
            self.logger.info("Voice changing disabled, returning original audio")
            return audio_file_path
        
        if not self.libraries_available:
            self.logger.warning("Audio libraries not available, returning original audio")
            return audio_file_path
        
        try:
            # Load audio file
            audio_data, sample_rate = self._load_audio(audio_file_path)
            
            # Apply effects
            processed_audio = self._apply_effects(audio_data, sample_rate)
            
            # Save processed audio
            output_path = self._save_processed_audio(processed_audio, sample_rate, audio_file_path)
            
            self.logger.info(f"Audio processing completed: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
            return audio_file_path  # Return original on error
    
    def _load_audio(self, audio_file_path: str) -> tuple:
        """Load audio file and return audio data and sample rate"""
        try:
            import librosa
            
            # Load audio file
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
            
            self.logger.debug(f"Loaded audio: {len(audio_data)} samples at {sample_rate} Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            raise
    
    def _apply_effects(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply various audio effects to the audio data"""
        processed_audio = audio_data.copy()
        
        # Apply pitch shift
        pitch_shift = self.effects.get('pitch_shift', 0)
        if pitch_shift != 0:
            processed_audio = self._apply_pitch_shift(processed_audio, sample_rate, pitch_shift)
        
        # Apply reverb
        reverb_amount = self.effects.get('reverb', 0)
        if reverb_amount > 0:
            processed_audio = self._apply_reverb(processed_audio, sample_rate, reverb_amount)
        
        # Apply compression
        if self.effects.get('compression', False):
            processed_audio = self._apply_compression(processed_audio)
        
        # Apply noise reduction
        if self.effects.get('noise_reduction', False):
            processed_audio = self._apply_noise_reduction(processed_audio, sample_rate)
        
        # Apply volume normalization
        processed_audio = self._normalize_volume(processed_audio)
        
        return processed_audio
    
    def _apply_pitch_shift(self, audio_data: np.ndarray, sample_rate: int, shift_amount: float) -> np.ndarray:
        """Apply pitch shifting to audio"""
        try:
            import librosa
            
            # Convert shift amount to semitones
            n_steps = shift_amount * 12  # Convert to semitones
            
            # Apply pitch shift
            shifted_audio = librosa.effects.pitch_shift(
                audio_data, 
                sr=sample_rate, 
                n_steps=n_steps
            )
            
            self.logger.debug(f"Applied pitch shift: {shift_amount}")
            return shifted_audio
            
        except Exception as e:
            self.logger.error(f"Error applying pitch shift: {e}")
            return audio_data
    
    def _apply_reverb(self, audio_data: np.ndarray, sample_rate: int, reverb_amount: float) -> np.ndarray:
        """Apply reverb effect to audio"""
        try:
            # Simple reverb implementation using delay and decay
            delay_samples = int(0.1 * sample_rate)  # 100ms delay
            decay_factor = 0.3 * reverb_amount
            
            # Create delayed version
            delayed_audio = np.zeros_like(audio_data)
            delayed_audio[delay_samples:] = audio_data[:-delay_samples] * decay_factor
            
            # Mix original with delayed
            reverb_audio = audio_data + delayed_audio
            
            # Prevent clipping
            max_val = np.max(np.abs(reverb_audio))
            if max_val > 1.0:
                reverb_audio = reverb_audio / max_val
            
            self.logger.debug(f"Applied reverb: {reverb_amount}")
            return reverb_audio
            
        except Exception as e:
            self.logger.error(f"Error applying reverb: {e}")
            return audio_data
    
    def _apply_compression(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Simple compression algorithm
            threshold = 0.5
            ratio = 4.0
            
            # Find samples above threshold
            above_threshold = np.abs(audio_data) > threshold
            
            # Apply compression to samples above threshold
            compressed_audio = audio_data.copy()
            compressed_audio[above_threshold] = (
                np.sign(compressed_audio[above_threshold]) * 
                (threshold + (np.abs(compressed_audio[above_threshold]) - threshold) / ratio)
            )
            
            self.logger.debug("Applied compression")
            return compressed_audio
            
        except Exception as e:
            self.logger.error(f"Error applying compression: {e}")
            return audio_data
    
    def _apply_noise_reduction(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply simple noise reduction"""
        try:
            import librosa
            
            # Simple spectral gating noise reduction
            # This is a basic implementation - more sophisticated methods exist
            
            # Compute short-time Fourier transform
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor from quiet sections
            noise_floor = np.percentile(magnitude, 10)
            
            # Apply spectral gating
            gate_threshold = noise_floor * 2
            mask = magnitude > gate_threshold
            
            # Apply mask
            filtered_magnitude = magnitude * mask
            
            # Reconstruct audio
            filtered_stft = filtered_magnitude * np.exp(1j * phase)
            filtered_audio = librosa.istft(filtered_stft, length=len(audio_data))
            
            self.logger.debug("Applied noise reduction")
            return filtered_audio
            
        except Exception as e:
            self.logger.error(f"Error applying noise reduction: {e}")
            return audio_data
    
    def _normalize_volume(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio volume"""
        try:
            # RMS normalization
            rms = np.sqrt(np.mean(audio_data ** 2))
            if rms > 0:
                target_rms = 0.2  # Target RMS level
                normalization_factor = target_rms / rms
                normalized_audio = audio_data * normalization_factor
                
                # Prevent clipping
                max_val = np.max(np.abs(normalized_audio))
                if max_val > 1.0:
                    normalized_audio = normalized_audio / max_val
                
                self.logger.debug("Applied volume normalization")
                return normalized_audio
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Error normalizing volume: {e}")
            return audio_data
    
    def _save_processed_audio(self, audio_data: np.ndarray, sample_rate: int, original_path: str) -> str:
        """Save processed audio to file"""
        try:
            import soundfile as sf
            
            # Generate output filename
            original_name = Path(original_path).stem
            output_filename = f"{original_name}_processed.{self.output_format}"
            output_path = self.output_dir / output_filename
            
            # Save audio file
            sf.write(str(output_path), audio_data, sample_rate)
            
            self.logger.debug(f"Saved processed audio: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error saving processed audio: {e}")
            # Fallback: copy original file
            import shutil
            fallback_path = self.output_dir / f"processed_{Path(original_path).name}"
            shutil.copy2(original_path, fallback_path)
            return str(fallback_path)
    
    def change_voice_gender(self, audio_file_path: str, target_gender: str = 'neutral') -> str:
        """
        Change voice gender characteristics
        
        Args:
            audio_file_path: Path to input audio file
            target_gender: Target gender ('male', 'female', 'neutral')
            
        Returns:
            str: Path to processed audio file
        """
        if not self.libraries_available:
            return audio_file_path
        
        try:
            # Load audio
            audio_data, sample_rate = self._load_audio(audio_file_path)
            
            # Apply gender-specific pitch shifts
            if target_gender == 'female':
                shift_amount = 0.15  # Shift up
            elif target_gender == 'male':
                shift_amount = -0.15  # Shift down
            else:  # neutral
                shift_amount = 0.05  # Slight upward shift
            
            # Apply pitch shift
            processed_audio = self._apply_pitch_shift(audio_data, sample_rate, shift_amount)
            
            # Save processed audio
            output_path = self._save_processed_audio(processed_audio, sample_rate, audio_file_path)
            
            self.logger.info(f"Applied gender change to {target_gender}: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error changing voice gender: {e}")
            return audio_file_path
    
    def add_background_music(self, voice_path: str, music_path: str, voice_volume: float = 0.8, music_volume: float = 0.2) -> str:
        """
        Mix voice with background music
        
        Args:
            voice_path: Path to voice audio file
            music_path: Path to background music file
            voice_volume: Volume level for voice (0.0 to 1.0)
            music_volume: Volume level for music (0.0 to 1.0)
            
        Returns:
            str: Path to mixed audio file
        """
        try:
            from pydub import AudioSegment
            
            # Load audio files
            voice = AudioSegment.from_file(voice_path)
            music = AudioSegment.from_file(music_path)
            
            # Adjust volumes
            voice = voice + (20 * np.log10(voice_volume))  # Convert to dB
            music = music + (20 * np.log10(music_volume))  # Convert to dB
            
            # Match duration - loop music if shorter than voice
            if len(music) < len(voice):
                music = music * (len(voice) // len(music) + 1)
            
            # Trim music to voice length
            music = music[:len(voice)]
            
            # Mix audio
            mixed = voice.overlay(music)
            
            # Save mixed audio
            output_filename = f"{Path(voice_path).stem}_with_music.mp3"
            output_path = self.output_dir / output_filename
            mixed.export(str(output_path), format="mp3")
            
            self.logger.info(f"Mixed audio with background music: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error adding background music: {e}")
            return voice_path
    
    def get_audio_info(self, audio_file_path: str) -> Dict[str, Any]:
        """Get information about audio file"""
        try:
            import librosa
            
            # Load audio
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
            
            # Calculate metrics
            duration = len(audio_data) / sample_rate
            rms = np.sqrt(np.mean(audio_data ** 2))
            peak = np.max(np.abs(audio_data))
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': 1,  # librosa loads as mono by default
                'rms_level': float(rms),
                'peak_level': float(peak),
                'file_size': os.path.getsize(audio_file_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting audio info: {e}")
            return {}
    
    def create_silence(self, duration: float, sample_rate: int = 44100) -> str:
        """Create a silent audio file of specified duration"""
        try:
            import soundfile as sf
            
            # Create silence
            silence = np.zeros(int(duration * sample_rate))
            
            # Save silence
            output_path = self.output_dir / f"silence_{duration}s.wav"
            sf.write(str(output_path), silence, sample_rate)
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating silence: {e}")
            return ""