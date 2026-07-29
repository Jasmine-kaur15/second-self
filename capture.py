import argparse
import sys
import uuid
from datetime import datetime, timezone
from lib.extract import extract_content, get_sha256
from lib.storage import is_duplicate, add_hash, save_raw_capture

def main():
    parser = argparse.ArgumentParser(description="SecondSelf: Capture anything (Text, URL, File)")
    parser.add_argument("input", type=str, help="The text string, URL, or file path to capture")
    args = parser.parse_args()

    try:
        print("Extracting content...")
        source_type, content = extract_content(args.input)
        
        print("Checking for duplicates...")
        content_hash = get_sha256(content)
        if is_duplicate(content_hash):
            print("Error: This content has already been captured (duplicate detected).")
            sys.exit(0)
            
        capture_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        metadata = {
            "id": capture_id,
            "timestamp": timestamp,
            "source": args.input,
            "source_type": source_type,
            "content_hash": content_hash
        }
        
        save_raw_capture(capture_id, content, metadata)
        add_hash(content_hash)
        
        print(f"Success! Captured as {capture_id}.md in raw/")
        
    except Exception as e:
        print(f"Capture failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
