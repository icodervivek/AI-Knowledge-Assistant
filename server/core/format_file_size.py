def format_file_size(size):

    if size < 1024:
        return f"{size} B"

    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"

    else:
        return f"{size / (1024 * 1024):.2f} MB"