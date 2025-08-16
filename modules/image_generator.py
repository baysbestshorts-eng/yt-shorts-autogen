"""
AI Image generation module for creating visuals for YouTube Shorts
"""

import os
import logging
import requests
import torch
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import tempfile
import base64
from io import BytesIO

from rewriter_tts import RewrittenContent
from utils import sanitize_filename, ensure_directory, retry_with_backoff

@dataclass
class GeneratedImage:
    """Data class for generated images"""
    image_path: str
    prompt: str
    timestamp: float
    style: str
    resolution: tuple
    file_size: int

class ImageGenerator:
    """AI-powered image generator for YouTube Shorts visuals"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.model = config.get('model', 'stable-diffusion-xl')
        self.resolution = self._parse_resolution(config.get('resolution', '1080x1920'))
        self.images_per_video = config.get('images_per_video', 5)
        self.style = config.get('style', 'realistic')
        self.enhancement = config.get('enhancement', True)
        self.safety_filter = config.get('safety_filter', True)
        
        # Output directory
        self.output_dir = Path('output/images')
        ensure_directory(str(self.output_dir))
        
        # Initialize the model (placeholder for actual implementation)
        self._init_model()
    
    def _parse_resolution(self, resolution_str: str) -> tuple:
        """Parse resolution string to tuple"""
        try:
            width, height = resolution_str.split('x')
            return (int(width), int(height))
        except:
            return (1080, 1920)  # Default vertical resolution
    
    def _init_model(self):
        """Initialize the image generation model"""
        try:
            # Check if we have GPU available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Image generation using device: {self.device}")
            
            # In a real implementation, you would initialize your model here
            # For now, we'll use a placeholder that calls external APIs
            self.model_initialized = True
            
        except Exception as e:
            self.logger.error(f"Error initializing image model: {e}")
            self.model_initialized = False
    
    def generate_images(self, content: RewrittenContent) -> List[GeneratedImage]:
        """
        Generate images for the video content
        
        Args:
            content: RewrittenContent object with script and metadata
            
        Returns:
            List[GeneratedImage]: List of generated images
        """
        try:
            # Create prompts for image generation
            prompts = self._create_image_prompts(content)
            
            generated_images = []
            for i, prompt in enumerate(prompts):
                try:
                    image = self._generate_single_image(prompt, i)
                    if image:
                        generated_images.append(image)
                except Exception as e:
                    self.logger.error(f"Error generating image {i}: {e}")
                    continue
            
            self.logger.info(f"Generated {len(generated_images)} images successfully")
            return generated_images
            
        except Exception as e:
            self.logger.error(f"Error in image generation pipeline: {e}")
            return []
    
    def _create_image_prompts(self, content: RewrittenContent) -> List[str]:
        """Create image generation prompts based on content"""
        script = content.rewritten_script
        keywords = content.keywords
        
        # Base prompt templates
        templates = self.config.get('prompt_templates', [
            "A stunning {subject} in {style}, high quality, detailed",
            "Beautiful {subject} with {description}, cinematic lighting"
        ])
        
        # Extract key concepts from script
        concepts = self._extract_visual_concepts(script, keywords)
        
        prompts = []
        for i in range(self.images_per_video):
            if i < len(concepts):
                concept = concepts[i]
            else:
                concept = concepts[i % len(concepts)] if concepts else "abstract concept"
            
            # Select template
            template = templates[i % len(templates)]
            
            # Create specific prompt
            prompt = self._create_specific_prompt(template, concept, content)
            prompts.append(prompt)
        
        return prompts
    
    def _extract_visual_concepts(self, script: str, keywords: List[str]) -> List[str]:
        """Extract visual concepts from script and keywords"""
        # Split script into segments
        sentences = script.split('.')
        concepts = []
        
        # Extract visual keywords
        visual_words = []
        for keyword in keywords:
            if self._is_visual_word(keyword):
                visual_words.append(keyword)
        
        # Create concepts based on script segments
        for i, sentence in enumerate(sentences[:self.images_per_video]):
            sentence = sentence.strip()
            if sentence:
                # Extract nouns and descriptive words
                concept = self._extract_main_concept(sentence)
                if concept:
                    concepts.append(concept)
        
        # Fill remaining slots with keywords
        while len(concepts) < self.images_per_video and visual_words:
            concepts.append(visual_words.pop(0))
        
        # Add generic concepts if needed
        generic_concepts = [
            "technology", "nature", "space", "innovation", "discovery",
            "science", "future", "energy", "light", "abstract pattern"
        ]
        
        while len(concepts) < self.images_per_video:
            concepts.append(generic_concepts[len(concepts) % len(generic_concepts)])
        
        return concepts
    
    def _is_visual_word(self, word: str) -> bool:
        """Check if a word represents something visual"""
        visual_categories = [
            'animal', 'plant', 'building', 'vehicle', 'tool', 'food',
            'landscape', 'person', 'object', 'machine', 'device'
        ]
        # This is a simplified check - in reality, you might use NLP
        return len(word) > 3 and word.isalpha()
    
    def _extract_main_concept(self, sentence: str) -> Optional[str]:
        """Extract the main visual concept from a sentence"""
        # Simple extraction - look for nouns
        words = sentence.lower().split()
        
        # Filter out common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'
        }
        
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        if meaningful_words:
            return meaningful_words[0]  # Return first meaningful word
        
        return None
    
    def _create_specific_prompt(self, template: str, concept: str, content: RewrittenContent) -> str:
        """Create a specific prompt from template and concept"""
        # Define style descriptions
        style_descriptions = {
            'realistic': 'photorealistic, detailed, high resolution',
            'artistic': 'artistic, stylized, creative composition',
            'modern': 'modern, clean, minimalist design',
            'vibrant': 'vibrant colors, energetic, dynamic',
            'cinematic': 'cinematic lighting, dramatic, professional'
        }
        
        style_desc = style_descriptions.get(self.style, 'high quality')
        
        # Fill template
        prompt = f"A {style_desc} image of {concept}, vertical 9:16 aspect ratio, perfect for social media, trending on instagram, professional photography"
        
        # Add quality modifiers
        prompt += ", sharp focus, detailed, high resolution, award winning"
        
        # Add safety filter keywords if enabled
        if self.safety_filter:
            prompt += ", safe for work, appropriate content"
        
        return prompt
    
    def _generate_single_image(self, prompt: str, index: int) -> Optional[GeneratedImage]:
        """Generate a single image from prompt"""
        try:
            # For this implementation, we'll use a placeholder that creates colored rectangles
            # In a real implementation, you would call your AI model here
            
            if self.model == 'stable-diffusion-xl':
                return self._generate_with_stable_diffusion(prompt, index)
            elif self.model == 'dalle':
                return self._generate_with_dalle(prompt, index)
            else:
                return self._generate_placeholder_image(prompt, index)
                
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return None
    
    def _generate_with_stable_diffusion(self, prompt: str, index: int) -> Optional[GeneratedImage]:
        """Generate image using Stable Diffusion (placeholder implementation)"""
        try:
            # This is a placeholder - in reality you would use diffusers library
            # or call an API like Hugging Face Inference API
            
            # For now, create a placeholder image
            return self._generate_placeholder_image(prompt, index)
            
        except Exception as e:
            self.logger.error(f"Stable Diffusion generation failed: {e}")
            return None
    
    def _generate_with_dalle(self, prompt: str, index: int) -> Optional[GeneratedImage]:
        """Generate image using DALL-E API"""
        try:
            # This would call OpenAI's DALL-E API
            # For now, create a placeholder
            return self._generate_placeholder_image(prompt, index)
            
        except Exception as e:
            self.logger.error(f"DALL-E generation failed: {e}")
            return None
    
    def _generate_placeholder_image(self, prompt: str, index: int) -> GeneratedImage:
        """Generate a placeholder image for testing"""
        # Create a colorful gradient image as placeholder
        width, height = self.resolution
        
        # Create image with gradient
        image = Image.new('RGB', (width, height))
        pixels = []
        
        # Create a vertical gradient with colors based on index
        colors = [
            (255, 87, 51),   # Red-orange
            (51, 255, 87),   # Green
            (51, 87, 255),   # Blue
            (255, 51, 255),  # Magenta
            (255, 255, 51),  # Yellow
        ]
        
        color = colors[index % len(colors)]
        
        for y in range(height):
            for x in range(width):
                # Create gradient effect
                factor = y / height
                r = int(color[0] * (1 - factor) + 50 * factor)
                g = int(color[1] * (1 - factor) + 50 * factor)
                b = int(color[2] * (1 - factor) + 50 * factor)
                pixels.append((r, g, b))
        
        image.putdata(pixels)
        
        # Add some texture/pattern
        if self.enhancement:
            image = self._enhance_image(image)
        
        # Save image
        filename = sanitize_filename(f"image_{index}_{prompt[:20]}")
        image_path = self.output_dir / f"{filename}.png"
        image.save(str(image_path), 'PNG', quality=95)
        
        # Get file size
        file_size = os.path.getsize(str(image_path))
        
        return GeneratedImage(
            image_path=str(image_path),
            prompt=prompt,
            timestamp=0,  # Would be actual generation time
            style=self.style,
            resolution=self.resolution,
            file_size=file_size
        )
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Apply enhancements to the generated image"""
        try:
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Enhance color
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            
            # Slight sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=2))
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error enhancing image: {e}")
            return image
    
    def resize_image_for_shorts(self, image_path: str) -> str:
        """Resize image to perfect shorts dimensions"""
        try:
            with Image.open(image_path) as img:
                # Resize to shorts dimensions (9:16 aspect ratio)
                target_width, target_height = self.resolution
                
                # Calculate scaling to fill the frame while maintaining aspect ratio
                img_width, img_height = img.size
                scale_width = target_width / img_width
                scale_height = target_height / img_height
                scale = max(scale_width, scale_height)
                
                # Resize image
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Crop to exact dimensions if needed
                if new_width > target_width or new_height > target_height:
                    left = (new_width - target_width) // 2
                    top = (new_height - target_height) // 2
                    right = left + target_width
                    bottom = top + target_height
                    img_resized = img_resized.crop((left, top, right, bottom))
                
                # Save resized image
                resized_path = image_path.replace('.png', '_shorts.png')
                img_resized.save(resized_path, 'PNG', quality=95)
                
                return resized_path
                
        except Exception as e:
            self.logger.error(f"Error resizing image: {e}")
            return image_path
    
    def create_thumbnail(self, images: List[GeneratedImage]) -> str:
        """Create thumbnail from generated images"""
        try:
            if not images:
                return ""
            
            # Use the first image as base for thumbnail
            base_image_path = images[0].image_path
            
            with Image.open(base_image_path) as img:
                # Create thumbnail size (1280x720 for YouTube)
                thumbnail_size = (1280, 720)
                
                # Resize and crop to thumbnail dimensions
                img_width, img_height = img.size
                scale_width = thumbnail_size[0] / img_width
                scale_height = thumbnail_size[1] / img_height
                scale = max(scale_width, scale_height)
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Crop to thumbnail dimensions
                left = (new_width - thumbnail_size[0]) // 2
                top = (new_height - thumbnail_size[1]) // 2
                right = left + thumbnail_size[0]
                bottom = top + thumbnail_size[1]
                thumbnail = img_resized.crop((left, top, right, bottom))
                
                # Enhance for thumbnail
                enhancer = ImageEnhance.Contrast(thumbnail)
                thumbnail = enhancer.enhance(1.3)
                
                enhancer = ImageEnhance.Color(thumbnail)
                thumbnail = enhancer.enhance(1.2)
                
                # Save thumbnail
                thumbnail_path = self.output_dir / "thumbnail.jpg"
                thumbnail.save(str(thumbnail_path), 'JPEG', quality=95)
                
                return str(thumbnail_path)
                
        except Exception as e:
            self.logger.error(f"Error creating thumbnail: {e}")
            return ""