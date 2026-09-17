from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VOICES_DIR = BASE_DIR / "voices"
OUTPUT_DIR = BASE_DIR / "output"

# Garantir criação dos diretórios caso não existam
DATA_DIR.mkdir(parents=True, exist_ok=True)
VOICES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = DATA_DIR / "settings.json"
VOICES_FILE = DATA_DIR / "voices.json"
HISTORY_FILE = DATA_DIR / "history.json"
