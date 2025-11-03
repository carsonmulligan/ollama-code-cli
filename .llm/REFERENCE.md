# LLM Reference - Ollama Code Agent

## Core Architecture
- **Single File**: `enhanced_code_agent.py` (559 lines, LLM-optimized)
- **Python 3**: Uses Ollama API for local LLM inference
- **Rich CLI**: Terminal UI with syntax highlighting, diffs, progress tracking
- **Tool System**: 10 built-in tools for file ops, shell commands, todo management

## Key Classes
- `TokenTracker`: Track token usage (prompt/completion/total)
- `Todo/TodoList`: Task management for iterative workflows
- `Tool`: Base class for agent tools
- `EnhancedCodeAgent`: Main orchestrator

## Tools
1. `read_file(filepath)` - Read files with syntax highlighting
2. `write_file(filepath,content)` - Write/create files with diffs
3. `edit_file(filepath,old_text,new_text)` - Edit via text replacement
4. `run_command(command)` - Execute shell commands (30s timeout)
5. `list_files(directory)` - Browse directory tree (depth 2, max 50 items)
6. `search_files(pattern)` - Find files by pattern (max 50 results)
7. `create_directory(path)` - Create directories
8. `add_todo(task)` - Add task to todo list
9. `update_todo(task_number,status)` - Update task status (pending/in_progress/completed)
10. `show_todos()` - Display task list

## Tool Call Format
`TOOL[tool_name](arg1, arg2, ...)`

Examples:
- `TOOL[read_file](main.py)`
- `TOOL[write_file](test.py, "print('hello')")`
- `TOOL[edit_file](config.py, "DEBUG = False", "DEBUG = True")`

## Commands
- `/init` - Analyze codebase (README, structure, tech stack)
- `/files [pattern]` - List files for @ mentions
- `/todo` - Show task list
- `/plan <request>` - Create execution plan
- `/clear` - Clear conversation history
- `/model <name>` - Switch Ollama model
- `/pwd` - Show working directory
- `/cd <path>` - Change directory
- `/tools` - List available tools
- `/exit` - Exit agent

## File Mentions
Use `@filename` to attach file context (up to 5000 chars per file)
Example: `@config.py what is the default model?`

## System Prompt Structure
```
You are an expert AI coding assistant running locally.
Tools: {tool_descriptions}
Format: TOOL[tool_name](args)
Guidelines: Explain before using tools, show code/content, confirm destructive ops
Iterative Workflow: Break down complex tasks into todos, mark in_progress, complete sequentially
```

## Key Features
- **Checkpoints**: Visual feedback (⏺) for each tool execution
- **Diffs**: Git-style diffs showing additions/removals
- **Thinking Time**: Shows model thinking duration (∴)
- **Token Tracking**: Input/output tokens, session time
- **Streaming**: Real-time response streaming from Ollama

## Configuration
- Default model: llama3.2
- Ollama URL: http://localhost:11434
- Temperature: 0.7
- Max tokens: 2048
- Context: Last 6 messages
- Timeout: 60s for API, 30s for shell commands

## Workflow
1. User input → Process @file mentions → Add to history
2. Build context: System prompt + last 6 messages + current input
3. Call Ollama API with streaming
4. Extract tool calls from response
5. Execute tools sequentially
6. Return cleaned response + tool results
7. Show status footer (current task, elapsed time, tokens)

## Project Detection
Tech indicators: package.json (Node.js), requirements.txt (Python), Cargo.toml (Rust), go.mod (Go), pom.xml/build.gradle (Java), Gemfile (Ruby)

## File Operations
- Read: Show first 100 lines with syntax highlighting
- Write: Show diffs for updates, line count for new files
- Edit: Replace text with diff display
- Search: Recursive glob, exclude hidden dirs, limit 50 results
- List: Tree view, depth 2, max 50 items, show file sizes

## Error Handling
- Graceful failures with error messages
- Timeout protection (30s commands, 60s API)
- Permission error handling
- File not found handling
- Invalid tool/argument handling

## Dependencies
- `rich` - Terminal UI (auto-installed if missing)
- `requests` - HTTP for Ollama API
- `difflib` - Diff generation
- Standard library: json, os, subprocess, sys, re, time, pathlib, datetime, typing
