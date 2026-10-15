from tools.bash import BASH_TOOL, run_bash
from tools.read_file import READ_FILE_TOOL, read_file

# Registry: tool name -> (schema, function). To add a tool, create a module in
# this package with its schema and function, import it above, and add one line
# here.
TOOLS = {
    "bash": (BASH_TOOL, run_bash),
    "read_file": (READ_FILE_TOOL, read_file),
}

# List of schemas to send to the API as the "tools" field.
SCHEMAS = [schema for schema, _ in TOOLS.values()]


def execute(name, args):
    """Run the tool the model asked for and return its output as text."""
    if name not in TOOLS:
        return f"Error: unknown tool {name}"
    _, func = TOOLS[name]
    try:
        # The model's arguments arrive as a dict, e.g. {"command": "dir"}.
        return func(**args)
    except TypeError as e:
        # Wrong or missing arguments; report it so the model can retry.
        return f"Error: bad arguments for {name}: {e}"
