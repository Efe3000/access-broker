from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/records")
def records():
    return jsonify([
        {"name": "Ada Lovelace",   "email": "ada@example.com",   "ssn": "111-22-3333"},
        {"name": "Alan Turing",    "email": "alan@example.com",  "ssn": "444-55-6666"},
        {"name": "Grace Hopper",   "email": "grace@example.com", "ssn": "777-88-9999"},
    ])



@app.route("/delete-records", methods=["GET"])
def delete_records():
    return jsonify({"status": "records deleted (simulated)"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)



