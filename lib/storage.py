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

def parse_markdown_with_frontmatter(filepath: str) -> tuple[dict, str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            header = parts[1]
            body = parts[2]
            metadata = {}
            for line in header.strip().split('\n'):
                if ': ' in line:
                    k, v = line.split(': ', 1)
                    metadata[k.strip()] = v.strip()
            return metadata, body
    return {}, content

def save_wiki_page(uuid_str: str, content: str, metadata: dict):
    os.makedirs(WIKI_DIR, exist_ok=True)
    filepath = os.path.join(WIKI_DIR, f"{uuid_str}.md")
    
    header = "---\n"
    for k, v in metadata.items():
        if isinstance(v, list):
            header += f"{k}:\n"
            for item in v:
                header += f"  - {item}\n"
        else:
            header += f"{k}: {v}\n"
    header += "---\n\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header + content)
