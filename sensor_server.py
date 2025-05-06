import argparse
import random
from flask import Flask, jsonify
try:
    import board
    import adafruit_dht
except ImportError:
    board = None
    adafruit_dht = None
app = Flask(__name__)

# Default mock sensor reading functions
def generate_mock_ccs811_data():
    return {
        "tvoc": random.randint(0, 600),
        "eco2": random.randint(400, 2000)
    }

def generate_mock_dht11_data():
    return {
        "temperature_celsius": round(random.uniform(20, 30), 2),
        "temperature_fahrenheit": round(random.uniform(68, 86), 2),
        "humidity": round(random.uniform(30, 70), 2)
    }

# Real sensor reading function for DHT11
def read_dht11_data(pin):
    try:
        dht_device = adafruit_dht.DHT11(getattr(board, f"D{pin}"), use_pulseio=False)
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        if temperature_c is None or humidity is None:
            return {"error": "Sensor returned None values"}

        temperature_f = round(temperature_c * 9 / 5 + 32, 2)

        return {
            "temperature_celsius": temperature_c,
            "temperature_fahrenheit": temperature_f,
            "humidity": humidity
        }

    except RuntimeError as error:
        return {"error": f"Runtime error: {str(error)}"}
    except Exception as error:
        return {"error": f"Unexpected error: {str(error)}"}

# Real sensor reading function for CCS811 (placeholder)
def read_ccs811_data(pin):
    return {"error": "Real CCS811 reading not implemented"}

# Global sensor config
sensor_type = None
sensor_pin = None
use_mock = True

@app.route('/sensor/data', methods=['GET'])
def get_sensor_data():
    # Validate sensor type
    if sensor_type not in ["DHT_11", "CCS811"]:
        return jsonify({"error": "Unknown or unsupported sensor type"}), 400

    # Use mock data if enabled
    if use_mock:
        if sensor_type == "DHT_11":
            data = generate_mock_dht11_data()
        elif sensor_type == "CCS811":
            data = generate_mock_ccs811_data()
    else:
        # Read real sensor data
        if sensor_type == "DHT_11":
            data = read_dht11_data(sensor_pin)
        elif sensor_type == "CCS811":
            data = read_ccs811_data(sensor_pin)

        # Handle sensor read error
        if isinstance(data, dict) and "error" in data:
            return jsonify({
                "type": sensor_type,
                "device-pin": sensor_pin,
                "error": data["error"]
            }), 404  # Sensor read failed or data not found

        # Validate data contents
        if not data or any(value is None for value in data.values()):
            return jsonify({
                "type": sensor_type,
                "device-pin": sensor_pin,
                "error": "Incomplete or missing sensor data"
            }), 400  # Bad data format

    return jsonify({
        "type": sensor_type,
        "device-pin": sensor_pin,
        "data": data
    }), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sensor REST API')
    parser.add_argument('--type', required=True, choices=['DHT_11', 'CCS811'], help='Sensor type (DHT_11 or CCS811)')
    parser.add_argument('--device-pin', required=True, type=int, help='Device pin number (0-100)')
    parser.add_argument('--mock', required=True, type=lambda x: x.lower() == 'true', help='Use mock data (true/false)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run on')
    parser.add_argument('--http-port', default=5000, type=int, help='HTTP server port')

    args = parser.parse_args()

    sensor_type = args.type
    sensor_pin = args.device_pin
    use_mock = args.mock

    print(f"[INFO] Starting server with type={sensor_type}, device-pin={sensor_pin}, mock={use_mock}")
    app.run(host=args.host, port=args.http_port)
