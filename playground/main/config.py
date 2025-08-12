"""Configuration settings for the RAG system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
GREENHOUSE_API_KEY = os.getenv('GREENHOUSE_API_KEY')

# Model Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
CONTEXT_MODEL = "claude-3-haiku-20240307"
ANSWER_MODEL = "claude-sonnet-4-20250514"

# Retrieval Settings
DEFAULT_TOP_K = 5
MAX_TOKENS_CONTEXT = 150
MAX_TOKENS_ANSWER = 2500
TEMPERATURE = 0.0

# File Paths
DATA_DIR = "../data"
EMPLOYEE_HANDBOOK_PATH = "../data/employee_handbook.json"
BENEFITS_WELLBEING_PATH = "../data/benefits_wellbeing.json"
BENEFITS_MARKDOWN_PATH = "../data/Benefits & Wellbeing.md"
EMPLOYEE_HANDBOOK_MARKDOWN_PATH = "../data/Employee Handbook.md"

# Vector Database Settings
EMBEDDING_BATCH_SIZE = 100
MAX_CHUNK_TOKENS = 7000
OVERLAP_TOKENS = 500
CACHE_TTL_MINUTES = 5 