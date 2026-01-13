def retrieve_context(query, memory):
    """
    Return COMPLETE conversation history - ALL messages
    No filtering, no truncation - full context for API
    """
    if not memory:
        return ""
    
    # Extract ALL text from memory
    texts = [m.get("text", "") for m in memory if m.get("text")]
    
    if not texts:
        return ""
    
    # Return EVERYTHING joined together
    return "\n---\n".join(texts)


def retrieve_full_context(memory):
    """
    Get absolutely ALL conversation history without any processing
    """
    if not memory:
        return ""
    
    texts = [m.get("text", "") for m in memory if m.get("text")]
    
    # Return complete history
    return "\n".join(texts)