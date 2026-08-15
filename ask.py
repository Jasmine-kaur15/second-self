"""Phase 4.1: RAG Search. Uses embeddings to retrieve relevant notes and Groq LLM to answer questions citing source UUIDs."""

import os
import numpy as np
from lib.embeddings import load_embeddings_cache, compute_embeddings, compute_similarity
from lib.storage import WIKI_DIR, parse_markdown_with_frontmatter
from lib.llm import get_groq_client

EMBEDDINGS_FILE = os.path.join("data", "embeddings.pkl")
TOP_K = 3

def ask(query: str) -> str:
    """
    Executes a Retrieval-Augmented Generation (RAG) search.
    1. Embeds the user query.
    2. Finds the top-k most similar notes in the wiki.
    3. Prompts the LLM to answer the query using only the retrieved notes.
    """
    print(f"Embedding query: '{query}'")
    
    # 1. Embed query
    try:
        query_emb = compute_embeddings([query])[0]
    except Exception as e:
        return f"Error: Failed to embed query. {e}"
        
    # 2. Retrieve top K notes
    cache = load_embeddings_cache(EMBEDDINGS_FILE)
    if not cache:
        return "Your brain is currently empty! Please capture some notes and run the pipeline first."
        
    uuids = list(cache.keys())
    embeddings_matrix = np.array([cache[u] for u in uuids])
    
    # Compute similarity between query and all notes
    sim_scores = compute_similarity(query_emb.reshape(1, -1), embeddings_matrix)[0]
    
    # Get top K indices
    top_indices = np.argsort(sim_scores)[::-1][:TOP_K]
    
    context_chunks = []
    retrieved_uuids = []
    
    print(f"Found top {TOP_K} relevant notes:")
    for idx in top_indices:
        uuid_str = uuids[idx]
        score = sim_scores[idx]
        print(f" - {uuid_str} (Score: {score:.4f})")
        
        filepath = os.path.join(WIKI_DIR, f"{uuid_str}.md")
        if os.path.exists(filepath):
            try:
                metadata, content = parse_markdown_with_frontmatter(filepath)
                # Prepare a chunk of text containing metadata and content
                title = metadata.get("summary", uuid_str)
                chunk = f"--- NOTE [{uuid_str}] ---\nTitle/Summary: {title}\nContent:\n{content}\n"
                context_chunks.append(chunk)
                retrieved_uuids.append(uuid_str)
            except Exception as e:
                print(f"   Error reading {filepath}: {e}")
                
    if not context_chunks:
        return "I couldn't read the retrieved notes from the wiki. Have they been processed?"
        
    context_text = "\n".join(context_chunks)
    
    # 3. Prompt LLM
    print("Synthesizing answer with LLM...")
    prompt = f"""
You are "The Oracle", an AI assistant built on top of the user's personal knowledge base.
You must answer the user's query using strictly the context provided below.

Rules:
1. Base your answer ONLY on the provided notes. Do not use outside knowledge.
2. If the context does not contain the answer, politely say: "I don't have enough information in your notes to answer that."
3. You MUST cite the source of your information using the exact note ID in double brackets. For example: "According to your notes [[d41d8cd98f00b204e9800998ecf8427e]], the project is due on Friday."
4. Be clear, concise, and helpful.

User Query:
{query}

Context (Retrieved Notes):
{context_text}
"""

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful and precise knowledge retrieval assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Low temperature for factual RAG
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: Failed to synthesize answer with Groq. {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        answer = ask(query)
        print("\n=== ANSWER ===")
        print(answer)
    else:
        print("Usage: python ask.py \"your question here\"")
