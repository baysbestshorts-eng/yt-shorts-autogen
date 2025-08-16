"""
Video editing and composition module for creating YouTube Shorts
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import tempfile

from image_generator import GeneratedImage
from rewriter_tts import RewrittenContent
from utils import sanitize_filename, ensure_directory, format_duration

@dataclass
class VideoSegment:
    """Data class for video segments"""
    image_path: str
    start_time: float
    duration: float
    text_overlay: Optional[str] = None
    transition: Optional[str] = None

@dataclass
class VideoMetadata:
    """Data class for video metadata"""
    title: str
    description: str
    tags: List[str]
    duration: float
    resolution: Tuple[int, int]
    fps: int
    file_size: int

class VideoEditor:
    """Video editing and composition for YouTube Shorts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Video settings
        self.resolution = self._parse_resolution(config.get('resolution', '1080x1920'))
        self.fps = config.get('fps', 30)
        self.duration = config.get('duration', 60)
        
        # Style settings
        self.transitions = config.get('transitions', ['fade', 'zoom', 'slide'])
        self.text_overlay = config.get('text_overlay', {})
        self.background_music = config.get('background_music', {})
        
        # Output directory
        self.output_dir = Path('output/videos')
        ensure_directory(str(self.output_dir))
        
        # Check for video processing libraries
        self._check_dependencies()
    
    def _parse_resolution(self, resolution_str: str) -> Tuple[int, int]:
        """Parse resolution string to tuple"""
        try:
            width, height = resolution_str.split('x')
            return (int(width), int(height))
        except:
            return (1080, 1920)  # Default vertical resolution
    
    def _check_dependencies(self):
        """Check if video processing libraries are available"""
        try:
            import moviepy.editor as mp
            from PIL import Image, ImageDraw, ImageFont
            self.libraries_available = True
            self.logger.info("Video processing libraries available")
        except ImportError as e:
            self.logger.warning(f"Video processing libraries not available: {e}")
            self.libraries_available = False
    
    def create_video(self, images: List[GeneratedImage], audio_path: str, content: RewrittenContent) -> str:
        """
        Create video from images, audio, and content
        
        Args:
            images: List of generated images
            audio_path: Path to audio file
            content: Rewritten content with script and metadata
            
        Returns:
            str: Path to created video file
        """
        if not self.libraries_available:
            self.logger.error("Video processing libraries not available")
            raise RuntimeError("Video processing libraries not available")
        
        try:
            # Get audio duration to adjust video timing
            audio_duration = self._get_audio_duration(audio_path)
            if audio_duration == 0:
                audio_duration = self.duration
            
            # Create video segments from images
            segments = self._create_video_segments(images, audio_duration, content)
            
            # Compose video
            video_path = self._compose_video(segments, audio_path, content)
            
            self.logger.info(f"Video created successfully: {video_path}")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Error creating video: {e}")
            raise
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file"""
        try:
            import moviepy.editor as mp
            
            audio_clip = mp.AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            
            return duration
            
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    def _create_video_segments(self, images: List[GeneratedImage], total_duration: float, content: RewrittenContent) -> List[VideoSegment]:
        """Create video segments from images and content"""
        if not images:
            raise ValueError("No images provided for video creation")
        
        segments = []
        
        # Calculate timing for each segment
        segment_duration = total_duration / len(images)
        
        # Split script into parts for text overlay
        script_parts = self._split_script_for_overlay(content.rewritten_script, len(images))
        
        for i, image in enumerate(images):
            start_time = i * segment_duration
            text_overlay = script_parts[i] if i < len(script_parts) else ""
            transition = self.transitions[i % len(self.transitions)]
            
            segment = VideoSegment(
                image_path=image.image_path,
                start_time=start_time,
                duration=segment_duration,
                text_overlay=text_overlay if self.text_overlay.get('enabled', True) else None,
                transition=transition
            )
            
            segments.append(segment)
        
        return segments
    
    def _split_script_for_overlay(self, script: str, num_segments: int) -> List[str]:
        """Split script into parts for text overlay"""
        # Split script into sentences
        sentences = script.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return [""] * num_segments
        
        # Group sentences into segments
        segments = []
        sentences_per_segment = max(1, len(sentences) // num_segments)
        
        for i in range(num_segments):
            start_idx = i * sentences_per_segment
            end_idx = start_idx + sentences_per_segment
            
            if i == num_segments - 1:  # Last segment gets remaining sentences
                segment_sentences = sentences[start_idx:]
            else:
                segment_sentences = sentences[start_idx:end_idx]
            
            segment_text = '. '.join(segment_sentences)
            if segment_text and not segment_text.endswith('.'):
                segment_text += '.'
            
            segments.append(segment_text)
        
        return segments
    
    def _compose_video(self, segments: List[VideoSegment], audio_path: str, content: RewrittenContent) -> str:
        """Compose final video from segments and audio"""
        try:
            import moviepy.editor as mp
            
            # Create video clips from segments
            video_clips = []
            
            for segment in segments:
                clip = self._create_video_clip_from_segment(segment)
                video_clips.append(clip)
            
            # Concatenate video clips
            if len(video_clips) == 1:
                final_video = video_clips[0]
            else:
                final_video = mp.concatenate_videoclips(video_clips, method="compose")
            
            # Load and add audio
            audio_clip = mp.AudioFileClip(audio_path)
            
            # Ensure video duration matches audio duration
            if final_video.duration > audio_clip.duration:
                final_video = final_video.subclip(0, audio_clip.duration)
            elif final_video.duration < audio_clip.duration:
                # Loop the video to match audio duration
                final_video = final_video.loop(duration=audio_clip.duration)
            
            # Set audio
            final_video = final_video.set_audio(audio_clip)
            
            # Generate output filename
            filename = sanitize_filename(content.rewritten_title[:50])
            output_path = self.output_dir / f"{filename}.mp4"
            
            # Write video file
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_video.close()
            audio_clip.close()
            for clip in video_clips:
                clip.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error composing video: {e}")
            raise
    
    def _create_video_clip_from_segment(self, segment: VideoSegment) -> any:
        """Create video clip from a single segment"""
        try:
            import moviepy.editor as mp
            
            # Load image and create image clip
            image_clip = mp.ImageClip(segment.image_path, duration=segment.duration)
            
            # Resize to target resolution
            image_clip = image_clip.resize(self.resolution)
            
            # Add text overlay if specified
            if segment.text_overlay and self.text_overlay.get('enabled', True):
                image_clip = self._add_text_overlay(image_clip, segment.text_overlay)
            
            # Apply transition effects
            if segment.transition:
                image_clip = self._apply_transition(image_clip, segment.transition)
            
            return image_clip
            
        except Exception as e:
            self.logger.error(f"Error creating video clip from segment: {e}")
            raise
    
    def _add_text_overlay(self, clip: any, text: str) -> any:
        """Add text overlay to video clip"""
        try:
            import moviepy.editor as mp
            
            # Text overlay settings
            font_size = self.text_overlay.get('size', 48)
            font_color = self.text_overlay.get('color', 'white')
            font_family = self.text_overlay.get('font', 'Arial-Bold')
            
            # Limit text length for readability
            if len(text) > 100:
                text = text[:97] + "..."
            
            # Create text clip
            text_clip = mp.TextClip(
                text,
                fontsize=font_size,
                color=font_color,
                font=font_family,
                size=self.resolution,
                method='caption'
            ).set_duration(clip.duration)
            
            # Position text at bottom of screen
            text_clip = text_clip.set_position(('center', 'bottom')).set_margin(60)
            
            # Add stroke/outline if enabled
            if self.text_overlay.get('outline', True):
                text_clip = text_clip.set_stroke(color='black', width=2)
            
            # Composite text over image
            composite_clip = mp.CompositeVideoClip([clip, text_clip])
            
            return composite_clip
            
        except Exception as e:
            self.logger.error(f"Error adding text overlay: {e}")
            return clip
    
    def _apply_transition(self, clip: any, transition_type: str) -> any:
        """Apply transition effect to clip"""
        try:
            import moviepy.editor as mp
            
            if transition_type == 'fade':
                # Fade in at start, fade out at end
                clip = clip.fadein(0.5).fadeout(0.5)
            
            elif transition_type == 'zoom':
                # Zoom effect
                def zoom_effect(get_frame, t):
                    frame = get_frame(t)
                    # Simple zoom by cropping center and resizing
                    zoom_factor = 1 + 0.1 * (t / clip.duration)
                    return frame
                
                clip = clip.fl(zoom_effect)
            
            elif transition_type == 'slide':
                # Slide in from right
                clip = clip.set_position(lambda t: (max(0, self.resolution[0] - self.resolution[0] * t * 2), 'center'))
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Error applying transition {transition_type}: {e}")
            return clip
    
    def create_thumbnail_video(self, images: List[GeneratedImage], content: RewrittenContent) -> str:
        """Create a short preview video for thumbnail"""
        try:
            import moviepy.editor as mp
            
            if not images:
                return ""
            
            # Use first 3 images for thumbnail video
            preview_images = images[:3]
            
            # Create short clips (1 second each)
            clips = []
            for image in preview_images:
                clip = mp.ImageClip(image.image_path, duration=1.0)
                clip = clip.resize(self.resolution)
                clip = clip.fadein(0.2).fadeout(0.2)
                clips.append(clip)
            
            # Concatenate clips
            thumbnail_video = mp.concatenate_videoclips(clips)
            
            # Add title text
            title_clip = mp.TextClip(
                content.rewritten_title,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                size=self.resolution,
                method='caption'
            ).set_duration(thumbnail_video.duration).set_position('center')
            
            # Composite
            final_thumbnail = mp.CompositeVideoClip([thumbnail_video, title_clip])
            
            # Save thumbnail video
            filename = sanitize_filename(f"thumbnail_{content.rewritten_title[:30]}")
            output_path = self.output_dir / f"{filename}_preview.mp4"
            
            final_thumbnail.write_videofile(
                str(output_path),
                fps=15,
                codec='libx264',
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_thumbnail.close()
            thumbnail_video.close()
            for clip in clips:
                clip.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating thumbnail video: {e}")
            return ""
    
    def get_video_metadata(self, video_path: str, content: RewrittenContent) -> VideoMetadata:
        """Get metadata for the created video"""
        try:
            import moviepy.editor as mp
            
            # Load video to get properties
            video = mp.VideoFileClip(video_path)
            
            metadata = VideoMetadata(
                title=content.rewritten_title,
                description=self._create_video_description(content),
                tags=content.keywords,
                duration=video.duration,
                resolution=self.resolution,
                fps=self.fps,
                file_size=os.path.getsize(video_path)
            )
            
            video.close()
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error getting video metadata: {e}")
            return VideoMetadata(
                title=content.rewritten_title,
                description="Auto-generated YouTube Short",
                tags=content.keywords or [],
                duration=0,
                resolution=self.resolution,
                fps=self.fps,
                file_size=0
            )
    
    def _create_video_description(self, content: RewrittenContent) -> str:
        """Create video description based on content"""
        description = f"{content.rewritten_script[:200]}...\n\n"
        description += "🤖 This video was automatically generated using AI\n"
        description += "#Shorts #AI #AutoGenerated\n\n"
        
        if content.keywords:
            tags = " ".join([f"#{tag}" for tag in content.keywords[:5]])
            description += f"Tags: {tags}"
        
        return description
    
    def optimize_for_mobile(self, video_path: str) -> str:
        """Optimize video for mobile viewing"""
        try:
            import moviepy.editor as mp
            
            # Load video
            video = mp.VideoFileClip(video_path)
            
            # Optimize settings for mobile
            optimized_path = video_path.replace('.mp4', '_mobile.mp4')
            
            video.write_videofile(
                optimized_path,
                fps=30,
                bitrate="2000k",
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                verbose=False,
                logger=None
            )
            
            video.close()
            
            self.logger.info(f"Video optimized for mobile: {optimized_path}")
            return optimized_path
            
        except Exception as e:
            self.logger.error(f"Error optimizing video for mobile: {e}")
            return video_path