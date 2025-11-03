#!/usr/bin/env python3
"""
Local Code Agent - A Claude Code-inspired CLI agent using Ollama
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
import requests
from datetime import datetime

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "--break-system-packages"])
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner

console = Console()

class OllamaAgent:
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.conversation_history: List[Dict] = []
        self.working_directory = Path.cwd()
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        return """You are an expert AI coding assistant running locally. You help users with:
- Writing and debugging code
- Explaining technical concepts
- File operations (reading, writing, editing)
- Running shell commands
- Project organization

When you need to perform actions, use these special command formats:
- `@read <filepath>` - Read a file
- `@write <filepath>` - Write content to a file
- `@edit <filepath>` - Edit an existing file
- `@shell <command>` - Run a shell command
- `@ls [directory]` - List directory contents
- `@search <pattern>` - Search for files/content

Always explain what you're doing and ask for confirmation before making significant changes.
Current directory: {cwd}
""".format(cwd=self.working_directory)

    def call_ollama(self, prompt: str, stream: bool = True) -> str:
        """Call Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        messages = self.system_prompt + "\n\n"
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages for context
            messages += f"{msg['role']}: {msg['content']}\n"
        messages += f"user: {prompt}\nassistant: "
        
        payload = {
            "model": self.model,
            "prompt": messages,
            "stream": stream
        }
        
        try:
            response = requests.post(url, json=payload, stream=stream)
            response.raise_for_status()
            
            full_response = ""
            if stream:
                with Live(Spinner("dots", text="Thinking..."), console=console) as live:
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                token = chunk['response']
                                full_response += token
                                live.update(Markdown(full_response))
                            if chunk.get('done', False):
                                break
            else:
                result = response.json()
                full_response = result.get('response', '')
            
            return full_response
        except Exception as e:
            console.print(f"[red]Error calling Ollama: {e}[/red]")
            return ""

    def execute_command(self, command: str, args: str) -> str:
        """Execute special commands"""
        try:
            if command == "@read":
                filepath = Path(args.strip())
                if filepath.exists():
                    content = filepath.read_text()
                    console.print(Panel(
                        Syntax(content, filepath.suffix[1:] or "text", theme="monokai"),
                        title=f"📄 {filepath}",
                        border_style="blue"
                    ))
                    return f"File content loaded: {filepath}"
                return f"File not found: {filepath}"
            
            elif command == "@write":
                parts = args.split('\n', 1)
                filepath = Path(parts[0].strip())
                content = parts[1] if len(parts) > 1 else ""
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(content)
                console.print(f"[green]✓ Written to {filepath}[/green]")
                return f"File written: {filepath}"
            
            elif command == "@shell":
                console.print(f"[yellow]$ {args}[/yellow]")
                result = subprocess.run(
                    args, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    cwd=self.working_directory
                )
                output = result.stdout + result.stderr
                console.print(output)
                return output
            
            elif command == "@ls":
                directory = Path(args.strip() or '.')
                if directory.exists() and directory.is_dir():
                    files = list(directory.iterdir())
                    for f in sorted(files):
                        icon = "📁" if f.is_dir() else "📄"
                        console.print(f"{icon} {f.name}")
                    return f"Listed {len(files)} items"
                return "Directory not found"
            
            elif command == "@search":
                pattern = args.strip()
                results = list(self.working_directory.rglob(f"*{pattern}*"))
                for r in results[:20]:  # Limit to 20 results
                    console.print(f"  {r.relative_to(self.working_directory)}")
                return f"Found {len(results)} matches"
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return f"Error: {e}"
        
        return "Unknown command"

    def process_response(self, response: str) -> str:
        """Process response and execute any commands"""
        lines = response.split('\n')
        processed = []
        
        for line in lines:
            if line.strip().startswith('@'):
                parts = line.strip().split(' ', 1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                result = self.execute_command(command, args)
                processed.append(result)
            else:
                processed.append(line)
        
        return '\n'.join(processed)

    def chat(self, user_input: str) -> str:
        """Main chat interface"""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        response = self.call_ollama(user_input)
        
        # Process any special commands in the response
        # processed_response = self.process_response(response)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response

def print_welcome():
    """Print welcome message"""
    welcome = """
# 🤖 Local Code Agent
    
**Powered by Ollama** • Running locally on your machine

Available commands:
- `/help` - Show this help message
- `/clear` - Clear conversation history
- `/model <name>` - Switch model
- `/pwd` - Show current directory
- `/cd <path>` - Change directory
- `/exit` - Exit the agent

The agent can help you with coding tasks, file operations, and more!
"""
    console.print(Panel(Markdown(welcome), border_style="cyan", title="Welcome"))

def main():
    # Print welcome screen
    print_welcome()
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        models = response.json().get('models', [])
        model_names = [m['name'] for m in models]
        
        if not model_names:
            console.print("[yellow]No models found. Please run: ollama pull llama3.2[/yellow]")
            return
            
        console.print(f"[green]✓ Connected to Ollama[/green]")
        console.print(f"Available models: {', '.join(model_names[:5])}\n")
        
        # Let user choose model
        default_model = model_names[0]
        model = Prompt.ask("Select model", default=default_model, choices=model_names)
        
    except Exception as e:
        console.print(f"[red]✗ Could not connect to Ollama: {e}[/red]")
        console.print("Make sure Ollama is running: [yellow]ollama serve[/yellow]")
        return
    
    # Initialize agent
    agent = OllamaAgent(model=model)
    console.print(f"\n[cyan]Agent ready with {model}[/cyan]\n")
    
    # Main loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if not user_input.strip():
                continue
            
            # Handle special commands
            if user_input.startswith('/'):
                cmd = user_input.split()[0]
                
                if cmd == '/exit':
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                elif cmd == '/clear':
                    agent.conversation_history = []
                    console.print("[green]✓ Conversation cleared[/green]")
                    continue
                elif cmd == '/help':
                    print_welcome()
                    continue
                elif cmd == '/pwd':
                    console.print(f"[blue]{agent.working_directory}[/blue]")
                    continue
                elif cmd == '/cd':
                    path = user_input.split(maxsplit=1)[1] if len(user_input.split()) > 1 else '.'
                    new_path = Path(path).resolve()
                    if new_path.exists() and new_path.is_dir():
                        agent.working_directory = new_path
                        console.print(f"[green]✓ Changed to {new_path}[/green]")
                    else:
                        console.print("[red]Directory not found[/red]")
                    continue
                elif cmd == '/model':
                    new_model = user_input.split(maxsplit=1)[1] if len(user_input.split()) > 1 else None
                    if new_model:
                        agent.model = new_model
                        console.print(f"[green]✓ Switched to {new_model}[/green]")
                    continue
            
            # Process normal chat
            console.print("\n[bold green]Assistant[/bold green]")
            response = agent.chat(user_input)
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Use /exit to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()