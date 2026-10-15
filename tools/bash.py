import subprocess

# Tool definition sent to the model in the "tools" field of the API request.
# The model never runs anything itself; it only reads this schema and, when it
# wants to use the tool, replies with a tool call that our harness executes.
BASH_TOOL = {
    # Tells the API this tool is a callable function.
    "type": "function",
    "function": {
        # Name the model uses when it calls the tool.
        "name": "bash",
        # Shown to the model so it can decide when this tool is useful.
        "description": "Run a shell command and return its output.",
        # JSON Schema describing the arguments the model must provide.
        "parameters": {
            "type": "object",
            "properties": {
                # The single argument: the command text to execute.
                "command": {
                    "type": "string",
                    "description": "The shell command to run",
                },
            },
            # The model must always supply "command".
            "required": ["command"],
        },
    },
}


def run_bash(command, timeout=60):
    """Run a shell command and return its output as text for the model."""
    try:
        # shell=True lets the model use pipes and shell builtins; stdout and
        # stderr are captured as text instead of printing to our terminal.
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        # Don't let a hanging command freeze the agent.
        return f"Error: command timed out after {timeout} seconds"
    # Combine both streams and include the exit code so the model can tell
    # whether the command succeeded.
    output = result.stdout + result.stderr
    return f"{output}\n[exit code: {result.returncode}]"
