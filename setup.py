"""
Setup script for the travel itinerary tool.
"""
import os
import subprocess
import sys

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def setup_environment():
    """Set up environment file."""
    env_file = ".env"
    env_example = "env_example.txt"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print("Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created! Please edit it with your API keys.")
        else:
            print("❌ env_example.txt not found!")
            return False
    else:
        print("✅ .env file already exists!")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Travel Itinerary Tool...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Setup environment
    if not setup_environment():
        return
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Run: streamlit run streamlit_app.py")
    print("3. Open your browser to the provided URL")
    print("\nRequired API keys:")
    print("- OpenAI API key (for itinerary generation)")
    print("- Tavily API key (for search)")
    print("- SerpAPI key (for additional search)")

if __name__ == "__main__":
    main()

