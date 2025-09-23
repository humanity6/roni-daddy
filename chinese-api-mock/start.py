#!/usr/bin/env python3
"""
Chinese API Mock Server Startup Script
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("=" * 60)
    print("🔧 Chinese API Mock Server")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment is configured correctly"""
    env_file = "../.env.local"
    if not os.path.exists(env_file):
        print(f"❌ Environment file not found: {env_file}")
        return False

    with open(env_file, 'r') as f:
        content = f.read()
        if "localhost:9000" in content:
            print("✅ Environment configured for mock mode")
            return True
        else:
            print("⚠️  Environment may not be configured for mock mode")
            print("   Check that CHINESE_API_BASE_URL=http://localhost:9000/mobileShell/en")
            return False

def start_mock_server():
    """Start the mock server"""
    print("\n🚀 Starting Chinese API Mock Server...")
    print("   Server will run on: http://localhost:9000")
    print("   Health check: http://localhost:9000/health")
    print()
    print("📋 Usage Instructions:")
    print("1. Start this mock server (keep running)")
    print("2. In another terminal, run your backend: python api_server.py")
    print("3. In another terminal, run your frontend: npm run dev")
    print("4. The app will use mock Chinese API for offline development")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)

    # Change to the directory containing main.py
    os.chdir(os.path.dirname(__file__))

    try:
        # Start the server
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Mock server stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to start server: {e}")

def main():
    print_banner()

    if not check_dependencies():
        sys.exit(1)

    if not check_environment():
        print("\n⚠️  Proceeding anyway - you may need to check your configuration")

    start_mock_server()

if __name__ == "__main__":
    main()