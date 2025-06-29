#!/usr/bin/env python3
"""
Launcher script for the AI Image Generator
GPT-4o Powered - 100% Python Application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'openai', 'requests', 'pillow', 'python-dotenv']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                import dotenv
            elif package == 'pillow':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Installing missing packages...")
        for package in missing:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package])

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("Creating a template .env file...")
        with open('.env', 'w') as f:
            f.write("OPENAI_API_KEY=sk-your-api-key-here\n")
        print("Please edit the .env file and add your OpenAI API key")
        return False
    
    # Check if API key is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'sk-your-api-key-here' in content or 'OPENAI_API_KEY=' not in content:
            print("⚠️  Please set your OpenAI API key in the .env file")
            return False
    
    return True

def main():
    """Main launcher function"""
    print("🎨 AI Image Generator - GPT-image-1 Powered")
    print("Advanced AI Art Creation with Reference Image Support")
    print("=" * 55)
    
    # Check requirements
    print("Checking Python requirements...")
    check_requirements()
    
    # Check environment
    print("Checking environment configuration...")
    if not check_env_file():
        print("\n❌ Please configure your OpenAI API key in the .env file before continuing.")
        print("💡 The application uses GPT-image-1 exclusively for advanced image generation")
        input("Press Enter to exit...")
        return
    
    # Start application
    print("Starting AI Image Generator...")
    print("🚀 Features:")
    print("   • GPT-image-1 powered image generation")
    print("   • Multiple reference image support (up to 10)")
    print("   • Advanced format options (PNG, JPEG, WEBP)")
    print("   • Transparent background support")
    print("   • Customizable compression settings")
    print("   • Gallery with filters")
    
    app_file = Path(__file__).parent / "ai_image_generator.py"
    
    if not app_file.exists():
        print(f"Error: {app_file} not found!")
        sys.exit(1)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            str(app_file),
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false'
        ])
    except KeyboardInterrupt:
        print("\nShutting down application...")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main() 