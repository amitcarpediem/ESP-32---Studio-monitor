"""
ESP32 Studio Silence & Environment Monitor
College Mini-Project Backend Server
Uses only Python Standard Library (No external pip install required!)
"""

import http.server
import socketserver
import json
import os
import time
import csv
from datetime import datetime

PORT = 5000
HOST = "0.0.0.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")
CSV_LOG_FILE = os.path.join(BASE_DIR, "sensor_log.csv")

# Initialize CSV log file with header if not exists
if not os.path.exists(CSV_LOG_FILE):
    with open(CSV_LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Temperature (C)", "Humidity (%)", "Sound Level (%)", "Silence Rating (/10)", "Status"])

# Global state for sensor data
current_data = {
    "temperature": 24.5,
    "humidity": 48.0,
    "sound_level": 15.0,
    "silence_rating": 8.5,
    "status": "OK TO RECORD",
    "status_code": "OK",
    "advice": "Studio is quiet. Perfect conditions for clear voice recording.",
    "last_updated": datetime.now().strftime("%I:%M:%S %p")
}

history_log = [
    {
        "time": datetime.now().strftime("%I:%M:%S %p"),
        "temperature": 24.5,
        "humidity": 48.0,
        "sound_level": 15.0,
        "silence_rating": 8.5,
        "status": "OK TO RECORD"
    }
]

def calculate_silence(sound_level):
    """
    Computes Silence Rating (0 to 10) from sound level (0 to 100%).
    Higher rating = Quieter room (Better for recording).
    """
    try:
        sound = float(sound_level)
    except (ValueError, TypeError):
        sound = 20.0

    # Ensure sound level is between 0 and 100
    sound = max(0.0, min(100.0, sound))

    # Silence Rating: 10 is absolute dead silence, 0 is very loud
    rating = round(max(0.0, min(10.0, 10.0 - (sound / 10.0))), 1)

    if rating >= 7.5:
        status = "OK TO RECORD"
        status_code = "OK"
        advice = "Studio is very quiet. Perfect environment for recording vocals!"
    elif rating >= 5.0:
        status = "CAUTION: MODERATE NOISE"
        status_code = "CAUTION"
        advice = "Background hum or slight noise detected. Use a noise gate or record with caution."
    else:
        status = "DO NOT RECORD - TOO NOISY"
        status_code = "NOISY"
        advice = "High noise level detected! Wait for noise to stop before recording."

    return rating, status, status_code, advice

class StudioMonitorHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Override to suppress default HTTP 200 clutter in terminal
        return

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status=200)

    def do_GET(self):
        global current_data, history_log

        # Serve Dashboard Web Page
        if self.path == "/" or self.path.startswith("/?"):
            if os.path.exists(HTML_FILE):
                self._set_headers("text/html; charset=utf-8", 200)
                with open(HTML_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._set_headers("text/plain", 404)
                self.wfile.write(b"index.html not found. Please create index.html in the same directory.")
            return

        # API Endpoint to fetch latest sensor values
        if self.path == "/api/data":
            self._set_headers("application/json", 200)
            payload = {
                "current": current_data,
                "history": history_log[:8]  # Last 8 entries
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        # 404 for unknown endpoints
        self._set_headers("application/json", 404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        global current_data, history_log

        # Endpoint for ESP32 or Simulator to send data
        if self.path == "/api/data":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)

            try:
                data = json.loads(post_body.decode("utf-8"))
            except Exception as e:
                self._set_headers("application/json", 400)
                self.wfile.write(json.dumps({"status": "error", "message": f"Invalid JSON: {str(e)}"}).encode("utf-8"))
                return

            # Extract fields with safe defaults
            temp = round(float(data.get("temperature", current_data["temperature"])), 1)
            hum = round(float(data.get("humidity", current_data["humidity"])), 1)
            
            # Sound level can be passed as raw adc or percentage
            raw_sound = float(data.get("sound_level", 15.0))
            if raw_sound > 100:  # If raw 12-bit ADC reading (0-4095)
                sound_level = round(min(100.0, (raw_sound / 2000.0) * 100.0), 1)
            else:
                sound_level = round(raw_sound, 1)

            rating, status, status_code, advice = calculate_silence(sound_level)
            current_time = datetime.now().strftime("%I:%M:%S %p")

            # Update current state
            current_data = {
                "temperature": temp,
                "humidity": hum,
                "sound_level": sound_level,
                "silence_rating": rating,
                "status": status,
                "status_code": status_code,
                "advice": advice,
                "last_updated": current_time
            }

            # Prepend to history log
            log_item = {
                "time": current_time,
                "temperature": temp,
                "humidity": hum,
                "sound_level": sound_level,
                "silence_rating": rating,
                "status": status
            }
            history_log.insert(0, log_item)
            if len(history_log) > 20:
                history_log.pop()

            # Append to CSV file
            try:
                with open(CSV_LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([current_time, temp, hum, sound_level, rating, status])
            except Exception:
                pass

            print(f"[{current_time}] Recv ESP32 -> Temp: {temp}C | Hum: {hum}% | Sound: {sound_level}% | Silence: {rating}/10 -> {status}")

            self._set_headers("application/json", 200)
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Data recorded successfully",
                "current": current_data
            }).encode("utf-8"))
            return

        # Simulation trigger from frontend buttons
        if self.path == "/api/simulate":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

            mode = "quiet"
            try:
                body = json.loads(post_body.decode("utf-8"))
                mode = body.get("mode", "quiet")
            except Exception:
                pass

            if mode == "quiet":
                sim_sound = 12.0
                sim_temp = 23.8
                sim_hum = 46.0
            elif mode == "moderate":
                sim_sound = 38.0
                sim_temp = 25.2
                sim_hum = 52.0
            else:  # loud
                sim_sound = 82.0
                sim_temp = 26.5
                sim_hum = 58.0

            rating, status, status_code, advice = calculate_silence(sim_sound)
            current_time = datetime.now().strftime("%I:%M:%S %p")

            current_data = {
                "temperature": sim_temp,
                "humidity": sim_hum,
                "sound_level": sim_sound,
                "silence_rating": rating,
                "status": status,
                "status_code": status_code,
                "advice": advice,
                "last_updated": current_time
            }

            history_log.insert(0, {
                "time": current_time,
                "temperature": sim_temp,
                "humidity": sim_hum,
                "sound_level": sim_sound,
                "silence_rating": rating,
                "status": status
            })

            print(f"[{current_time}] Demo Mode [{mode.upper()}] -> Sound: {sim_sound}% | Silence: {rating}/10 -> {status}")

            self._set_headers("application/json", 200)
            self.wfile.write(json.dumps({"status": "simulated", "current": current_data}).encode("utf-8"))
            return

        self._set_headers("application/json", 404)
        self.wfile.write(json.dumps({"error": "Unknown POST route"}).encode("utf-8"))

def run():
    server_address = (HOST, PORT)
    # Enable address reuse so restarting doesn't hit 'Address already in use'
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(server_address, StudioMonitorHandler)
    print("=" * 60)
    print(" [ESP32 STUDIO SILENCE & ENVIRONMENT MONITOR - SERVER]")
    print("=" * 60)
    print(f" -> Local Dashboard:   http://localhost:{PORT}")
    print(f" -> Network (ESP32):   http://192.168.1.4:{PORT}/api/data")
    print(f" -> Sensor Log CSV:    {CSV_LOG_FILE}")
    print(" Press Ctrl+C in terminal to stop.")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run()
