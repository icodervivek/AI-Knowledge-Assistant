def chunk_text(text,chunk_size=500,overlap=100):
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        # Prevent overflow
        if end > text_length:
            end = text_length

        chunk = text[start:end]

        # Try ending chunk at sentence boundary
        last_period = chunk.rfind(".")

        # Only adjust if period exists
        # and chunk is reasonably long
        if last_period > 100:
            chunk = chunk[:last_period + 1]
            end = start + last_period + 1

        # Clean chunk
        chunk = chunk.strip()

        # Avoid empty chunks
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Move window with overlap
        previous_start = start
        start = end - overlap

        # Prevent negative loop
        if start < 0:
            start = 0

        if start <= previous_start:
            start = end

    return chunks
