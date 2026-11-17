from datetime import datetime, timezone
from email.message import EmailMessage
import json
import os
import re
import smtplib
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
CONTACT_EMAIL = "adogbejoseph419@gmail.com"
app = Flask(__name__, static_folder=None)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "https://jptechnologies-ng.github.io"
        }
    }
)


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


def send_inquiry_email(record):
    username = os.environ.get("SMTP_USERNAME")
    password = "".join(os.environ.get("SMTP_PASSWORD", "").split())
    if not username or not password:
        raise RuntimeError("Contact email is not configured on the server.")

    message = EmailMessage()
    message["Subject"] = "Website contact form inquiry"
    message["From"] = username
    message["To"] = CONTACT_EMAIL
    message["Reply-To"] = record["email"]
    message.set_content(
        f"Name: {record['name']}\n"
        f"Email: {record['email']}\n"
        f"Grade: {record['grade']}\n\n"
        f"{record['message']}\n\n"
        f"Submitted: {record['submitted_at']}"
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


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

    try:
        send_inquiry_email(record)
    except RuntimeError as error:
        return jsonify({"ok": False, "error": str(error)}), 503
    except (OSError, smtplib.SMTPException):
        app.logger.exception("Unable to deliver contact form inquiry")
        return jsonify({"ok": False, "error": "We could not deliver your message right now. Please try again later."}), 503

    with (ROOT / "inquiries.jsonl").open("a", encoding="utf-8") as inquiries:
        inquiries.write(json.dumps(record, ensure_ascii=True) + "\n")
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, port=5000)