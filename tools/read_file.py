from pathlib import Path

# Tool definition sent to the model in the "tools" field of the API request.
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read a text file and return its contents with line numbers. "
            "Use offset and limit to read a slice of a large file."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                },
                "offset": {
                    "type": "integer",
                    "description": "Line number to start from (1-based, default 1)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to return (default 2000)",
                },
            },
            "required": ["path"],
        },
    },
}


def read_file(path, offset=1, limit=2000):
    """Return the requested lines of a file, numbered, as text for the model."""
    file = Path(path).expanduser()
    if not file.exists():
        return f"Error: file not found: {path}"
    if not file.is_file():
        return f"Error: not a file: {path}"
    try:
        # errors="replace" keeps odd bytes from crashing the read.
        with open(file, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError as e:
        return f"Error: could not read {path}: {e}"

    start = max(offset, 1) - 1
    chunk = lines[start : start + max(limit, 1)]
    if not chunk:
        return f"(no lines in range; file has {len(lines)} lines)"
    output = "\n".join(f"{start + i + 1}\t{line}" for i, line in enumerate(chunk))
    # Tell the model when it got a partial view so it can ask for more.
    end = start + len(chunk)
    if end < len(lines):
        output += f"\n[showing lines {start + 1}-{end} of {len(lines)}; use offset to read more]"
    return output
