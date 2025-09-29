"""
Configuration management for the travel itinerary tool.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing API keys and settings."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
    
    # Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_required_keys(cls):
        """Validate that all required API keys are present."""
        required_keys = {
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'TAVILY_API_KEY': cls.TAVILY_API_KEY,
            'SERPAPI_API_KEY': cls.SERPAPI_API_KEY
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    @classmethod
    def get_api_key(cls, service):
        """Get API key for a specific service."""
        key_mapping = {
            'openai': cls.OPENAI_API_KEY,
            'tavily': cls.TAVILY_API_KEY,
            'serpapi': cls.SERPAPI_API_KEY
        }
        
        if service not in key_mapping:
            raise ValueError(f"Unknown service: {service}")
        
        key = key_mapping[service]
        if not key:
            raise ValueError(f"API key for {service} not found")
        
        return key