# Ollama Code Agent

Local code agent with Claude Code-like functionality. Single-file implementation (559 lines) optimized for LLM consumption.

## Install & Run
```bash
./setup.sh && python3 enhanced_code_agent.py
```

## Core
- **File**: `enhanced_code_agent.py` (559 lines, 51% smaller than original)
- **Optimization**: No docstrings, minimal whitespace, semicolon-separated statements
- **Deps**: `rich` (auto-installed), `requests`, standard library
- **Requires**: Ollama running locally (`ollama serve`)

## Tools (10)
1. `read_file(filepath)` - Read with syntax highlighting (100 line preview)
2. `write_file(filepath,content)` - Write with diff display
3. `edit_file(filepath,old,new)` - Replace text with diff
4. `run_command(command)` - Shell execution (30s timeout)
5. `list_files(directory)` - Tree view (depth 2, max 50)
6. `search_files(pattern)` - Recursive search (max 50)
7. `create_directory(path)` - Create dirs
8. `add_todo(task)` - Add task
9. `update_todo(num,status)` - Update status (pending/in_progress/completed)
10. `show_todos()` - Display tasks

Tool format: `TOOL[name](args)`

## Commands
`/init` `/files [pattern]` `/todo` `/plan <req>` `/clear` `/model <name>` `/pwd` `/cd <path>` `/tools` `/exit`

## Features
- **@file mentions**: Attach file context (5000 char limit)
- **Streaming**: Real-time Ollama responses
- **Checkpoints** (⏺): Visual tool feedback
- **Diffs**: Git-style additions/removals
- **Thinking time** (∴): Model inference duration
- **Token tracking**: ↓in·↑out·total
- **Iterative workflows**: Auto-breakdown of complex tasks into todos
- **Project detection**: Auto-detect tech stack (/init)

## Config
- Model: llama3.2 (default), switch via `/model`
- Ollama: http://localhost:11434
- Context: Last 6 messages
- Temperature: 0.7
- Max tokens: 2048
- Timeouts: 60s API, 30s shell

## Architecture
```
EnhancedCodeAgent
├── Tools: File ops, shell, todos
├── TodoList: Task tracking
├── TokenTracker: Usage stats
└── Ollama API: Streaming, tool extraction
```

## Workflow
Input → @files → Context → Ollama → Extract tools → Execute → Results + status

## Examples
```bash
# Analyze file
❯ @config.py what is the default model?

# Complex task
❯ Create a REST API with authentication
# Creates todos, works iteratively

# Planning
❯ /plan Add OAuth2 authentication

# List files
❯ /files *.py
```

## Ollama Setup
```bash
ollama serve                  # Start server
ollama pull qwen2.5-coder:7b  # Code model
ollama pull llama3.2          # General model
```

## Structure
```
enhanced_code_agent.py  # Main (559 lines)
requirements.txt        # rich
setup.sh               # Setup
config.py              # Optional config
CLAUDE.md              # LLM guidance
.llm/REFERENCE.md      # Quick reference
```

## Extension
- Tools: Add to `_register_tools()`
- Commands: Add to main() parser
- Prompt: Modify `_build_system_prompt()`

## LLM Optimization
- 1146→559 lines (51% reduction)
- Removed: Docstrings, comments, formatting
- Kept: Functionality, visual feedback, errors
- Purpose: Fast LLM parsing

## Privacy
100% local: No external APIs, requires Ollama

## Tech Detection
Node.js (package.json), Python (requirements.txt), Rust (Cargo.toml), Go (go.mod), Java (pom.xml/build.gradle), Ruby (Gemfile)

## System Prompt
```
Expert AI coding assistant with 10 tools
Format: TOOL[name](args)
Workflow: Break tasks→todos→in_progress→completed
Guidelines: Explain, show code, confirm destructive ops
```

## Error Handling
Graceful failures, timeout protection (30s/60s), permission/not found handling

## Performance
Token efficient (compact code), streaming responses, 6-message context, sequential tool execution
