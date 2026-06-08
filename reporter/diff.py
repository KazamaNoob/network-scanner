import json
from difflib import SequenceMatcher


def diff_scans(prev_path, curr_path, threshold=0.8):
    with open(prev_path, "r") as f_prev, open(curr_path, "r") as f_curr:
        prev_data = json.load(f_prev)
        curr_data = json.load(f_curr)

    prev_map = {
        (item["ip"], item["port"]): item
        for item in prev_data
        if "ip" in item and "port" in item
    }
    curr_map = {
        (item["ip"], item["port"]): item
        for item in curr_data
        if "ip" in item and "port" in item
    }

    results = {"opened": [], "closed": [], "modified": []}

    for key, entry in curr_map.items():
        if entry.get("status") == "open":
            if key not in prev_map or prev_map[key].get("status") != "open":
                results["opened"].append(entry)

    for key, entry in prev_map.items():
        if entry.get("status") == "open":
            if key not in curr_map or curr_map[key].get("status") != "open":
                results["closed"].append(entry)

    for key in curr_map.keys() & prev_map.keys():
        if (
            curr_map[key].get("status") == "open"
            and prev_map[key].get("status") == "open"
        ):
            old_banner = str(prev_map[key].get("banner", ""))
            new_banner = str(curr_map[key].get("banner", ""))

            similarity = SequenceMatcher(None, old_banner, new_banner).ratio()

            if similarity < threshold:
                results["modified"].append({
                    "ip": key[0],
                    "port": key[1],
                    "prev_banner": old_banner,
                    "curr_banner": new_banner,
                })

    return results


def format_diff(results):
    lines = []

    if results.get("opened"):
        lines.append("=== NEWLY OPENED PORTS ===")
        for item in results["opened"]:
            service = item.get("service", "Unknown")
            lines.append(
                f"[+] OPENED:  {item['ip']:<15} | Port: {item['port']:<5} | Service: {service}"
            )
            if item.get("banner"):
                clean = str(item["banner"]).replace("\n", " ").replace("\r", "")
                lines.append(f"    └── Banner: {clean[:70]}")
        lines.append("")

    if results.get("closed"):
        lines.append("=== NEWLY CLOSED OR FILTERED PORTS ===")
        for item in results["closed"]:
            service = item.get("service", "Unknown")
            lines.append(
                f"[-] CLOSED:  {item['ip']:<15} | Port: {item['port']:<5} | Last Known Service: {service}"
            )
        lines.append("")

    if results.get("modified"):
        lines.append("=== MODIFIED SERVICE SIGNATURES ===")
        for item in results["modified"]:
            lines.append(
                f"[*] CHANGED: {item['ip']:<15} | Port: {item['port']:<5}"
            )
            old_b = (
                str(item["prev_banner"])
                .replace("\n", " ")
                .replace("\r", "")
                .strip()
                or "[None]"
            )
            new_b = (
                str(item["curr_banner"])
                .replace("\n", " ")
                .replace("\r", "")
                .strip()
                or "[None]"
            )
            lines.append(f"    ├── Old: {old_b[:70]}")
            lines.append(f"    └── New: {new_b[:70]}")
        lines.append("")

    if not any(results.values()):
        lines.append(
            "[=] No network profile changes detected between these scan sets."
        )

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python diff.py <prev_scan.json> <curr_scan.json>")
        sys.exit(1)

    try:
        diff_data = diff_scans(sys.argv[1], sys.argv[2])
        print(format_diff(diff_data))
    except FileNotFoundError as e:
        print(f"Error: Could not find file — {e.filename}")
    except Exception as e:
        print(f"Unexpected error: {e}")

