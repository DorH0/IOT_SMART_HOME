# IoT Project
# Publisher

import paho.mqtt.client as mqtt
import random
import time

# Broker settings
broker = "127.0.0.1"
port = 1884
topic = "pr/home/id3164/sts"
command_topic = "pr/home/id3164/cmd"

# Creating a unique Client ID
client_id = f"Publisher-{random.randint(1000, 9999)}"

# Initialize MQTT client with the latest callback API version
client = mqtt.Client(client_id=client_id, clean_session=False)

# Define callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to broker")
        client.subscribe(command_topic)  # Subscribe to command topic
    else:
        print(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected from broker, result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with MID {mid}")

def on_message(client, userdata, msg):
    global selected_appliance
    payload = msg.payload.decode("utf-8")
    print(f"Command received: {payload}")
    selected_appliance = payload.lower()  # Update the selected appliance

# Assign callbacks
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_message = on_message

# Connect to the broker
try:
    print(f"Connecting to broker {broker}:{port}")
    client.connect(broker, port)
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Start the loop
client.loop_start()

# Global variable to store the selected appliance
selected_appliance = None

# Continuous publishing loop
try:
    while True:
        if selected_appliance:
            # Generate random kWh reading for the selected appliance
            reading = round(random.uniform(0.1, 2.0), 2)  # Random kWh reading
            message = f"{selected_appliance}:{reading}"
            # Publish the message
            print(f"Publishing: {message}")
            client.publish(topic, message, qos=2, retain=True)
        # Wait for 5 seconds before the next publication
        time.sleep(5)
except KeyboardInterrupt:
    print("Publisher stopped by user.")
except Exception as e:
    print(f"Error during publishing: {e}")

# Disconnect after publishing
client.disconnect()
client.loop_stop()