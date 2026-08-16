"""Phase 4.1: RAG Search.
Uses embeddings to retrieve relevant notes and Groq LLM
to answer questions citing source UUIDs.
"""

import os
import numpy as np

from lib.embeddings import (
    load_embeddings_cache,
    compute_embeddings,
    compute_similarity
)
from lib.storage import WIKI_DIR, parse_markdown_with_frontmatter
from lib.llm import get_groq_client


EMBEDDINGS_FILE = os.path.join("data", "embeddings.pkl")

TOP_K = 3

# Prevent very large notes from being sent to the LLM
MAX_CHARS_PER_NOTE = 4000

# Prevent the complete RAG context from becoming too large
# Reduced to 10,000 to stay safely under Groq's 6,000 Tokens Per Minute limit
MAX_CONTEXT_CHARS = 10000


def ask(query: str) -> str:
    """
    Executes a Retrieval-Augmented Generation (RAG) search.

    1. Embeds the user query.
    2. Finds the top-k most similar notes.
    3. Limits the amount of text retrieved from each note.
    4. Sends the relevant context to the Groq LLM.
    """

    print(f"Embedding query: '{query}'")

    # --------------------------------------------------
    # 1. Embed query
    # --------------------------------------------------

    try:
        query_emb = compute_embeddings([query])[0]
    except Exception as e:
        return f"Error: Failed to embed query. {e}"

    # --------------------------------------------------
    # 2. Load embedding cache
    # --------------------------------------------------

    cache = load_embeddings_cache(EMBEDDINGS_FILE)

    if not cache:
        return (
            "Your brain is currently empty! "
            "Please capture some notes and run the pipeline first."
        )

    uuids = list(cache.keys())

    embeddings_matrix = np.array(
        [cache[u] for u in uuids]
    )

    # --------------------------------------------------
    # 3. Compute similarity
    # --------------------------------------------------

    sim_scores = compute_similarity(
        query_emb.reshape(1, -1),
        embeddings_matrix
    )[0]

    # Get top K notes
    top_indices = np.argsort(sim_scores)[::-1][:TOP_K]

    context_chunks = []
    retrieved_uuids = []

    print(f"Found top {TOP_K} relevant notes:")

    # --------------------------------------------------
    # 4. Retrieve notes
    # --------------------------------------------------

    total_chars = 0

    for idx in top_indices:

        uuid_str = uuids[idx]
        score = sim_scores[idx]

        print(
            f" - {uuid_str} "
            f"(Score: {score:.4f})"
        )

        filepath = os.path.join(
            WIKI_DIR,
            f"{uuid_str}.md"
        )

        if not os.path.exists(filepath):
            continue

        try:
            metadata, content = parse_markdown_with_frontmatter(
                filepath
            )

            title = metadata.get(
                "summary",
                uuid_str
            )

            # Limit individual note size
            content = content[:MAX_CHARS_PER_NOTE]

            chunk = (
                f"--- NOTE [{uuid_str}] ---\n"
                f"Title/Summary: {title}\n"
                f"Content:\n{content}\n"
            )

            # Stop if adding this note would exceed
            # the total context limit
            if total_chars + len(chunk) > MAX_CONTEXT_CHARS:

                remaining = MAX_CONTEXT_CHARS - total_chars

                if remaining > 500:
                    chunk = chunk[:remaining]
                    context_chunks.append(chunk)
                    retrieved_uuids.append(uuid_str)

                break

            context_chunks.append(chunk)
            retrieved_uuids.append(uuid_str)

            total_chars += len(chunk)

        except Exception as e:
            print(
                f"   Error reading {filepath}: {e}"
            )

    # --------------------------------------------------
    # 5. Check retrieved context
    # --------------------------------------------------

    if not context_chunks:
        return (
            "I couldn't read the retrieved notes "
            "from the wiki. Have they been processed?"
        )

    context_text = "\n".join(context_chunks)

    print(f"[RAG] Retrieved notes: {len(retrieved_uuids)}")
    print(f"[RAG] Context size: {len(context_text)} characters")
    print(f"[RAG] Context limit: {MAX_CONTEXT_CHARS} characters")
    
    within_limit = "YES" if len(context_text) <= MAX_CONTEXT_CHARS else "NO"
    print(f"[RAG] Request within safe limit: {within_limit}")

    # --------------------------------------------------
    # 6. Build RAG prompt
    # --------------------------------------------------

    prompt = f"""
You are "The Oracle", an AI assistant built on top of
the user's personal knowledge base.

Answer the user's query using ONLY the retrieved notes.

Rules:
1. Do not use outside knowledge.
2. If the answer is not present in the notes, say:
   "I don't have enough information in your notes to answer that."
3. Cite information using the exact note ID in double brackets.
4. Be concise and directly answer the question.

User Query:
{query}

Retrieved Notes:
{context_text}
"""

    # --------------------------------------------------
    # 7. Ask Groq
    # --------------------------------------------------

    print("Synthesizing answer with LLM...")

    try:

        client = get_groq_client()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful and precise "
                        "knowledge retrieval assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=800
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        return (
            f"Error: Failed to synthesize answer "
            f"with Groq. {e}"
        )


if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:

        query = " ".join(sys.argv[1:])

        answer = ask(query)

        print("\n=== ANSWER ===")
        print(answer)

    else:

        print(
            'Usage: python ask.py '
            '"your question here"'
        )