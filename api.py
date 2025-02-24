from flask import Flask, request, jsonify, make_response
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import json_util
import json

app = Flask(__name__)

uri = "mongodb+srv://admin:admin@sic6.55wav.mongodb.net/?retryWrites=true&w=majority&appName=SIC6"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["esp32_db"]
collection = db["sensor_data"]

# Status LED
led_status = {"led_1": 0}

# Endpoint untuk menerima data dari ESP32
@app.route('/esp32/data', methods=['POST'])
def receive_data():
    data = request.json
    collection.insert_one(data)  # Simpan ke MongoDB
    load_data = json.loads(json_util.dumps(data))
    return make_response(jsonify({"message": "Data received", "data": load_data}), 201)

# Endpoint untuk mendapatkan status LED
@app.route('/esp32/led', methods=['GET'])
def get_led_status():
    return make_response(jsonify(led_status), 200)

# Endpoint untuk mendapatkan semua data dari MongoDB
@app.route('/esp32/data', methods=['GET'])
def get_all_data():
    data = list(collection.find({}, {"_id": 0}))
    return make_response(jsonify(data), 200)

# Endpoint untuk mengontrol LED
@app.route('/esp32/led', methods=['POST'])
def control_led():
    global led_status
    data = request.json
    if "led_1" in data:
        led_status["led_1"] = data["led_1"]
        return make_response(jsonify({"message": "LED updated", "led_1": led_status["led_1"]}), 201)
    return make_response(jsonify({"error": "Invalid request"}), 400)

if __name__ == '__main__':
    app.run(host="192.168.1.79", port=8000, debug=True)