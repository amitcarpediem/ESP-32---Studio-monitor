"""
ESP32 Mock Telemetry Simulator
Sends simulated Temperature, Humidity, and Sound data to the server
Uses only Python standard library (no pip packages needed)
"""

import urllib.request
import json
import time
import random

SERVER_URL = "http://127.0.0.1:5000/api/data"

print("=" * 60)
print(" [ESP32 SENSOR SIMULATOR - STUDIO NOISE & CLIMATE]")
print("=" * 60)
print(f" Target Server URL: {SERVER_URL}")
print(" Streaming simulated sensor packets every 3 seconds...")
print(" Press Ctrl+C to stop.")
print("=" * 60)

temp = 24.0
hum = 48.0

cycle = 0

while True:
    cycle += 1

    # Simulate realistic temperature and humidity drift
    temp += round(random.uniform(-0.2, 0.2), 1)
    temp = max(21.0, min(28.0, round(temp, 1)))

    hum += round(random.uniform(-0.5, 0.5), 1)
    hum = max(40.0, min(65.0, round(hum, 1)))

    # Simulate noise: mostly quiet studio with occasional talking or clatter
    event_chance = random.random()
    if event_chance > 0.85:
        sound_level = round(random.uniform(70.0, 95.0), 1)
        event_name = "LOUD EVENT (Door / Clapping)"
    elif event_chance > 0.60:
        sound_level = round(random.uniform(30.0, 48.0), 1)
        event_name = "MODERATE SOUND (AC / Soft Talk)"
    else:
        sound_level = round(random.uniform(8.0, 22.0), 1)
        event_name = "QUIET STUDIO"

    payload = {
        "temperature": temp,
        "humidity": hum,
        "sound_level": sound_level
    }

    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            SERVER_URL,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            curr = res_json.get("current", {})
            print(f"[Packet #{cycle:03d}] {event_name:<30} | Temp: {temp}C | Hum: {hum}% | Noise: {sound_level}% | Silence: {curr.get('silence_rating')}/10 -> {curr.get('status')}")

    except urllib.error.URLError as e:
        print(f"[Packet #{cycle:03d}] Error connecting to server: {e.reason}. Make sure 'python server.py' is running!")
    except Exception as e:
        print(f"[Packet #{cycle:03d}] Error: {e}")

    time.sleep(3)
