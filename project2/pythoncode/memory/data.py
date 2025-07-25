import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "user_data.json"

def load_user_data():
    if not MEMORY_FILE.exists():
        return {"user_context": []}
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user_data(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
