import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = BASE_DIR / "storage"
PLANTILLAS_DIR = STORAGE_DIR / "plantillas_base"
LICITACIONES_DATA_DIR = STORAGE_DIR / "licitaciones_data"

PLANTILLAS_DIR.mkdir(parents=True, exist_ok=True)
LICITACIONES_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Credenciales de sistema
CHILECOMPRA_TICKET = os.getenv("CHILECOMPRA_TICKET", "")
MONGO_URI = os.getenv("MONGO_URI", "")

# Keys de Inteligencia Artificial
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]