import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, socket, ssl, json, threading
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""
SUBTITLE = "D E E P - T R A C E   G E O I N T E L L I G E N C E   A N D   N E T W O R K   O R A C L E"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // IP ORACLE")
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    lines = ASCII.strip("\n").split("\n")
    t0 = time.time()
    try:
        while time.time() - t0 < 1.4:
            t = time.time() - t0
            sys.stdout.write("\033[H\n")
            for line in lines:
                sys.stdout.write(" ")
                for c, ch in enumerate(line):
                    if ch == " ":
                        sys.stdout.write(" ")
                    else:
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.12))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def current_time_hour():
    return time.strftime("%H:%M:%S")

def _req(url):
    try:
        r = requests.get(url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
        return r.json()
    except: return {}

def ssl_probe(host):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, 443), timeout=4) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert(binary_form=False)
                if not cert: return {"ver": tls.version()}
                return {
                    "subject": dict(x[0] for x in cert.get("subject", [])).get("commonName", "—"),
                    "issuer": dict(x[0] for x in cert.get("issuer", [])).get("organizationName", "—"),
                    "expires": cert.get("notAfter", "—"),
                    "ver": tls.version()
                }
    except: return {}

def port_sample(ip):
    ports = {21:"FTP", 22:"SSH", 80:"HTTP", 443:"HTTPS", 3306:"MySQL", 3389:"RDP", 8080:"HTTP-Alt"}
    found = []
    def probe(p):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.8)
                if s.connect_ex((ip, p)) == 0:
                    found.append((p, ports[p]))
        except: pass
    threads = [threading.Thread(target=probe, args=(p,)) for p in ports]
    for t in threads: t.start()
    for t in threads: t.join()
    return sorted(found)

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP ORACLE[/]  [dim]//[/]  [red]DEEP TRACE[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Target IP / Hostname [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not target: sys.exit(0)

        # Resolve
        if not target.replace(".","").isdigit():
            try:
                resolved = socket.gethostbyname(target)
                console.print(f" [dim]Resolved [red]{target}[/] > [white]{resolved}[/]")
                ip = resolved
            except:
                console.print(" [bold red][!] DNS Resolution failed.")
                ip = target
        else: ip = target

        console.print(f"\n [dim]Initiating multi-source Intelligence on [red]{ip}[/]...\n")

        results = {}
        def fetch_geo():
            results["api"] = _req(f"http://ip-api.com/json/{ip}?fields=66846719")
        def fetch_ssl():
            results["ssl"] = ssl_probe(ip)
        def fetch_ports():
            results["ports"] = port_sample(ip)
        
        threads = [threading.Thread(target=fetch_geo), threading.Thread(target=fetch_ssl), threading.Thread(target=fetch_ports)]
        for t in threads: t.start()
        for t in threads: t.join()

        geo = results.get("api", {})
        ssl_d = results.get("ssl", {})
        ports = results.get("ports", [])

        # Geo Table
        gtbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False)
        gtbl.add_column("K", style="dim red"); gtbl.add_column("V", style="white")
        gtbl.add_row("COUNTRY", geo.get("country", "—"))
        gtbl.add_row("CITY", geo.get("city", "—"))
        gtbl.add_row("REGION", geo.get("regionName", "—"))
        gtbl.add_row("ISP", geo.get("isp", "—"))
        gtbl.add_row("ASN", geo.get("as", "—"))
        gtbl.add_row("PROXY/VPN", "[bold red]DETECTED[/]" if geo.get("proxy") else "No")
        gtbl.add_row("DATACENTER", "Yes" if geo.get("hosting") else "No")
        
        console.print(Align.center(Panel(gtbl, title="[bold red] GEOLOCATION [/]", border_style="red")))

        if ssl_d:
            stbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False)
            stbl.add_row("COMMON NAME", ssl_d.get("subject", "—"))
            stbl.add_row("ISSUER", ssl_d.get("issuer", "—"))
            stbl.add_row("EXPIRES", ssl_d.get("expires", "—"))
            stbl.add_row("TLS VERSION", ssl_d.get("ver", "—"))
            console.print(Align.center(Panel(stbl, title="[bold red] SSL CERTIFICATE [/]", border_style="red")))

        if ports:
            ptbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=True, header_style="bold red")
            ptbl.add_column("PORT", style="cyan"); ptbl.add_column("SERVICE")
            for p, s in ports: ptbl.add_row(str(p), s)
            console.print(Align.center(Panel(ptbl, title="[bold red] OPEN SERVICES [/]", border_style="red")))

        console.print()
        console.input(" [dim]Press [bold red]ENTER[/] to exit...[/]")

    except (KeyboardInterrupt, EOFError):
        pass
