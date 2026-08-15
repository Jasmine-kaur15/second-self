"""Phase 3: Auto-Linking. Computes embeddings for wiki notes and injects bidirectional links."""

import os
import numpy as np
from lib.storage import parse_markdown_with_frontmatter, WIKI_DIR
from lib.embeddings import load_embeddings_cache, save_embeddings_cache, compute_embeddings, compute_similarity

EMBEDDINGS_FILE = os.path.join("data", "embeddings.pkl")
SIMILARITY_THRESHOLD = 0.65
FALLBACK_SIMILARITY = 0.35
MAX_FALLBACK_LINKS = 3

def main():
    print("Starting Auto-Linking process...")
    
    if not os.path.exists(WIKI_DIR):
        print("No wiki directory found. Nothing to link.")
        return
        
    cache = load_embeddings_cache(EMBEDDINGS_FILE)
    
    # 1. Discover all wiki files
    wiki_files = [f for f in os.listdir(WIKI_DIR) if f.endswith('.md')]
    
    if not wiki_files:
        print("No files in wiki directory.")
        return
        
    # 2. Find missing embeddings
    missing_uuids = []
    missing_texts = []
    all_uuids = []
    
    for filename in wiki_files:
        uuid_str = filename[:-3] # strip .md
        all_uuids.append(uuid_str)
        
        if uuid_str not in cache:
            filepath = os.path.join(WIKI_DIR, filename)
            try:
                metadata, content = parse_markdown_with_frontmatter(filepath)
                
                # Embed a combination of rich metadata and content for better semantic clustering
                summary = metadata.get('summary', '')
                para = metadata.get('para', 'Uncategorized')
                tags_list = metadata.get('tags', [])
                tags = ", ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
                
                text_to_embed = f"Title: {summary}\nCategory: {para}\nTags: {tags}\nSummary: {summary}\nContent: {content}".strip()
                
                if not text_to_embed:
                    continue
                missing_uuids.append(uuid_str)
                missing_texts.append(text_to_embed)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
    # 3. Compute missing embeddings
    if missing_uuids:
        print(f"Computing embeddings for {len(missing_uuids)} new/modified notes...")
        try:
            embeddings = compute_embeddings(missing_texts)
            for i, uuid_str in enumerate(missing_uuids):
                cache[uuid_str] = embeddings[i]
            save_embeddings_cache(EMBEDDINGS_FILE, cache)
            print("Successfully updated embeddings cache.")
        except Exception as e:
            print(f"Error computing embeddings: {e}")
            return
    else:
        print("All notes are already embedded. No new embeddings needed.")
        
    if len(cache) < 2:
        print("Not enough embedded notes to compute similarities (need at least 2).")
        return
        
    # 4. Compute pairwise similarities
    print("Computing similarities and injecting links...")
    
    valid_uuids = [u for u in all_uuids if u in cache]
    if len(valid_uuids) < 2:
        print("Not enough valid embedded notes.")
        return
        
    embeddings_matrix = np.array([cache[u] for u in valid_uuids])
    
    try:
        sim_matrix = compute_similarity(embeddings_matrix, embeddings_matrix)
        
        # Verify normalization
        assert np.max(sim_matrix) <= 1.001, "Similarity exceeds 1.0 - embeddings might not be normalized properly."
        assert np.min(sim_matrix) >= -1.001, "Similarity below -1.0 - embeddings might not be normalized properly."
        
    except Exception as e:
        print(f"Error computing similarities: {e}")
        return
        
    links_to_add = {u: set() for u in valid_uuids}
    
    total_pairs = 0
    sim_scores = []
    
    # Track which nodes have high similarity links
    has_high_sim = {u: False for u in valid_uuids}
    
    for i in range(len(valid_uuids)):
        for j in range(i + 1, len(valid_uuids)):
            score = float(sim_matrix[i][j])
            sim_scores.append(score)
            total_pairs += 1
            
            if score >= SIMILARITY_THRESHOLD:
                u1 = valid_uuids[i]
                u2 = valid_uuids[j]
                links_to_add[u1].add(u2)
                links_to_add[u2].add(u1)
                has_high_sim[u1] = True
                has_high_sim[u2] = True
                
    # Fallback for isolated nodes: connect to top 3 if > FALLBACK_SIMILARITY
    for i in range(len(valid_uuids)):
        if not has_high_sim[valid_uuids[i]]:
            u1 = valid_uuids[i]
            # Get scores for this node against all others
            node_scores = []
            for j in range(len(valid_uuids)):
                if i != j:
                    node_scores.append((float(sim_matrix[i][j]), valid_uuids[j]))
                    
            # Sort descending
            node_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Take top 3 above fallback threshold
            added = 0
            for score, u2 in node_scores:
                if score >= FALLBACK_SIMILARITY and added < MAX_FALLBACK_LINKS:
                    links_to_add[u1].add(u2)
                    links_to_add[u2].add(u1) # bidirectional
                    added += 1
                
    # 5. Inject bidirectional links into markdown files
    links_injected = 0
    files_updated = 0
    total_links_created = sum(len(v) for v in links_to_add.values()) // 2
    
    print("\nModifying files:")
    for uuid_str, related_uuids in links_to_add.items():
        if not related_uuids:
            continue
            
        filepath = os.path.join(WIKI_DIR, f"{uuid_str}.md")
        if not os.path.exists(filepath):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                full_content = f.read()
                
            added_any = False
            
            # Find or append Related Notes section
            if "## Related Notes\n" not in full_content and "## Related Notes\r\n" not in full_content:
                # Add trailing newline if missing
                if not full_content.endswith('\n'):
                    full_content += "\n"
                full_content += "\n## Related Notes\n"
                
            # Create a clean block of content to check for existing links
            lines = full_content.split('\n')
            
            # Append new links to the end of the file
            new_lines = []
            for r_uuid in related_uuids:
                link_str = f"[[{r_uuid}]]"
                if link_str not in full_content:
                    new_lines.append(f"- {link_str}")
                    added_any = True
                    links_injected += 1
                    
            if added_any:
                # Write back the modified content
                if new_lines:
                    # Make sure there is a newline before we append list items
                    if not full_content.endswith('\n'):
                        full_content += '\n'
                    full_content += '\n'.join(new_lines) + '\n'
                    
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                files_updated += 1
                print(f"  - Updated {uuid_str}.md")
                
        except Exception as e:
            print(f"Error injecting links to {uuid_str}: {e}")
            
    # Calculate stats
    avg_sim = sum(sim_scores) / len(sim_scores) if sim_scores else 0
    max_sim = max(sim_scores) if sim_scores else 0
    min_sim = min(sim_scores) if sim_scores else 0
            
    print("\n" + "="*40)
    print("Auto-Linking Complete")
    print("="*40)
    print(f"Total notes            : {len(valid_uuids)}")
    print(f"Total pair comparisons : {total_pairs}")
    print(f"Average similarity     : {avg_sim:.4f}")
    print(f"Highest similarity     : {max_sim:.4f}")
    print(f"Lowest similarity      : {min_sim:.4f}")
    print(f"High threshold         : {SIMILARITY_THRESHOLD}")
    print(f"Fallback threshold     : {FALLBACK_SIMILARITY}")
    print(f"Links created          : {total_links_created}")
    print(f"Files updated          : {files_updated}")
    print("="*40)

if __name__ == "__main__":
    main()
