from flask import Flask, jsonify
import json
import time

app = Flask(__name__)

LOG_PATH = "/var/log/access/access.log"
WINDOW_SECONDS = 60
DENY_THRESHOLD = 3

def read_log():
    entries = []
    try:
        with open(LOG_PATH, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    except FileNotFoundError:
        pass
    return entries

def detect_anomalies(entries):
    now = time.time()
    recent_denies = {}

    for entry in entries:
        if entry["decision"] in ("deny", "deny_timeout"):
            if now - entry["timestamp"] <= WINDOW_SECONDS:
                sub = entry["sub"]
                recent_denies.setdefault(sub, []).append(entry)

    alerts = []
    for sub, denies in recent_denies.items():
        if len(denies) >= DENY_THRESHOLD:
            alerts.append({
                "sub": sub,
                "count": len(denies),
                "window_seconds": WINDOW_SECONDS,
                "paths": [d["path"] for d in denies]
            })
    return alerts

@app.route("/alerts")
def alerts():
    entries = read_log()
    return jsonify(detect_anomalies(entries))

@app.route("/log")
def full_log():
    return jsonify(read_log())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)