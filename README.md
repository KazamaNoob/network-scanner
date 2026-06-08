# 🔍 Network Port Scanner & Service Detector

A modular, multi-threaded network port scanner built from scratch in Python. Scans single IPs, ranges, and CIDR blocks for open TCP ports, identifies running services via banner grabbing and signature matching, and detects network profile changes between scans using fuzzy diff analysis.

Built as a hands-on cybersecurity learning project — no third-party scanning libraries used.

---

## Features

- Scan single IPs, ranges (`192.168.1.1-254`), CIDR blocks (`192.168.1.0/24`), or hostnames
- Detect open, closed, and filtered TCP ports
- Banner grabbing with protocol-aware probes (HTTP, FTP, SMTP, Redis, and more)
- TLS/SSL support for HTTPS, IMAPS, POP3S, and SMTPS
- Service fingerprinting via banner signatures and port fallbacks
- Multi-threaded scanning with configurable thread pool
- Rate limiting via semaphore + velocity control to avoid network flooding
- Output reports in text, CSV, or JSON format
- Automatic scan diffing — detects newly opened, closed, or modified services between runs using fuzzy matching

---

## Architecture

```
network-scanner/
├── main.py                  # CLI entry point, threading engine, report orchestration
├── scanner/
│   ├── target_parser.py     # Resolves IP ranges, CIDR, and hostnames → list of IPs
│   ├── port_scanner.py      # TCP connect scan, response time, ScanResult dataclass
│   ├── banner_grabber.py    # Protocol-aware banner grabbing with TLS support
│   ├── service_detector.py  # Maps port + banner → service name
│   └── rate_limiter.py      # Semaphore + velocity rate limiter (context manager)
├── reporter/
│   ├── formatter.py         # Formats results as text table, CSV, or JSON
│   └── diff.py              # Fuzzy diff engine comparing two scan JSON files
├── reports/                 # Auto-saved JSON scan history (gitignored)
└── config.py                # Reserved for shared configuration
```

---

## Installation

```bash
git clone https://github.com/KazamaNoob/network-scanner.git
cd network-scanner
```

No external dependencies — uses Python standard library only. Requires Python 3.8+.

---

## Usage

```bash
python3 main.py <target> [options]
```

### Examples

```bash
# Scan common ports on a single host
python3 main.py scanme.nmap.org

# Scan specific ports
python3 main.py 192.168.1.1 -p 22,80,443,3306

# Scan a port range
python3 main.py 192.168.1.1 -p 1-1000

# Scan a full subnet
python3 main.py 192.168.1.0/24 -p 22,80

# Scan an IP range and save JSON report
python3 main.py 192.168.1.1-10 -p common -f json -o scan_results

# Tune for high-latency remote targets
python3 main.py scanme.nmap.org -p common -t 2.0 --pps 5 --max-cap 3
```

---

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `target` | required | IP, hostname, range, or CIDR |
| `-p`, `--ports` | `common` | Ports to scan: `22,80`, `1-1000`, or `common` |
| `-f`, `--format` | `text` | Output format: `text`, `csv`, or `json` |
| `-o`, `--output` | none | File path to save report |
| `-w`, `--workers` | `50` | Max parallel threads |
| `-t`, `--timeout` | `1.0` | Socket timeout in seconds |
| `--pps` | `20` | Max connections per second |
| `--max-cap` | `10` | Max concurrent active sockets |

---

## Sample Output

```
Scanning 1 host(s) across 34 port(s)...

[OPEN    ] 45.33.32.156:22 | SSH                  | 271.23ms | SSH-2.0-OpenSSH_6.6.1p1 Ubuntu
[OPEN    ] 45.33.32.156:80 | HTTP (Apache)        | 278.85ms | HTTP/1.1 200 OK
[FILTERED] 45.33.32.156:443 | unknown             | 1001.96ms

Scan completed in 4.14s — 34 results.
```

### Scan Diff Output

```
=== NEWLY OPENED PORTS ===
[+] OPENED:  192.168.1.1     | Port: 8080  | Service: HTTP-Alt
    └── Banner: HTTP/1.1 200 OK Server: nginx/1.18

=== NEWLY CLOSED OR FILTERED PORTS ===
[-] CLOSED:  192.168.1.1     | Port: 3306  | Last Known Service: MySQL

=== MODIFIED SERVICE SIGNATURES ===
[*] CHANGED: 192.168.1.1     | Port: 22
    ├── Old: SSH-2.0-OpenSSH_7.4
    └── New: SSH-2.0-OpenSSH_8.9
```

---

## Technical Notes

- **TCP Connect scan** — completes full 3-way handshake. No raw sockets required, works without root privileges.
- **Port states** — `open` (SYN-ACK received), `closed` (RST received), `filtered` (timeout — likely firewall).
- **Rate limiting** — combines a semaphore (concurrency cap) with velocity control (connections/sec) to avoid triggering IDS/IPS systems.
- **Fuzzy diff** — uses `difflib.SequenceMatcher` with a 0.8 similarity threshold to ignore volatile banner fields like HTTP `Date:` headers while still catching real version changes.
- **Thread safety** — results collected via `concurrent.futures.as_completed`, print output protected by `threading.Lock`.

---

## Disclaimer

This tool is intended for use on networks and systems you own or have explicit permission to scan. Unauthorized port scanning may be illegal in your jurisdiction.

---

## Author

**KazamaNoob** — built as part of an active cybersecurity learning journey.
