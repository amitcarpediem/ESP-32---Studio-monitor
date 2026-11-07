# 🎓 College Viva & Presentation Guide
### ESP32 Voice Studio Silence & Environment Monitor

Use this guide to prepare for your presentation and viva questions. Professors love structured, technical answers!

---

## 1. Project Title & 30-Second Elevator Pitch
> **"Our project is an ESP32-based Smart Studio Silence and Environmental Telemetry System. It monitors acoustic noise levels in a voice recording studio using an analog microphone module, along with room temperature and humidity using a DHT11 sensor. It calculates a real-time 'Silence Rating' out of 10 and provides a live decision banner on a web dashboard indicating whether it is quiet enough to record voice without background noise."**

---

## 2. Top Viva Questions & Model Answers

### Q1: Why did you choose ESP32 over Arduino Uno?
**Answer:**
- The ESP32 has **built-in Wi-Fi and Bluetooth**, eliminating the need for an external Wi-Fi shield like ESP8266 or Ethernet module.
- It operates at **240 MHz (dual-core)** compared to Arduino Uno's 16 MHz, allowing fast audio signal sampling while handling network requests.
- It has multiple 12-bit ADC channels for higher analog resolution (0–4095 compared to 0–1023 on Arduino Uno).

---

### Q2: How does the microphone measure noise loudness?
**Answer:**
- Sound is an AC pressure wave centered around a DC offset voltage. Reading a single analog sample can easily hit the wave near the zero-crossing, giving a false quiet reading.
- To solve this, our code uses a **50ms sample window** to measure the **peak-to-peak amplitude** ($\text{Max Voltage} - \text{Min Voltage}$).
- The peak-to-peak value accurately reflects the actual volume/amplitude of acoustic sound in the room regardless of wave phase.

---

### Q3: Why is the microphone connected to GPIO 34 specifically?
**Answer:**
- The ESP32 has two Analog-to-Digital Converters: **ADC1** (GPIO 32 to 39) and **ADC2** (GPIO 0, 2, 4, 12–15, 25–27).
- When the ESP32 turns on its **Wi-Fi radio**, the hardware Wi-Fi driver permanently occupies **ADC2**.
- Therefore, all analog sensors must be connected to **ADC1 pins** (such as GPIO 34) when Wi-Fi is enabled.

---

### Q4: How does data transfer from ESP32 to the website?
**Answer:**
- The ESP32 acts as an **HTTP Client**.
- It bundles the sensor values into a **JSON payload**:
  `{"temperature": 24.5, "humidity": 48.0, "sound_level": 15.0}`
- It sends an **HTTP POST request** over the local Wi-Fi network to the Python server at `http://<PC_IP>:5000/api/data`.
- The Python server processes the payload, computes the Silence Rating, and saves it into memory and a CSV log file.

---

### Q5: How does the web dashboard update in real-time?
**Answer:**
- We implemented a clean, lightweight polling mechanism using vanilla JavaScript: `setInterval(fetchSensorData, 2000)`.
- Every 2 seconds, the client calls `fetch('/api/data')` asynchronously without refreshing or flickering the webpage.
- The DOM updates the silence progress bar, color classes, and log table instantly.

---

### Q6: Why did you monitor Temperature and Humidity in a recording studio?
**Answer:**
- Professional studio condenser microphones (like Neumann or Rode mics) and acoustic instruments (violins, guitars) are sensitive to relative humidity.
- High humidity (>65%) causes moisture condensation on microphone diaphragms, leading to crackling noises and mold on acoustic foam.
- High temperatures (>28°C) cause thermal discomfort for voice artists and cause computer fans inside the control room to spin louder, increasing room noise.

---

### Q7: What software tools and libraries did you use?
**Answer:**
- **Microcontroller:** ESP32 programmed with C++ in the Arduino IDE (using `WiFi.h`, `HTTPClient.h`, and `DHT.h`).
- **Backend:** Pure Python 3 using the built-in `http.server` library (no external heavy frameworks, lightweight and fast).
- **Frontend:** Pure HTML5, CSS3, and JavaScript (Fetch API).
- **Data Persistence:** Automated logging to `sensor_log.csv`.

---

## 3. Demo Checklist for Presentation Day

1. **Start Server:** Double-click `run_server.bat` (Starts server on `http://localhost:5000`).
2. **If ESP32 is powered on:** Confirm ESP32 Serial Monitor shows `[SUCCESS] Connected to Wi-Fi!` and `[HTTP Success] Response code: 200`.
3. **If demonstrating without ESP32:**
   - Double-click `run_simulator.bat` to show real-time incoming sensor packets.
