"""Configuration du projet TelecomPlus"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ========================================
# Google Gemini Configuration
# ========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        " GOOGLE_API_KEY manquante!\n"
        "Ajoutez-la dans le fichier .env : GOOGLE_API_KEY=AIzaSy..."
    )

# Modèles Gemini
LLM_MODEL = "gemini-2.5-flash"  # Latest stable model
LLM_TEMPERATURE = 0
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Local free embeddings

# ========================================
# Langfuse Configuration
# ========================================
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

ENABLE_MONITORING = bool(LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)

if ENABLE_MONITORING:
    print(" Monitoring Langfuse activé")
else:
    print(" Monitoring Langfuse désactivé (clés manquantes)")

# ========================================
# Chemins du projet
# ========================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore_db"

# Fichiers Excel
CLIENTS_FILE = DATA_DIR / "clients.xlsx"
FORFAITS_FILE = DATA_DIR / "forfaits.xlsx"
ABONNEMENTS_FILE = DATA_DIR / "abonnements.xlsx"
CONSOMMATION_FILE = DATA_DIR / "consommation.xlsx"
FACTURES_FILE = DATA_DIR / "factures.xlsx"
TICKETS_FILE = DATA_DIR / "tickets_support.xlsx"
EVAL_QUESTIONS_FILE = DATA_DIR / "evaluation_questions.xlsx"

# ========================================
# Configuration RAG
# ========================================
CHUNK_SIZE = 1200  # Larger chunks to fit full model descriptions
CHUNK_OVERLAP = 700  # Higher overlap to ensure model names + years stay together across page breaks
TOP_K_RESULTS = 10  # Good coverage