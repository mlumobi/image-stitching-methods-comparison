import os
import base64
import tempfile
import threading
import webbrowser
from flask import Flask, request, jsonify, render_template
from backend import ImageAlignBackend

# ----------------------------------------------------
# Flask App Setup
# ----------------------------------------------------
# server.py is inside /code, so templates/ and static/
# must be inside the same directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

backend = ImageAlignBackend()

# ----------------------------------------------------
# Helper: Save Uploaded Image to Temp File
# ----------------------------------------------------
def save_temp_file(data_bytes, filename):
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, filename)
    with open(path, "wb") as f:
        f.write(data_bytes)
    return path

# ----------------------------------------------------
# Routes
# ----------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/run_pipeline")
def run_pipeline():
    if "img1" not in request.files or "img2" not in request.files:
        return jsonify({"error": "Missing images"}), 400

    img1 = request.files["img1"]
    img2 = request.files["img2"]
    method = request.form.get("method", "SIFT")

    # Save input images to temp
    path1 = save_temp_file(img1.read(), img1.filename)
    path2 = save_temp_file(img2.read(), img2.filename)

    # Run your stitching backend
    results = backend.run_pipeline(path1, path2, method)

    # Convert output files to base64 for browser display
    output = {}
    for key, filepath in results.items():
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        output[key] = f"data:image/jpeg;base64,{encoded}"

    return jsonify(output)

# ----------------------------------------------------
# Auto-open Browser
# ----------------------------------------------------
def open_browser():
    webbrowser.open_new("http://localhost:5050")

# ----------------------------------------------------
# Start Flask + Auto Browser
# ----------------------------------------------------
if __name__ == "__main__":
    # Open browser automatically 1 sec after start
    threading.Timer(1.0, open_browser).start()

    # Run Flask on a safe, unused port on macOS
    app.run(host="0.0.0.0", port=5050, debug=True)