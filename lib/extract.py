import os
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import PyPDF2

def get_sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def is_url(string: str) -> bool:
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_from_url(url: str) -> str:
    try:
        # Use a user-agent to avoid getting blocked by simple scrapers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text(separator='\n')
        
        # Basic cleanup: remove excessive blank lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text.strip():
            raise ValueError("Extracted text is empty. Might be a JS-heavy SPA.")
            
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract from URL {url}: {e}")

def extract_from_pdf(filepath: str) -> str:
    try:
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if not text.strip():
            raise ValueError("No extractable text found in PDF (might be a scanned image).")
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract from PDF {filepath}: {e}")

def extract_content(input_string: str) -> tuple[str, str]:
    """Returns (source_type, content)"""
    if not input_string or not input_string.strip():
        raise ValueError("Input string is empty.")
        
    if is_url(input_string):
        return ("url", extract_from_url(input_string))
    
    if os.path.exists(input_string):
        _, ext = os.path.splitext(input_string)
        ext = ext.lower()
        if ext == '.pdf':
            return ("file_pdf", extract_from_pdf(input_string))
        elif ext in ['.txt', '.md', '.csv', '.json']:
            try:
                with open(input_string, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        raise ValueError("File is empty.")
                    return (f"file_{ext[1:]}", content)
            except Exception as e:
                raise ValueError(f"Failed to read file {input_string}: {e}")
        else:
            raise ValueError(f"Unsupported file extension: {ext}. Only PDF, TXT, MD, CSV, JSON supported.")
            
    # Default: Plain text
    return ("text", input_string)
