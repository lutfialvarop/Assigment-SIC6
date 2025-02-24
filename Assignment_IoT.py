import network
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, ADC
from time import sleep
import dht
import utime as time
import urequests as requests

ldr = ADC(Pin(32))
ldr.atten(ADC.ATTN_11DB)

led = Pin(19, Pin.OUT)
d = dht.DHT11(Pin(15))

button = Pin(18, Pin.IN, Pin.PULL_UP)
ledStatus = 0

USERNAME_WIFI="Ara"
PASSWORD_WIFI="narasan1"

DEVICE_ID = "esp32-uni159"
TOKEN = "BBUS-6L3O4cSRsFqpUEW4e5dJNVxCyiOwJa"
TOPIC_SUBSCRIBE = "/v1.6/devices/esp32-uni159/led_1/lv"
ENDPOINT = "http://192.168.1.79:8000/"

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(USERNAME_WIFI, PASSWORD_WIFI)
while not sta_if.isconnected():
  print(".", end="")
  sleep(0.1)
print(" Connected!")

def on_message(topic, msg):
    if topic == TOPIC_SUBSCRIBE.encode():
        if msg.decode() == "1.0":
            print("on")
            led.on()
            ledStatus = 1
            print("LED is ON")
        elif msg.decode() == "0.0":
            print("off")
            led.off()
            ledStatus = 0
            print("LED is OFF")

print("Connecting to MQTT server... ", end="")
client = MQTTClient("clientID", "industrial.api.ubidots.com", 1883, user=TOKEN, password="")
client.set_callback(on_message)
client.connect()
client.subscribe(TOPIC_SUBSCRIBE)
print("Connected!")

def send_data(temperature, humidity, light, ledStatuss):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "ldr_value": light,
        "led_1": ledStatuss,
    }
    response = requests.post(url, json=data, headers=headers)
    print("Done Sending Data!")
    print("Response:", response.text)

def send_data_to_flask(temperature, humidity, light, ledStatuss):
    url = ENDPOINT + "esp32/data"
    headers = {"Content-Type": "application/json"}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "ldr_value": light,
        "led_1": ledStatuss,
    }
    response = requests.post(url, json=data, headers=headers)
    print("Sent to Flask:", response.text)

while True:
    d.measure()
    
    client.check_msg()
    
    if button.value() == 0:
        if ledStatus == 0:
            led.on()
            ledStatus = 1
            print("LED is ON")
        elif ledStatus == 1:
            led.off()
            ledStatus = 0
            print("LED is OFF")
    
    
    send_data_to_flask(d.temperature(), d.humidity(), ldr.read(), ledStatus)
    send_data(d.temperature(), d.humidity(), ldr.read(), ledStatus)
    
    time.sleep(0.01)