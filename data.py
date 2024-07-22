import pymongo
import datetime
import time
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
from datetime import datetime

broker = "broker.hivemq.com"
port = 1883
topik = "kualitas/sensor"
url = "mongodb+srv://Reygan:ilham@data.p6svddp.mongodb.net/?retryWrites=true&w=majority&appName=Data" 
mongo_client = MongoClient(url)
db = mongo_client["clara"]
collection = db["data"]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topik)

def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode()
        print(f"Message received: {message}")
        data = json.loads(message)
        data["timestamp"] = datetime.now()
        
        if "suhu" in data and "kelembaban" in data and "udara" in data:
            collection.insert_one(data)
            print("Data terkirim ke MongoDB")
        else:
            print("Kata Clara ERROR")

    except json.JSONDecodeError:
        print("JSON ERROR")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(1)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 60)
client.loop_forever()