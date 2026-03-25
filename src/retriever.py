from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_chunks(query, index, all_chunks, selected_category=None, k=10):
    query_vector = model.encode([query])

    distances, indices = index.search(np.array(query_vector), k)

    results = [all_chunks[i] for i in indices[0] if i < len(all_chunks)]

    # Category filter
    if selected_category and selected_category != "All":
        filtered = [r for r in results if r["category"] == selected_category]
        if filtered:
            results = filtered

    # Rerank using simple keyword overlap
    query_words = set(query.lower().split())

    def score(chunk):
        text_words = set(chunk["text"].lower().split())
        return len(query_words & text_words)

    results = sorted(results, key=score, reverse=True)

    return results[:5]