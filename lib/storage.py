import os
import json
from dotenv import load_dotenv

# Load env variables (useful for local dev, Streamlit Cloud uses st.secrets automatically if configured)
load_dotenv()

# Initialize Supabase
try:
    from supabase import create_client, Client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        # Fallback for Streamlit Cloud
        import streamlit as st
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Warning: Supabase client initialization failed. {e}")
    supabase = None

BUCKET_NAME = "second-self"
DATA_DIR = "data"
RAW_DIR = "raw"
WIKI_DIR = "wiki"
HASHES_FILE = os.path.join(DATA_DIR, "hashes.json").replace("\\", "/")

# ---------------------------------------------------------
# Core Supabase Storage Wrappers
# ---------------------------------------------------------

def ensure_bucket():
    if not supabase: return
    # Try to get bucket, if it doesn't exist, this fails silently or we could create it.
    # We assume the user created it manually as per instructions.
    pass

def read_bytes(filepath: str) -> bytes:
    """Read file as bytes from Supabase Storage."""
    if not supabase: raise ValueError("Supabase client not initialized")
    filepath = filepath.replace("\\", "/")
    res = supabase.storage.from_(BUCKET_NAME).download(filepath)
    return res

def write_bytes(filepath: str, data: bytes):
    """Write bytes to Supabase Storage."""
    if not supabase: raise ValueError("Supabase client not initialized")
    filepath = filepath.replace("\\", "/")
    try:
        supabase.storage.from_(BUCKET_NAME).upload(filepath, data)
    except Exception as e:
        if "Duplicate" in str(e) or "already exists" in str(e).lower():
            # If it exists, update it
            supabase.storage.from_(BUCKET_NAME).update(filepath, data)
        else:
            raise e

def read_text(filepath: str) -> str:
    """Read file as string from Supabase Storage."""
    data = read_bytes(filepath)
    return data.decode('utf-8')

def write_text(filepath: str, content: str):
    """Write string to Supabase Storage."""
    write_bytes(filepath, content.encode('utf-8'))

def list_files(directory: str) -> list[str]:
    """List filenames in a directory in Supabase Storage."""
    if not supabase: return []
    directory = directory.replace("\\", "/")
    # If directory is empty string, it lists root
    try:
        res = supabase.storage.from_(BUCKET_NAME).list(directory)
        # return list of filenames, ignoring the hidden placeholder '.emptyFolderPlaceholder'
        filenames = [f['name'] for f in res if f['name'] != '.emptyFolderPlaceholder']
        return filenames
    except Exception:
        return []

def file_exists(filepath: str) -> bool:
    """Check if a file exists in Supabase Storage."""
    if not supabase: return False
    filepath = filepath.replace("\\", "/")
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    files = list_files(directory)
    return filename in files

def move_file(old_filepath: str, new_filepath: str):
    """Move a file in Supabase Storage."""
    if not supabase: return
    old_filepath = old_filepath.replace("\\", "/")
    new_filepath = new_filepath.replace("\\", "/")
    supabase.storage.from_(BUCKET_NAME).move(old_filepath, new_filepath)

def delete_file(filepath: str):
    """Delete a file in Supabase Storage."""
    if not supabase: return
    filepath = filepath.replace("\\", "/")
    supabase.storage.from_(BUCKET_NAME).remove([filepath])


# ---------------------------------------------------------
# App-Specific Storage Logic
# ---------------------------------------------------------

def load_json(filepath: str, default_val=None):
    if default_val is None:
        default_val = {}
    if not file_exists(filepath):
        return default_val
    try:
        content = read_text(filepath)
        return json.loads(content)
    except Exception:
        return default_val

def save_json(filepath: str, data):
    content = json.dumps(data, indent=2)
    write_text(filepath, content)

def is_duplicate(content_hash: str) -> bool:
    hashes = load_json(HASHES_FILE, default_val=[])
    return content_hash in hashes

def add_hash(content_hash: str):
    hashes = load_json(HASHES_FILE, default_val=[])
    if content_hash not in hashes:
        hashes.append(content_hash)
        save_json(HASHES_FILE, hashes)

def save_raw_capture(uuid_str: str, content: str, metadata: dict):
    filepath = os.path.join(RAW_DIR, f"{uuid_str}.md").replace("\\", "/")
    
    # Store metadata as YAML frontmatter
    header = "---\n"
    for k, v in metadata.items():
        header += f"{k}: {v}\n"
    header += "---\n\n"
    
    write_text(filepath, header + content)

def parse_markdown_with_frontmatter(filepath: str) -> tuple[dict, str]:
    try:
        content = read_text(filepath)
    except Exception:
        return {}, ""
        
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
    filepath = os.path.join(WIKI_DIR, f"{uuid_str}.md").replace("\\", "/")
    
    header = "---\n"
    for k, v in metadata.items():
        if isinstance(v, list):
            header += f"{k}:\n"
            for item in v:
                header += f"  - {item}\n"
        else:
            header += f"{k}: {v}\n"
    header += "---\n\n"
    
    write_text(filepath, header + content)
