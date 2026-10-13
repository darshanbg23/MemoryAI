import os
import sys
import struct
import math
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_client = None

if _API_KEY:
    from google import genai
    _client = genai.Client(api_key=_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
_USER_ID = "user"

_cache_lock = threading.Lock()
_embedding_cache = None
_norm_cache = {}

def _invalidate_cache():
    global _embedding_cache, _norm_cache
    with _cache_lock:
        _embedding_cache = None
        _norm_cache = {}

def _compute_norm(vec):
    return math.sqrt(sum(v * v for v in vec))

def generate_embedding(text):
    if not _client or not text or not text.strip():
        return None
    try:
        response = _client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"[WARN] Embedding generation failed: {e}")
        return None

def _serialize_embedding(embedding):
    return struct.pack(f"{len(embedding)}f", *embedding)

def _deserialize_embedding(blob):
    count = len(blob) // 4
    return list(struct.unpack(f"{count}f", blob))

def store_embedding(message_id, text, embedding, importance_score=None, category=None):
    from database import get_connection
    conn = get_connection()
    conn.execute(
        "INSERT INTO embeddings (message_id, user_id, text, embedding, importance_score, category) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (message_id, _USER_ID, text, _serialize_embedding(embedding), importance_score, category),
    )
    conn.commit()
    _invalidate_cache()

def get_all_embeddings():
    global _embedding_cache
    with _cache_lock:
        if _embedding_cache is not None:
            return _embedding_cache

    from database import get_connection
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, message_id, text, embedding, importance_score, pinned, category "
        "FROM embeddings WHERE user_id = ? ORDER BY id",
        (_USER_ID,),
    ).fetchall()

    result = []
    for row in rows:
        emb_vec = _deserialize_embedding(row["embedding"])
        result.append({
            "id": row["id"],
            "message_id": row["message_id"],
            "text": row["text"],
            "embedding": emb_vec,
            "importance_score": row["importance_score"],
            "pinned": bool(row["pinned"]),
            "category": row["category"],
        })

    with _cache_lock:
        _embedding_cache = result
        _norm_cache.clear()
        for entry in result:
            _norm_cache[entry["id"]] = _compute_norm(entry["embedding"])

    return result

def get_embedding_count():
    from database import get_connection
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM embeddings WHERE user_id = ?",
        (_USER_ID,),
    ).fetchone()
    return row["cnt"]

def delete_all_embeddings():
    from database import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM embeddings WHERE user_id = ?", (_USER_ID,))
    conn.commit()
    _invalidate_cache()

def delete_embedding(embedding_id):
    from database import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM embeddings WHERE id = ? AND user_id = ?",
                 (embedding_id, _USER_ID))
    conn.commit()
    _invalidate_cache()

def update_embedding_text(embedding_id, new_text, new_embedding):
    from database import get_connection
    conn = get_connection()
    conn.execute(
        "UPDATE embeddings SET text = ?, embedding = ? WHERE id = ? AND user_id = ?",
        (new_text, _serialize_embedding(new_embedding), embedding_id, _USER_ID),
    )
    conn.commit()
    _invalidate_cache()

def toggle_pin(embedding_id, pinned):
    from database import get_connection
    conn = get_connection()
    conn.execute(
        "UPDATE embeddings SET pinned = ? WHERE id = ? AND user_id = ?",
        (1 if pinned else 0, embedding_id, _USER_ID),
    )
    conn.commit()
    _invalidate_cache()

def update_embedding_category(embedding_id, category):
    from database import get_connection
    conn = get_connection()
    conn.execute(
        "UPDATE embeddings SET category = ? WHERE id = ? AND user_id = ?",
        (category, embedding_id, _USER_ID),
    )
    conn.commit()
    _invalidate_cache()

def get_pinned_embeddings():
    from database import get_connection
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, text FROM embeddings WHERE user_id = ? AND pinned = 1 ORDER BY id",
        (_USER_ID,),
    ).fetchall()
    return [{"id": row["id"], "text": row["text"]} for row in rows]

def export_all_memories():
    from database import get_connection
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, message_id, text, importance_score, pinned, category "
        "FROM embeddings WHERE user_id = ? ORDER BY id",
        (_USER_ID,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "message_id": row["message_id"],
            "text": row["text"],
            "importance_score": row["importance_score"],
            "pinned": bool(row["pinned"]),
            "category": row["category"],
        }
        for row in rows
    ]

def semantic_search(query_text, top_k=10):
    query_embedding = generate_embedding(query_text)
    if query_embedding is None:
        return []

    all_emb = get_all_embeddings()
    if not all_emb:
        return []

    query_norm = _compute_norm(query_embedding)
    if query_norm == 0.0:
        return []

    scored = []
    for entry in all_emb:
        sim = _fast_cosine_similarity(query_embedding, query_norm, entry)
        scored.append({
            "id": entry["id"],
            "text": entry["text"],
            "similarity": round(sim, 4),
            "importance_score": entry.get("importance_score"),
            "pinned": entry.get("pinned", False),
            "category": entry.get("category"),
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]

def _fast_cosine_similarity(query_vec, query_norm, entry):
    stored_vec = entry["embedding"]
    stored_norm = _norm_cache.get(entry["id"])
    if stored_norm is None:
        stored_norm = _compute_norm(stored_vec)

    if query_norm == 0.0 or stored_norm == 0.0:
        return 0.0

    dot = sum(a * b for a, b in zip(query_vec, stored_vec))
    return dot / (query_norm * stored_norm)

def cosine_similarity(vec_a, vec_b):
    if len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
