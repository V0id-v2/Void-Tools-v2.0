import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, socket, ssl, json, threading, re, concurrent.futures
import requests, urllib3
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.columns import Columns
from rich import box

console = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASCII = r"""
   ██╗   ██╗ ██████╗ ██╗██████╗      ██╗    ██╗███████╗██████╗ 
   ██║   ██║██╔═══██╗██║██╔══██╗     ██║    ██║██╔════╝██╔══██╗
   ██║   ██║██║   ██║██║██║  ██║█████╗██║ █╗ ██║█████╗  ██████╔╝
   ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║███╗██║██╔══╝  ██╔══██╗
    ╚████╔╝ ╚██████╔╝██║██████╔╝      ╚███╔███╔╝███████╗██████╔╝
     ╚═══╝   ╚═════╝ ╚═╝╚═════╝        ╚══╝╚══╝ ╚══════╝╚═════╝ 
"""
SUBTITLE = " S U I T E   D ' I N T E L L I G E N C E   W E B   A V A N C É E "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID")
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
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.08))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": UA}
results = {}
lock = threading.Lock()

def store(k, v):
    with lock: results[k] = v

def network_recon(domain):
    try:
        ip = socket.gethostbyname(domain)
        try: rdns = socket.gethostbyaddr(ip)[0]
        except: rdns = "—"
        geo = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=5).json()
        return {"ip": ip, "rdns": rdns, "geo": geo, "version": "IPv6" if ":" in ip else "IPv4"}
    except: return {}

def http_recon(url):
    try:
        r = requests.get(url, timeout=10, headers=HEADERS, verify=False, allow_redirects=True)
        soup = BeautifulSoup(r.text, "html.parser")
        meta = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        gen = soup.find("meta", attrs={"name": re.compile(r"generator", re.I)})
        return {
            "status": r.status_code, "final_url": r.url, "redirects": len(r.history),
            "server": r.headers.get("server", "—"), "powered": r.headers.get("x-powered-by", "—"),
            "content_type": r.headers.get("content-type", "—"), "content_len": r.headers.get("content-length", "—"),
            "encoding": r.encoding or "—", "title": soup.find("title").text if soup.find("title") else "—",
            "meta_desc": meta["content"][:100] if meta and meta.get("content") else "—",
            "generator": gen["content"][:60] if gen and gen.get("content") else "—",
            "headers": dict(r.headers), "cookies": r.cookies, "text": r.text
        }
    except: return {}

def ssl_inspect(domain):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((domain, 443), timeout=5) as raw:
            with ctx.wrap_socket(raw, server_hostname=domain) as tls:
                cert = tls.getpeercert(binary_form=False)
                if not cert: return {"ver": tls.version()}
                return {
                    "cn": dict(x[0] for x in cert.get("subject", [])).get("commonName", "—"),
                    "issuer": dict(x[0] for x in cert.get("issuer", [])).get("organizationName", "—"),
                    "expires": cert.get("notAfter", "—"), "ver": tls.version(),
                    "cipher": tls.cipher()[0], "sans": [s[1] for s in cert.get("subjectAltName", [])]
                }
    except: return {}

TECH_SIGS = {
    "WordPress": r"wp-content|wp-includes", "Joomla": r"joomla", "Drupal": r"drupal",
    "React": r"react", "Vue": r"vue", "Angular": r"angular", "jQuery": r"jquery",
    "Bootstrap": r"bootstrap", "Tailwind": r"tailwindcss", "Cloudflare": r"cloudflare",
    "Nginx": r"nginx", "Apache": r"apache", "PHP": r"php", "ASP.NET": r"asp.net"
}

def detect_tech(text, headers, cookies):
    found = set()
    full = (text + str(headers) + str(cookies)).lower()
    for tech, sig in TECH_SIGS.items():
        if re.search(sig, full): found.add(tech)
    return sorted(list(found))

SEC_HEADERS = [
    ("Content-Security-Policy", "Mitige les risques XSS/injection"),
    ("Strict-Transport-Security", "Force HTTPS (HSTS)"),
    ("X-Content-Type-Options", "Empêche le MIME sniffing"),
    ("X-Frame-Options", "Empêche le clickjacking"),
    ("X-XSS-Protection", "Filtre XSS (Hérité)"),
    ("Referrer-Policy", "Contrôle les fuites de referrer"),
    ("Permissions-Policy", "Contrôle les fonctionnalités browser"),
    ("Cross-Origin-Resource-Policy", "Isolation CORP"),
    ("Cross-Origin-Opener-Policy", "Isolation COOP"),
]

def scan_ports(ip):
    ports = {21:"FTP", 22:"SSH", 53:"DNS", 80:"HTTP", 443:"HTTPS", 3306:"MySQL", 3389:"RDP", 8080:"HTTP-Alt", 8443:"HTTPS-Alt"}
    found = []
    def probe(p):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.8)
                if s.connect_ex((ip, p)) == 0: found.append((p, ports[p]))
        except: pass
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool: pool.map(probe, ports.keys())
    return sorted(found)

def make_table(title, rows):
    t = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, expand=True)
    t.add_column("K", style="dim red", width=25); t.add_column("V", style="white")
    for k, v in rows: t.add_row(str(k), str(v) if v else "—")
    return t

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]WEB INSPECTOR[/]  [dim]//[/]  [red]RECON[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(f" [dim]User-Agent > {UA}[/]\n")
        console.print(" [bold red]┌─[[/][bold white] URL ou Domaine Cible [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not target: sys.exit(0)
        if not target.startswith("http"): target = "https://" + target
        domain = target.replace("https://","").replace("http://","").split("/")[0]

        console.print(f" [dim][{time.strftime('%H:%M:%S')}] Lancement des modules VOID sur [red]{target}[/]...\n")

        t1 = threading.Thread(target=lambda: store("net", network_recon(domain)))
        t2 = threading.Thread(target=lambda: store("http", http_recon(target)))
        t3 = threading.Thread(target=lambda: store("ssl", ssl_inspect(domain)))
        for t in (t1, t2, t3): t.start()
        for t in (t1, t2, t3): t.join()

        net = results.get("net", {})
        http = results.get("http", {})
        ssl_d = results.get("ssl", {})
        geo = net.get("geo", {})
        ip_addr = net.get("ip", "—")
        if ip_addr != "—": store("ports", scan_ports(ip_addr))

        # 1. Réseau
        net_rows = [
            ("URL", target), ("Domaine", domain), ("Adresse IP", ip_addr),
            ("Version IP", net.get("version", "—")), ("Nom d'hôte", net.get("rdns", "—")),
            ("Pays", geo.get("country", "—")), ("Région", geo.get("regionName", "—")),
            ("Ville", geo.get("city", "—")), ("FAI", geo.get("isp", "—")),
            ("ASN", geo.get("as", "—")), ("Proxy/VPN", "[bold red]OUI[/]" if geo.get("proxy") else "Non"),
            ("Hébergement", "Oui" if geo.get("hosting") else "Non")
        ]
        console.print(Align.center(make_table("[bold red]* Réseau & Géolocalisation[/]", net_rows)))

        # 2. HTTP
        if http:
            http_rows = [
                ("Statut HTTP", http.get("status", "—")), ("URL Finale", http.get("final_url", "—")),
                ("Redirections", http.get("redirects", "—")), ("Serveur", http.get("server", "—")),
                ("Powered By", http.get("powered", "—")), ("Type de contenu", http.get("content_type", "—")),
                ("Longueur contenu", http.get("content_len", "—")), ("Encodage", http.get("encoding", "—")),
                ("Titre de page", http.get("title", "—")), ("Meta Description", http.get("meta_desc", "—")),
                ("Générateur", http.get("generator", "—")), ("Sécurisé (HTTPS)", "Oui" if target.startswith("https") else "Non")
            ]
            console.print(Align.center(make_table("[bold red]* Intelligence HTTP[/]", http_rows)))

            # 3. Technologies
            techs = detect_tech(http.get("text", ""), http.get("headers", {}), http.get("cookies", []))
            if techs:
                ttbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, expand=True)
                ttbl.add_column("ID", style="dim red", width=5); ttbl.add_column("TECH", style="white")
                for i, tech in enumerate(techs): ttbl.add_row(f"[{i+1}]", tech)
                console.print(Align.center(Panel(ttbl, title="[bold red]* Technologies Détectées[/]", border_style="red")))

            # 4. En-têtes de sécurité
            htbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", expand=True)
            htbl.add_column("Header", style="white"); htbl.add_column("Statut", justify="center"); htbl.add_column("Objectif", style="dim")
            h_lower = {k.lower(): v for k, v in http.get("headers", {}).items()}
            for name, tip in SEC_HEADERS:
                status = "[bold green]+ Présent[/]" if name.lower() in h_lower else "[bold red]x Manquant[/]"
                htbl.add_row(name, status, tip)
            console.print(Align.center(Panel(htbl, title="[bold red]* Audit des En-têtes de Sécurité[/]", border_style="red")))

        # 5. SSL
        if ssl_d:
            ssl_rows = [
                ("Nom Commun", ssl_d.get("cn", "—")), ("Émetteur", ssl_d.get("issuer", "—")),
                ("Expire le", ssl_d.get("expires", "—")), ("Version TLS", ssl_d.get("ver", "—")),
                ("Algorithme", ssl_d.get("cipher", "—")), ("SANs", ", ".join(ssl_d.get("sans", [])[:5]) or "—")
            ]
            console.print(Align.center(make_table("[bold red]* Certificat TLS[/]", ssl_rows)))

        # 6. Ports
        ports = results.get("ports", [])
        if ports:
            ptbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", expand=True)
            ptbl.add_column("Port", style="red", justify="right"); ptbl.add_column("Service", style="white")
            for p, s in ports: ptbl.add_row(str(p), s)
            console.print(Align.center(Panel(ptbl, title="[bold red]* Services Ouverts[/]", border_style="red")))

        console.print()
        console.input(" [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")
    except (KeyboardInterrupt, EOFError): pass
