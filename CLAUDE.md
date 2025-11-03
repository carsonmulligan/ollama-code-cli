# CLAUDE.md - LLM-Optimized Ollama Code Agent

## Project Overview
Local code agent mimicking Claude Code functionality using Ollama. Single-file implementation (559 lines) optimized for LLM consumption, not human readability.

## Quick Start
```bash
./setup.sh              # Install deps, check Ollama, pull models
python3 enhanced_code_agent.py
```

## Core File
**`enhanced_code_agent.py`** - Complete implementation (559 lines)
- Compact code: removed docstrings, minimal whitespace, semicolon-separated statements
- All functionality preserved: 10 tools, todo list, file mentions, streaming, diffs
- Dependencies: rich (auto-installed), requests, difflib, standard library

## Architecture (Quick Reference)
```
EnhancedCodeAgent
├── Tools (10): read_file, write_file, edit_file, run_command, list_files, search_files, create_directory, add_todo, update_todo, show_todos
├── TodoList: Task tracking for iterative workflows
├── TokenTracker: Usage monitoring (↓ in · ↑ out · total)
└── Ollama API: Streaming responses, tool extraction, context management
```

## Tool Call Format
`TOOL[tool_name](arg1, arg2, ...)`

## Commands
`/init` `/files [pattern]` `/todo` `/plan <request>` `/clear` `/model <name>` `/pwd` `/cd <path>` `/tools` `/exit`

## File Mentions
`@filename` - Attaches file content (5000 char limit) to context

## Config
- Model: llama3.2 (default), configurable via `/model`
- Ollama: http://localhost:11434
- Context: Last 6 messages
- Temperature: 0.7, Max tokens: 2048
- Timeouts: 60s API, 30s commands

## System Prompt
```
Expert AI coding assistant with 10 tools
Format: TOOL[name](args)
Workflow: Break complex tasks into todos, mark in_progress, complete sequentially
Guidelines: Explain before tools, show code, confirm destructive ops
```

## Key Features
- Checkpoints (⏺): Visual tool execution feedback
- Diffs: Git-style additions/removals
- Thinking time (∴): Model inference duration
- Token tracking: Real-time usage display
- Streaming: Live response updates

## Workflow
Input → Process @files → Build context → Ollama API → Extract tools → Execute → Return results + status

## Project Detection
Auto-detects: Node.js (package.json), Python (requirements.txt), Rust (Cargo.toml), Go (go.mod), Java (pom.xml/build.gradle), Ruby (Gemfile)

## File Operations
- Read: First 100 lines, syntax highlighting
- Write: Diffs for updates, line count for new
- Edit: Text replacement with diff
- Search: Recursive, exclude hidden, limit 50
- List: Tree (depth 2, max 50), file sizes

## Dependencies
```bash
pip3 install rich --break-system-packages
```
Auto-installs if missing. Requires Ollama running (`ollama serve`).

## Ollama Models
```bash
ollama pull qwen2.5-coder:7b  # Recommended for code
ollama pull llama3.2          # General purpose
ollama list                   # Show installed
```

## Error Handling
- Graceful failures with messages
- Timeout protection (30s/60s)
- Permission/not found handling
- Invalid tool/arg handling

## LLM Optimization Notes
- Code compacted from 1146→559 lines (51% reduction)
- Removed: All docstrings, verbose comments, human-friendly formatting
- Kept: Full functionality, visual feedback, error handling
- Optimized: Single semicolon-separated statements, minimal whitespace
- Purpose: Fast parsing for LLMs, not human maintenance

## Repository Structure
```
enhanced_code_agent.py  # Main (559 lines, LLM-optimized)
requirements.txt        # Dependencies
setup.sh               # Setup script
config.py              # Optional configuration
CLAUDE.md              # This file (LLM guidance)
README.md              # Documentation
.llm/REFERENCE.md      # LLM quick reference
```

## Usage Examples
```python
# Read and analyze
❯ @config.py what is the default model?

# Iterative task
❯ Create a REST API with authentication
# Agent creates todos, works through each sequentially

# Planning
❯ /plan Refactor authentication to OAuth2
# Agent creates detailed plan with todos

# File operations
❯ /files *.py          # List Python files
❯ /init               # Analyze codebase
❯ /todo               # Show task progress
```

## Extension Points
1. Add tools: Register in `_register_tools()`, format `Tool(name, desc, func)`
2. Add commands: Add to main() slash command parser
3. Customize prompt: Modify `_build_system_prompt()`
4. Change config: Edit defaults in `__init__` or use commands

## Performance
- LLM token efficiency: Compact code reduces context window usage
- Streaming: Real-time response display
- Context limit: Last 6 messages to stay within Ollama limits
- Tool execution: Sequential, synchronous (simple but reliable)

## Privacy
100% local: No external APIs, all data on machine, requires local Ollama
