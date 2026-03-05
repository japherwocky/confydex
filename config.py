"""
Configuration management - loads from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "./data")
DATABASE_URL = os.getenv("DATABASE_URL", "confydex.db")

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Embedding config
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# Search weights
KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", "0.5"))
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.5"))

# API config
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Frontend config
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5173"))

# Upload directory
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "./uploads")

# LLM config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# OpenCode Go
OPENCODE_GO_API_KEY = os.getenv("OPENCODE_GO_API_KEY", "")
OPENCODE_GO_MODEL = os.getenv("OPENCODE_GO_MODEL", "glm-5")  # glm-5, kimi-k2.5, or minimax-m2.5
