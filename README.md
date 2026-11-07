# 🎙️ ESP32 Voice Studio Silence & Environment Monitor
### College IoT Mini-Project

A clean, lightweight IoT system designed to monitor a voice recording studio before capturing audio. It measures **Room Noise (Microphone)**, **Temperature**, and **Humidity** via an **ESP32 microcontroller** and displays live data on a clean, responsive web dashboard with a clear recording decision banner (**OK to Record** vs **Do Not Record**).

---

## 💡 Why This Project?
In voice recording studios, background noise (such as air conditioning hum, fan noise, outside traffic, or people talking) ruins vocal takes. Retaking audio wastes time and money. 
This IoT project acts as an automatic **Studio Silence Indicator**:
- **Silence Rating (0 to 10)**: Real-time noise score from an analog microphone.
- **Recording Status Banner**: Instantly informs voice artists:
  - 🟢 **OK TO RECORD** (Studio is quiet, Silence Rating >= 7.5)
  - 🟡 **CAUTION** (Moderate background sound, Silence Rating 5.0 to 7.4)
  - 🔴 **DO NOT RECORD** (Too noisy, Silence Rating < 5.0)
- **Temperature & Humidity**: Ensures condenser microphones and audio equipment are not damaged by high moisture or extreme heat.

---

## 🛠️ Project Structure

```text
studio_noise_monitor/
├── server.py              # Pure Python web server (Zero external pip packages needed!)
├── index.html             # Clean, responsive student web dashboard
├── simulate_esp32.py      # Test simulator to generate realistic sensor data
├── run_server.bat         # 1-Click launcher: starts server & opens browser
├── run_simulator.bat      # 1-Click launcher: starts test simulator
├── sensor_log.csv         # Automatically created CSV file logging all readings
├── esp32_code/
│   └── studio_monitor_esp32.ino  # Complete Arduino code for ESP32
└── COLLEGE_VIVA_GUIDE.md  # Viva questions & answers for college presentation
```

---

## 🚀 How to Run (Takes 10 Seconds)

### Step 1: Start the Python Web Server
Open a terminal inside this folder and run:
```bash
python server.py
```
*(Or simply double-click `run_server.bat`)*

The server will start on:
- **Local Dashboard:** [http://localhost:5000](http://localhost:5000)
- **Network API for ESP32:** `http://192.168.1.4:5000/api/data`

---

### Step 2: Test Without Hardware (Using Simulator)
If you are presenting in college and don't have the ESP32 plugged in, open another terminal and run:
```bash
python simulate_esp32.py
```
*(Or simply double-click `run_simulator.bat`)*

You will see live simulated readings appear in your browser every 3 seconds, alternating between quiet studio conditions, soft speaking, and loud events.


---

## ⚡ Hardware Connections (ESP32)

### 📌 Pinout Diagram

| Sensor | Sensor Pin | ESP32 Pin | Purpose |
|---|---|---|---|
| **DHT11 / DHT22** | VCC | 3.3V | Power |
| **DHT11 / DHT22** | GND | GND | Ground |
| **DHT11 / DHT22** | DATA | **GPIO 4** | Digital Temperature & Humidity |
| **Microphone Module** | VCC | 3.3V (or 5V/VIN) | Power |
| **Microphone Module** | GND | GND | Ground |
| **Microphone Module** | OUT / AO | **GPIO 34** | Analog Sound Signal (ADC1) |

*(Supported Mic Modules: KY-037, KY-038, MAX4466, MAX9814)*

> ⚠️ **Important for Viva:** Analog pin GPIO 34 belongs to **ADC1**. ESP32 disables ADC2 when Wi-Fi is active, so analog sensors must always use ADC1 (GPIO 32 to 39).

---

## 📡 Flashing ESP32 Code
1. Open the Arduino IDE.
2. Open `esp32_code/studio_monitor_esp32.ino`.
3. In lines 29-30, enter your Wi-Fi SSID and password (or mobile hotspot):
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";
   const char* password = "YOUR_PASSWORD";
   ```
4. Verify that the PC IP is correct:
   ```cpp
   const char* serverUrl = "http://192.168.1.4:5000/api/data";
   ```
5. Install the **"DHT sensor library" by Adafruit** from the Arduino Library Manager.
6. Select your ESP32 board and COM port, then click **Upload**.

---

## 📊 How the Silence Rating is Calculated
1. The ESP32 samples the analog microphone over a **50ms window** to measure the **peak-to-peak amplitude** of the sound wave:
   $$\text{PeakToPeak} = \text{Max ADC} - \text{Min ADC}$$
2. The peak-to-peak amplitude is normalized into a **0–100% Noise Level**.
3. The server computes the **Silence Rating (0 to 10)**:
   $$\text{Silence Rating} = 10.0 - \left(\frac{\text{Noise Level}}{10}\right)$$
   - Higher rating = Quieter room (Silence Rating 10 is absolute dead silence).
   - If Silence Rating $\ge 7.5$: **OK TO RECORD** (Green)
   - If Silence Rating is between $5.0$ and $7.4$: **CAUTION** (Yellow)
   - If Silence Rating $< 5.0$: **DO NOT RECORD** (Red)
