# memory/__init__.py
import json
import os
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "user_data.json"

DEFAULT_DATA = {
    "user_context": [],
    "preferences": {},
    "memories": []
}

def load_user_data():
    if not MEMORY_FILE.exists():
        return DEFAULT_DATA.copy()
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_DATA.copy()

def save_user_data(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
