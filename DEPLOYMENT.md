# Deployment Guide

This document provides detailed instructions for deploying the GitHub Repository Analyzer on different platforms.

## Table of Contents

1. [GitHub Deployment](#github-deployment)
2. [Hugging Face Spaces Deployment](#hugging-face-spaces-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Continuous Integration](#continuous-integration)
5. [Monitoring](#monitoring)

## GitHub Deployment

### Creating a GitHub Repository

1. Log in to your GitHub account
2. Click "New repository" button
3. Enter repository name (e.g., "github-repo-analyzer")
4. Add a description
5. Choose visibility (public or private)
6. Initialize with README.md
7. Add MIT license
8. Click "Create repository"

### Pushing Code to GitHub

```bash
# Initialize git repository locally
git init

# Add the remote repository
git remote add origin https://github.com/yourusername/github-repo-analyzer.git

# Add all files
git add .

# Commit changes
git commit -m "Initial commit"

# Push to GitHub
git push -u origin main
```

### Setting Up GitHub Pages (Optional)

1. Go to repository Settings
2. Navigate to "Pages" section
3. Choose branch to deploy (usually "main")
4. Select folder (usually "/docs" or "/(root)")
5. Click "Save"
6. Wait for deployment to complete

## Hugging Face Spaces Deployment

### Creating a Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the form:
   - Owner: Your Hugging Face username
   - Space name: "github-repo-analyzer"
   - License: MIT
   - SDK: Streamlit
   - Space hardware: CPU (Standard is sufficient)
   - Visibility: Public or Private

### Deployment Methods

#### Option 1: Connect to GitHub Repository

1. In Space settings, select "Repository"
2. Choose "Link external GitHub repository"
3. Enter your GitHub repository URL
4. Select branch to deploy
5. Click "Save"

#### Option 2: Direct File Upload

1. In your Space, click "Files" tab
2. Upload all project files directly:
   - main.py
   - github_api.py
   - code_analysis.py
   - visualization.py
   - utils.py
   - styles.css
   - .streamlit/config.toml
   - README_HUGGINGFACE.md (rename to README.md)

### Required Files for Hugging Face Spaces

Ensure your repository contains these files:

1. `requirements.txt` - List all dependencies

   ```
   streamlit>=1.20.0
   pandas>=1.5.0
   plotly>=5.10.0
   requests>=2.28.0
   transformers>=4.25.0
   torch>=2.0.0
   ```

2. `README.md` - Documentation (use README_HUGGINGFACE.md content)

3. `.streamlit/config.toml` - Streamlit configuration
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 7860  # Hugging Face uses port 7860 by default
   ```

## Environment Configuration

### GitHub Secrets

1. Go to repository Settings
2. Select "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add `GITHUB_TOKEN` with your personal access token
5. Click "Add secret"

### Hugging Face Space Secrets

1. Open your Space settings
2. Click "Repository Secrets"
3. Add `GITHUB_TOKEN` with your personal access token
4. Click "Add secret"

## Continuous Integration

### GitHub Actions

Create a workflow file at `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Lint with flake8
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      - name: Test with pytest
        run: |
          pytest

  deploy:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Hugging Face Spaces
        uses: huggingface/huggingface-spaces-deploy-action@main
        with:
          token: ${{ secrets.HF_TOKEN }}
          space_id: yourusername/github-repo-analyzer
```

## Monitoring

### Hugging Face Spaces Monitoring

1. Go to your Space Settings
2. Navigate to "Hardware" tab to monitor:
   - CPU usage
   - Memory usage
   - Disk usage
3. Check Space logs to troubleshoot issues

### Custom Monitoring (Optional)

Add monitoring code to your Streamlit application:

```python
import logging
import streamlit as st
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Add logging throughout your application
def log_repository_analysis(repo_url, analysis_options):
    """Log repository analysis attempts"""
    logging.info(f"Repository analysis requested: {repo_url}")
    logging.info(f"Analysis options: {analysis_options}")
```

## Updating Your Deployment

### GitHub Repository

```bash
# Make changes locally
git add .
git commit -m "Update application features"
git push origin main
```

### Hugging Face Spaces

If connected to GitHub, your Space will automatically update when you push to your repository.

For manual updates:

1. Go to your Space
2. Click "Files" tab
3. Upload or edit files directly

## Troubleshooting

### Common Deployment Issues

1. **Dependencies Missing**

   - Check requirements.txt is complete
   - Verify Hugging Face Spaces requirements

2. **Port Configuration**

   - Ensure Streamlit config uses correct port (7860 for Hugging Face)

3. **API Rate Limiting**

   - Add GITHUB_TOKEN to environment secrets
   - Implement retry logic for API calls

4. **Memory/CPU Limitations**
   - Optimize code for performance
   - Limit number of files analyzed
   - Consider upgrading Space hardware
