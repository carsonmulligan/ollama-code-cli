#!/usr/bin/env python3
import json,os,subprocess,sys,re,requests,time,difflib
from pathlib import Path
from typing import List,Dict,Optional,Callable
from datetime import datetime
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt,Confirm
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.tree import Tree
    from rich.table import Table
except ImportError:
    subprocess.check_call([sys.executable,"-m","pip","install","rich","--break-system-packages"])
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt,Confirm
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.tree import Tree
    from rich.table import Table
console=Console()

class TokenTracker:
    def __init__(self):self.total_tokens=self.prompt_tokens=self.completion_tokens=0
    def add_tokens(self,prompt:int=0,completion:int=0):self.prompt_tokens+=prompt;self.completion_tokens+=completion;self.total_tokens=self.prompt_tokens+self.completion_tokens
    def get_summary(self)->str:return f"↓{self.prompt_tokens//1000}k·↑{self.completion_tokens//1000}k·{self.total_tokens//1000}k"

def show_checkpoint(tool_name:str,message:str=""):
    console.print(f"\n[blue]⏺[/blue][bold]{tool_name}[/bold]")
    if message:console.print(f"[dim]⎿{message}[/dim]")

def show_diff(old:str,new:str,filename:str):
    old_lines,new_lines=old.splitlines(keepends=True),new.splitlines(keepends=True)
    diff=difflib.unified_diff(old_lines,new_lines,lineterm='',n=3)
    changes,diff_lines={'additions':0,'removals':0},[]
    for line in diff:
        if line.startswith('+++')or line.startswith('---'):continue
        elif line.startswith('@@'):diff_lines.append(('header',line.strip()))
        elif line.startswith('+'):changes['additions']+=1;diff_lines.append(('add',line))
        elif line.startswith('-'):changes['removals']+=1;diff_lines.append(('remove',line))
        else:diff_lines.append(('context',line))
    if diff_lines:
        console.print(f"[dim]⎿Updated {filename} with {changes['additions']} additions and {changes['removals']} removals[/dim]")
        for dtype,line in diff_lines[:20]:
            line_content=line.rstrip()
            if dtype=='header':console.print(f"[dim]{line_content}[/dim]")
            elif dtype=='add':console.print(f"[green]{line_content}[/green]")
            elif dtype=='remove':console.print(f"[red]{line_content}[/red]")
            else:console.print(f"[dim]{line_content}[/dim]")
        if len(diff_lines)>20:console.print(f"[dim]...{len(diff_lines)-20} more lines[/dim]")

class Todo:
    def __init__(self,content:str,status:str="pending",active_form:str=""):
        self.content,self.status,self.active_form=content,status,active_form or f"Working on: {content}"
    def to_dict(self):return{"content":self.content,"status":self.status,"activeForm":self.active_form}

class TodoList:
    def __init__(self):self.todos:List[Todo]=[]
    def add(self,content:str,status:str="pending",active_form:str=""):self.todos.append(Todo(content,status,active_form))
    def update(self,index:int,status:str=None,content:str=None):
        if 0<=index<len(self.todos):
            if status:self.todos[index].status=status
            if content:self.todos[index].content=content
    def get_current(self)->Optional[Todo]:
        for todo in self.todos:
            if todo.status=="in_progress":return todo
        return None
    def mark_complete(self,index:int):self.update(index,status="completed")
    def display(self):
        if not self.todos:console.print("[dim]No todos[/dim]");return
        table=Table(title="Task List")
        table.add_column("#",style="dim",width=3)
        table.add_column("Status",width=12)
        table.add_column("Task",style="cyan")
        status_icons={"pending":"⏸️ Pending","in_progress":"▶️ In Progress","completed":"✅ Completed"}
        for i,todo in enumerate(self.todos):
            status_display=status_icons.get(todo.status,todo.status)
            if todo.status=="in_progress":status_display=f"[yellow]{status_display}[/yellow]"
            elif todo.status=="completed":status_display=f"[green]{status_display}[/green]"
            table.add_row(str(i+1),status_display,todo.content)
        console.print(table)
    def get_summary(self)->str:
        if not self.todos:return "No todos"
        lines=[]
        for i,todo in enumerate(self.todos):
            status_icon={"pending":"⏸️","in_progress":"▶️","completed":"✅"}[todo.status]
            lines.append(f"{i+1}.[{todo.status}]{status_icon}{todo.content}")
        return"\n".join(lines)

class Tool:
    def __init__(self,name:str,description:str,func:Callable):self.name,self.description,self.func=name,description,func
    def execute(self,*args,**kwargs):return self.func(*args,**kwargs)

class EnhancedCodeAgent:
    def __init__(self,model:str="llama3.2",base_url:str="http://localhost:11434"):
        self.model,self.base_url=model,base_url
        self.conversation_history:List[Dict]=[]
        self.working_directory=Path.cwd()
        self.tools=self._register_tools()
        self.session_start=datetime.now()
        self.todo_list=TodoList()
        self.iterative_mode=False
        self.project_context=""
        self.token_tracker=TokenTracker()
        self.thinking_time=0

    def _register_tools(self)->Dict[str,Tool]:
        tools={}
        tools['read_file']=Tool('read_file','Read file. Usage: read_file(filepath)',self._read_file)
        tools['write_file']=Tool('write_file','Write file. Usage: write_file(filepath,content)',self._write_file)
        tools['edit_file']=Tool('edit_file','Edit file. Usage: edit_file(filepath,old_text,new_text)',self._edit_file)
        tools['run_command']=Tool('run_command','Run command. Usage: run_command(command)',self._run_command)
        tools['list_files']=Tool('list_files','List files. Usage: list_files() or list_files(directory)',lambda*args:self._list_files(args[0]if args and args[0]else"."))
        tools['search_files']=Tool('search_files','Search files. Usage: search_files(pattern)',self._search_files)
        tools['create_directory']=Tool('create_directory','Create directory. Usage: create_directory(path)',self._create_directory)
        tools['add_todo']=Tool('add_todo','Add todo. Usage: add_todo(task_description)',self._add_todo)
        tools['update_todo']=Tool('update_todo','Update todo. Usage: update_todo(task_number,status)',self._update_todo)
        tools['show_todos']=Tool('show_todos','Show todos. Usage: show_todos()',lambda*args:self._show_todos())
        return tools

    def _read_file(self,filepath:str)->str:
        try:
            path=Path(filepath)if Path(filepath).is_absolute()else self.working_directory/filepath
            if not path.exists():return f"Error: File not found: {filepath}"
            content=path.read_text()
            num_lines=len(content.splitlines())
            show_checkpoint(f"Read({path.name})",f"Read {num_lines} lines")
            display_content='\n'.join(content.splitlines()[:100])
            if num_lines>100:display_content+=f"\n...{num_lines-100} more lines"
            console.print(Panel(Syntax(display_content,path.suffix[1:]or"text",theme="monokai",line_numbers=True),title=f"📄{path.name}",border_style="blue"))
            return f"Successfully read {len(content)} characters from {filepath}"
        except Exception as e:return f"Error reading file: {str(e)}"

    def _write_file(self,filepath:str,content:str)->str:
        try:
            path=Path(filepath)if Path(filepath).is_absolute()else self.working_directory/filepath
            file_exists,old_content=path.exists(),path.read_text()if path.exists()else ""
            path.parent.mkdir(parents=True,exist_ok=True)
            try:processed_content=content.encode('utf-8').decode('unicode_escape')
            except:processed_content=content.replace('\\n','\n').replace('\\t','\t').replace('\\r','\r')
            path.write_text(processed_content)
            if file_exists:show_checkpoint(f"Update({path.name})");show_diff(old_content,processed_content,path.name)
            else:num_lines=len(processed_content.splitlines());show_checkpoint(f"Write({path.name})",f"Created with {num_lines} lines")
            return f"Successfully wrote to {filepath}"
        except Exception as e:return f"Error writing file: {str(e)}"

    def _edit_file(self,filepath:str,old_text:str,new_text:str)->str:
        try:
            path=Path(filepath)if Path(filepath).is_absolute()else self.working_directory/filepath
            if not path.exists():return f"Error: File not found: {filepath}"
            old_content=path.read_text()
            if old_text not in old_content:return f"Error: Text to replace not found in file"
            new_content=old_content.replace(old_text,new_text)
            path.write_text(new_content)
            show_checkpoint(f"Update({path.name})")
            show_diff(old_content,new_content,path.name)
            return f"Successfully edited {filepath}"
        except Exception as e:return f"Error editing file: {str(e)}"

    def _run_command(self,command:str)->str:
        try:
            console.print(f"[yellow]${command}[/yellow]")
            result=subprocess.run(command,shell=True,capture_output=True,text=True,cwd=self.working_directory,timeout=30)
            output=result.stdout
            if result.stderr:output+=f"\n[stderr]\n{result.stderr}"
            if output:console.print(output)
            return f"Command executed. Exit code: {result.returncode}\n{output}"
        except subprocess.TimeoutExpired:return "Error: Command timed out after 30 seconds"
        except Exception as e:return f"Error executing command: {str(e)}"

    def _list_files(self,directory:str=".")->str:
        try:
            path=Path(directory)if Path(directory).is_absolute()else self.working_directory/directory
            if not path.exists()or not path.is_dir():return f"Error: Directory not found: {directory}"
            tree=Tree(f"📁{path.name}/",guide_style="blue")
            def add_to_tree(parent,current_path,level=0):
                if level>2:return
                try:
                    items=sorted(current_path.iterdir(),key=lambda x:(not x.is_dir(),x.name))
                    for item in items[:50]:
                        if item.name.startswith('.'):continue
                        if item.is_dir():branch=parent.add(f"📁{item.name}/");add_to_tree(branch,item,level+1)
                        else:size=item.stat().st_size;size_str=self._format_size(size);parent.add(f"📄{item.name}[dim]({size_str})[/dim]")
                except PermissionError:parent.add("[red]Permission denied[/red]")
            add_to_tree(tree,path)
            console.print(tree)
            return f"Listed contents of {directory}"
        except Exception as e:return f"Error listing directory: {str(e)}"

    def _search_files(self,pattern:str)->str:
        try:
            matches=list(self.working_directory.rglob(f"*{pattern}*"))
            matches=[m for m in matches if not any(part.startswith('.')for part in m.parts)]
            matches=matches[:50]
            if not matches:console.print(f"[yellow]No matches found for: {pattern}[/yellow]");return "No matches found"
            console.print(f"\n[green]Found {len(matches)} matches:[/green]")
            for match in matches:
                rel_path=match.relative_to(self.working_directory)
                icon="📁"if match.is_dir()else"📄"
                console.print(f"{icon}{rel_path}")
            return f"Found {len(matches)} matches for '{pattern}'"
        except Exception as e:return f"Error searching: {str(e)}"

    def _create_directory(self,path:str)->str:
        try:
            dir_path=Path(path)if Path(path).is_absolute()else self.working_directory/path
            dir_path.mkdir(parents=True,exist_ok=True)
            console.print(f"[green]✓Created directory: {dir_path}[/green]")
            return f"Successfully created {path}"
        except Exception as e:return f"Error creating directory: {str(e)}"

    def _format_size(self,size:int)->str:
        for unit in['B','KB','MB','GB']:
            if size<1024:return f"{size:.1f}{unit}"
            size/=1024
        return f"{size:.1f}TB"

    def _add_todo(self,task:str)->str:
        try:
            self.todo_list.add(task,status="pending",active_form=f"Working on: {task}")
            console.print(f"[green]✓Added todo: {task}[/green]")
            return f"Added task: {task}"
        except Exception as e:return f"Error adding todo: {str(e)}"

    def _update_todo(self,task_number:str,status:str)->str:
        try:
            index=int(task_number)-1
            if status not in["pending","in_progress","completed"]:return f"Error: Invalid status. Use pending, in_progress, or completed"
            self.todo_list.update(index,status=status)
            console.print(f"[green]✓Updated task {task_number} to {status}[/green]")
            return f"Updated task {task_number} to {status}"
        except Exception as e:return f"Error updating todo: {str(e)}"

    def _show_todos(self)->str:
        try:self.todo_list.display();return "Displayed todo list"
        except Exception as e:return f"Error showing todos: {str(e)}"

    def init_project(self)->str:
        console.print("\n[cyan]🔍Analyzing codebase...[/cyan]\n")
        analysis=[]
        readme_files=['README.md','README.txt','README']
        for readme in readme_files:
            readme_path=self.working_directory/readme
            if readme_path.exists():
                try:content=readme_path.read_text()[:2000];analysis.append(f"## README Summary\n{content[:500]}...");break
                except:pass
        analysis.append("\n## Project Structure")
        try:
            items=sorted(self.working_directory.iterdir(),key=lambda x:(not x.is_dir(),x.name))
            structure_lines=[]
            for item in items[:20]:
                if item.name.startswith('.'):continue
                icon="📁"if item.is_dir()else"📄"
                structure_lines.append(f"{icon}{item.name}")
            analysis.append("\n".join(structure_lines))
        except Exception as e:analysis.append(f"Error reading structure: {e}")
        analysis.append("\n## Detected Technologies")
        tech_indicators={'package.json':'Node.js/JavaScript','requirements.txt':'Python','Cargo.toml':'Rust','go.mod':'Go','pom.xml':'Java (Maven)','build.gradle':'Java (Gradle)','Gemfile':'Ruby'}
        found_tech=[]
        for file,tech in tech_indicators.items():
            if(self.working_directory/file).exists():found_tech.append(f"•{tech}")
        if found_tech:analysis.append("\n".join(found_tech))
        else:analysis.append("•No common project files detected")
        self.project_context="\n".join(analysis)
        console.print(Panel(Markdown(self.project_context),title="📋Project Analysis",border_style="cyan"))
        return "Project initialized and analyzed"

    def _build_system_prompt(self)->str:
        tools_desc="\n".join([f"-{name}:{tool.description}"for name,tool in self.tools.items()])
        context_section=f"\n## Project Context\n{self.project_context}\n"if self.project_context else""
        todo_section=f"\n## Current Tasks\n{self.todo_list.get_summary()}\n"if self.todo_list.todos else""
        return f"""You are an expert AI coding assistant running locally. You help with coding, debugging, and file operations.

You have access to these tools:
{tools_desc}

To use a tool, format it exactly as: TOOL[tool_name](arg1, arg2, ...)

IMPORTANT FORMATTING RULES:
- Put each tool call on its own line
- For write_file and edit_file, wrap content in quotes
- Use proper escaping for quotes inside content
- For multi-line content, use triple quotes or escape newlines

Examples:
- TOOL[read_file](main.py)
- TOOL[run_command](ls -la)
- TOOL[write_file](test.py, "print('hello world')")
- TOOL[write_file](app.js, "function greet() {{\\n  console.log('Hi');\\n}}")
- TOOL[edit_file](config.py, "DEBUG = False", "DEBUG = True")
- TOOL[add_todo](Implement user authentication)
- TOOL[update_todo](1, in_progress)
- TOOL[show_todos]()

Current directory: {self.working_directory}
Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{context_section}{todo_section}

Guidelines:
1. Always explain what you're doing before using tools
2. For file operations, show the relevant code/content
3. Ask for confirmation before destructive operations
4. Provide clear, concise explanations
5. Use markdown formatting for better readability
6. When writing files, always show what content you're writing

ITERATIVE WORKFLOW (for complex tasks):
1. Break down complex requests into smaller tasks using TOOL[add_todo](task_description)
2. Mark tasks as in_progress when you start: TOOL[update_todo](1, in_progress)
3. Complete each task before moving to the next
4. Mark tasks as completed: TOOL[update_todo](1, completed)
5. Check your work and verify results
6. Continue until all tasks are done

Example workflow:
User asks: "Create a REST API with authentication"
1. TOOL[add_todo](Design API endpoints and structure)
2. TOOL[add_todo](Implement basic server setup)
3. TOOL[add_todo](Add authentication middleware)
4. TOOL[add_todo](Create API routes)
5. TOOL[add_todo](Write tests)
6. Then work through each task iteratively

Always think step-by-step and use the todo list for multi-step tasks!
"""

    def _extract_tool_calls(self,text:str)->List[Dict]:
        tool_calls=[]
        pattern=r'TOOL\[(\w+)\]'
        for match in re.finditer(pattern,text):
            tool_name=match.group(1)
            start_pos=match.end()
            if start_pos<len(text)and text[start_pos]=='(':
                paren_count,in_quotes,quote_char,end_pos=0,False,None,start_pos
                for i in range(start_pos,len(text)):
                    char=text[i]
                    if char in['"',"'"]and(i==0 or text[i-1]!='\\'):
                        if not in_quotes:in_quotes,quote_char=True,char
                        elif char==quote_char:in_quotes,quote_char=False,None
                    if not in_quotes:
                        if char=='(':paren_count+=1
                        elif char==')':
                            paren_count-=1
                            if paren_count==0:end_pos=i;break
                if end_pos>start_pos:
                    args_str=text[start_pos+1:end_pos]
                    tool_calls.append({'tool':tool_name,'args':args_str.strip()})
        return tool_calls

    def _parse_args(self,args_str:str)->tuple:
        args,current_arg,in_quotes,quote_char,paren_depth,i=[],"",False,None,0,0
        while i<len(args_str):
            char=args_str[i]
            if char=='\\'and i+1<len(args_str)and in_quotes:
                current_arg+=char;i+=1
                if i<len(args_str):current_arg+=args_str[i]
                i+=1;continue
            if char in['"',"'"]and paren_depth==0:
                if not in_quotes:in_quotes,quote_char=True,char
                elif char==quote_char:in_quotes,quote_char=False,None
                else:current_arg+=char
                i+=1;continue
            if not in_quotes:
                if char=='(':paren_depth+=1
                elif char==')':paren_depth-=1
            if char==','and not in_quotes and paren_depth==0:args.append(current_arg.strip());current_arg=""
            else:current_arg+=char
            i+=1
        if current_arg.strip():args.append(current_arg.strip())
        return tuple(args)

    def call_ollama(self,prompt:str)->str:
        url=f"{self.base_url}/api/generate"
        context=self._build_system_prompt()+"\n\n"
        for msg in self.conversation_history[-6:]:context+=f"{msg['role']}:{msg['content']}\n\n"
        context+=f"user:{prompt}\n\nassistant:"
        payload={"model":self.model,"prompt":context,"stream":True,"options":{"temperature":0.7,"num_predict":2048}}
        try:
            start_time=time.time()
            response=requests.post(url,json=payload,stream=True,timeout=60)
            response.raise_for_status()
            full_response,token_count,prompt_tokens="",0,len(context.split())
            with Live(Spinner("dots",text="Thinking..."),console=console,refresh_per_second=10)as live:
                for line in response.iter_lines():
                    if line:
                        chunk=json.loads(line)
                        if'response'in chunk:token=chunk['response'];full_response+=token;token_count+=1;live.update(Markdown(full_response))
                        if chunk.get('done',False):self.thinking_time=time.time()-start_time;console.print(f"\n[dim]∴Thought for {self.thinking_time:.1f}s[/dim]");break
            self.token_tracker.add_tokens(prompt=prompt_tokens,completion=token_count)
            return full_response
        except requests.exceptions.Timeout:return "Error: Request timed out. The model might be too slow."
        except Exception as e:console.print(f"[red]Error calling Ollama: {e}[/red]");return ""

    def execute_tool_calls(self,response:str)->str:
        tool_calls=self._extract_tool_calls(response)
        if not tool_calls:return response
        results=[]
        for call in tool_calls:
            tool_name=call['tool']
            if tool_name not in self.tools:results.append(f"Error: Unknown tool '{tool_name}'");continue
            try:
                args=self._parse_args(call['args'])
                tool=self.tools[tool_name]
                result=tool.execute(*args)
                results.append(result)
            except Exception as e:
                error_msg=f"Error executing {tool_name}: {str(e)}"
                console.print(f"[red]✗{error_msg}[/red]")
                results.append(error_msg)
        tool_results="\n".join(results)
        cleaned_response=re.sub(r'TOOL\[\w+\]\((.*?)\)(?=\s|$|TOOL)','',response,flags=re.DOTALL|re.MULTILINE).strip()
        return cleaned_response+"\n\n"+tool_results

    def _extract_file_mentions(self,text:str)->List[str]:
        pattern=r'@([\w\-./]+\.\w+)'
        matches=re.findall(pattern,text)
        return matches

    def _get_available_files(self,pattern:str="*")->List[Path]:
        try:
            files=[]
            for path in self.working_directory.rglob(pattern):
                if any(part.startswith('.')for part in path.parts):continue
                if any(ignore in str(path)for ignore in['node_modules','__pycache__','venv','.git']):continue
                if path.is_file():files.append(path)
            return sorted(files,key=lambda p:p.name)[:100]
        except Exception as e:console.print(f"[red]Error listing files: {e}[/red]");return[]

    def _process_file_mentions(self,user_input:str)->str:
        mentioned_files=self._extract_file_mentions(user_input)
        if not mentioned_files:return user_input
        file_contexts=[]
        for mentioned_file in mentioned_files:
            file_path=Path(mentioned_file)if Path(mentioned_file).is_absolute()else self.working_directory/mentioned_file
            if file_path.exists()and file_path.is_file():
                try:
                    content=file_path.read_text()[:5000]
                    rel_path=file_path.relative_to(self.working_directory)if file_path.is_relative_to(self.working_directory)else file_path
                    file_contexts.append(f"\n## Context from @{rel_path}\n```\n{content}\n```\n")
                    console.print(f"[dim]📎Attached: {rel_path}[/dim]")
                except Exception as e:console.print(f"[yellow]⚠️Could not read {mentioned_file}: {e}[/yellow]")
        if file_contexts:enhanced_input=user_input+"\n\n"+"\n".join(file_contexts);return enhanced_input
        return user_input

    def chat(self,user_input:str)->str:
        enhanced_input=self._process_file_mentions(user_input)
        self.conversation_history.append({"role":"user","content":enhanced_input})
        response=self.call_ollama(enhanced_input)
        final_response=self.execute_tool_calls(response)
        self.conversation_history.append({"role":"assistant","content":final_response})
        status_parts=[]
        current_todo=self.todo_list.get_current()
        if current_todo:status_parts.append(f"·{current_todo.active_form}")
        elapsed=(datetime.now()-self.session_start).total_seconds()
        elapsed_str=f"{int(elapsed)}s"if elapsed<60 else f"{int(elapsed/60)}m"
        status_parts.append(f"·{elapsed_str}")
        status_parts.append(f"·{self.token_tracker.get_summary()}")
        if status_parts:console.print(f"\n[dim]{' '.join(status_parts)}[/dim]")
        return final_response

def print_welcome():
    welcome="""# 🤖 Local Code Agent
**Powered by Ollama**•Running locally
## Commands
`/help` `/init` `/files [pattern]` `/clear` `/model <name>` `/pwd` `/cd <path>` `/tools` `/todo` `/plan <request>` `/exit`
## Features
- **File Mentions**: Use `@filename` to attach context
- **Iterative Tasks**: Agent breaks down complex tasks
- **Todo List**: Track multi-step tasks
- **Project Context**: Use `/init` for codebase understanding"""
    console.print(Panel(Markdown(welcome),border_style="cyan",title="Welcome",padding=1))

def main():
    print_welcome()
    try:
        response=requests.get("http://localhost:11434/api/tags",timeout=5)
        response.raise_for_status()
        models=response.json().get('models',[])
        if not models:console.print("[yellow]No models found. Install one with: ollama pull llama3.2[/yellow]");return
        console.print("[green]✓Connected to Ollama[/green]")
        table=Table(title="Available Models")
        table.add_column("Model",style="cyan")
        table.add_column("Size",style="magenta")
        for model in models[:10]:size=model.get('size',0)/(1024**3);table.add_row(model['name'],f"{size:.1f}GB")
        console.print(table)
        model_names=[m['name']for m in models]
        default_model=model_names[0]
        model=Prompt.ask("\nSelect model",default=default_model,choices=model_names)
    except requests.exceptions.Timeout:console.print("[red]✗Could not connect to Ollama (timeout)[/red]");console.print("Make sure Ollama is running: [yellow]ollama serve[/yellow]");return
    except Exception as e:console.print(f"[red]✗Error connecting to Ollama: {e}[/red]");return
    agent=EnhancedCodeAgent(model=model)
    console.print(f"\n[cyan]🚀Agent ready with {model}[/cyan]")
    console.print(f"[dim]Working directory: {agent.working_directory}[/dim]\n")
    while True:
        try:
            user_input=Prompt.ask("\n[bold cyan]❯[/bold cyan]")
            if not user_input.strip():continue
            if user_input.startswith('/'):
                cmd_parts=user_input.split(maxsplit=1)
                cmd=cmd_parts[0]
                if cmd=='/exit':console.print("[yellow]👋Goodbye![/yellow]");break
                elif cmd=='/clear':agent.conversation_history=[];console.clear();console.print("[green]✓Conversation cleared[/green]");continue
                elif cmd=='/help'or cmd=='/commands':print_welcome();continue
                elif cmd=='/files':
                    pattern=cmd_parts[1]if len(cmd_parts)>1 else"*"
                    files=agent._get_available_files(pattern)
                    if files:
                        console.print(f"\n[cyan]📁Available files (use @filename to mention):[/cyan]\n")
                        for file in files[:50]:
                            rel_path=file.relative_to(agent.working_directory)
                            size=file.stat().st_size
                            size_str=agent._format_size(size)
                            console.print(f"@{rel_path}[dim]({size_str})[/dim]")
                        if len(files)>50:console.print(f"\n[dim]...and {len(files)-50} more files[/dim]")
                    else:console.print(f"[yellow]No files found matching pattern: {pattern}[/yellow]")
                    continue
                elif cmd=='/pwd':console.print(f"[blue]{agent.working_directory}[/blue]");continue
                elif cmd=='/cd':
                    if len(cmd_parts)>1:
                        path=Path(cmd_parts[1]).resolve()
                        if path.exists()and path.is_dir():agent.working_directory=path;console.print(f"[green]✓Changed to {path}[/green]")
                        else:console.print("[red]Directory not found[/red]")
                    continue
                elif cmd=='/model':
                    if len(cmd_parts)>1:agent.model=cmd_parts[1];console.print(f"[green]✓Switched to {agent.model}[/green]")
                    continue
                elif cmd=='/tools':
                    table=Table(title="Available Tools")
                    table.add_column("Tool",style="cyan")
                    table.add_column("Description",style="white")
                    for name,tool in agent.tools.items():table.add_row(name,tool.description)
                    console.print(table)
                    continue
                elif cmd=='/init':agent.init_project();continue
                elif cmd=='/todo':agent.todo_list.display();continue
                elif cmd=='/plan':
                    if len(cmd_parts)>1:
                        request=cmd_parts[1]
                        console.print(f"\n[cyan]📋Creating plan for: {request}[/cyan]\n")
                        plan_prompt=f"Create a detailed step-by-step plan to accomplish this: {request}. Break it down into specific tasks that can be tracked. Use the add_todo tool for each step."
                        console.print("\n[bold green]🤖Assistant[/bold green]")
                        response=agent.chat(plan_prompt)
                        console.print()
                    else:console.print("[yellow]Usage: /plan <your request>[/yellow]")
                    continue
            console.print("\n[bold green]🤖Assistant[/bold green]")
            response=agent.chat(user_input)
            console.print()
        except KeyboardInterrupt:console.print("\n[yellow]Use /exit to quit[/yellow]")
        except Exception as e:console.print(f"[red]Error: {e}[/red]");import traceback;traceback.print_exc()

if __name__=="__main__":main()
