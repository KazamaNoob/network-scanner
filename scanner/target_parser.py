import ipaddress
import socket


def parse_targets(ip_input):
    if not isinstance(ip_input, str):
        raise TypeError(f"Expected a string, but received {type(ip_input).__name__}")

    ip_input = ip_input.strip()

    if "/" in ip_input:
        network = ipaddress.IPv4Network(ip_input, strict=False)
        return [str(ip) for ip in network.hosts()]

    elif "-" in ip_input:
        parts = ip_input.split("-")
        base = parts[0].rsplit(".", 1)[0]
        start_ip = ipaddress.IPv4Address(parts[0])
        end_ip = ipaddress.IPv4Address(f"{base}.{parts[1]}")
        if int(end_ip) < int(start_ip):
            raise ValueError(f"End IP {end_ip} is less than start IP {start_ip}")
        return [str(ipaddress.IPv4Address(x)) for x in range(int(start_ip), int(end_ip) + 1)]

    else:
        try:
            resolved = socket.gethostbyname(ip_input)
            return [str(ipaddress.IPv4Address(resolved))]
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {ip_input}")


if __name__ == "__main__":
    tests = [
        ("192.168.1.5",        "single IP"),
        ("192.168.1.1-5",      "range"),
        ("192.168.1.0/30",     "CIDR"),
        ("10.0.0.1-3",         "range across base"),
        ("192.168.1.5-1",      "reversed range — should raise"),
        ("192.168.1.999",      "invalid IP — should raise"),
        (12345,                "wrong type — should raise"),
    ]

    for inp, label in tests:
        try:
            result = parse_targets(inp)
            print(f"[OK] {label}: {inp} -> {result}")
        except (TypeError, ValueError, ipaddress.AddressValueError) as e:
            print(f"[ERR] {label}: {inp} -> {type(e).__name__}: {e}")
