# Local Code Agent - Cheat Sheet 📋

Quick reference for using your local code agent.

---

## 🚀 Installation (One-Time)

```bash
# 1. Install Ollama
brew install ollama

# 2. Pull a model
ollama pull qwen2.5-coder:7b

# 3. Run setup
./setup.sh
```

---

## ⚡ Quick Start

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Agent
python3 enhanced_code_agent.py
```

---

## 💬 Agent Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show help | `/help` |
| `/clear` | Clear history | `/clear` |
| `/model` | Switch model | `/model llama3.2:3b` |
| `/pwd` | Show directory | `/pwd` |
| `/cd` | Change directory | `/cd ~/projects` |
| `/tools` | List tools | `/tools` |
| `/exit` | Quit agent | `/exit` |

---

## 🛠️ Available Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `read_file` | View file contents | "Read main.py" |
| `write_file` | Create new file | "Create test.py with hello world" |
| `edit_file` | Modify file | "Add error handling to parse()" |
| `run_command` | Execute shell command | "Run pytest" |
| `list_files` | Browse directory | "List all Python files" |
| `search_files` | Find files | "Search for config.yaml" |
| `create_directory` | Make folder | "Create tests directory" |

---

## 💡 Example Queries

### File Operations
```
Read the contents of main.py
Create a new file called utils.py with helper functions
Edit config.json to change the port to 8080
List all files in the src directory
Search for TODO comments in the project
```

### Code Tasks
```
Write a Python function to parse CSV files
Add error handling to the authentication module
Refactor the database connection code
Create unit tests for the API endpoints
Optimize this SQL query for better performance
```

### Project Management
```
Show me the project structure
Find all files larger than 1MB
List all Python files modified in the last week
Create a new React component for user profiles
Set up a basic Express.js server
```

### Debugging
```
Help me debug this error: [paste error]
Explain what this code does
Why is this function failing?
Run the tests and show me any failures
Check for syntax errors in app.js
```

---

## 🎨 Response Formatting

Agent automatically formats:
- **Code blocks** with syntax highlighting
- **File contents** with line numbers
- **Command output** with clear formatting
- **Errors** in red
- **Success** in green

---

## ⚙️ Model Selection

### For Speed 🚀
```bash
ollama pull llama3.2:3b
/model llama3.2:3b
```

### For Coding ⭐ (Recommended)
```bash
ollama pull qwen2.5-coder:7b
/model qwen2.5-coder:7b
```

### For Quality 🎯
```bash
ollama pull deepseek-coder-v2:16b
/model deepseek-coder-v2:16b
```

---

## 🐛 Common Issues & Fixes

### Can't Connect to Ollama
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start it
ollama serve
```

### Model Not Found
```bash
# List available models
ollama list

# Pull a model
ollama pull llama3.2:3b
```

### Slow Responses
```bash
# Use smaller model
/model llama3.2:3b

# Or check system resources
top
```

### Permission Errors
```bash
# Make scripts executable
chmod +x *.py *.sh

# Run with python directly
python3 enhanced_code_agent.py
```

---

## 🔧 Configuration Tips

### Change Temperature (Randomness)
Edit in `enhanced_code_agent.py`:
```python
"temperature": 0.7  # Lower = more focused
                    # Higher = more creative
```

### Adjust Context Window
```python
"num_ctx": 4096  # Smaller = faster
                 # Larger = more context
```

### Limit History
```python
for msg in self.conversation_history[-6:]:  # Keep last 6
```

---

## 📊 Performance Guide

### M3 Max (36GB RAM)

| Model Size | Speed | Memory | Best For |
|------------|-------|--------|----------|
| 3B | ⚡⚡⚡⚡⚡ | 2GB | Quick tasks |
| 7B | ⚡⚡⚡⚡ | 5GB | General coding ⭐ |
| 13B | ⚡⚡⚡ | 8GB | Complex tasks |
| 16B | ⚡⚡⚡ | 10GB | Best quality |
| 30B+ | ⚡⚡ | 20GB+ | Critical work |

---

## 🎯 Workflow Examples

### Starting a New Project
```
❯ Create a new Python project structure
❯ Add a README with project description
❯ Create a requirements.txt with common packages
❯ Set up a basic test framework
```

### Code Review
```
❯ Read main.py
❯ Analyze this code for potential issues
❯ Suggest improvements for better performance
❯ Add docstrings to all functions
```

### Debugging Session
```
❯ Read the error logs
❯ Explain what this error means
❯ Show me the function that's failing
❯ Fix the bug and update the file
❯ Run the tests to verify
```

---

## 🔐 Privacy Features

✅ **Everything Local**
- No internet required
- No API calls
- No data collection
- Your code never leaves your machine

✅ **Full Control**
- Modify any part
- Add custom tools
- Change behavior
- Own your data

---

## 📚 File Structure

```
your-agent/
├── enhanced_code_agent.py  # Main app ⭐
├── local_code_agent.py     # Simple version
├── config.example.py       # Configuration
├── requirements.txt        # Dependencies
├── setup.sh                # Setup script
├── README.md               # Full docs
├── QUICKSTART.md           # Fast setup
├── ARCHITECTURE.md         # System design
└── CHEATSHEET.md          # This file
```

---

## 🚦 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Interrupt (don't quit) |
| `Ctrl+D` | Exit |
| `↑` / `↓` | Command history |
| `Tab` | Autocomplete paths |

---

## 🎁 Pro Tips

1. **Start with simple models** - Try 3B first, upgrade if needed
2. **Use descriptive queries** - More context = better results
3. **Chain tasks** - Let the agent do multiple steps
4. **Clear history** - Use `/clear` for fresh context
5. **Check /tools** - See what's available
6. **Read the docs** - ARCHITECTURE.md has deep details
7. **Customize freely** - It's your agent!

---

## 🔄 Ollama Commands

```bash
# List models
ollama list

# Pull model
ollama pull <model>

# Remove model
ollama rm <model>

# Show model info
ollama show <model>

# Run model directly
ollama run <model>

# Stop server
pkill ollama

# Check version
ollama --version
```

---

## 📦 Recommended Models

### Top 3 for Coding

1. **qwen2.5-coder:7b** ⭐ Best balance
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

2. **deepseek-coder-v2:16b** 🎯 Best quality
   ```bash
   ollama pull deepseek-coder-v2:16b
   ```

3. **llama3.2:3b** 🚀 Fastest
   ```bash
   ollama pull llama3.2:3b
   ```

---

## 🆘 Getting Help

1. **In the agent**: `/help`
2. **Documentation**: `README.md`
3. **Architecture**: `ARCHITECTURE.md`
4. **Ollama docs**: https://github.com/ollama/ollama

---

## ✨ Next Steps

1. ✅ Install and run agent
2. ✅ Try basic commands
3. ✅ Create a simple file
4. ✅ Run a shell command
5. ✅ Read the full docs
6. ✅ Customize to your needs
7. ✅ Add custom tools
8. ✅ Share your improvements!

---

**Keep this handy while learning the agent! 📌**

Version 1.0 | For M3 Max optimization