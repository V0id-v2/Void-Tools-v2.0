import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, socket, ssl, threading
import requests, urllib3
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""
SUBTITLE = "M U L T I - F A C E T E D   S E R V E R   E X P O S U R E"

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
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.1))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def fetch_json(url):
    try:
        r = requests.get(url, timeout=7, headers={"User-Agent": "void-tools/2.0"})
        return r.json()
    except: return {}

def ssl_audit(host):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, 443), timeout=3) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert(binary_form=False)
                if not cert: return {"version": tls.version()}
                return {
                    "cn": dict(x[0] for x in cert.get("subject", [])).get("commonName", "—"),
                    "issuer": dict(x[0] for x in cert.get("issuer", [])).get("organizationName", "—"),
                    "expires": cert.get("notAfter", "—"),
                    "version": tls.version()
                }
    except: return {}

def port_check(ip):
    ports = {21:"FTP", 22:"SSH", 53:"DNS", 80:"HTTP", 443:"HTTPS", 3306:"MySQL", 3389:"RDP"}
    opened = []
    def probe(p):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.7); 
                if s.connect_ex((ip, p)) == 0: opened.append((p, ports[p]))
        except: pass
    ts = [threading.Thread(target=probe, args=(p,)) for p in ports]
    for t in ts: t.start()
    for t in ts: t.join()
    return sorted(opened)

def make_table(title, rows):
    t = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, padding=(0, 2))
    t.add_column("K", style="dim red", width=18); t.add_column("V", style="white")
    for k, v in rows: t.add_row(str(k), str(v) if v else "—")
    return t

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP ORACLE[/]  [dim]//[/]  [red]GEOINT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] IP or Hostname [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not target: sys.exit(0)

        ip = target
        if not target[0].isdigit() and ":" not in target:
            try: ip = socket.gethostbyname(target)
            except: pass

        console.print(f"\n [dim]Launching multi-source trace on [red]{ip}[/]...\n")
        
        results = {}
        def run_api(): results["geo"] = fetch_json(f"http://ip-api.com/json/{ip}?fields=66846719")
        def run_ssl(): results["ssl"] = ssl_audit(ip)
        def run_ports(): results["ports"] = port_check(ip)

        t1 = threading.Thread(target=run_api); t1.start()
        t2 = threading.Thread(target=run_ssl); t2.start()
        t3 = threading.Thread(target=run_ports); t3.start()
        t1.join(); t2.join(); t3.join()

        geo = results.get("geo", {})
        console.print(make_table("  Geolocation & Network", [
            ("IP", ip), ("Country", geo.get("country")), ("Region", geo.get("regionName")),
            ("City", geo.get("city")), ("LAT/LON", f"{geo.get('lat')}/{geo.get('lon')}"),
            ("ISP", geo.get("isp")), ("ASN", geo.get("as")),
            ("Proxy/VPN", "[red]YES[/]" if geo.get("proxy") else "No"),
            ("Hosting", "Yes" if geo.get("hosting") else "No"),
        ]))

        ssl_i = results.get("ssl", {})
        if ssl_i:
            console.print(make_table("  TLS Security", [
                ("Common Name", ssl_i.get("cn")), ("Issuer", ssl_i.get("issuer")),
                ("Expires", ssl_i.get("expires")), ("Version", ssl_i.get("version")),
            ]))
        
        ports = results.get("ports", [])
        if ports:
            ptbl = Table(title="  Open Services", box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=True)
            ptbl.add_column("Port", style="red"); ptbl.add_column("Service", style="white")
            for p, s in ports: ptbl.add_row(str(p), s)
            console.print(ptbl)

        console.input("\n [dim]Press [bold red]ENTER[/] to exit...[/]")

    except (KeyboardInterrupt, EOFError):
        pass
