from flask import Flask, jsonify
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv("SECRET_KEY")

@app.route("/token", methods=["POST"])
def issue_token():
    payload = {
        "sub": "agent-1",
        "scope": "records:read",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return jsonify({"token": token})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)