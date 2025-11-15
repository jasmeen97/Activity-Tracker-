from fastapi import FastAPI, Request
import time
import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN_HERE",  # Replace with your Sentry DSN
    traces_sample_rate=1.0
)

app = FastAPI()

# In-memory activity store (replace with DB if needed)
activity_log = []

@app.post("/track")
async def track_activity(request: Request):
    try:
        data = await request.json()
        user = data["user"]
        action = data["action"]
        timestamp = data.get("timestamp", time.time())
    except Exception as e:
        # Capture any error in Sentry
        sentry_sdk.capture_exception(e)
        return {"status": "invalid event"}

    # Store the event
    event = {"user": user, "action": action, "timestamp": timestamp}
    activity_log.append(event)

    # Simple anomaly detection: too many actions from one user
    user_events = [a for a in activity_log if a["user"] == user]
    if len(user_events) > 20:
        sentry_sdk.capture_message(
            f"Suspicious activity detected for user {user}", 
            level="warning"
        )

    return {"status": "ok"}

@app.get("/stats")
def get_stats():
    # Simple stats for demo purposes
    return {
        "total_events": len(activity_log),
        "users_tracked": list({e["user"] for e in activity_log})
    }

@app.get("/trigger-error")
def trigger_error():
    # Demo endpoint to trigger Sentry error
    1 / 0  # Intentional divide by zero
