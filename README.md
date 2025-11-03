# Local Code Agent 🤖

A Claude Code-inspired CLI AI agent that runs completely locally using Ollama. Build your own coding assistant with local LLMs!

## Features

✨ **100% Local** - Runs entirely on your machine, no API keys needed  
🎨 **Beautiful TUI** - Rich terminal interface with syntax highlighting  
🛠️ **Tool Support** - File operations, shell commands, code execution  
💬 **Conversational** - Natural language interface for coding tasks  
🔧 **Extensible** - Easy to add custom tools and capabilities  
📁 **Project Aware** - Understands your working directory context  

## Prerequisites

### 1. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull Models

Download your preferred model:

```bash
# Recommended models:
ollama pull llama3.2          # 2B - Fast, good for coding
ollama pull llama3.2:3b       # 3B - Balanced
ollama pull qwen2.5-coder:7b  # 7B - Best for code (recommended!)
ollama pull deepseek-coder-v2 # Great for coding tasks
```

**For your M3 Max MacBook Pro**, the 7B-14B models will run smoothly!

### 3. Start Ollama Server

```bash
ollama serve
```

Keep this running in a separate terminal.

## Installation

1. **Download the scripts**

```bash
# Basic version
curl -O local_code_agent.py

# Enhanced version (recommended)
curl -O enhanced_code_agent.py
```

2. **Make executable**

```bash
chmod +x enhanced_code_agent.py
```

3. **Install dependencies**

The script will auto-install `rich` on first run, or install manually:

```bash
pip3 install rich --break-system-packages
```

## Usage

### Quick Start

```bash
python3 enhanced_code_agent.py
```

### Basic Commands

```
/help      - Show help message
/clear     - Clear conversation history
/model     - Switch between models
/pwd       - Show current directory
/cd <path> - Change working directory
/tools     - List available tools
/exit      - Exit the agent
```

### Example Conversations

**Reading a file:**
```
❯ Read the contents of main.py and explain what it does
🤖 Assistant: [reads file, provides explanation with syntax highlighting]
```

**Creating a new project:**
```
❯ Create a new Python project with a main.py file that has a hello world function
🤖 Assistant: I'll create that for you!
[creates files and shows results]
```

**Running tests:**
```
❯ Run pytest on the tests directory and show me any failures
🤖 Assistant: [executes pytest, shows output]
```

**Code refactoring:**
```
❯ Refactor the authentication logic in auth.py to use decorators
🤖 Assistant: [reads file, suggests changes, implements them]
```

## Available Tools

The enhanced agent comes with these built-in tools:

- **read_file** - Read and display file contents with syntax highlighting
- **write_file** - Create new files with content
- **edit_file** - Edit existing files by replacing text
- **run_command** - Execute shell commands safely
- **list_files** - Browse directory structure as a tree
- **search_files** - Find files matching patterns
- **create_directory** - Create new directories

## Architecture

```
┌─────────────────────────────────────────┐
│         CLI Interface (Rich)            │
│  ┌───────────────────────────────────┐  │
│  │  User Input / Display Output       │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┼───────────────────────┐
│                 │     Agent Core        │
│  ┌──────────────▼──────────────┐        │
│  │   Conversation Manager       │        │
│  │  (History, Context)          │        │
│  └──────────────┬──────────────┘        │
│                 │                        │
│  ┌──────────────▼──────────────┐        │
│  │   Ollama API Client          │        │
│  │  (Streaming, Prompts)        │        │
│  └──────────────┬──────────────┘        │
│                 │                        │
│  ┌──────────────▼──────────────┐        │
│  │   Tool Executor              │        │
│  │  (File ops, Shell, etc)      │        │
│  └──────────────────────────────┘        │
└───────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼─────┐    ┌─────▼────┐
    │  Ollama  │    │   Your   │
    │  Server  │    │   Files  │
    └──────────┘    └──────────┘
```

## Configuration

### Customizing the System Prompt

Edit the `_build_system_prompt()` method in the agent class to customize behavior:

```python
def _build_system_prompt(self) -> str:
    return f"""You are an expert in [YOUR DOMAIN].
    
    Your specialties:
    - [Specialty 1]
    - [Specialty 2]
    
    ...
    """
```

### Adding Custom Tools

Add new tools to the `_register_tools()` method:

```python
tools['my_tool'] = Tool(
    'my_tool',
    'Description of what it does',
    self._my_tool_function
)
```

Then implement the tool function:

```python
def _my_tool_function(self, arg1: str) -> str:
    """Your tool implementation"""
    result = do_something(arg1)
    return f"Success: {result}"
```

## Model Recommendations

Based on your M3 Max (36GB RAM), here are the best models:

### For Coding Tasks:
1. **qwen2.5-coder:7b** ⭐ Best balance of speed/quality
2. **deepseek-coder-v2:16b** - Excellent for complex code
3. **codellama:13b** - Good all-rounder

### For General Tasks:
1. **llama3.2:3b** - Fast, good quality
2. **mistral:7b** - Excellent reasoning
3. **llama3.1:8b** - Great general purpose

### For Maximum Quality:
1. **qwen2.5:14b** - Best reasoning
2. **llama3.1:70b** - Will be slow but highest quality

## Performance Tips

### On M3 Max:

- **7B models**: ~30-50 tokens/sec (smooth experience)
- **13-14B models**: ~15-25 tokens/sec (still good)
- **30B+ models**: ~5-10 tokens/sec (usable for important tasks)

### Optimization:

1. **Use quantized models** for speed:
   ```bash
   ollama pull qwen2.5-coder:7b-q4_K_M
   ```

2. **Adjust context window** in the code:
   ```python
   "options": {
       "num_ctx": 4096,  # Smaller = faster
       "temperature": 0.7
   }
   ```

3. **Limit conversation history**:
   ```python
   for msg in self.conversation_history[-4:]:  # Keep fewer messages
   ```

## Troubleshooting

### Ollama not connecting

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Check logs
ollama logs
```

### Model too slow

- Try a smaller model (3b instead of 7b)
- Use quantized versions (q4_K_M)
- Reduce context window

### Out of memory

- Use smaller models
- Restart Ollama service
- Check activity monitor for memory usage

### Tool execution fails

- Check file permissions
- Verify working directory with `/pwd`
- Use absolute paths for files outside working dir

## Comparison with Claude Code

| Feature | Claude Code | Local Agent | Notes |
|---------|-------------|-------------|-------|
| Speed | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | Local models slower but improving |
| Privacy | Cloud | 🔒 Local | Your code never leaves your machine |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Claude Sonnet 4.5 is more capable |
| Cost | Subscription | Free | After initial hardware investment |
| Offline | ❌ | ✅ | Works without internet |
| Customization | Limited | 🎨 Full | You control everything |

## Advanced Usage

### Multi-turn Workflows

The agent maintains conversation context, so you can have multi-turn workflows:

```
❯ Read main.py
❯ Now add error handling to the parse_input function
❯ Write tests for those error cases
❯ Run the tests
```

### Project Analysis

```
❯ Analyze this codebase and suggest improvements
❯ List all TODO comments in the project
❯ Show me the dependency graph
```

### Batch Operations

```
❯ For each Python file in src/, add a docstring if missing
❯ Convert all var declarations to const in the JS files
❯ Run prettier on all TypeScript files
```

## Future Enhancements

Potential additions:

- [ ] Web search integration
- [ ] Git operations
- [ ] Docker container support
- [ ] Database queries
- [ ] API testing tools
- [ ] Code linting/formatting
- [ ] Documentation generation
- [ ] Test generation
- [ ] Refactoring suggestions

## Contributing

Feel free to extend this agent! Some ideas:

1. Add more specialized tools
2. Integrate with your favorite dev tools
3. Create domain-specific agents (web dev, data science, etc.)
4. Add voice input/output
5. Create a web UI version

## License

MIT License - Use freely!

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs)
- [Rich Terminal Library](https://rich.readthedocs.io/)
- [Claude Documentation](https://docs.claude.com)


---

**Built with ❤️ for local-first AI development**

Questions? Issues? Feel free to modify and improve!