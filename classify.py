"""Phase 2: Classification. Uses Groq LLM to categorize raw captures into PARA, extract tags, and summarize. Updates index.json."""

import os
from lib.storage import load_json, save_json, RAW_DIR, parse_markdown_with_frontmatter, save_wiki_page
from lib.llm import classify_content

INDEX_FILE = os.path.join("data", "index.json")

def main():
    print("Starting classification process...")
    index = load_json(INDEX_FILE, default_val={})
    
    if not os.path.exists(RAW_DIR):
        print("No raw directory found. Nothing to classify.")
        return
        
    for filename in os.listdir(RAW_DIR):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(RAW_DIR, filename)
        uuid_str = filename[:-3] # remove .md
        
        if uuid_str in index:
            # print(f"Skipping {uuid_str}, already classified.")
            continue
            
        print(f"Classifying {uuid_str}...")
        try:
            metadata, content = parse_markdown_with_frontmatter(filepath)
            
            if not content.strip():
                print(f"Skipping {uuid_str}, content is empty.")
                continue
                
            # Use LLM to classify
            classification = classify_content(content)
            
            # Merge metadata
            for k, v in classification.items():
                metadata[k] = v
                
            # Save to wiki
            save_wiki_page(uuid_str, content, metadata)
            
            # Update index
            index[uuid_str] = {
                "status": "classified",
                "para": classification.get("para"),
                "tags": classification.get("tags")
            }
            save_json(INDEX_FILE, index)
            print(f"\nDocument: {uuid_str}")
            print(f"Predicted PARA: {classification.get('para')}")
            print(f"Confidence: {classification.get('confidence', 'Unknown')}")
            print(f"Summary: {classification.get('summary')}")
            print(f"Tags: {', '.join(classification.get('tags', []))}")
            
        except Exception as e:
            print(f"Error classifying {uuid_str}: {e}")

if __name__ == "__main__":
    main()
