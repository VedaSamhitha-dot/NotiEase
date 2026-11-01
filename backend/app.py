from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from information_extraction import extract_information

app = Flask(__name__)
CORS(app)

# Frontend files are in the sibling "frontend" folder.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def clean_heading(text):
    """Remove a leading NOTICE label and the sample heading."""
    import re

    text = re.sub(r"^\s*NOTICE\s*:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"^\s*Internal Assessment\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return text.strip()


def build_short_version(information):
    parts = []

    if information["required_actions"]:
        first_action = clean_heading(information["required_actions"][0])
        if first_action:
            parts.append(first_action)

    if information["eligibility"]:
        first_eligibility = clean_heading(information["eligibility"][0])
        if first_eligibility:
            parts.append(first_eligibility)

    if not parts:
        return information.get("summary") or (
            "No key details could be identified. "
            "Please check the original notice."
        )

    return " ".join(parts)


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>", methods=["GET"])
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/process", methods=["POST"])
def process_notice():
    data = request.get_json(silent=True) or {}
    notice = data.get("notice", "")

    if not isinstance(notice, str) or not notice.strip():
        return jsonify({
            "error": "Please enter a valid college notice.",
        }), 400

    try:
        information = extract_information(notice)
        summary = build_short_version(information)

        return jsonify({
            "summary": summary,
            "event_dates": information["event_dates"],
            "deadlines": information["deadlines"],
            "amounts": information["amounts"],
            "eligibility": information["eligibility"],
            "required_actions": information["required_actions"],
            "consequences": information["consequences"],
        })

    except Exception:
        app.logger.exception("Error processing notice")
        return jsonify({
            "error": "Unable to process the notice. Please try again.",
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)