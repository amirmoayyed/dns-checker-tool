import dns.resolver
import socket
import time
import re
import os
import sys
import msvcrt

from colorama import init, Fore
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

init(autoreset=True)


# -------------------------------------------------
# PATH SUPPORT (EXE SAFE)
# -------------------------------------------------
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# -------------------------------------------------
# LOAD DNS LIST
# -------------------------------------------------
def load_dns(file_name):
    path = os.path.join(get_base_path(), file_name)

    if not os.path.exists(path):
        print(Fore.RED + "dns.txt not found!")
        input("Press ENTER to exit...")
        sys.exit(1)

    with open(path, "r") as f:
        return [x.strip() for x in f if x.strip()]


# -------------------------------------------------
# VALIDATE DOMAIN
# -------------------------------------------------
def is_valid_domain(domain):
    domain = domain.lower().strip()
    pattern = r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z]{2,})+$"
    return re.match(pattern, domain) is not None


# -------------------------------------------------
# PTR
# -------------------------------------------------
def get_ptr(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"


# -------------------------------------------------
# REACHABILITY
# -------------------------------------------------
def is_reachable(ip):
    try:
        socket.create_connection((ip, 53), timeout=2)
        return True
    except:
        return False


# -------------------------------------------------
# TRUNCATE
# -------------------------------------------------
def cut(text, size):
    text = str(text)
    return text if len(text) <= size else text[:size-3] + "..."


# -------------------------------------------------
# ALL RECORDS
# -------------------------------------------------
ALL_RECORDS = ["A", "AAAA", "MX", "CNAME", "NS", "TXT", "SOA"]


# -------------------------------------------------
# DNS TEST
# -------------------------------------------------
def test_dns(ip, domain, rtype):

    reachable = is_reachable(ip)

    resolver = dns.resolver.Resolver()
    resolver.nameservers = [ip]
    resolver.timeout = 2
    resolver.lifetime = 2

    if not reachable:
        return {
            "ip": ip,
            "ptr": get_ptr(ip),
            "reachable": "NO",
            "resolved": "NO",
            "answers": "",
            "latency": ""
        }

    # ---------------- ALL MODE ----------------
    if rtype == "ALL":

        out = []

        for t in ALL_RECORDS:
            try:
                start = time.time()
                res = resolver.resolve(domain, t)
                end = time.time()

                latency = round((end - start) * 1000, 2)
                ans = ",".join([r.to_text() for r in res])

                out.append(f"{t}:{ans} ({latency}ms)")
            except:
                continue

        return {
            "ip": ip,
            "ptr": get_ptr(ip),
            "reachable": "YES",
            "resolved": "YES" if out else "NO",
            "answers": out,
            "latency": ""
        }

    # ---------------- NORMAL MODE ----------------
    try:
        start = time.time()
        res = resolver.resolve(domain, rtype)
        end = time.time()

        latency = round((end - start) * 1000, 2)

        return {
            "ip": ip,
            "ptr": get_ptr(ip),
            "reachable": "YES",
            "resolved": "YES",
            "answers": ",".join([r.to_text() for r in res]),
            "latency": latency
        }

    except:
        return {
            "ip": ip,
            "ptr": get_ptr(ip),
            "reachable": "YES",
            "resolved": "NO",
            "answers": "",
            "latency": ""
        }


# -------------------------------------------------
# PROGRESS BAR
# -------------------------------------------------
def render_progress(done, total, ip):
    percent = done / total
    bar_len = 30
    filled = int(bar_len * percent)

    bar = "█" * filled + "░" * (bar_len - filled)

    return f"[{bar}] {round(percent*100,2)}% ({done}/{total}) - {ip}"


# -------------------------------------------------
# SUMMARY
# -------------------------------------------------
def print_summary(results, domain, rtype):

    total = len(results)
    reachable = sum(1 for r in results if r["reachable"] == "YES")
    resolved = sum(1 for r in results if r["resolved"] == "YES")

    lat = [r["latency"] for r in results if isinstance(r["latency"], (int, float))]
    avg = round(sum(lat) / len(lat), 2) if lat else 0

    best = min(
        (r for r in results if isinstance(r["latency"], (int, float))),
        key=lambda x: x["latency"],
        default=None
    )

    print("\n" + "=" * 60)
    print(Fore.CYAN + "DNS SUMMARY")
    print("=" * 60)

    print(Fore.YELLOW + f"Domain      : {domain}")
    print(Fore.YELLOW + f"Type        : {rtype}")
    print(Fore.GREEN + f"Reachable   : {reachable}")
    print(Fore.RED + f"Failed      : {total - reachable}")
    print(Fore.GREEN + f"Resolved    : {resolved}")
    print(Fore.RED + f"Not Resolved: {total - resolved}")
    print(Fore.CYAN + f"Avg Latency : {avg} ms")

    if best:
        print(Fore.GREEN + f"Fastest DNS : {best['ip']} ({best['latency']} ms)")

    print("=" * 60 + "\n")


# -------------------------------------------------
# TABLE (NORMAL + ALL)
# -------------------------------------------------
def print_table(results, rtype):

    # ---------------- ALL MODE ----------------
    if rtype == "ALL":

        print("\n" + "=" * 60)
        print(Fore.CYAN + "ALL MODE RESULTS")
        print("=" * 60)

        for r in results:

            color = Fore.GREEN if r["resolved"] == "YES" else Fore.RED

            print(color + f"\nDNS: {r['ip']} | PTR: {r['ptr']}")
            print(f"Reachable: {r['reachable']} | Resolved: {r['resolved']}")

            if r["answers"]:
                print("Records:")
                for a in r["answers"]:
                    print("  - " + a)
            else:
                print("No records")

            print("-" * 60)

        return

    # ---------------- NORMAL TABLE ----------------

    print(f"{'DNS IP':<16}{'PTR':<28}{'Reach':<8}{'Res':<6}{'Answer':<28}{'Lat'}")
    print("-" * 100)

    for r in results:

        color = Fore.GREEN if r["resolved"] == "YES" else Fore.RED

        print(
            color +
            f"{cut(r['ip'],15):<16}"
            f"{cut(r['ptr'],27):<28}"
            f"{r['reachable']:<8}"
            f"{r['resolved']:<6}"
            f"{cut(r['answers'],27):<28}"
            f"{r['latency']}"
        )


# -------------------------------------------------
# EXIT SCREEN
# -------------------------------------------------
def wait_for_exit():

    print(Fore.YELLOW + "\nDeveloped by Amir Reza Moayyed")
    print("\n\n")
    print("Press ENTER to run again")
    print("Press ESC to exit")

    while True:
        k = msvcrt.getch()

        if k == b'\x1b':
            sys.exit()
        elif k == b'\r':
            return


# -------------------------------------------------
# MENU
# -------------------------------------------------
def show_menu():

    print("\n" + Fore.CYAN + "=" * 40)
    print(Fore.CYAN + "        SELECT RECORD TYPE")
    print(Fore.CYAN + "=" * 40)

    print(Fore.YELLOW + "  [1] A       [2] MX      [3] AAAA")
    print(Fore.YELLOW + "  [4] CNAME   [5] NS      [6] TXT")
    print(Fore.YELLOW + "  [7] SOA     [8] ALL")

    print(Fore.CYAN + "=" * 40)


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():

    dns_list = load_dns("dns.txt")

    record_map = {
        "1": "A", "a": "A",
        "2": "MX", "mx": "MX",
        "3": "AAAA", "aaaa": "AAAA",
        "4": "CNAME", "cname": "CNAME",
        "5": "NS", "ns": "NS",
        "6": "TXT", "txt": "TXT",
        "7": "SOA", "soa": "SOA",
        "8": "ALL", "all": "ALL"
    }

    while True:

        raw = input("Enter domain: ").strip().lower()

        if not raw:
            print(Fore.RED + "Empty input!")
            continue

        parts = raw.split()

        domain = None
        rtype = None

        # smart parsing
        for p in parts:
            p = p.strip().lower()

            if p.startswith("-"):
                rtype = record_map.get(p[1:])
            else:
                domain = p

        if not domain or not is_valid_domain(domain):
            print(Fore.RED + "Invalid domain!")
            continue

        if not rtype:

            show_menu()
            c = input("Choice: ").strip().lower()
            rtype = record_map.get(c)

            if not rtype:
                print(Fore.RED + "Invalid choice!")
                continue

        break


    # ---------------- EXECUTION ----------------

    results = []
    total = len(dns_list)
    done = 0
    lock = Lock()

    def worker(ip):
        nonlocal done

        r = test_dns(ip, domain, rtype)

        with lock:
            done += 1
            print("\r" + render_progress(done, total, ip) + " " * 10, end="", flush=True)

        return r


    with ThreadPoolExecutor(max_workers=30) as ex:
        futures = [ex.submit(worker, ip) for ip in dns_list]
        for f in futures:
            results.append(f.result())


    print("\n")

    results.sort(key=lambda x: x["latency"] if isinstance(x["latency"], (int, float)) else 999999)

    print_summary(results, domain, rtype)
    print_table(results, rtype)


# -------------------------------------------------
# LOOP
# -------------------------------------------------
if __name__ == "__main__":

    while True:
        main()
        wait_for_exit()