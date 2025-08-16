# YouTube Shorts Auto-Generator

An automated tool for generating YouTube Shorts content using AI and automated workflows.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [GitHub Actions Secrets Configuration](#github-actions-secrets-configuration)
- [Local Development](#local-development)
- [Usage](#usage)
- [Contributing](#contributing)

## Overview

This project automates the creation of YouTube Shorts by leveraging AI services and YouTube APIs. The tool can generate content, create videos, and upload them to YouTube automatically through GitHub Actions workflows.

## Prerequisites

Before setting up this project, ensure you have:

- Python 3.8 or higher
- A YouTube Channel and YouTube Data API access
- OpenAI API access (for content generation)
- GitHub account with Actions enabled
- Git installed on your local machine

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/baysbestshorts-eng/yt-shorts-autogen.git
cd yt-shorts-autogen
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys and configuration values (see [Environment Variables](#environment-variables) section below).

## Environment Variables

The following environment variables are required for the project to function properly:

### Required API Keys

| Variable Name | Description | Where to Get |
|---------------|-------------|--------------|
| `OPENAI_API_KEY` | OpenAI API key for content generation | [OpenAI API Keys](https://platform.openai.com/api-keys) |
| `YOUTUBE_API_KEY` | YouTube Data API key | [Google Cloud Console](https://console.cloud.google.com/apis/api/youtube.googleapis.com) |
| `YOUTUBE_CLIENT_ID` | OAuth 2.0 client ID for YouTube | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `YOUTUBE_CLIENT_SECRET` | OAuth 2.0 client secret for YouTube | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |

### Optional Configuration

| Variable Name | Description | Default Value |
|---------------|-------------|---------------|
| `VIDEO_DURATION` | Duration of generated shorts in seconds | `60` |
| `UPLOAD_SCHEDULE` | Cron schedule for automated uploads | `0 12 * * *` |
| `CONTENT_THEME` | Theme for content generation | `general` |

## GitHub Actions Secrets Configuration

To enable automated workflows, you need to configure GitHub Actions secrets. These secrets allow the GitHub Actions workflows to access your API keys securely without exposing them in your code.

### Step-by-Step Guide to Add GitHub Secrets

#### 1. Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/baysbestshorts-eng/yt-shorts-autogen`
2. Click on the **"Settings"** tab (located in the top navigation bar)
3. In the left sidebar, scroll down to the **"Security"** section
4. Click on **"Secrets and variables"**
5. Select **"Actions"**

#### 2. Add Repository Secrets

Click the **"New repository secret"** button and add each of the following secrets:

##### Required Secrets

| Secret Name | Description | Value Source |
|-------------|-------------|--------------|
| `OPENAI_API_KEY` | Your OpenAI API key | From your OpenAI account dashboard |
| `YOUTUBE_API_KEY` | Your YouTube Data API key | From Google Cloud Console |
| `YOUTUBE_CLIENT_ID` | OAuth 2.0 client ID | From Google Cloud Console |
| `YOUTUBE_CLIENT_SECRET` | OAuth 2.0 client secret | From Google Cloud Console |
| `YOUTUBE_REFRESH_TOKEN` | OAuth 2.0 refresh token | Generated during OAuth flow |

##### Optional Secrets

| Secret Name | Description | Default in Workflow |
|-------------|-------------|---------------------|
| `VIDEO_DURATION` | Duration for generated videos | `60` |
| `CONTENT_THEME` | Theme for content generation | `general` |

#### 3. How to Add Each Secret

For each secret:

1. Click **"New repository secret"**
2. Enter the **Name** (e.g., `OPENAI_API_KEY`)
3. Enter the **Value** (your actual API key)
4. Click **"Add secret"**

**Important Security Notes:**
- Never commit API keys or secrets to your repository
- Use different API keys for development and production
- Regularly rotate your API keys
- Monitor API usage for unexpected activity

### How GitHub Actions Uses These Secrets

GitHub Actions workflows access these secrets using the `secrets` context. Here's how they're typically used in workflow files:

```yaml
# Example workflow step
- name: Generate Content
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
  run: python main.py
```

The secrets are:
- Automatically masked in workflow logs
- Only accessible to workflows in the repository
- Encrypted at rest by GitHub
- Available as environment variables during workflow execution

## Local Development

### Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Copy and configure your environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your local API keys
   ```

### Running Locally

```bash
python main.py
```

### Testing

```bash
# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=.
```

## Usage

### Automated Workflow

The GitHub Actions workflow automatically:
1. Generates content using OpenAI API
2. Creates video content
3. Uploads to YouTube on a scheduled basis

### Manual Execution

To run manually:

```bash
python main.py --generate --upload
```

### Command Line Options

```bash
python main.py --help
```

Options:
- `--generate`: Generate new content
- `--upload`: Upload to YouTube
- `--theme THEME`: Specify content theme
- `--duration SECONDS`: Set video duration

## API Setup Guides

### OpenAI API Setup

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key and add it to your GitHub secrets as `OPENAI_API_KEY`

### YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the YouTube Data API v3
4. Create credentials (API key and OAuth 2.0 client)
5. Configure OAuth consent screen
6. Add the credentials to your GitHub secrets

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues:

1. Check the [Issues](https://github.com/baysbestshorts-eng/yt-shorts-autogen/issues) page
2. Review the API documentation for external services
3. Ensure all environment variables are correctly configured
4. Verify your API keys have the necessary permissions

## Security

- Keep your API keys secure and never commit them to version control
- Use environment variables for all sensitive configuration
- Regularly rotate your API keys
- Monitor your API usage for unexpected activity
- Report security vulnerabilities through GitHub's security advisory feature