from flask import Flask, jsonify, request
import uuid
import time

app = Flask(__name__)

# in-memory store — fine for a demo, would be a real DB in production
pending_approvals = {}

@app.route("/approvals", methods=["POST"])
def create_approval():
    approval_id = str(uuid.uuid4())
    pending_approvals[approval_id] = {
        "status": "pending",
        "created_at": time.time(),
        "details": request.get_json()
    }
    return jsonify({"approval_id": approval_id}), 201

@app.route("/approvals/<approval_id>", methods=["GET"])
def get_approval(approval_id):
    approval = pending_approvals.get(approval_id)
    if not approval:
        return jsonify({"error": "Not found"}), 404
    return jsonify(approval)

@app.route("/approvals/<approval_id>/decide", methods=["POST"])
def decide_approval(approval_id):
    approval = pending_approvals.get(approval_id)
    if not approval:
        return jsonify({"error": "Not found"}), 404

    decision = request.get_json().get("decision")  # "approved" or "denied"
    if decision not in ("approved", "denied"):
        return jsonify({"error": "decision must be 'approved' or 'denied'"}), 400

    approval["status"] = decision
    return jsonify(approval)


@app.route("/approvals", methods=["GET"])
def list_approvals():
    return jsonify(pending_approvals)








if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)