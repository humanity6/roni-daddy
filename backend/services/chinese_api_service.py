"""Chinese manufacturer API service"""

from backend.config.settings import CHINESE_API_BASE_URL

class ChineseAPIService:
    """Service for communicating with Chinese manufacturer API"""
    
    def __init__(self):
        self.base_url = CHINESE_API_BASE_URL
    
    @staticmethod
    def get_api_base_url():
        """Get the base URL for Chinese API"""
        return CHINESE_API_BASE_URL