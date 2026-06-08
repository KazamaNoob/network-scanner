import time
import threading


class RateLimiter:
    def __init__(self, connections_per_second, max_concurrent_connections):
        self.connections_per_second = connections_per_second
        self.max_concurrent_connections = max_concurrent_connections
        self.delay_interval = 1.0 / connections_per_second
        self.next_allowed_time = time.perf_counter()
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(max_concurrent_connections)

    def __enter__(self):
        self.semaphore.acquire()
        with self.lock:
            now = time.perf_counter()
            if now < self.next_allowed_time:
                time.sleep(self.next_allowed_time - now)
            self.next_allowed_time = max(now, self.next_allowed_time) + self.delay_interval
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()
        return False   # don't suppress exceptions


if __name__ == "__main__":
    import concurrent.futures

    limiter = RateLimiter(connections_per_second=5, max_concurrent_connections=3)

    def simulated_scan(port):
        with limiter:
            print(f"Scanning port {port} at {time.perf_counter():.2f}")
            time.sleep(0.1)
            return port

    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(simulated_scan, range(10)))
    print(f"\nAll done in {time.perf_counter() - start:.2f}s — ports: {results}")
