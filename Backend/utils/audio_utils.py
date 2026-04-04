def chunk_text_for_streaming(text: str, max_chars: int = 200):
    sentences = text.replace('. ', '.|').replace('? ', '?|').replace('! ', '!|').split('|')
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) <= max_chars:
            current += s + " "
        else:
            if current:
                chunks.append(current.strip())
            current = s + " "
    if current:
        chunks.append(current.strip())
    return chunks if chunks else [text]
