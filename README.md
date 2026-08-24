<p align="center">
  <img src="ai-surveillance-banner.png" alt="AI Surveillance System">
</p>

<p align="center">
  <b>Real-time AI-powered multi-camera surveillance system</b>
</p>

<p align="center">
  Detect • Track • Analyze • Alert • Record
</p>

---


## 🚨 Overview

AI Surveillance System is a real-time computer vision platform designed to monitor multiple camera feeds and automatically identify potentially suspicious activity.

The system combines AI-based person detection, object tracking, intrusion-zone monitoring, loitering detection, automated recording, Telegram notifications, persistent activity logging, and a web-based monitoring dashboard into a single surveillance pipeline.

### What it does

- 🎥 **Multi-Camera Monitoring** — Monitor multiple cameras simultaneously.
- 🧠 **AI Person Detection** — Detect people in real time using YOLO.
- 🎯 **Object Tracking** — Track detected people across frames.
- 🚨 **Intrusion Detection** — Detect when a person enters a configured restricted zone.
- 🚶 **Loitering Detection** — Identify people remaining in an area for an unusual duration.
- 🎬 **Automated Recording** — Automatically record relevant detection events.
- 📸 **Snapshots** — Capture frames during important events.
- 📱 **Telegram Alerts** — Send real-time surveillance notifications.
- 🗃️ **Activity Logging** — Persist intrusion events using SQLite.
- 📊 **Anomaly Detection** — Compare activity against historical time-of-day patterns.
- 🖥️ **Web Dashboard** — Monitor camera status, detections, recordings, and events in real time.
- 🌡️ **Heatmap Visualization** — Visualize spatial activity within camera feeds.

The architecture is designed so that the camera-processing layer, API layer, activity logging system, and dashboard remain separated, making the system easier to extend with additional cameras and detection capabilities.

---

## 🏗️ System Architecture

```mermaid
flowchart TB

    CAM["🎥 Camera Sources<br/>Laptop Camera • External Camera"]

    subgraph CV["🧠 Computer Vision Pipeline"]
        CAP["Frame Capture"]
        MOT["Motion Detection"]
        YOLO["YOLO Person Detection"]
        TRACK["Object Tracking"]
        ZONE["Intrusion Zone Analysis"]
        LOITER["Loitering Detection"]
        HEAT["Heatmap Generation"]
    end

    subgraph EVENTS["🚨 Event Processing"]
        ENGINE["Event Detection Engine"]
        RECORD["🎬 Automated Recording"]
        SNAP["📸 Snapshot Capture"]
        ALERT["📱 Telegram Alerts"]
        LOG["🗃️ Activity Logger"]
    end

    subgraph BACKEND["⚙️ Backend"]
        STATE["Shared Camera State"]
        API["Flask REST API"]
        STREAM["Live MJPEG Streams"]
        DB[("SQLite Database")]
    end

    subgraph DASHBOARD["🖥️ Web Dashboard"]
        UI["Real-Time Monitoring UI"]
        STATUS["Camera & Detection Status"]
        EVENTS_UI["Event History"]
        FULL["Fullscreen Camera View"]
    end

    CAM --> CAP

    CAP --> MOT
    CAP --> YOLO

    YOLO --> TRACK

    TRACK --> ZONE
    TRACK --> LOITER
    TRACK --> HEAT

    MOT --> ENGINE
    ZONE --> ENGINE
    LOITER --> ENGINE

    ENGINE --> RECORD
    ENGINE --> SNAP
    ENGINE --> ALERT
    ENGINE --> LOG

    LOG --> DB

    MOT --> STATE
    YOLO --> STATE
    TRACK --> STATE
    ZONE --> STATE
    LOITER --> STATE
    RECORD --> STATE

    STATE --> API
    STATE --> STREAM

    API --> UI
    STREAM --> UI

    UI --> STATUS
    UI --> EVENTS_UI
    UI --> FULL
```

### 🔄 Processing Pipeline

**Camera → Frame Capture → AI Detection → Tracking → Event Analysis → Response → Storage → API → Dashboard**

| Stage | Function |
|---|---|
| 🎥 Capture | Acquire frames from configured cameras |
| 🧠 Detection | Detect people using YOLO |
| 🎯 Tracking | Track detected people across frames |
| 🚨 Intrusion | Detect entry into configured restricted zones |
| 🚶 Loitering | Detect prolonged presence |
| 🔥 Heatmap | Visualize activity distribution |
| 🎬 Recording | Automatically record relevant events |
| 📸 Snapshot | Capture detection snapshots |
| 📱 Alerting | Send Telegram notifications |
| 🗃️ Logging | Persist surveillance events in SQLite |
| ⚙️ API | Expose camera status, events and streams |
| 🖥️ Dashboard | Display real-time surveillance information |
---



## 🧠 Core Technologies

| Category | Technology |
|---|---|
| Programming Language | Python |
| Computer Vision | OpenCV |
| Object Detection | Ultralytics YOLO |
| Object Tracking | ByteTrack |
| Backend API | Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Notifications | Telegram Bot API |
| Version Control | Git / GitHub |

---
