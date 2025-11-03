# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a local code agent that mimics Claude Code's functionality but runs entirely locally using Ollama. It provides a CLI AI assistant with tool support for file operations, shell commands, and code execution.

## Development Commands

### Setup and Installation

```bash
# Run initial setup (installs dependencies, checks Ollama, pulls models)
./setup.sh

# Manual dependency installation if needed
pip3 install -r requirements.txt --break-system-packages
```

### Running the Agent

```bash
# Run the enhanced version (recommended)
python3 enhanced_code_agent.py

# Or make it executable and run directly
chmod +x enhanced_code_agent.py
./enhanced_code_agent.py

# Run the basic version
python3 local_code_agent.py
```

### Agent Commands

The enhanced agent supports these commands:
- `/init` - Analyze the codebase and provide context (like Claude Code's init)
- `/help` or `/commands` - Show help and available commands
- `/files [pattern]` - List files for @ mentions (e.g., `/files *.py`)
- `/todo` - Display current task list
- `/plan <request>` - Ask agent to create a plan and todos for your request
- `/clear` - Clear conversation history
- `/model <name>` - Switch between Ollama models
- `/pwd` - Show current working directory
- `/cd <path>` - Change working directory
- `/tools` - List all available tools
- `/exit` - Exit the agent

### File Mentions (@)

Like Claude Code, you can mention files in your messages using `@filename`:
```
❯ @config.py what is the default model?
📎 Attached: config.py

🤖 Looking at the config file, the default model is "qwen2.5-coder:7b"...
```

Features:
- Automatically reads and attaches file content to your message
- Supports relative paths: `@src/main.py` or `@./README.md`
- Use `/files` to list all available files
- Use `/files *.py` to list specific file types
- Limits file content to 5000 chars to manage context size

### Ollama Commands

```bash
# Start Ollama server (must be running for agent to work)
ollama serve

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull recommended coding model
ollama pull qwen2.5-coder:7b

# List installed models
ollama list
```

## Architecture

### Core Components

**Two Agent Implementations:**
- `local_code_agent.py` - Basic version with minimal features
- `enhanced_code_agent.py` - Full-featured version with Rich UI and comprehensive tool support

**Configuration:**
- `config.py` - Main configuration file (copied from config.example.py)
- Configures Ollama URL, default model, model-specific settings, UI preferences, and tool behavior

**Key Classes:**
- `EnhancedCodeAgent` - Main agent orchestrator
  - Manages conversation history
  - Coordinates tool execution
  - Handles Ollama API communication
  - Builds system prompts with context
- `Tool` - Base class for agent tools (file ops, shell commands, etc.)

### Tool System

The agent exposes these built-in tools:
- `read_file(filepath)` - Read and display file contents with syntax highlighting
- `write_file(filepath, content)` - Create new files
- `edit_file(filepath, old_text, new_text)` - Edit existing files by replacing text
- `run_command(command)` - Execute shell commands
- `list_files(directory)` - Browse directory structure as tree
- `search_files(pattern)` - Find files matching patterns
- `create_directory(path)` - Create new directories

Tools are registered in `_register_tools()` method and executed via Tool.execute().

### Agent Flow

1. User input → Rich Terminal UI
2. Agent Core adds to conversation history + builds context
3. Prompt sent to Ollama via HTTP POST (streaming enabled)
4. Tokens stream back and display live
5. Agent extracts tool calls from response (pattern: `TOOL[tool_name](args)`)
6. Tools execute and results added to conversation context
7. Agent continues conversation with tool results

### Ollama Integration

- Communicates via localhost:11434 (configurable in config.py)
- Supports streaming responses for real-time display
- Model-specific settings in config.py control temperature, context window, token limits
- Designed for local models: llama3.2, qwen2.5-coder:7b, deepseek-coder-v2

## Configuration Notes

**Important config.py settings:**
- `DEFAULT_MODEL` - Which Ollama model to use (default: qwen2.5-coder:7b)
- `MODEL_CONFIGS` - Per-model temperature, context window, token prediction settings
- `MAX_CONVERSATION_HISTORY` - How many messages to keep in context (default: 10)
- `ENABLE_AUTO_TOOL_EXECUTION` - Auto-execute tools without confirmation (default: True)
- `IGNORED_DIRECTORIES` - Directories to skip when listing/searching files

## New Features (Claude Code-inspired)

**Visual Indicators:**
The agent now displays Claude Code-style visual feedback:
- **Checkpoints** (⏺) - Shows each tool execution (Read, Write, Update)
- **Thinking indicators** (∴) - Displays thinking time for model responses
- **Diffs** - Clean git-style diffs showing additions/removals with line numbers
- **Token tracking** - Shows input/output tokens and session time
- **Progress status** - Displays current task, elapsed time, and token usage

Example output:
```
⏺ Read(config.py)
  ⎿ Read 271 lines

⏺ Update(config.py)
  ⎿ Updated config.py with 3 additions and 1 removal
       ...
       -  DEFAULT_MODEL = "llama3.2"
       +  DEFAULT_MODEL = "qwen2.5-coder:7b"
       ...

∴ Thought for 2.3s

· Working on: Update configuration · 45s · ↓ 2k in · ↑ 1k out · 3k total
```

**Iterative Task Execution:**
The agent can now work iteratively on complex, multi-step tasks:
- Automatically breaks down complex requests into subtasks
- Creates and manages a todo list for tracking progress
- Works through tasks step-by-step
- Updates task status (pending → in_progress → completed)

**Codebase Analysis (`/init`):**
Like Claude Code's /init command, this analyzes the project:
- Reads README for project overview
- Lists project structure
- Detects technologies (Python, Node.js, Rust, etc.)
- Stores context for better assistance

**Todo List Management:**
Built-in task tracking similar to Claude Code's TodoWrite:
- `add_todo` tool - Add tasks to the list
- `update_todo` tool - Change task status
- `show_todos` tool - Display current tasks
- Visual task list with status indicators (⏸️ pending, ▶️ in progress, ✅ completed)

**Planning Mode:**
The `/plan` command asks the agent to create a detailed plan:
- Breaks down complex requests into actionable steps
- Creates todos automatically
- Provides a roadmap before starting work

## Key Implementation Details

**System Prompt Construction:**
The agent builds a detailed system prompt in `_build_system_prompt()` that:
- Describes available tools and their usage
- Provides working directory context
- Explains tool call syntax: `TOOL[tool_name](args)`
- Includes project context from `/init` if available
- Shows current todo list to maintain task awareness
- Provides iterative workflow guidance
- Can be customized via `CUSTOM_SYSTEM_PROMPT` in config.py

**Tool Call Parsing:**
Agent responses are parsed for patterns like `TOOL[read_file](main.py)` to identify and execute tool calls during conversation.

**Error Handling:**
Tools catch exceptions and return user-friendly error messages rather than crashing, allowing conversation to continue.

## Extending the Agent

**Adding Custom Tools:**
1. Define tool function in EnhancedCodeAgent class
2. Register in `_register_tools()` method:
```python
tools['my_tool'] = Tool(
    'my_tool',
    'Description of what it does',
    self._my_tool_function
)
```

**Custom Commands:**
Add slash commands (like `/help`, `/clear`) in the main() function's command parser.

**System Prompt Customization:**
Modify `_build_system_prompt()` or set `CUSTOM_SYSTEM_PROMPT` in config.py.

## Usage Examples

**Basic Analysis:**
```
❯ /init
[Agent analyzes your codebase and shows README, structure, technologies]

❯ What does this repo do?
[Agent uses project context to explain the codebase]
```

**Iterative Task Execution:**
```
❯ Create a REST API with authentication and tests

🤖 I'll break this down into steps:
TOOL[add_todo](Design API endpoints and data models)
TOOL[add_todo](Set up Express server with basic routes)
TOOL[add_todo](Implement JWT authentication middleware)
TOOL[add_todo](Create user registration and login endpoints)
TOOL[add_todo](Write integration tests)
TOOL[show_todos]()

[Agent then works through each task, updating status as it goes]
```

**Planning Mode:**
```
❯ /plan Refactor the authentication system to use OAuth2

📋 Creating plan for: Refactor the authentication system to use OAuth2

🤖 Here's my plan:
TOOL[add_todo](Research OAuth2 flow and select library)
TOOL[add_todo](Update dependencies in package.json)
TOOL[add_todo](Create OAuth2 configuration file)
TOOL[add_todo](Refactor auth middleware)
TOOL[add_todo](Update login/register endpoints)
TOOL[add_todo](Update tests for OAuth2)
TOOL[add_todo](Update documentation)

[Shows task list, then ask to proceed with implementation]
```

**Checking Progress:**
```
❯ /todo

Task List
─────────────────────────────────────────
 #   Status            Task
─────────────────────────────────────────
 1   ✅ Completed      Design API endpoints
 2   ▶️  In Progress   Set up Express server
 3   ⏸️  Pending       Implement JWT auth
 4   ⏸️  Pending       Create endpoints
 5   ⏸️  Pending       Write tests
```

## Privacy & Local-First

This project runs entirely locally:
- No external API calls required
- All code and data stays on your machine
- Requires Ollama running locally
- No internet connection needed (after models downloaded)
