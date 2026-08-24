<p align="center">
  <img src="ai-surveillance-logo.png" alt="AI Surveillance System">
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
flowchart LR

    CAM["🎥 Camera Sources<br/>Laptop • External"]

    subgraph CV["🧠 COMPUTER VISION"]
        CAP["Frame Capture"]
        YOLO["YOLO Detection"]
        TRACK["Object Tracking"]
        CAP --> YOLO --> TRACK
    end

    subgraph ANALYSIS["🔎 ANALYSIS"]
        MOT["Motion Detection"]
        ZONE["Intrusion Detection"]
        LOITER["Loitering Detection"]
        HEAT["Heatmap"]
        TRACK --> ZONE
        TRACK --> LOITER
        TRACK --> HEAT
    end

    subgraph EVENTS["🚨 EVENT ENGINE"]
        ENGINE["Event Detection"]
        RECORD["🎬 Record"]
        SNAP["📸 Snapshot"]
        ALERT["📱 Telegram"]
        LOG["🗃️ Activity Log"]

        ENGINE --> RECORD
        ENGINE --> SNAP
        ENGINE --> ALERT
        ENGINE --> LOG
    end

    subgraph BACKEND["⚙️ BACKEND"]
        STATE["Shared State"]
        API["Flask API"]
        STREAM["MJPEG Stream"]
        DB[("SQLite")]
    end

    DASH["🖥️ Web Dashboard"]

    CAM --> CAP

    CAP --> MOT
    MOT --> ENGINE
    ZONE --> ENGINE
    LOITER --> ENGINE

    YOLO --> STATE
    TRACK --> STATE
    MOT --> STATE
    RECORD --> STATE

    LOG --> DB
    STATE --> API
    STATE --> STREAM

    API --> DASH
    STREAM --> DASH
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


---

## 🖥️ Dashboard

The web dashboard provides real-time visibility into connected cameras, AI detections, motion status, intrusion events, recording status, and surveillance activity.

### Main Dashboard

<p align="center">
  <img src="dashboard/dashboard.png" alt="AI Surveillance Dashboard" width="900">
</p>

### Dual-Camera Monitoring

<p align="center">
  <img src="dashboard/Dual-Camera AI Surveillance Dashboard.png" alt="Dual-Camera AI Surveillance Dashboard" width="900">
</p>

### Detection & Heatmap

<p align="center">
  <img src="dashboard/detection-heatmap.png" alt="Detection Heatmap" width="900">
</p>

### Surveillance Events

<p align="center">
  <img src="dashboard/events.png" alt="Surveillance Events" width="900">
</p>

### Dark Dashboard View

<p align="center">
  <img src="dashboard/Dark AI Surveillance Dashboard.png" alt="Dark AI Surveillance Dashboard" width="900">
</p>
