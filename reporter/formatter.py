import csv
import json
import io
from dataclasses import asdict


IP_W      = 20
PORT_W    = 6
STATUS_W  = 10
SERVICE_W = 22
BANNER_W  = 50
TIME_W    = 12

TEMPLATE = (
    f"{{ip:<{IP_W}}} | {{port:<{PORT_W}}} | {{status:<{STATUS_W}}} | "
    f"{{service:<{SERVICE_W}}} | {{banner:<{BANNER_W}}} | {{time:>{TIME_W}}}"
)

DIVIDER_LENGTH = IP_W + PORT_W + STATUS_W + SERVICE_W + BANNER_W + TIME_W + 17


def to_text(results):
    lines = []
    lines.append(TEMPLATE.format(
        ip="IP Address", port="Port", status="Status",
        service="Service", banner="Banner", time="Latency"
    ))
    lines.append("-" * DIVIDER_LENGTH)
    for r in results:
        clean_banner = r.banner.replace("\n", " ").replace("\r", "")[:BANNER_W]
        lines.append(TEMPLATE.format(
            ip=r.ip,
            port=str(r.port),
            status=r.status.upper(),
            service=r.service,
            banner=clean_banner,
            time=f"{r.response_ms:.2f}ms",
        ))
    return "\n".join(lines)


def to_csv(results):
    fieldnames = ["ip", "port", "status", "service", "banner", "response_ms"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(asdict(r))
    return output.getvalue()


def to_json(results):
    return json.dumps([asdict(r) for r in results], indent=4)


if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class ScanResult:
        ip: str
        port: int
        status: str
        response_ms: float
        service: str = "unknown"
        banner: str = ""

    dummy = [
        ScanResult("192.168.1.1", 22,   "open",     104.5,  "SSH",          "SSH-2.0-OpenSSH_8.9"),
        ScanResult("192.168.1.1", 80,   "open",     88.3,   "HTTP (Nginx)",  "HTTP/1.1 200 OK"),
        ScanResult("192.168.1.1", 9999, "filtered", 1012.0, "Unknown",       ""),
    ]

    print("--- TEXT ---")
    print(to_text(dummy))

    print("\n--- CSV ---")
    print(to_csv(dummy))

    print("\n--- JSON ---")
    print(to_json(dummy))
