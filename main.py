import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now imports will work
from src.core.config import settings
from src.core.orchestrator import AIOrchestrator
from src.services.openai_client import OpenAIClient
from src.services.prompt_manager import PromptManager
from src.slack.app import SlackApp
from src.utils.logging import StructuredLogger

def main():
    """Main application entry point"""
    logger = StructuredLogger(__name__)
    logger.setup_logging(settings.log_level)

    try:
        # Initialize services
        openai_client = OpenAIClient()
        prompt_manager = PromptManager()
        orchestrator = AIOrchestrator(openai_client, prompt_manager)

        # Initialize and start Slack bot
        bot = SlackApp()

        logger.logger.info("Starting Slack AI Orchestrator...")

        # This will be an async call
        asyncio.run(bot.start())

    except Exception as e:
        logger.log_error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
