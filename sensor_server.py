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
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dht_device.humidity

        return {
            "temperature_celsius": temperature_c,
            "temperature_fahrenheit": temperature_f,
            "humidity": humidity
        }

    except RuntimeError as error:
        error_msg = str(error)
        if "Checksum did not validate" in error_msg:
            return {
                "temperature_celsius": -80,
                "temperature_fahrenheit": -80,
                "humidity": -80
            }
        return {"error": error_msg}

    except Exception as error:
        return {"error": "Unexpected error: " + str(error)}



# Real sensor reading function for CCS811 (placeholder)
def read_ccs811_data(pin):
    return {"error": "Real CCS811 reading not implemented"}

# Global sensor config
sensor_type = None
sensor_pin = None
use_mock = True

@app.route('/sensor/data', methods=['GET'])
def get_sensor_data():
    if use_mock:
        if sensor_type == "CCS":
            data = generate_mock_ccs811_data()
        elif sensor_type == "DHT":
            data = generate_mock_dht11_data()
        else:
            return jsonify({"error": "Unknown sensor type"}), 400
    else:
        if sensor_type == "DHT":
            data = read_dht11_data(sensor_pin)
        elif sensor_type == "CCS":
            data = read_ccs811_data(sensor_pin)
        else:
            return jsonify({"error": "Unknown sensor type"}), 400

    return jsonify({
        "type": sensor_type,
        "device-pin": sensor_pin,
        "data": data
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sensor REST API')
    parser.add_argument('--type', required=True, choices=['DHT', 'CCS'], help='Sensor type (DHT or CCS)')
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
