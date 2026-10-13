import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def retrieve_context(query, memory):
    if not memory:
        return ""
    texts = [m.get("text", "") for m in memory if m.get("text")]
    if not texts:
        return ""
    return "\n---\n".join(texts)

def retrieve_full_context(memory):
    if not memory:
        return ""
    texts = [m.get("text", "") for m in memory if m.get("text")]
    return "\n".join(texts)

def retrieve_recent_context(recent_messages):
    if not recent_messages:
        return ""

    lines = []
    for msg in recent_messages:
        role = msg.get("user", "")
        text = msg.get("text", "")
        if not text:
            continue
        if role == "user":
            lines.append(f"USER: {text}")
        elif role == "bot":
            lines.append(f"ASSISTANT: {text}")
    return "\n\n".join(lines)

def retrieve_semantic_context(query, top_k=10, exclude_message_ids=None):
    from retrieval.embedding_service import (
        generate_embedding, get_all_embeddings, cosine_similarity,
    )

    query_embedding = generate_embedding(query)
    if query_embedding is None:
        from memory.memory_store import get_all_messages
        return retrieve_full_context(get_all_messages())

    all_embeddings = get_all_embeddings()
    if not all_embeddings:
        from memory.memory_store import get_all_messages
        return retrieve_full_context(get_all_messages())

    if exclude_message_ids is None:
        exclude_message_ids = set()

    scored = []
    for entry in all_embeddings:
        if entry.get("message_id") in exclude_message_ids:
            continue
        sim = cosine_similarity(query_embedding, entry["embedding"])
        scored.append((sim, entry["text"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_memories = scored[:top_k]

    if not top_memories:
        return ""

    return "\n---\n".join(text for _, text in top_memories)