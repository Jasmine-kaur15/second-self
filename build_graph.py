"""Phase 4: Graph Generation. Parses wiki/ directory to generate data/graph.json with nodes, edges, and metadata."""

import os
import re
from datetime import datetime, timezone
from lib.storage import WIKI_DIR, save_json, parse_markdown_with_frontmatter

GRAPH_FILE = os.path.join("data", "graph.json")

def main():
    print("Starting Graph Generation process...")
    
    if not os.path.exists(WIKI_DIR):
        print("No wiki directory found. Nothing to build.")
        return
        
    nodes = []
    edges = []
    
    # Keep track of added edges to avoid duplicates if needed
    # Though directed edges for a knowledge graph are fine
    seen_edges = set()
    
    wiki_files = [f for f in os.listdir(WIKI_DIR) if f.endswith('.md')]
    
    if not wiki_files:
        print("No files in wiki directory.")
        return
        
    for filename in wiki_files:
        uuid_str = filename[:-3] # remove .md
        filepath = os.path.join(WIKI_DIR, filename)
        
        try:
            metadata, content = parse_markdown_with_frontmatter(filepath)
            
            summary = metadata.get("summary", "")
            tags = metadata.get("tags", [])
            group = metadata.get("para", "Archives")
            
            # Extract date from filename if present
            date_prefix = ""
            if len(uuid_str) >= 10 and re.match(r'\d{4}-\d{2}-\d{2}', uuid_str[:10]):
                date_prefix = f"[{uuid_str[:10]}] "

            # Label: use first 30 chars of summary or content
            base_label = summary[:30] + "..." if len(summary) > 30 else summary
            if not base_label:
                base_label = content[:30].strip() + "..." if len(content) > 30 else content.strip()
            
            if not base_label:
                base_label = uuid_str
                
            label = date_prefix + base_label
                
            preview = content[:150].strip() + "..." if len(content) > 150 else content.strip()
            
            color_map = {
                "Projects": "#2B7CE9",
                "Areas": "#109618",
                "Resources": "#FF9900",
                "Archives": "#808080"
            }
            node_color = color_map.get(group, "#808080")
            
            # Formatted tooltip title for UI
            title_html = f"<b>Group:</b> {group}<br>"
            if summary:
                title_html += f"<b>Summary:</b> {summary}<br>"
            if tags:
                title_html += f"<b>Tags:</b> {', '.join(tags)}<br>"
            title_html += f"<b>Preview:</b> {preview}"
            
            # Node object
            node = {
                "id": uuid_str,
                "label": label,
                "title": title_html,
                "group": group,
                "color": node_color,
                "summary": summary,
                "tags": tags,
                "preview": preview
            }
            nodes.append(node)
            
            # Extract edges
            # Matches [[UUID]]
            links = re.findall(r'\[\[(.*?)\]\]', content)
            for target_id in links:
                edge_tuple = (uuid_str, target_id)
                # optionally, keep it directed or undirected. Let's do directed for simplicity
                if edge_tuple not in seen_edges:
                    edges.append({
                        "source": uuid_str,
                        "target": target_id
                    })
                    seen_edges.add(edge_tuple)
                    
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    # Compile Graph Data
    graph_data = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
    }
    
    save_json(GRAPH_FILE, graph_data)
    print(f"Graph generated successfully: {len(nodes)} nodes, {len(edges)} edges saved to {GRAPH_FILE}.")

if __name__ == "__main__":
    main()
