"""
Content rewriting and text-to-speech module
"""

import os
import logging
import openai
from gtts import gTTS
import tempfile
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import re

from scraper import ScrapedContent
from utils import sanitize_filename, ensure_directory, retry_with_backoff

@dataclass
class RewrittenContent:
    """Data class for rewritten content"""
    original_title: str
    rewritten_title: str
    rewritten_script: str
    hook: str
    call_to_action: str
    estimated_duration: float
    keywords: List[str]
    
class ContentRewriter:
    """AI-powered content rewriter for YouTube Shorts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = config.get('max_tokens', 300)
        self.temperature = config.get('temperature', 0.7)
        self.target_duration = config.get('target_duration', 60)
    
    def rewrite_content(self, content: ScrapedContent) -> RewrittenContent:
        """
        Rewrite scraped content into engaging short-form video script
        
        Args:
            content: ScrapedContent object to rewrite
            
        Returns:
            RewrittenContent: Rewritten content optimized for shorts
        """
        try:
            # Generate engaging script
            script = self._generate_script(content)
            
            # Extract components
            hook = self._extract_hook(script)
            call_to_action = self._extract_cta(script)
            rewritten_title = self._generate_title(content, script)
            
            # Estimate duration (approximately 150 words per minute for speech)
            word_count = len(script.split())
            estimated_duration = (word_count / 150) * 60
            
            # Extract keywords
            keywords = self._extract_keywords(script)
            
            return RewrittenContent(
                original_title=content.title,
                rewritten_title=rewritten_title,
                rewritten_script=script,
                hook=hook,
                call_to_action=call_to_action,
                estimated_duration=estimated_duration,
                keywords=keywords
            )
            
        except Exception as e:
            self.logger.error(f"Error rewriting content: {e}")
            raise
    
    def _generate_script(self, content: ScrapedContent) -> str:
        """Generate engaging script from original content"""
        style = self.config.get('style', 'engaging_shorts')
        include_hook = self.config.get('include_hook', True)
        include_cta = self.config.get('include_cta', True)
        
        # Create prompt based on style
        prompt = self._create_prompt(content, style, include_hook, include_cta)
        
        def make_request():
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()
        
        return retry_with_backoff(make_request)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI rewriting"""
        return """You are an expert YouTube Shorts scriptwriter. Your job is to transform content into engaging, attention-grabbing scripts that are perfect for 60-second vertical videos.

Guidelines:
- Start with a powerful hook that grabs attention in the first 3 seconds
- Use conversational, energetic language
- Include surprising facts or "did you know" moments
- Keep sentences short and punchy
- Build curiosity and maintain engagement throughout
- Include natural pauses for visual transitions
- End with a strong call-to-action
- Target 60 seconds when spoken at normal pace
- Use simple, accessible language
- Include moments where viewers might want to pause or rewatch

Focus on entertainment value while being informative."""
    
    def _create_prompt(self, content: ScrapedContent, style: str, include_hook: bool, include_cta: bool) -> str:
        """Create specific prompt for content rewriting"""
        prompt = f"""Transform this content into an engaging YouTube Shorts script:

Title: {content.title}
Content: {content.content}

Requirements:
- Target duration: {self.target_duration} seconds
- Style: {style}
- Make it engaging and entertaining
- Include surprising elements or "wow" moments
"""
        
        if include_hook:
            prompt += "- Start with a powerful hook that grabs attention immediately\n"
        
        if include_cta:
            prompt += "- End with an engaging call-to-action\n"
        
        prompt += "\nGenerate ONLY the script text, no additional formatting or explanations."
        
        return prompt
    
    def _extract_hook(self, script: str) -> str:
        """Extract the hook (first sentence/opening) from the script"""
        sentences = script.split('.')
        if sentences:
            # Take first sentence as hook
            hook = sentences[0].strip() + '.'
            return hook
        return ""
    
    def _extract_cta(self, script: str) -> str:
        """Extract call-to-action from the script"""
        sentences = script.split('.')
        if len(sentences) >= 2:
            # Take last sentence as CTA
            cta = sentences[-1].strip()
            if not cta.endswith('.'):
                cta += '.'
            return cta
        return ""
    
    def _generate_title(self, content: ScrapedContent, script: str) -> str:
        """Generate engaging title for the video"""
        prompt = f"""Create an engaging YouTube Shorts title based on this script:

Script: {script[:200]}...

Requirements:
- Maximum 60 characters
- Attention-grabbing and clickable
- Include power words or numbers if relevant
- Create curiosity
- NO clickbait or misleading content

Generate ONLY the title, nothing else."""
        
        def make_request():
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You create viral YouTube Shorts titles that are engaging but not clickbait."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        
        try:
            title = retry_with_backoff(make_request)
            # Clean and validate title
            title = re.sub(r'[^\w\s\-!?]', '', title)
            if len(title) > 60:
                title = title[:57] + "..."
            return title
        except Exception as e:
            self.logger.error(f"Error generating title: {e}")
            return content.title[:60]  # Fallback to original title
    
    def _extract_keywords(self, script: str) -> List[str]:
        """Extract relevant keywords from the script"""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{4,}\b', script.lower())
        
        # Filter common words
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been',
            'were', 'said', 'each', 'which', 'their', 'time', 'about', 'would',
            'there', 'could', 'other', 'after', 'first', 'well', 'water',
            'long', 'little', 'very', 'when', 'much', 'before', 'right', 'good'
        }
        
        keywords = [word for word in words if word not in stop_words]
        
        # Count frequency and return most common
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:8]]

class TextToSpeech:
    """Text-to-speech conversion for video narration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.engine = config.get('engine', 'gtts')
        self.language = config.get('language', 'en')
        self.speed = config.get('speed', 1.0)
        self.output_format = config.get('output_format', 'mp3')
        self.sample_rate = config.get('sample_rate', 44100)
        
        # Ensure output directory exists
        self.output_dir = Path('output/audio')
        ensure_directory(str(self.output_dir))
    
    def generate_speech(self, content: RewrittenContent) -> str:
        """
        Generate speech audio from rewritten content
        
        Args:
            content: RewrittenContent object
            
        Returns:
            str: Path to generated audio file
        """
        try:
            if self.engine == 'gtts':
                return self._generate_gtts(content)
            else:
                raise ValueError(f"Unsupported TTS engine: {self.engine}")
                
        except Exception as e:
            self.logger.error(f"Error generating speech: {e}")
            raise
    
    def _generate_gtts(self, content: RewrittenContent) -> str:
        """Generate speech using Google Text-to-Speech"""
        script = content.rewritten_script
        
        # Clean script for TTS
        script = self._prepare_text_for_tts(script)
        
        # Generate filename
        filename = sanitize_filename(content.rewritten_title[:50])
        audio_path = self.output_dir / f"{filename}.mp3"
        
        try:
            # Create TTS object
            tts = gTTS(
                text=script,
                lang=self.language,
                slow=False if self.speed >= 1.0 else True
            )
            
            # Save audio file
            tts.save(str(audio_path))
            
            # Apply speed adjustment if needed
            if self.speed != 1.0:
                audio_path = self._adjust_speed(str(audio_path), self.speed)
            
            self.logger.info(f"Generated speech audio: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            self.logger.error(f"Error with gTTS: {e}")
            raise
    
    def _prepare_text_for_tts(self, text: str) -> str:
        """Prepare text for optimal TTS output"""
        # Add pauses for better pacing
        text = re.sub(r'([.!?])', r'\1 ', text)
        text = re.sub(r'([,;:])', r'\1 ', text)
        
        # Remove problematic characters
        text = re.sub(r'[^\w\s\.,!?;:\-()]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def _adjust_speed(self, audio_path: str, speed: float) -> str:
        """Adjust audio playback speed"""
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_mp3(audio_path)
            
            # Adjust speed
            adjusted_audio = audio.speedup(playback_speed=speed)
            
            # Save adjusted audio
            adjusted_path = audio_path.replace('.mp3', f'_speed_{speed}.mp3')
            adjusted_audio.export(adjusted_path, format="mp3")
            
            # Remove original if different
            if adjusted_path != audio_path:
                os.remove(audio_path)
            
            return adjusted_path
            
        except ImportError:
            self.logger.warning("pydub not available, skipping speed adjustment")
            return audio_path
        except Exception as e:
            self.logger.error(f"Error adjusting audio speed: {e}")
            return audio_path
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert to seconds
        except ImportError:
            self.logger.warning("pydub not available, cannot get audio duration")
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {e}")
            return 0.0