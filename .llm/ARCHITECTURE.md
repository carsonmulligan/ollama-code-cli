# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR M3 MAX MACBOOK PRO                   │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Terminal (Your Interface)                 │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │     enhanced_code_agent.py                      │  │  │
│  │  │                                                   │  │  │
│  │  │  ┌──────────────────────────────────────────┐   │  │  │
│  │  │  │  Rich Terminal UI                        │   │  │  │
│  │  │  │  • Syntax highlighting                   │   │  │  │
│  │  │  │  • Markdown rendering                    │   │  │  │
│  │  │  │  • Pretty tables & trees                 │   │  │  │
│  │  │  │  • Streaming display                     │   │  │  │
│  │  │  └──────────────────────────────────────────┘   │  │  │
│  │  │                      ↕                           │  │  │
│  │  │  ┌──────────────────────────────────────────┐   │  │  │
│  │  │  │  Agent Core                              │   │  │  │
│  │  │  │  • Conversation manager                  │   │  │  │
│  │  │  │  • Context builder                       │   │  │  │
│  │  │  │  • Tool orchestrator                     │   │  │  │
│  │  │  │  • Response processor                    │   │  │  │
│  │  │  └──────────────────────────────────────────┘   │  │  │
│  │  │                      ↕                           │  │  │
│  │  │  ┌──────────────────────────────────────────┐   │  │  │
│  │  │  │  Tool System                             │   │  │  │
│  │  │  │  ┌────────────────────────────────────┐ │   │  │  │
│  │  │  │  │ • read_file                        │ │   │  │  │
│  │  │  │  │ • write_file                       │ │   │  │  │
│  │  │  │  │ • edit_file                        │ │   │  │  │
│  │  │  │  │ • run_command                      │ │   │  │  │
│  │  │  │  │ • list_files                       │ │   │  │  │
│  │  │  │  │ • search_files                     │ │   │  │  │
│  │  │  │  │ • create_directory                 │ │   │  │  │
│  │  │  │  │ • [your custom tools...]           │ │   │  │  │
│  │  │  │  └────────────────────────────────────┘ │   │  │  │
│  │  │  └──────────────────────────────────────────┘   │  │  │
│  │  │                      ↕                           │  │  │
│  │  │  ┌──────────────────────────────────────────┐   │  │  │
│  │  │  │  Ollama Client                           │   │  │  │
│  │  │  │  • HTTP requests                         │   │  │  │
│  │  │  │  • Streaming handler                     │   │  │  │
│  │  │  │  • Token processing                      │   │  │  │
│  │  │  └──────────────────────────────────────────┘   │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│                            ↕                                │
│                   (localhost:11434)                         │
│                            ↕                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Ollama Server                           │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │  Model Runtime                                 │  │  │
│  │  │  • qwen2.5-coder:7b (or your choice)          │  │  │
│  │  │  • Token generation                            │  │  │
│  │  │  • Context management                          │  │  │
│  │  │  • Memory optimization                         │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│                            ↕                                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Your File System                        │  │
│  │  • Source code                                       │  │
│  │  • Configuration files                               │  │
│  │  • Project files                                     │  │
│  │  • All your data (stays local!)                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Query Flow
```
User Input
    ↓
Terminal UI (Rich)
    ↓
Agent Core (conversation history + context)
    ↓
Prompt Builder (system prompt + user query)
    ↓
Ollama Client (HTTP POST with streaming)
    ↓
Ollama Server (model inference)
    ↓
Streaming Tokens Back
    ↓
Live Display in Terminal
    ↓
Tool Extraction & Execution
    ↓
Final Response to User
```

### 2. Tool Execution Flow
```
Agent identifies tool call in response
    ↓
Parse tool name and arguments
    ↓
Validate tool exists
    ↓
Execute tool function
    ↓
Capture tool output
    ↓
Display result in terminal
    ↓
Add result to conversation context
    ↓
Continue conversation
```

## Component Responsibilities

### 1. **Rich Terminal UI**
- Renders beautiful terminal output
- Syntax highlighting for code
- Markdown formatting
- Progress indicators
- Live streaming display

### 2. **Agent Core**
- Manages conversation history
- Builds prompts with context
- Coordinates tool execution
- Handles errors gracefully
- Maintains working directory state

### 3. **Tool System**
- Defines available tools
- Executes tool functions
- Validates tool inputs
- Returns structured results
- Extensible architecture

### 4. **Ollama Client**
- Communicates with Ollama API
- Handles streaming responses
- Manages timeouts
- Processes tokens
- Error handling

### 5. **Ollama Server**
- Runs the LLM model
- Generates tokens
- Manages GPU/CPU usage
- Handles concurrent requests
- Optimizes memory

## Communication Patterns

### Agent ↔ Ollama
```
POST http://localhost:11434/api/generate
{
  "model": "qwen2.5-coder:7b",
  "prompt": "<system prompt>\n\n<conversation history>\n\nuser: ...",
  "stream": true,
  "options": {
    "temperature": 0.7,
    "num_predict": 2048
  }
}

Response (streaming):
{"response": "I", "done": false}
{"response": "'ll", "done": false}
{"response": " help", "done": false}
...
{"response": "", "done": true}
```

### Tool Call Pattern
```
Agent Response: "Let me read that file for you.

TOOL[read_file](main.py)

Now I'll analyze the code..."

↓ Agent extracts tool call
↓ Executes: agent.tools['read_file'].execute('main.py')
↓ Tool reads file and displays with syntax highlighting
↓ Returns: "Successfully read 150 characters from main.py"
↓ Agent continues with analysis
```

## Privacy & Security

```
┌─────────────────────────────────────┐
│      Your Machine (M3 Max)          │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  All processing happens here  │ │
│  │                                │ │
│  │  • Code never leaves machine  │ │
│  │  • No external API calls      │ │
│  │  • No data collection         │ │
│  │  • No internet required       │ │
│  │                                │ │
│  │  Your Data + Local Model =    │ │
│  │  Complete Privacy 🔒           │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
         ❌ No cloud connections
         ❌ No API keys needed
         ❌ No tracking
```

## Extensibility Points

### 1. Add New Tools
```python
# In EnhancedCodeAgent class
def _register_tools(self):
    tools['your_tool'] = Tool(
        'your_tool',
        'Description',
        self._your_tool_func
    )
```

### 2. Customize System Prompt
```python
def _build_system_prompt(self):
    return """Your custom instructions here..."""
```

### 3. Add New Commands
```python
# In main() function
elif cmd == '/your_command':
    your_command_logic()
```

### 4. Integrate External Services
```python
# Add to tool system
def _call_api(self, endpoint):
    response = requests.get(endpoint)
    return response.json()
```

## Deployment Options

### Local Development
```
Terminal → Agent → Ollama (localhost) → Local Files
```

### Network Setup (Advanced)
```
Terminal 1 (laptop) → Agent
                       ↓
           Network → Ollama Server (desktop)
                       ↓
                   Powerful GPU Model
```

### Container Setup (Future)
```
Docker Container
├── Agent
├── Ollama
└── Isolated File System
```

## Performance Characteristics

### With M3 Max (36GB RAM)

**Small Models (3B)**
- Speed: 60+ tokens/sec
- Memory: ~2GB
- Latency: Instant response
- Use case: Quick queries

**Medium Models (7B)** ⭐ Recommended
- Speed: 30-50 tokens/sec
- Memory: ~5GB
- Latency: Fast response
- Use case: General coding

**Large Models (13-16B)**
- Speed: 15-25 tokens/sec
- Memory: ~9-10GB
- Latency: Good response
- Use case: Complex tasks

**Very Large Models (30B+)**
- Speed: 5-10 tokens/sec
- Memory: ~20GB
- Latency: Slower but acceptable
- Use case: Critical tasks

## State Management

```
Session State:
├── conversation_history []
├── working_directory Path
├── model str
├── tools Dict[str, Tool]
└── session_start datetime

Conversation History:
[
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."},
  ...
]

Tool State:
{
  "tool_name": Tool(name, description, func),
  ...
}
```

## Error Handling

```
User Input
    ↓
Try: Parse & Validate
    ↓
Try: Call Ollama
    ↓  (timeout, connection error, etc.)
    ↓
Catch: Show user-friendly error
    ↓
Try: Execute Tools
    ↓  (file not found, permission error, etc.)
    ↓
Catch: Return error message
    ↓
Continue conversation
```

---

**This architecture ensures:**
- ✅ Complete privacy (everything local)
- ✅ Fast responses (optimized for M3 Max)
- ✅ Extensibility (easy to add features)
- ✅ Reliability (proper error handling)
- ✅ User control (you own the system)