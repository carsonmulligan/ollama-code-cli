# Quick Start Guide 🚀

Get up and running with your local code agent in 5 minutes!

## Step 1: Install Ollama (2 minutes)

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Download a Model (2 minutes)

Pick one based on your needs:

### For Coding (Recommended) ⭐
```bash
ollama pull qwen2.5-coder:7b
```
- Size: 4.7 GB
- Speed: Fast on M3 Max
- Best for: Code generation, debugging, refactoring

### For Speed 🚀
```bash
ollama pull llama3.2:3b
```
- Size: 2 GB
- Speed: Very fast
- Best for: Quick queries, simple tasks

### For Quality 🎯
```bash
ollama pull deepseek-coder-v2:16b
```
- Size: 8.9 GB
- Speed: Moderate
- Best for: Complex coding tasks

## Step 3: Start Ollama Server

Open a terminal and run:
```bash
ollama serve
```

Keep this terminal open! This is your AI server.

## Step 4: Run the Agent (30 seconds)

In a NEW terminal:

```bash
# Run setup
chmod +x setup.sh
./setup.sh

# Start the agent
python3 enhanced_code_agent.py
```

That's it! You should see:

```
🤖 Enhanced Local Code Agent

Powered by Ollama • Running locally on your machine
...
```

## First Commands to Try

Once the agent is running:

1. **Test basic conversation**
   ```
   ❯ Hello! Can you help me code?
   ```

2. **List files**
   ```
   ❯ List all files in the current directory
   ```

3. **Read a file**
   ```
   ❯ Read README.md
   ```

4. **Create a simple script**
   ```
   ❯ Create a Python script called hello.py that prints "Hello, World!"
   ```

5. **Get help**
   ```
   ❯ /help
   ```

## Troubleshooting

### "Could not connect to Ollama"
- Make sure `ollama serve` is running in another terminal
- Check: `curl http://localhost:11434/api/tags`

### "No models found"
- Pull a model: `ollama pull llama3.2:3b`
- List models: `ollama list`

### Script won't run
- Make it executable: `chmod +x enhanced_code_agent.py`
- Use Python directly: `python3 enhanced_code_agent.py`

### Too slow
- Try a smaller model (3b instead of 7b)
- Check Activity Monitor - close other apps
- Use quantized models: `ollama pull llama3.2:3b-q4_K_M`

## What's Next?

Check out the full [README.md](README.md) for:
- Advanced usage examples
- Custom tool creation
- Performance tuning
- Project ideas

## Quick Reference Card

### Agent Commands
```
/help    - Show help
/clear   - Clear history
/model   - Switch model
/tools   - List tools
/exit    - Quit
```

### Example Queries
```
"Read main.py and explain it"
"Create a React component for a login form"
"Run pytest and show me any failures"
"List all Python files larger than 100 lines"
"Add error handling to the auth function"
```

## System Requirements

- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 5-10GB for models
- **OS**: macOS, Linux, or Windows (WSL)
- **CPU**: Any modern CPU (Apple Silicon is great!)

Your M3 Max with 36GB RAM is perfect for running 7B-14B models! 🎉

## Getting Help

If you get stuck:
1. Check the [README.md](README.md) for detailed docs
2. Run `/help` in the agent
3. Check Ollama docs: https://github.com/ollama/ollama

---

**You're all set! Start building with your local AI coding assistant! 🎉**