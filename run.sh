#!/bin/bash
echo "🚀 Setting up Autonomous SRE Incident Response Agent..."

# Install python dependencies
pip install -r requirements.txt

# Launch the Gradio app
echo "✨ Starting Gradio Console..."
python app.py
