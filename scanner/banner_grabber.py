import ssl
import socket

CLIENT_FIRST_PROBES = {
    80:    b"HEAD / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n",
    443:   b"HEAD / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n",
    6379:  b"PING\r\n",
    11211: b"stats\r\n",
}

BANNER_FIRST_FALLBACKS = {
    21:  b"USER anonymous\r\n",
    25:  b"EHLO localhost\r\n",
    110: b"USER anonymous\r\n",
    143: b"A001 CAPABILITY\r\n",
}

TLS_PORTS = {443, 8443, 465, 993, 995}


def grab_banner(sock, port, timeout=1.0):
    target_socket = sock

    if port in TLS_PORTS:
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            target_socket = context.wrap_socket(sock, server_hostname=None)
        except Exception:
            return ""

    if port in CLIENT_FIRST_PROBES:
        try:
            target_socket.sendall(CLIENT_FIRST_PROBES[port])
            data = target_socket.recv(1024)
            return data.decode("utf-8", errors="ignore").strip()
        except Exception:
            return ""

    target_socket.settimeout(timeout)
    try:
        data = target_socket.recv(1024)
        decoded = data.decode("utf-8", errors="ignore").strip()
        if decoded:
            return decoded
    except socket.timeout:
        probe = BANNER_FIRST_FALLBACKS.get(port, b"\r\n\r\n")
        try:
            target_socket.sendall(probe)
            data = target_socket.recv(1024)
            return data.decode("utf-8", errors="ignore").strip()
        except Exception:
            return ""
    except Exception:
        return ""

    return ""
