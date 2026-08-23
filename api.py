from flask import Flask, jsonify, Response
from flask_cors import CORS
from shared_state import shared_frames
import cv2

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "online"
    })


@app.get("/api/cameras")
def cameras():
    result = {}

    for name, data in shared_frames.items():
        if "error" in data:
            result[name] = {
                "online": False,
                "error": data["error"],
            }
        else:
            result[name] = {
                "online": True,
                "fps": round(data.get("fps", 0), 1),
                "motion_detected": data.get("motion_detected", False),
                "person_count": data.get("person_count", 0),
                "intrusion": data.get("intrusion", False),
                "recording": data.get("recording", False),
            }

    return jsonify(result)

def generate_stream(camera_name):
    while True:
        frames = shared_frames.get(camera_name)

        if not frames or "display" not in frames:
            continue

        frame = frames["display"]

        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

@app.get("/api/stream/<camera_name>")
def stream(camera_name):
    return Response(
        generate_stream(camera_name),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def start_api():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)