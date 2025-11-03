#!/usr/bin/env python3
"""
Enhanced Local Code Agent with Tool Support
Inspired by Claude Code but running locally with Ollama
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional, Callable
import re
import requests
from datetime import datetime

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.tree import Tree
    from rich.table import Table
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "--break-system-packages"])
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.tree import Tree
    from rich.table import Table

console = Console()

class Tool:
    """Base class for tools"""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class EnhancedCodeAgent:
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.conversation_history: List[Dict] = []
        self.working_directory = Path.cwd()
        self.tools = self._register_tools()
        self.session_start = datetime.now()
        
    def _register_tools(self) -> Dict[str, Tool]:
        """Register available tools"""
        tools = {}
        
        tools['read_file'] = Tool(
            'read_file',
            'Read contents of a file. Usage: read_file(filepath)',
            self._read_file
        )
        
        tools['write_file'] = Tool(
            'write_file',
            'Write content to a file. Usage: write_file(filepath, content)',
            self._write_file
        )
        
        tools['edit_file'] = Tool(
            'edit_file',
            'Edit a file by replacing old content with new. Usage: edit_file(filepath, old_text, new_text)',
            self._edit_file
        )
        
        tools['run_command'] = Tool(
            'run_command',
            'Execute a shell command. Usage: run_command(command)',
            self._run_command
        )
        
        tools['list_files'] = Tool(
            'list_files',
            'List files in a directory. Usage: list_files(directory)',
            self._list_files
        )
        
        tools['search_files'] = Tool(
            'search_files',
            'Search for files matching a pattern. Usage: search_files(pattern)',
            self._search_files
        )
        
        tools['create_directory'] = Tool(
            'create_directory',
            'Create a new directory. Usage: create_directory(path)',
            self._create_directory
        )
        
        return tools
    
    def _read_file(self, filepath: str) -> str:
        """Read a file and return its contents"""
        try:
            path = Path(filepath)
            if not path.is_absolute():
                path = self.working_directory / path
            
            if not path.exists():
                return f"Error: File not found: {filepath}"
            
            content = path.read_text()
            
            # Display with syntax highlighting
            console.print(Panel(
                Syntax(content, path.suffix[1:] or "text", theme="monokai", line_numbers=True),
                title=f"📄 {path.name}",
                border_style="blue"
            ))
            
            return f"Successfully read {len(content)} characters from {filepath}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _write_file(self, filepath: str, content: str) -> str:
        """Write content to a file"""
        try:
            path = Path(filepath)
            if not path.is_absolute():
                path = self.working_directory / path
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            path.write_text(content)
            
            console.print(f"[green]✓ Written {len(content)} characters to {path}[/green]")
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def _edit_file(self, filepath: str, old_text: str, new_text: str) -> str:
        """Edit a file by replacing text"""
        try:
            path = Path(filepath)
            if not path.is_absolute():
                path = self.working_directory / path
            
            if not path.exists():
                return f"Error: File not found: {filepath}"
            
            content = path.read_text()
            
            if old_text not in content:
                return f"Error: Text to replace not found in file"
            
            new_content = content.replace(old_text, new_text)
            path.write_text(new_content)
            
            console.print(f"[green]✓ Edited {path}[/green]")
            return f"Successfully edited {filepath}"
        except Exception as e:
            return f"Error editing file: {str(e)}"
    
    def _run_command(self, command: str) -> str:
        """Execute a shell command"""
        try:
            console.print(f"[yellow]$ {command}[/yellow]")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.working_directory,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            
            if output:
                console.print(output)
            
            return f"Command executed. Exit code: {result.returncode}\n{output}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def _list_files(self, directory: str = ".") -> str:
        """List files in a directory"""
        try:
            path = Path(directory)
            if not path.is_absolute():
                path = self.working_directory / path
            
            if not path.exists() or not path.is_dir():
                return f"Error: Directory not found: {directory}"
            
            tree = Tree(f"📁 {path.name}/", guide_style="blue")
            
            def add_to_tree(parent, current_path, level=0):
                if level > 2:  # Limit depth
                    return
                
                try:
                    items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                    for item in items[:50]:  # Limit items
                        if item.name.startswith('.'):
                            continue
                        
                        if item.is_dir():
                            branch = parent.add(f"📁 {item.name}/")
                            add_to_tree(branch, item, level + 1)
                        else:
                            size = item.stat().st_size
                            size_str = self._format_size(size)
                            parent.add(f"📄 {item.name} [dim]({size_str})[/dim]")
                except PermissionError:
                    parent.add("[red]Permission denied[/red]")
            
            add_to_tree(tree, path)
            console.print(tree)
            
            return f"Listed contents of {directory}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def _search_files(self, pattern: str) -> str:
        """Search for files matching a pattern"""
        try:
            matches = list(self.working_directory.rglob(f"*{pattern}*"))
            matches = [m for m in matches if not any(part.startswith('.') for part in m.parts)]
            matches = matches[:50]  # Limit results
            
            if not matches:
                console.print(f"[yellow]No matches found for: {pattern}[/yellow]")
                return "No matches found"
            
            console.print(f"\n[green]Found {len(matches)} matches:[/green]")
            for match in matches:
                rel_path = match.relative_to(self.working_directory)
                icon = "📁" if match.is_dir() else "📄"
                console.print(f"  {icon} {rel_path}")
            
            return f"Found {len(matches)} matches for '{pattern}'"
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    def _create_directory(self, path: str) -> str:
        """Create a new directory"""
        try:
            dir_path = Path(path)
            if not dir_path.is_absolute():
                dir_path = self.working_directory / dir_path
            
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✓ Created directory: {dir_path}[/green]")
            return f"Successfully created {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with tool descriptions"""
        tools_desc = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])
        
        return f"""You are an expert AI coding assistant running locally. You help with coding, debugging, and file operations.

You have access to these tools:
{tools_desc}

To use a tool, write: TOOL[tool_name](arg1, arg2, ...)
Example: TOOL[read_file](main.py)
Example: TOOL[run_command](ls -la)
Example: TOOL[write_file](test.py, "print('hello')")

Current directory: {self.working_directory}
Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Guidelines:
1. Always explain what you're doing before using tools
2. For file operations, show the relevant code/content
3. Ask for confirmation before destructive operations
4. Provide clear, concise explanations
5. Use markdown formatting for better readability
"""
    
    def _extract_tool_calls(self, text: str) -> List[Dict]:
        """Extract tool calls from agent response"""
        # Pattern: TOOL[tool_name](args)
        pattern = r'TOOL\[(\w+)\]\((.*?)\)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        tool_calls = []
        for tool_name, args_str in matches:
            tool_calls.append({
                'tool': tool_name,
                'args': args_str
            })
        
        return tool_calls
    
    def _parse_args(self, args_str: str) -> tuple:
        """Parse tool arguments"""
        # Simple parsing - split by comma, strip quotes
        args = []
        current_arg = ""
        in_quotes = False
        
        for char in args_str:
            if char in ['"', "'"]:
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                args.append(current_arg.strip().strip('"').strip("'"))
                current_arg = ""
            else:
                current_arg += char
        
        if current_arg:
            args.append(current_arg.strip().strip('"').strip("'"))
        
        return tuple(args)
    
    def call_ollama(self, prompt: str) -> str:
        """Call Ollama API with streaming"""
        url = f"{self.base_url}/api/generate"
        
        # Build context from history
        context = self._build_system_prompt() + "\n\n"
        for msg in self.conversation_history[-6:]:  # Keep last 6 messages
            context += f"{msg['role']}: {msg['content']}\n\n"
        context += f"user: {prompt}\n\nassistant: "
        
        payload = {
            "model": self.model,
            "prompt": context,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "num_predict": 2048
            }
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            full_response = ""
            with Live(Spinner("dots", text="Thinking..."), console=console, refresh_per_second=10) as live:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            token = chunk['response']
                            full_response += token
                            # Update display
                            live.update(Markdown(full_response))
                        if chunk.get('done', False):
                            break
            
            return full_response
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be too slow."
        except Exception as e:
            console.print(f"[red]Error calling Ollama: {e}[/red]")
            return ""
    
    def execute_tool_calls(self, response: str) -> str:
        """Execute any tool calls in the response"""
        tool_calls = self._extract_tool_calls(response)
        
        if not tool_calls:
            return response
        
        # Display tool calls
        console.print("\n[cyan]🔧 Executing tools...[/cyan]")
        
        results = []
        for call in tool_calls:
            tool_name = call['tool']
            
            if tool_name not in self.tools:
                results.append(f"Error: Unknown tool '{tool_name}'")
                continue
            
            try:
                args = self._parse_args(call['args'])
                tool = self.tools[tool_name]
                result = tool.execute(*args)
                results.append(result)
            except Exception as e:
                results.append(f"Error executing {tool_name}: {str(e)}")
        
        # Combine results
        tool_results = "\n".join(results)
        
        # Remove tool calls from response and add results
        cleaned_response = re.sub(r'TOOL\[\w+\]\(.*?\)', '', response, flags=re.DOTALL)
        
        return cleaned_response + "\n\n" + tool_results
    
    def chat(self, user_input: str) -> str:
        """Main chat interface"""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response from Ollama
        response = self.call_ollama(user_input)
        
        # Execute any tool calls
        final_response = self.execute_tool_calls(response)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response


def print_welcome():
    """Print welcome screen"""
    welcome = """
# 🤖 Enhanced Local Code Agent
    
**Powered by Ollama** • Running locally on your machine

## Available Commands
- `/help` - Show this help
- `/clear` - Clear conversation history
- `/model <name>` - Switch model
- `/pwd` - Show current directory
- `/cd <path>` - Change directory
- `/tools` - List available tools
- `/exit` - Exit

## Tools
The agent has access to file operations, shell commands, and more!
Just describe what you want to do naturally.

**Examples:**
- "Read the contents of main.py"
- "List all Python files in this directory"
- "Run the tests using pytest"
- "Create a new file called test.js with a hello world function"
"""
    console.print(Panel(Markdown(welcome), border_style="cyan", title="Welcome", padding=1))


def main():
    print_welcome()
    
    # Check Ollama connection
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
        
        if not models:
            console.print("[yellow]No models found. Install one with: ollama pull llama3.2[/yellow]")
            return
        
        console.print("[green]✓ Connected to Ollama[/green]")
        
        # Show available models
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Size", style="magenta")
        
        for model in models[:10]:
            size = model.get('size', 0) / (1024**3)  # Convert to GB
            table.add_row(model['name'], f"{size:.1f} GB")
        
        console.print(table)
        
        model_names = [m['name'] for m in models]
        default_model = model_names[0]
        
        model = Prompt.ask("\nSelect model", default=default_model, choices=model_names)
        
    except requests.exceptions.Timeout:
        console.print("[red]✗ Could not connect to Ollama (timeout)[/red]")
        console.print("Make sure Ollama is running: [yellow]ollama serve[/yellow]")
        return
    except Exception as e:
        console.print(f"[red]✗ Error connecting to Ollama: {e}[/red]")
        return
    
    # Initialize agent
    agent = EnhancedCodeAgent(model=model)
    console.print(f"\n[cyan]🚀 Agent ready with {model}[/cyan]")
    console.print(f"[dim]Working directory: {agent.working_directory}[/dim]\n")
    
    # Main loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]❯[/bold cyan]")
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0]
                
                if cmd == '/exit':
                    console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                    
                elif cmd == '/clear':
                    agent.conversation_history = []
                    console.clear()
                    console.print("[green]✓ Conversation cleared[/green]")
                    continue
                    
                elif cmd == '/help':
                    print_welcome()
                    continue
                    
                elif cmd == '/pwd':
                    console.print(f"[blue]{agent.working_directory}[/blue]")
                    continue
                    
                elif cmd == '/cd':
                    if len(cmd_parts) > 1:
                        path = Path(cmd_parts[1]).resolve()
                        if path.exists() and path.is_dir():
                            agent.working_directory = path
                            console.print(f"[green]✓ Changed to {path}[/green]")
                        else:
                            console.print("[red]Directory not found[/red]")
                    continue
                    
                elif cmd == '/model':
                    if len(cmd_parts) > 1:
                        agent.model = cmd_parts[1]
                        console.print(f"[green]✓ Switched to {agent.model}[/green]")
                    continue
                    
                elif cmd == '/tools':
                    table = Table(title="Available Tools")
                    table.add_column("Tool", style="cyan")
                    table.add_column("Description", style="white")
                    
                    for name, tool in agent.tools.items():
                        table.add_row(name, tool.description)
                    
                    console.print(table)
                    continue
            
            # Normal chat
            console.print("\n[bold green]🤖 Assistant[/bold green]")
            response = agent.chat(user_input)
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Use /exit to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()