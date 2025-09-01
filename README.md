# FleetCast Demo

This is a version of FleetCast meant for demonstration. Its implementation in Xlab uses Kubernetes.

## Live Demo
Visit the site here: [fleetcast.onrender.com](https://fleetcast.onrender.com)

## Features
- Dashboard with total satellites, active contacts, low battery alerts, and error states
- Station view showing latest telemetry per ground station
- Scheduled background jobs to simulate satellite activity

## Run Locally (optional)
If you’d like to run this locally:

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8080
