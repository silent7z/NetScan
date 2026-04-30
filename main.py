import socket
import threading
from queue import Queue
import time
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
print_lock = threading.Lock()
target = ""
open_ports = []

def banner():
    ascii_art = """
     ██████╗██╗██╗     ███████╗███╗   ██╗████████╗███████╗
    ██╔════╝██║██║     ██╔════╝████╗  ██║╚══██╔══╝╚══███╔╝
    ╚█████╗ ██║██║     █████╗  ██╔██╗ ██║   ██║     ███╔╝ 
     ╚═══██╗██║██║     ██╔══╝  ██║╚██╗██║   ██║    ███╔╝  
    ██████╔╝██║███████╗███████╗██║ ╚████║   ██║   ███████╗
    ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
               [ NETWORK SCANNER TOOL ]
    """
    console.print(Panel(ascii_art, style="bold green", expand=False))

def scan_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        con = s.connect((target, port))
        try:
            s.send(b"Hello\r\n")
            banner_grab = s.recv(1024).decode().strip()[:30]
        except:
            banner_grab = "Service actif"
        
        with print_lock:
            open_ports.append((port, banner_grab))
        con.close()
    except:
        pass

def threader():
    while True:
        worker = q.get()
        scan_port(worker)
        q.task_done()

def main():
    global target, q
    os.system('cls' if os.name == 'nt' else 'clear')
    banner()
    
    target = console.input("[bold yellow]Cible (IP ou Domaine) : [/bold yellow]")
    try:
        t_ip = socket.gethostbyname(target)
    except:
        console.print("[bold red]Erreur : Impossible de résoudre l'hôte.[/bold red]")
        return

    port_input = console.input("[bold yellow]Ports (ex: 80 ou 1-1000) : [/bold yellow]")
    
    if "-" in port_input:
        start_port, end_port = map(int, port_input.split("-"))
    else:
        start_port = end_port = int(port_input)

    console.print(f"\n[bold cyan]Scan de {t_ip} ({start_port} -> {end_port})...[/bold cyan]")
    
    q = Queue()
    for _ in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    start_time = time.time()

    for worker in range(start_port, end_port + 1):
        q.put(worker)

    q.join()

    runtime = round(time.time() - start_time, 2)
    
    if open_ports:
        table = Table(title=f"Résultats pour {target}")
        table.add_column("Port", style="cyan")
        table.add_column("Statut", style="green")
        table.add_column("Banner/Service", style="magenta")

        for p, b in sorted(open_ports):
            table.add_row(str(p), "OUVERT", b)
        console.print("\n")
        console.print(table)
    else:
        console.print("\n[bold red]Aucun port ouvert détecté.[/bold red]")

    console.print(f"\n[bold white]Terminé en {runtime}s.[/bold white]")

if __name__ == "__main__":
    main()
