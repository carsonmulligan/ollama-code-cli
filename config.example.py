"""
Configuration file for Local Code Agent
Copy this to config.py and customize as needed
"""

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"

# Model-specific settings
MODEL_CONFIGS = {
    "llama3.2:3b": {
        "temperature": 0.7,
        "num_predict": 2048,
        "top_k": 40,
        "top_p": 0.9,
        "context_window": 4096,
    },
    "qwen2.5-coder:7b": {
        "temperature": 0.5,  # Lower for more deterministic code
        "num_predict": 3072,
        "top_k": 40,
        "top_p": 0.95,
        "context_window": 8192,
    },
    "deepseek-coder-v2:16b": {
        "temperature": 0.4,
        "num_predict": 4096,
        "top_k": 50,
        "top_p": 0.95,
        "context_window": 16384,
    }
}

# Agent Behavior
MAX_CONVERSATION_HISTORY = 10  # Number of messages to keep in context
ENABLE_AUTO_TOOL_EXECUTION = True  # Auto-execute tool calls without confirmation
STREAM_RESPONSE = True  # Stream tokens as they arrive
SHOW_THINKING = True  # Show "Thinking..." spinner

# File Operations
MAX_FILE_SIZE_MB = 10  # Maximum file size to read (MB)
ALLOWED_FILE_EXTENSIONS = [
    # Code
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
    # Web
    '.html', '.css', '.scss', '.sass', '.less',
    # Config
    '.json', '.yaml', '.yml', '.toml', '.ini', '.xml',
    # Docs
    '.md', '.txt', '.rst',
    # Data
    '.csv', '.tsv',
    # Other
    '.sh', '.bash', '.zsh', '.fish', '.sql'
]

IGNORED_DIRECTORIES = [
    'node_modules', '__pycache__', '.git', '.venv', 'venv',
    'dist', 'build', '.next', '.nuxt', 'target', 'bin', 'obj',
    '.idea', '.vscode', '*.egg-info'
]

# Shell Commands
COMMAND_TIMEOUT_SECONDS = 30
SAFE_COMMANDS = [
    'ls', 'cat', 'head', 'tail', 'grep', 'find', 'pwd',
    'echo', 'git status', 'git log', 'git diff',
    'python --version', 'node --version', 'npm --version'
]

# Dangerous commands that require confirmation
DANGEROUS_COMMANDS = [
    'rm', 'rmdir', 'del', 'format', 'dd', 'mv',
    'chmod +x', 'sudo', 'su', 'shutdown', 'reboot'
]

# UI Configuration
THEME = "monokai"  # Syntax highlighting theme
SHOW_LINE_NUMBERS = True
MAX_DISPLAY_LINES = 500  # Maximum lines to display for file contents
TRUNCATE_LONG_OUTPUT = True

# Colors
COLOR_SCHEME = {
    "user_prompt": "bold cyan",
    "assistant": "bold green",
    "system": "yellow",
    "error": "red",
    "success": "green",
    "info": "blue",
    "warning": "yellow"
}

# Custom System Prompt (optional)
CUSTOM_SYSTEM_PROMPT = """
You are an expert AI coding assistant specialized in:
- Modern web development (React, Next.js, TypeScript)
- Python development and data science
- System administration and DevOps
- Clean code practices and design patterns

Your approach:
1. Always explain your reasoning
2. Provide code examples when relevant
3. Suggest best practices
4. Ask clarifying questions when needed
5. Be concise but thorough

When using tools:
- Always explain what you're about to do
- Show relevant code with syntax highlighting
- Confirm before making destructive changes
"""

# Logging
ENABLE_LOGGING = True
LOG_FILE = "agent.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Performance
ENABLE_CACHING = True  # Cache model responses (experimental)
CACHE_DIR = ".agent_cache"

# Features
FEATURES = {
    "web_search": False,  # Coming soon
    "git_integration": False,  # Coming soon
    "database_tools": False,  # Coming soon
    "api_testing": False,  # Coming soon
}

# Keyboard Shortcuts (for future GUI version)
SHORTCUTS = {
    "clear_history": "Ctrl+L",
    "interrupt": "Ctrl+C",
    "paste_mode": "Ctrl+V",
    "run_last_command": "Ctrl+R"
}

# Custom Tools
# Add your own tool definitions here
CUSTOM_TOOLS = [
    # Example:
    # {
    #     "name": "deploy_to_production",
    #     "description": "Deploy the application to production",
    #     "command": "bash scripts/deploy.sh",
    #     "requires_confirmation": True
    # }
]

# API Keys (for future integrations)
API_KEYS = {
    # "anthropic": "sk-...",  # For Claude API fallback
    # "openai": "sk-...",     # For GPT fallback
    # "github": "ghp_...",    # For GitHub integration
}

# Model Aliases
MODEL_ALIASES = {
    "fast": "llama3.2:3b",
    "balanced": "qwen2.5-coder:7b",
    "powerful": "deepseek-coder-v2:16b",
    "default": "qwen2.5-coder:7b"
}

# Experimental Features
EXPERIMENTAL = {
    "multi_agent": False,  # Multiple agents working together
    "auto_debug": False,   # Automatically debug failing code
    "code_review": False,  # Automated code review
    "refactoring": False,  # Suggest refactorings
}

# Session Settings
AUTO_SAVE_HISTORY = True
HISTORY_FILE = ".agent_history"
MAX_HISTORY_SIZE = 1000

# Context Awareness
ANALYZE_PROJECT_STRUCTURE = True  # Auto-analyze project on start
DETECT_LANGUAGE = True            # Auto-detect programming language
SUGGEST_TOOLS = True              # Suggest relevant tools for tasks

# Safety
REQUIRE_CONFIRMATION_FOR = [
    "delete_files",
    "run_sudo",
    "modify_system_files",
    "commit_changes",
    "push_to_remote"
]

SANDBOX_MODE = False  # Run all commands in isolated environment (requires Docker)

# Advanced
ENABLE_FUNCTION_CALLING = True  # Use structured function calling
PARALLEL_TOOL_EXECUTION = False  # Execute multiple tools simultaneously
MAX_PARALLEL_TOOLS = 3

# Development
DEBUG_MODE = False
VERBOSE_LOGGING = False
SHOW_RAW_RESPONSES = False  # Show raw model output

# Custom Prompts for Specific Tasks
TASK_PROMPTS = {
    "refactor": "Focus on improving code quality, readability, and maintainability.",
    "debug": "Carefully analyze the error and provide a step-by-step solution.",
    "optimize": "Look for performance bottlenecks and suggest optimizations.",
    "test": "Write comprehensive tests covering edge cases.",
    "document": "Add clear, helpful documentation and docstrings."
}

# File Templates
FILE_TEMPLATES = {
    "python": """#!/usr/bin/env python3
'''
{filename}
{description}
'''

def main():
    pass

if __name__ == "__main__":
    main()
""",
    "javascript": """/**
 * {filename}
 * {description}
 */

function main() {
    // Your code here
}

main();
""",
}

# Git Integration Settings
GIT_CONFIG = {
    "auto_commit": False,
    "commit_message_template": "[Agent] {action}: {description}",
    "auto_push": False,
    "branch_prefix": "agent/"
}

# Project Defaults
PROJECT_DEFAULTS = {
    "python": {
        "venv": ".venv",
        "requirements": "requirements.txt",
        "formatter": "black",
        "linter": "pylint"
    },
    "javascript": {
        "package_manager": "npm",
        "formatter": "prettier",
        "linter": "eslint"
    }
}

# Notes:
# 1. To use this config, rename to config.py and import in your agent
# 2. Sensitive data (API keys) should be in a separate .env file
# 3. You can override any setting via command line arguments
# 4. Settings marked "Coming soon" are placeholders for future features