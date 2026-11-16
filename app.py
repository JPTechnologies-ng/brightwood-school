from datetime import datetime, timezone
import json
import re
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=None)


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.get("/<page>")
def pages(page):
    page = page.removesuffix(".html")
    if page not in {"about", "admissions"}:
        return send_from_directory(ROOT, "index.html")
    return send_from_directory(ROOT, f"{page}.html")


@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ROOT / "assets", filename)


@app.post("/api/inquiries")
def submit_inquiry():
    data = request.get_json(silent=True) or request.form
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    grade = str(data.get("grade", "")).strip()
    message = str(data.get("message", "")).strip()

    if data.get("website"):
        return jsonify({"ok": True})
    if not name or len(name) > 100:
        return jsonify({"ok": False, "error": "Please enter your name."}), 400
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return jsonify({"ok": False, "error": "Please enter a valid email address."}), 400
    if not grade or len(grade) > 80:
        return jsonify({"ok": False, "error": "Please choose a grade level."}), 400
    if len(message) > 2000:
        return jsonify({"ok": False, "error": "Please keep your message under 2,000 characters."}), 400

    record = {
        "name": name,
        "email": email,
        "grade": grade,
        "message": message,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    with (ROOT / "inquiries.jsonl").open("a", encoding="utf-8") as inquiries:
        inquiries.write(json.dumps(record, ensure_ascii=True) + "\n")
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, port=5000)