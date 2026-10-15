import json
from pathlib import Path

import requests

from tools import SCHEMAS, execute

URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "qwen/qwen3.5-9b"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"


def call_llm(messages):
    """Send the conversation to the model and return its reply message."""
    payload = {"model": MODEL, "messages": messages, "tools": SCHEMAS}
    resp = requests.post(URL, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]


def main():
    with open(SYSTEM_PROMPT_PATH, encoding="utf-8") as f:
        messages = [{"role": "system", "content": f.read()}]
    print(f"Chatting with {MODEL}. Type 'quit' to exit.")
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"quit", "exit"}:
            break
        if not user:
            continue
        messages.append({"role": "user", "content": user})

        while True:
            message = call_llm(messages)
            messages.append(message)

            if message.get("content"):
                print("\nAgent:", message["content"], "\n")

            if not message.get("tool_calls"):
                break

            for tool_call in message["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                result = execute(name, args)
                print("Tool:", name, args)
                print(result, "\n")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    }
                )


if __name__ == "__main__":
    main()
