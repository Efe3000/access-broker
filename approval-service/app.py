from flask import Flask, jsonify, request
import uuid
import time
from models import Approval, SessionLocal

app = Flask(__name__)

@app.route("/approvals", methods=["POST"])
def create_approval():
    approval_id = str(uuid.uuid4())
    data = request.get_json()

    approval = Approval(
        id=approval_id,
        status="pending",
        path=data.get("path"),
        sub=data.get("sub"),
        created_at=time.time()
    )

    session = SessionLocal()
    session.add(approval)
    session.commit()
    session.close()

    return jsonify({"approval_id": approval_id}), 201

@app.route("/approvals/<approval_id>", methods=["GET"])
def get_approval(approval_id):
    session = SessionLocal()
    approval = session.query(Approval).get(approval_id)
    session.close()

    if not approval:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "status": approval.status,
        "path": approval.path,
        "sub": approval.sub,
        "created_at": approval.created_at
    })

@app.route("/approvals/<approval_id>/decide", methods=["POST"])
def decide_approval(approval_id):
    decision = request.get_json().get("decision")
    if decision not in ("approved", "denied"):
        return jsonify({"error": "decision must be 'approved' or 'denied'"}), 400

    session = SessionLocal()
    approval = session.query(Approval).get(approval_id)

    if not approval:
        session.close()
        return jsonify({"error": "Not found"}), 404

    approval.status = decision
    session.commit()
    result = {"status": approval.status, "path": approval.path, "sub": approval.sub}
    session.close()

    return jsonify(result)

@app.route("/approvals", methods=["GET"])
def list_approvals():
    session = SessionLocal()
    approvals = session.query(Approval).all()
    session.close()

    return jsonify({
        a.id: {"status": a.status, "path": a.path, "sub": a.sub, "created_at": a.created_at}
        for a in approvals
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)