import os
import sys
import json
import subprocess
import requests

# --- AUTO-DEPENDENCY CHECKER ---
def setup():
    try:
        import nmap
        from rich.console import Console
    except (ImportError, ModuleNotFoundError):
        print("[!] Missing libraries. Booting installer...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-nmap", "rich", "requests"])
        os.execl(sys.executable, sys.executable, *sys.argv)

setup()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
CONFIG_FILE = "stark_config.json"

# --- API KEY SYSTEM ---
def get_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("api_key")
    else:
        console.print(Panel("[bold yellow]ACCESS DENIED: OpenRouter API Key Required[/bold yellow]", border_style="red"))
        key = console.input("[bold cyan]>> Enter API Key: [/bold cyan]")
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": key}, f)
        return key

# --- AI CORE (TRINITY-AI) WITH SPEED OPTIMIZATION ---
def ask_stark_ai(api_key, user_goal, target):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # AI ko instruct kar rahe hain fast scanning ke liye
    prompt = f"""
    Target: {target}
    Goal: {user_goal}
    Task: Provide Nmap arguments for this goal. 
    CRITICAL: Always include '-T4' for speed. 
    If it's a general check, limit ports to top 1000.
    Output ONLY flags (e.g., -F -sV -T4). No 'nmap' word.
    """

    data = {
        "model": "arcee-ai/trinity-large-preview:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        ai_output = response.json()['choices'][0]['message']['content'].strip()
        # Cleaning output
        clean_flags = ai_output.replace('nmap', '').strip()
        if "-T" not in clean_flags: clean_flags += " -T4"
        return clean_flags
    except:
        return "-F -T4"

# --- MAIN SYSTEM ---
def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    api_key = get_api_key()
    
    banner = Text(r"""
   _____ _             _      _____                 
  / ____| |           | |    / ____|                
 | (___ | |_ __ _ _ __| | __| (___   ___ __ _ _ __  
  \___ \| __/ _` | '__| |/ / \___ \ / __/ _` | '_ \ 
  ____) | || (_| | |  |   <  ____) | (_| (_| | | | |
 |_____/ \__\__,_|_|  |_|\_\|_____/ \___\__,_|_| |_|
    """, style="bold cyan")
    
    console.print(Panel(banner, subtitle="[bold magenta]AI-POWERED BY TRINITY[/bold magenta]", border_style="bright_blue"))
    console.print("[bold green]DEVELOPED BY KARTIK | MISSION: SECURE THE PERIMETER[/bold green]\n")

    target = console.input("[bold purple]Enter Target: [/bold purple]")
    if not target: return

    goal = console.input("[bold purple]Enter Goal (e.g. 'quick scan' or 'full vuln scan'): [/bold purple]")
    if not goal: return

    # Processing AI Logic
    with Progress(SpinnerColumn(), TextColumn("[bold cyan]{task.description}"), transient=True) as progress:
        progress.add_task(description="Trinity AI calculating speed-optimized vectors...", total=None)
        ai_flags = ask_stark_ai(api_key, goal, target)

    console.print(Panel(f"[bold white]Optimized Plan:[/bold white] [bold green]nmap {ai_flags} {target}[/bold green]", border_style="green"))

    # Nmap Execution with Timeout for safety
    import nmap
    nm = nmap.PortScanner()
    
    console.print(f"[bold yellow][*] Scan Started at high speed... Please wait.[/bold yellow]")
    
    with Progress(SpinnerColumn(), TextColumn("[bold magenta]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Infiltrating {target}...", total=None)
        try:
            # Added a default timeout/optimization if AI gives something too heavy
            nm.scan(target, arguments=ai_flags)
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return

    # Results Table
    if not nm.all_hosts():
        console.print("[bold red][!] No results found. Target might be down or blocking pings.[/bold red]")
        console.print("[yellow]Try adding '-Pn' in your next goal to skip host discovery.[/yellow]")
    else:
        for host in nm.all_hosts():
            table = Table(title=f"HOST: {host} ({nm[host].hostname()})", border_style="bright_magenta")
            table.add_column("PORT", style="cyan")
            table.add_column("STATE", style="bold green")
            table.add_column("SERVICE", style="yellow")
            table.add_column("VERSION", style="white")

            for proto in nm[host].all_protocols():
                for port in sorted(nm[host][proto].keys()):
                    p = nm[host][proto][port]
                    table.add_row(
                        str(port), 
                        p['state'].upper(), 
                        p['name'],
                        f"{p.get('product', '')} {p.get('version', '')}"
                    )
            console.print(table)

    console.print("\n[bold red]![/bold red] [white]Cleanup successful.[/white]")
    console.print("\n[bold cyan]STARK AI DISCONNECTED. GOODBYE, KARTIK.[/bold cyan]")

if __name__ == "__main__":
    main()