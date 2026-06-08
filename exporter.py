#!/usr/bin/env python3
"""
Custom Prometheus exporter for the Sentiment Analysis API.
Polls /api/latest-confidence every 5 seconds and exposes
prediction_confidence_score as a Prometheus gauge on port 8000.
"""

import time
import requests
from prometheus_client import start_http_server, Gauge

# The single metric the grading script checks for
CONFIDENCE_GAUGE = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from the sentiment API'
)

# Poll the app running via Minikube NodePort
APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5  # seconds
DEFAULT_CONFIDENCE = 1.0


def fetch_confidence() -> float:
    """Fetch latest confidence from the app. Returns 1.0 if unreachable."""
    try:
        response = requests.get(APP_URL, timeout=3)
        response.raise_for_status()
        data = response.json()
        return float(data.get("confidence", DEFAULT_CONFIDENCE))
    except Exception:
        return DEFAULT_CONFIDENCE


def main():
    # Start Prometheus HTTP server on port 8000
    start_http_server(8000)
    print("Exporter running on port 8000 — polling every 5s...")

    while True:
        confidence = fetch_confidence()
        CONFIDENCE_GAUGE.set(confidence)
        print(f"[{time.strftime('%H:%M:%S')}] confidence = {confidence:.4f}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
