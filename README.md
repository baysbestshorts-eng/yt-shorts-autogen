# AI YouTube Shorts Generator 🎬🤖

An automated system for generating engaging YouTube Shorts using AI technologies including content scraping, text rewriting, text-to-speech, image generation, and video editing.

## Features

- **Content Scraping**: Automatically scrape interesting content from Reddit, news APIs, and other sources
- **AI Rewriting**: Use GPT models to rewrite content into engaging short-form video scripts
- **Text-to-Speech**: Convert scripts to natural-sounding audio with voice effects
- **Image Generation**: Create relevant visuals using Stable Diffusion
- **Video Editing**: Automatically combine audio, images, and text overlays into vertical videos
- **YouTube Upload**: Automated uploading with proper metadata and scheduling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/baysbestshorts-eng/yt-shorts-autogen.git
cd yt-shorts-autogen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Configure the system:
```bash
# Edit config.yaml with your preferences
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `OPENAI_API_KEY`: Your OpenAI API key for content rewriting
- `YOUTUBE_API_KEY`: YouTube Data API key for uploading
- `YOUTUBE_CLIENT_ID` & `YOUTUBE_CLIENT_SECRET`: OAuth credentials for YouTube
- `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET`: Reddit API credentials for content scraping

### Config File

Edit `config.yaml` to customize:

- Content sources and filters
- AI model parameters
- Video generation settings
- Upload preferences
- Rate limiting options

## Usage

### Basic Usage

Run the complete pipeline:
```bash
python main.py
```

### Module Usage

Use individual modules:

```python
from modules.scraper import ContentScraper
from modules.rewriter_tts import ContentRewriter

# Scrape content
scraper = ContentScraper(config['scraper'])
content = scraper.scrape_content()

# Rewrite for shorts
rewriter = ContentRewriter(config['rewriter'])
script = rewriter.rewrite_content(content)
```

## Architecture

The system is modular and consists of:

- **main.py**: Main orchestration script
- **modules/scraper.py**: Content scraping from various sources
- **modules/rewriter_tts.py**: AI content rewriting and text-to-speech
- **modules/image_generator.py**: AI image generation for visuals
- **modules/video_editor.py**: Video composition and editing
- **modules/uploader.py**: YouTube upload automation
- **modules/voice_changer.py**: Audio processing and voice effects
- **modules/utils.py**: Utility functions and helpers

## Content Pipeline

1. **Scrape** interesting content from configured sources
2. **Rewrite** content into engaging short-form scripts using AI
3. **Generate** speech audio from the script
4. **Process** audio with voice effects and enhancements
5. **Create** relevant images using AI image generation
6. **Compose** video by combining audio, images, and text overlays
7. **Upload** to YouTube with proper metadata

## Requirements

### System Requirements

- Python 3.8+
- FFmpeg (for video processing)
- At least 4GB RAM
- GPU recommended for image generation

### API Requirements

- OpenAI API access (for content rewriting)
- YouTube Data API v3 access
- Reddit API access (optional, for content scraping)
- Stable Diffusion API or local model (for image generation)

## Content Guidelines

The system includes built-in content filtering to ensure:

- Family-friendly content
- Factual accuracy where possible
- Compliance with YouTube community guidelines
- Avoidance of controversial topics

## Customization

### Adding New Content Sources

Extend the `ContentScraper` class in `modules/scraper.py`:

```python
def scrape_custom_source(self):
    # Your custom scraping logic
    pass
```

### Custom Voice Effects

Modify `modules/voice_changer.py` to add new audio effects:

```python
def apply_custom_effect(self, audio_data):
    # Your custom audio processing
    pass
```

### Video Templates

Customize video generation in `modules/video_editor.py`:

```python
def create_custom_template(self, images, audio, text):
    # Your custom video composition
    pass
```

## Monitoring and Logging

- Comprehensive logging to files and console
- Progress tracking for long-running operations
- Error handling and recovery mechanisms
- Rate limiting to respect API quotas

## Safety and Ethics

This tool is designed for:

- Educational content creation
- Entertainment purposes
- Factual information sharing
- Creative expression

Please use responsibly and in compliance with:

- YouTube Terms of Service
- Content platform guidelines
- Copyright and fair use laws
- Community standards

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and creative purposes. Users are responsible for:

- Ensuring content compliance with platform guidelines
- Respecting copyright and intellectual property
- Following applicable laws and regulations
- Using AI-generated content ethically

## Support

For issues and questions:

- Create an issue on GitHub
- Check the documentation
- Review configuration examples

## Roadmap

- [ ] Support for more content sources
- [ ] Advanced video templates
- [ ] Multi-language support
- [ ] Analytics and performance tracking
- [ ] Batch processing capabilities
- [ ] Web interface for easier management