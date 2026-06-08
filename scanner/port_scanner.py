import socket
import time
from dataclasses import dataclass
from scanner.banner_grabber import grab_banner
from scanner.service_detector import detect_service


@dataclass
class ScanResult:
    ip: str
    port: int
    status: str           # "open" | "closed" | "filtered"
    response_ms: float
    service: str = "unknown"
    banner: str = ""


def port_scanner(ip, port, timeout=1.0):
    start = time.perf_counter()
    banner = ""
    service = "unknown"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        response_ms = (time.perf_counter() - start) * 1000

        if result == 0:
            status = "open"
            banner = grab_banner(sock, port, timeout=0.5)
            service = detect_service(port, banner)
        elif response_ms >= timeout * 1000 * 0.9:
            status = "filtered"
        else:
            status = "closed"

    return ScanResult(
        ip=ip,
        port=port,
        status=status,
        response_ms=round(response_ms, 2),
        service=service,
        banner=banner,
    )


if __name__ == "__main__":
    tests = [
        ("scanme.nmap.org", 22),
        ("scanme.nmap.org", 80),
        ("scanme.nmap.org", 9999),
    ]
    for ip, port in tests:
        result = port_scanner(ip, port)
        output = f"[{result.status.upper():8}] {result.ip}:{result.port} | {result.service:20} | {result.response_ms}ms"
        if result.banner:
            output += f" | Banner: {result.banner[:50]}"
        print(output)
