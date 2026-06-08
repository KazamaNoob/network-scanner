BANNER_SIGNATURES = [
    ("openssh",    "SSH"),
    ("ssh-",       "SSH"),
    ("dropbear",   "SSH"),
    ("telnet",     "Telnet"),
    ("nginx",      "HTTP (Nginx)"),
    ("apache",     "HTTP (Apache)"),
    ("gunicorn",   "HTTP (Gunicorn)"),
    ("cloudflare", "HTTP (Cloudflare)"),
    ("http/1.",    "HTTP"),
    ("http/2",     "HTTP"),
    ("mysql",      "MySQL"),
    ("mariadb",    "MariaDB"),
    ("postgresql", "PostgreSQL"),
    ("redis",      "Redis"),
    ("mongodb",    "MongoDB"),
    ("postfix",    "SMTP (Postfix)"),
    ("exim",       "SMTP (Exim)"),
    ("smtp",       "SMTP"),
    ("ftp",        "FTP"),
    ("pop3",       "POP3"),
    ("+ok",        "POP3"),
    ("imap",       "IMAP"),
    ("amqp",       "RabbitMQ/AMQP"),
    ("mqtt",       "MQTT"),
    ("docker",     "Docker Daemon"),
    ("kubernetes", "Kubernetes API"),
    ("rfb 00",     "VNC"),
    ("smb",        "SMB"),
]

PORT_FALLBACKS = {
    21:    "FTP",
    22:    "SSH",
    23:    "Telnet",
    25:    "SMTP",
    53:    "DNS",
    80:    "HTTP",
    110:   "POP3",
    143:   "IMAP",
    443:   "HTTPS",
    465:   "SMTPS",
    993:   "IMAPS",
    995:   "POP3S",
    3306:  "MySQL",
    5432:  "PostgreSQL",
    6379:  "Redis",
    8080:  "HTTP-Alt",
    8443:  "HTTPS-Alt",
    27017: "MongoDB",
}


def detect_service(port, banner):
    if banner:
        banner_lower = banner.lower()
        for signature, service in BANNER_SIGNATURES:
            if signature in banner_lower:
                return service
    return PORT_FALLBACKS.get(port, "Unknown")


if __name__ == "__main__":
    tests = [
        (22,   "SSH-2.0-OpenSSH_8.9p1 Ubuntu"),
        (80,   "HTTP/1.1 200 OK\r\nServer: nginx/1.18"),
        (3306, "mysql_native_password"),
        (9999, ""),
        (443,  ""),
    ]
    for port, banner in tests:
        print(f"Port {port:5} | Banner: {banner[:40]:40} | Service: {detect_service(port, banner)}")
