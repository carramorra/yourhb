"""
Run:  python app.py
Then open:  http://localhost:5000
"""

import os
from flask import Flask, render_template, request, jsonify
from rewriter import apply_rules, word_diff, MOODS

# Resolve paths relative to this file, so Flask finds templates
# no matter which directory you run the script from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "template"))

DEFAULT_TEXT = (
    "I wanted to let you know that the meeting today was productive. "
    "We covered all the points on the agenda and decided on the next steps."
)

@app.route("/")
def index():
    return render_template("index.html", moods=MOODS, default_text=DEFAULT_TEXT)


@app.route("/rewrite", methods=["POST"])
def rewrite():
    data     = request.get_json()
    text     = data.get("text", "").strip()
    mood     = data.get("mood", "formal")
    intensity = int(data.get("intensity", 1))

    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = apply_rules(text, mood, intensity)
    diff   = word_diff(text, result["modified"])

    return jsonify({
        "modified":     result["modified"],
        "explanations": result["explanations"],
        "diff":         diff,
    })


if __name__ == "__main__":
    print("🚀  Mood → Text Rewriter  →  http://localhost:5000")
    app.run(port=5000, debug=True)