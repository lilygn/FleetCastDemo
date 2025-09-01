from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pymysql
import os

# --- env & paths ---
load_dotenv()
HERE = Path(__file__).resolve().parent              # .../OrbitalApp/backend
CA_PATH = HERE / "tidb-ca.pem"                      # expects cert at backend/tidb-ca.pem
if not CA_PATH.exists():
    raise FileNotFoundError(f"CA file not found at {CA_PATH}, cannot connect to TiDB securely")

TIDB_HOST = os.getenv("TIDB_HOST")
TIDB_PORT = int(os.getenv("TIDB_PORT", "4000"))
TIDB_USER = os.getenv("TIDB_USER")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_DATABASE = os.getenv("TIDB_DATABASE", "satellite_sim")

# import after envs to avoid circular surprises
from satellite_config import main as simulate_and_log

def get_conn():
    """Create a TLS MySQL/TiDB connection with CA verification."""
    return pymysql.connect(
        host=TIDB_HOST,
        port=TIDB_PORT,
        user=TIDB_USER,
        password=TIDB_PASSWORD,
        database=TIDB_DATABASE,
        ssl={"ca": str(CA_PATH)},      # use container path (/app/backend/...) when dockerized
        autocommit=True,
        connect_timeout=8,
    )

app = FastAPI()

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://orbital.local:8080",
        "https://fleet-cast-demo.vercel.app",
        "https://fleet-cast.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = BackgroundScheduler()

def scheduled_simulation():
    print(f"[{datetime.utcnow().isoformat()}] Running scheduled simulation")
    try:
        simulate_and_log()
    except Exception as e:
        # don't crash the scheduler thread
        print("[sched] job failed:", repr(e))

@app.on_event("startup")
def start_jobs():
    if not scheduler.running:
        scheduler.add_job(scheduled_simulation, "interval", seconds=10)
        scheduler.start()

@app.on_event("shutdown")
def stop_jobs():
    if scheduler.running:
        scheduler.shutdown(wait=False)

@app.get("/api/simulate")
def run_simulation():
    simulate_and_log()
    return {"message": "Simulation completed and data logged to TiDB"}

@app.get("/api/dashboard")
def get_dashboard_summary():
    conn = get_conn()
    try:
        cursor = conn.cursor()

        # Total telemetry logs ever recorded
        cursor.execute("SELECT COUNT(*) FROM telemetry")
        total_telemetry = cursor.fetchone()[0]

        # Low battery count across latest telemetry per satellite
        cursor.execute("""
            SELECT COUNT(*) FROM telemetry t
            INNER JOIN (
                SELECT satellite_id, MAX(timestamp) AS latest_time
                FROM telemetry
                GROUP BY satellite_id
            ) latest ON t.satellite_id = latest.satellite_id AND t.timestamp = latest.latest_time
            WHERE t.battery_level < 30
        """)
        low_battery = cursor.fetchone()[0]

        # Error status across latest telemetry per satellite
        cursor.execute("""
            SELECT COUNT(*) FROM telemetry t
            INNER JOIN (
                SELECT satellite_id, MAX(timestamp) AS latest_time
                FROM telemetry
                GROUP BY satellite_id
            ) latest ON t.satellite_id = latest.satellite_id AND t.timestamp = latest.latest_time
            WHERE t.status = 'ERROR'
        """)
        errors = cursor.fetchone()[0]

        # Active contacts now
        cursor.execute("""
            SELECT COUNT(DISTINCT satellite_id)
            FROM contact_windows
            WHERE assigned = TRUE AND end_time > UTC_TIMESTAMP()
        """)
        active_contacts = cursor.fetchone()[0]

        cursor.close()
    finally:
        conn.close()

    return {
        "totalSatellites": 100,
        "activeContacts": active_contacts,
        "lowBattery": low_battery,
        "errorState": errors,
        "totalTelemetry": total_telemetry,
    }

@app.get("/api/station/{station_id}")
def get_station_data(station_id: str):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
            sub.ground_station_id, 
            sub.satellite_id,
            sub.battery_level,
            sub.temperature,
            sub.status,
            sub.timestamp
        FROM (
            SELECT 
                cw.ground_station_id, 
                cw.satellite_id,
                t.battery_level,
                t.temperature,
                t.status,
                t.timestamp,
                ROW_NUMBER() OVER (
                    PARTITION BY cw.satellite_id 
                    ORDER BY t.timestamp DESC
                ) AS rn
            FROM contact_windows cw
            JOIN telemetry t ON cw.satellite_id = t.satellite_id 
                             AND cw.ground_station_id = t.ground_station_id
            WHERE cw.assigned = TRUE 
              AND cw.end_time > UTC_TIMESTAMP()
              AND cw.ground_station_id = %s
        ) sub
        WHERE sub.rn = 1
        """, (station_id,))
        results = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()

    station_data = [
        {
            "satellite_id": row[1],
            "battery_level": row[2],
            "temperature": row[3],
            "status": row[4],
            "timestamp": row[5],
        }
        for row in results
    ]
    return {"station_id": station_id, "satellites": station_data}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
