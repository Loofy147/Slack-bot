"""
إعدادات التطبيق المركزية
"""
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """إعدادات التطبيق"""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')

    # Application Configuration
    PORT = int(os.getenv('PORT', "3000"))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # File Paths
    PROMPTS_DIR = 'prompts'
    EXAMPLES_DIR = 'examples'
    LOGS_DIR = 'logs'

    # Processing Configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))

    @classmethod
    def validate_required_vars(cls, required_vars):
        """التحقق من وجود المتغيرات المطلوبة"""
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        return missing_vars

    @classmethod
    def is_slack_configured(cls):
        """التحقق من إعداد Slack"""
        return all([cls.SLACK_BOT_TOKEN, cls.SLACK_SIGNING_SECRET])

    @classmethod
    def is_openai_configured(cls):
        """التحقق من إعداد OpenAI"""
        return bool(cls.OPENAI_API_KEY)
