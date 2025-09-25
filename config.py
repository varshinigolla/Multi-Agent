import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

# System Configuration
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
MAX_AGENTS = 10

# Financial Data Configuration
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1mo"
