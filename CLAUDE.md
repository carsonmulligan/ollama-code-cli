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

## Key Implementation Details

**System Prompt Construction:**
The agent builds a detailed system prompt in `_build_system_prompt()` that:
- Describes available tools and their usage
- Provides working directory context
- Explains tool call syntax: `TOOL[tool_name](args)`
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

## Privacy & Local-First

This project runs entirely locally:
- No external API calls required
- All code and data stays on your machine
- Requires Ollama running locally
- No internet connection needed (after models downloaded)
