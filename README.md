# Project: Building Local AI coding Agent Harness 


## Introduction:

I am building an AI coding agent, similar to Claude Code, completely from scratch. Instead of using a hosted API or a ready-made framework like Langchain, I set up a local model on my own machine (Qwen via LM Studio) and build the agent around it one step at a time. Run it with `python main.py`.

I am using Qwen3.5 9B (Q4_K_M) from Hugging Face, a open-source model that fits in the 16GB GPU of my laptop. It is small, but it capable for our goal: learning how to build a coding agent.

You can download the model here:
https://huggingface.co/Qwen/Qwen3.5-9B

Our goal:

- **Build:** end up with a working coding agent that can read files, run commands, and edit code.
- **Learn:** understand how an AI agent really works by writing every piece myself, such as the system prompt, tools, the agent loop, and harness.

Each step is small and comes with notes on what I learned and why it is built that way.If you are curious about how agents like Claude Code work under the hood, feel free to follow along.


## Roadmap

1. [x] Connect to the local model
2. [x] Write a system prompt
3. [x] Create a `bash` tool
4. [x] Create a `read_file` tool
5. [x] Run tools on our side and send the result back to the model
6. [ ] Add a step limit (`MAX_STEPS`)
7. [ ] Add more tools (list, write, edit, search)
8. [ ] Control a browser

## Notes

### 1. Connect to the local model
- Download the model in LMStudio, and run the LMStudio as server so that we can chat with the model via calling API, e.g.  
POST http://localhost:1234/api/v1/chat
- We can also see the log which show the message sent by user.


### 2. System prompt
- Before adding system prompt, ask the model who it is, it answers that it is Qwen3.5.
- After adding system prompt, it answers that it is a coding agent.
- Every request includes the system prompt, because the model is stateless.
- System prompt:
  - Defines Persona & Role: Sets the AI's identity (e.g., "You are a coding agent").
  - Provides Rules & Constraints: Specifies tone, boundaries, ethical guidelines, and what topics to avoid.
  - Determines Output Format: Dictates how responses are structured (e.g., "Answer only in code" or "Use bullet points").  
  - Loads into context each request.



### 2.1 Streaming (`stream = true`)

The server sends the reply in small pieces while the model is still writing it. If stream = false, you stare at a blank screen until the whole answer is done. With it, words appear right away, so it feels much faster.

### 3. Tools

The model never runs anything itself. It only asks for a tool, and our code runs it and sends the result back.

Tools we provide so far:

- **`bash`**: runs a shell command and returns its output (stdout and stderr) plus the exit code. It times out after 60 seconds so a hanging command can't freeze the agent.
- **`read_file`**: reads a text file and returns its lines with line numbers. Use `offset` and `limit` to read a slice of a large file (defaults: start at line 1, up to 2000 lines).

### 5. Agent loop

For each message you type, we keep calling the model until it stops asking for tools:

1. Call the model.
2. If it asks for a tool, run the tool, add the result to the conversation, and go back to step 1.
3. If it doesn't, print the answer and stop.

### 6. `MAX_STEPS`

The maximum number of model calls for one user message (default 10).

**Why:** a model can get stuck calling the same failing tool forever. The limit makes sure every turn ends.

**Standard practice:** yes. For example, OpenAI Agents SDK uses `max_turns` (default 10) and LangChain uses `max_iterations` (default 15).

**Tip:** raise it to about 25 to 50 for longer tasks.

**Does a mode or effort level change it?** Not in this harness: it is a fixed number, and nothing reads a mode or effort setting. In products like Claude or ChatGPT (internal limits unknown, so this is the general pattern):

- **Research mode** is a separate setup with a much larger budget, since it runs many searches and reads.
- **Effort level** mostly sets how much the model thinks (a token budget), not the step cap. Higher effort can lead to more tool calls, so you may hit the cap sooner.

To support modes here, pick the cap per run, for example `{"normal": 10, "research": 50}`.
