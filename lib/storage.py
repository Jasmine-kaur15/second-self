import os
import json

DATA_DIR = "data"
RAW_DIR = "raw"
WIKI_DIR = "wiki"
HASHES_FILE = os.path.join(DATA_DIR, "hashes.json")

def load_json(filepath: str, default_val=None):
    if default_val is None:
        default_val = {}
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_val

def save_json(filepath: str, data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def is_duplicate(content_hash: str) -> bool:
    hashes = load_json(HASHES_FILE, default_val=[])
    return content_hash in hashes

def add_hash(content_hash: str):
    hashes = load_json(HASHES_FILE, default_val=[])
    if content_hash not in hashes:
        hashes.append(content_hash)
        save_json(HASHES_FILE, hashes)

def save_raw_capture(uuid_str: str, content: str, metadata: dict):
    os.makedirs(RAW_DIR, exist_ok=True)
    filepath = os.path.join(RAW_DIR, f"{uuid_str}.md")
    
    # Store metadata as YAML frontmatter
    header = "---\n"
    for k, v in metadata.items():
        header += f"{k}: {v}\n"
    header += "---\n\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header + content)
