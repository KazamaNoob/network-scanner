import os
import time
import threading
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from scanner.rate_limiter import RateLimiter
from scanner.port_scanner import port_scanner
from scanner.target_parser import parse_targets
from reporter import formatter, diff


COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    465, 587, 993, 995, 1433, 1521, 2181, 3000, 3306, 3389, 4444,
    5000, 5432, 5900, 6379, 8080, 8443, 8888, 9200, 9300, 27017
]

print_lock = threading.Lock()


def parse_arguments():
    parser = argparse.ArgumentParser(description="High-Speed Modular Network Scanner Suite")
    parser.add_argument("target", help="Target host, IP address, range, or CIDR notation")
    parser.add_argument("-p", "--ports", default="common",
                        help="Comma-separated ports (22,80), range (1-100), or 'common'")
    parser.add_argument("-f", "--format", choices=["text", "csv", "json"], default="text",
                        help="Output display or report format")
    parser.add_argument("-o", "--output", help="Optional file path to save the generated report")
    parser.add_argument("-w", "--workers", type=int, default=50,
                        help="Maximum number of parallel thread pool workers")
    parser.add_argument("-t", "--timeout", type=float, default=1.0,
                        help="Network socket connection timeout in seconds")
    parser.add_argument("--pps", type=int, default=20,
                        help="Connections per second velocity limit")
    parser.add_argument("--max-cap", type=int, default=10,
                        help="Maximum concurrent active sockets")
    return parser.parse_args()


def parse_ports(port_string):
    if port_string == "common":
        return COMMON_PORTS
    if "," in port_string:
        return [int(p.strip()) for p in port_string.split(",")]
    if "-" in port_string:
        start, end = port_string.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(port_string)]


def find_latest_scan(clean_host):
    if not os.path.exists("reports"):
        return None
    files = [
        f for f in os.listdir("reports")
        if f.startswith(f"scan_{clean_host}_") and f.endswith(".json")
    ]
    if not files:
        return None
    files.sort()
    return os.path.join("reports", files[-1])


def scan_with_limiter(ip, port, timeout, limiter):
    with limiter:
        return port_scanner(ip, port, timeout)


def run_parallel_scan(targets, ports, workers, timeout, pps, max_cap):
    results = []
    limiter = RateLimiter(pps, max_cap)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(scan_with_limiter, ip, port, timeout, limiter): (ip, port)
            for ip in targets
            for port in ports
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                if result.status in ("open", "filtered"):
                    line = (f"[{result.status.upper():8}] {result.ip}:{result.port}"
                            f" | {result.service:<20} | {result.response_ms}ms")
                    if result.banner:
                        line += f" | {result.banner[:50]}"
                    with print_lock:
                        print(line)
            except Exception as e:
                ip, port = futures[future]
                with print_lock:
                    print(f"[ERROR] {ip}:{port} — {e}")

    return sorted(results, key=lambda x: (x.ip, x.port))


def save_report(results, fmt, path):
    if fmt == "json":
        content = formatter.to_json(results)
    elif fmt == "csv":
        content = formatter.to_csv(results)
    else:
        content = formatter.to_text(results)
    with open(path, "w") as f:
        f.write(content)


def main():
    args = parse_arguments()

    try:
        targets = parse_targets(args.target)
        ports = parse_ports(args.ports)
    except Exception as e:
        print(f"Input error: {e}")
        return

    clean_host = args.target.replace("/", "_").replace("*", "_")
    prev_scan_path = find_latest_scan(clean_host)

    print(f"Scanning {len(targets)} host(s) across {len(ports)} port(s)...\n")
    start_time = time.perf_counter()
    results = run_parallel_scan(targets, ports, args.workers, args.timeout, args.pps, args.max_cap)
    total_duration = time.perf_counter() - start_time

    print(f"\nScan completed in {total_duration:.2f}s — {len(results)} results.\n")
    print(formatter.to_text(results))

    os.makedirs("reports", exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    current_json_path = os.path.join("reports", f"scan_{clean_host}_{timestamp}.json")
    save_report(results, "json", current_json_path)
    print(f"\nReport saved: {current_json_path}")

    if args.output:
        ext = {"json": "json", "csv": "csv", "text": "txt"}.get(args.format, "txt")
        out_path = args.output if "." in args.output else f"{args.output}.{ext}"
        save_report(results, args.format, out_path)
        print(f"Custom report saved: {out_path}")

    if prev_scan_path:
        print(f"\nComparing with previous scan: {prev_scan_path}\n")
        try:
            diff_data = diff.diff_scans(prev_scan_path, current_json_path)
            print(diff.format_diff(diff_data))
        except Exception as e:
            print(f"Diff failed: {e}")


if __name__ == "__main__":
    main()
