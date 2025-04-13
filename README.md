# Raspberry Pi Sensor REST API

## 📋 Overview

This project provides a simple REST API built with **Python Flask** for reading data from **DHT11** or **CCS811** sensors on Raspberry Pi (or mocking them for development/testing).

It supports:
- Mock sensor data generation (for dev/testing)
- Real DHT11 sensor readings via `adafruit_dht` (if hardware and library are available)
- JSON response via `/sensor/data` endpoint

---

## 🚀 Project Setup

### ✅ Requirements

- Python 3.8+
- Flask
- Optional: `adafruit-circuitpython-dht` and `blinka` libraries (for real hardware readings)

### 🔧 Installation

```
# Clone the project (or copy files locally)
cd your-project-folder

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Flask
pip install flask

# Optional: Install Adafruit DHT support (only if using real sensors)
pip install adafruit-circuitpython-dht
pip install RPI.GPIO
pip install --upgrade setuptools
```

⚙️ Running the App
🧪 Mock mode (no hardware needed)
```
python main.py --type DHT --device-pin 17 --mock true --http-port 5000
```

Command-Line Flags

| Flag         | Description                                    |
|--------------|------------------------------------------------|
| --type       | Sensor type: DHT or CCS                        |
| --device-pin | GPIO pin number used (e.g., 17)                |
| --mock       | Whether to use mock data (true or false)       |
| --http-port  | HTTP port to expose the server (default: 5000) |

🌐 API Usage
GET /sensor/data
Returns the current sensor data with metadata.

🔄 Example Request:
```
curl http://localhost:5000/sensor/data
```