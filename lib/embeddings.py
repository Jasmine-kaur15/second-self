"""Module for generating text embeddings and calculating similarities."""

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Use a small, fast model suitable for semantic search and clustering
MODEL_NAME = 'all-MiniLM-L6-v2'
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def load_embeddings_cache(filepath: str) -> dict:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading embeddings cache from {filepath}: {e}")
    return {}

def save_embeddings_cache(filepath: str, cache: dict):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(cache, f)

def compute_embeddings(texts: list[str]) -> np.ndarray:
    model = get_model()
    # normalize_embeddings=True makes the vectors unit length, allowing fast dot-product for cosine similarity
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

def compute_similarity(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    # Since embeddings are normalized, dot product is equivalent to cosine similarity
    # return np.dot(emb1, emb2.T)
    # Alternatively, use sentence_transformers util (returns tensor, so convert to numpy)
    return util.cos_sim(emb1, emb2).numpy()
