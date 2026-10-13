import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_store import (
    USER_ID, BOT_ID,
    store_message, get_all_messages, get_message_count, clear_all_messages,
    get_recent_messages as _get_recent_messages,
    get_total_message_count, get_oldest_messages, delete_oldest_messages,
    create_conversation, get_conversations, get_conversation,
    get_conversation_messages, clear_conversation_messages, delete_conversation,
    update_conversation_title,
)
from retrieval.context_retriever import (
    retrieve_full_context, retrieve_semantic_context, retrieve_recent_context,
)
from retrieval.embedding_service import (
    generate_embedding, store_embedding,
    delete_embedding as _delete_embedding,
    update_embedding_text as _update_embedding_text,
    update_embedding_category as _update_embedding_category,
    toggle_pin as _toggle_pin,
    get_pinned_embeddings, export_all_memories,
    get_all_embeddings as _get_all_embeddings,
    get_embedding_count as _get_embedding_count,
    semantic_search as _semantic_search,
)
from memory.importance_scorer import (
    score_importance, is_duplicate_memory,
    DEFAULT_IMPORTANCE_THRESHOLD,
)
from memory.memory_categorizer import (
    categorize_memory, ALL_CATEGORIES, DEFAULT_CATEGORY,
)
from memory.conversation_summarizer import (
    should_summarize, summarize_messages, get_current_summary,
    store_summary, clear_all_summaries,
    SUMMARIZATION_THRESHOLD, MESSAGES_TO_KEEP,
)

class MemoryManager:
    DEFAULT_TOP_K = 10
    DEFAULT_RECENT_MESSAGES = 20
    IMPORTANCE_THRESHOLD = DEFAULT_IMPORTANCE_THRESHOLD

    def create_conversation(self, title="New Chat"):
        return create_conversation(title=title)

    def get_conversations(self):
        return get_conversations()

    def get_conversation(self, conversation_id):
        return get_conversation(conversation_id)

    def load_conversation_messages(self, conversation_id):
        raw = get_conversation_messages(conversation_id)
        return self._raw_to_chat_format(raw)

    def clear_conversation(self, conversation_id):
        clear_conversation_messages(conversation_id)

    def delete_conversation(self, conversation_id):
        delete_conversation(conversation_id)

    def update_conversation_title(self, conversation_id, title):
        update_conversation_title(conversation_id, title)

    def save_conversation(self, user_msg, bot_msg, conversation_id="default"):
        conv_id = conversation_id or "default"
        user_msg_id = store_message(USER_ID, user_msg, conversation_id=conv_id)
        store_message(BOT_ID, bot_msg, conversation_id=conv_id)

        importance = score_importance(user_msg, bot_msg)
        print(f"[INFO] Importance score: {importance:.2f} "
              f"(threshold: {self.IMPORTANCE_THRESHOLD:.2f}) | \"{user_msg[:60]}\"")

        if importance < self.IMPORTANCE_THRESHOLD:
            print(f"[INFO] Skipping long-term storage (below threshold)")
        elif is_duplicate_memory(user_msg):
            print(f"[INFO] Skipping long-term storage (duplicate detected)")
        else:
            category = categorize_memory(user_msg)
            print(f"[INFO] Memory category: {category}")
            self._embed_and_store(
                user_msg_id, user_msg,
                importance_score=importance, category=category,
            )

        self._check_and_summarize()

    def load_conversations(self):
        raw = get_all_messages()
        return self._raw_to_chat_format(raw)

    def load_recent_messages(self, limit=20):
        return self.load_conversations()[-limit:]

    def delete_conversations(self):
        clear_all_messages()
        clear_all_summaries()

    def get_summary(self):
        return get_current_summary()

    def delete_memory(self, embedding_id):
        _delete_embedding(embedding_id)

    def edit_memory(self, embedding_id, new_text):
        new_embedding = generate_embedding(new_text)
        if new_embedding is None:
            return False
        _update_embedding_text(embedding_id, new_text, new_embedding)
        return True

    def toggle_memory_pin(self, embedding_id, pinned):
        _toggle_pin(embedding_id, pinned)

    def search_memories(self, query):
        all_memories = _get_all_embeddings()
        if not query or not query.strip():
            return all_memories
        query_lower = query.lower()
        return [m for m in all_memories if query_lower in m.get("text", "").lower()]

    def semantic_search_memories(self, query, top_k=10):
        if not query or not query.strip():
            return self.search_memories(query)
        results = _semantic_search(query, top_k=top_k)
        if not results:
            return self.search_memories(query)
        return results

    def filter_memories_by_category(self, category):
        all_memories = _get_all_embeddings()
        if not category or category == "All":
            return all_memories
        return [m for m in all_memories if (m.get("category") or DEFAULT_CATEGORY) == category]

    def recategorize_memory(self, embedding_id, new_category):
        _update_embedding_category(embedding_id, new_category)

    def export_memories(self):
        return export_all_memories()

    def get_pinned_memories(self):
        pinned = get_pinned_embeddings()
        if not pinned:
            return ""
        return "\n---\n".join(m["text"] for m in pinned)

    def get_message_count(self):
        return get_message_count()

    def get_memory_count(self):
        return _get_embedding_count()

    def get_raw_memory(self):
        return get_all_messages()

    def get_full_context(self):
        return retrieve_full_context(get_all_messages())

    def get_semantic_context(self, query, top_k=None, exclude_message_ids=None):
        if top_k is None:
            top_k = self.DEFAULT_TOP_K
        return retrieve_semantic_context(
            query, top_k=top_k, exclude_message_ids=exclude_message_ids,
        )

    def get_recent_messages(self, limit=None):
        if limit is None:
            limit = self.DEFAULT_RECENT_MESSAGES
        return _get_recent_messages(limit)

    def get_hybrid_context(self, query, recent_limit=None, top_k=None):
        if recent_limit is None:
            recent_limit = self.DEFAULT_RECENT_MESSAGES
        if top_k is None:
            top_k = self.DEFAULT_TOP_K

        summary = self.get_summary()
        pinned_text = self.get_pinned_memories()
        recent_raw = self.get_recent_messages(recent_limit)
        recent_text = retrieve_recent_context(recent_raw)

        recent_ids = {msg["id"] for msg in recent_raw if "id" in msg}

        long_term_text = self.get_semantic_context(
            query, top_k=top_k, exclude_message_ids=recent_ids,
        )

        return {
            "conversation_summary": summary or "",
            "pinned_memories": pinned_text,
            "recent_conversation": recent_text,
            "long_term_memories": long_term_text,
        }

    def _check_and_summarize(self):
        try:
            total = get_total_message_count()
            if not should_summarize(total, self.DEFAULT_RECENT_MESSAGES):
                return

            old_count = total - MESSAGES_TO_KEEP
            if old_count <= 0:
                return

            old_messages = get_oldest_messages(old_count)
            existing_summary = get_current_summary()

            new_summary = summarize_messages(old_messages, existing_summary)
            if new_summary:
                store_summary(new_summary, len(old_messages))
                delete_oldest_messages(MESSAGES_TO_KEEP)
                print(f"[INFO] Summarized {len(old_messages)} messages and archived")
            else:
                print("[WARN] Summarization returned empty result, skipping archival")
        except Exception as e:
            print(f"[WARN] Summarization check failed: {e}")

    @staticmethod
    def _embed_and_store(message_id, text, importance_score=None, category=None):
        try:
            embedding = generate_embedding(text)
            if embedding is not None:
                store_embedding(
                    message_id, text, embedding,
                    importance_score=importance_score, category=category,
                )
        except Exception as e:
            print(f"[WARN] Failed to embed message {message_id}: {e}")

    @staticmethod
    def _raw_to_chat_format(raw_memory):
        messages = []
        i = 0
        while i < len(raw_memory):
            msg = raw_memory[i]
            role = msg.get("user", "")

            if role == USER_ID:
                messages.append({"role": "user", "content": msg.get("text", "")})
                if i + 1 < len(raw_memory) and raw_memory[i + 1].get("user") == BOT_ID:
                    messages.append({"role": "assistant", "content": raw_memory[i + 1].get("text", "")})
                    i += 2
                else:
                    i += 1
            else:
                i += 1

        return messages
