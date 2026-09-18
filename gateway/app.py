import json
import time

from flask import Flask, jsonify, request
import requests
import jwt
import os

app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
allowed_routes = ["/health", "/records", "/delete-records"]
LOG_PATH = "/var/log/access/access.log"


def verify_token():
    """Returns (payload, None) on success, or (None, (response, status)) on failure."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Missing token"}), 401)

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Invalid token"}), 401)

    return payload, None


def log_decision(sub, path, decision):
    entry = {
        "timestamp": time.time(),
        "sub": sub,
        "path": path,
        "decision": decision
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")



def check_policy(payload, path):
    opa_input = {"input": {"scope": payload.get("scope", ""), "path": path}}
    resp = requests.post("http://opa:8181/v1/data/authz/decision", json=opa_input)
    return resp.json().get("result", "deny")


def wait_for_approval(path, payload, timeout=90, poll_interval=2):
    create_resp = requests.post("http://approval-service:8000/approvals",
        json={"path": path, "sub": payload.get("sub")})
    approval_id = create_resp.json()["approval_id"]

    elapsed = 0
    while elapsed < timeout:
        status_resp = requests.get(f"http://approval-service:8000/approvals/{approval_id}")
        status = status_resp.json()["status"]
        if status != "pending":
            return status == "approved"
        time.sleep(poll_interval)
        elapsed += poll_interval

    return False  


@app.route("/health")
def health_check():
    # health stays open — no data behind it, useful for uptime checks
    resp = requests.get("http://resource-api:8000/health")
    return jsonify(resp.json()), resp.status_code

@app.route("/<path:subpath>")
def gateway(subpath):
    path = "/" + subpath

    if path not in allowed_routes:
        log_decision("unknown", path, "deny")
        return jsonify({"error": "Forbidden"}), 403

    payload, error = verify_token()
    if error:
        log_decision("unknown", path, "deny")
        return error

    sub = payload.get("sub", "unknown")
    decision = check_policy(payload, path)

    if decision == "deny":
        log_decision(sub, path, "deny")
        return jsonify({"error": "Forbidden by policy"}), 403

    if decision == "requires_approval":
        approved = wait_for_approval(path, payload)
        if not approved:
            log_decision(sub, path, "deny_timeout")
            return jsonify({"error": "Denied or approval timed out"}), 403
        log_decision(sub, path, "approved")

    log_decision(sub, path, "allow")
    resp = requests.get(f"http://resource-api:8000{path}")
    return jsonify(resp.json()), resp.status_code








if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)