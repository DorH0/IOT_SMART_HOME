#IoT Project
# Relay Button

# relay_button_script.py
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import random

# Default Client ID
DEFAULT_CLIENT_ID = "IOT_client-3164"
broker_ip = "127.0.0.1"
broker_port = 1884
button_topic = 'pr/home/id3164/sts'

class MqttClient:
    def __init__(self):
        # Broker settings
        self.broker = ''
        self.port = ''
        self.client_name = DEFAULT_CLIENT_ID
        self.publish_topic = ''
        self.on_connected_to_form = None
        self.client = None

    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def connect_to(self):
        try:
            # Initialize MQTT client
            self.client = mqtt.Client(client_id=self.client_name, clean_session=True)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_log = self.on_log
            print(f"Connecting to broker {self.broker}:{self.port}")
            self.client.connect(self.broker, int(self.port))
            self.client.loop_start()
        except Exception as e:
            print(f"Connection failed: {e}")

    def disconnect_from(self):
        try:
            if self.client:
                self.client.disconnect()
        except Exception as e:
            print(f"Disconnection failed: {e}")

    def publish_to(self, topic, message):
        if self.client:
            self.client.publish(topic, message)
            print(f"Published to topic '{topic}': {message}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected OK")
            if self.on_connected_to_form:
                self.on_connected_to_form()
        else:
            print(f"Bad connection. Returned code={rc}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected. Result code={rc}")

    def on_log(self, client, userdata, level, buf):
        print(f"log: {buf}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mc = MqttClient()
        self.mc.set_on_connected_to_form(self.on_connected)

        # Broker Connection Section
        self.ip_input = QLineEdit()
        self.ip_input.setInputMask('999.999.999.999')
        self.ip_input.setText(broker_ip)

        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator())
        self.port_input.setMaxLength(4)
        self.port_input.setText(str(broker_port))

        self.client_id_input = QLineEdit()
        self.client_id_input.setText(DEFAULT_CLIENT_ID)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("background-color: gray")
        self.connect_button.clicked.connect(self.on_button_connect_click)

        self.relay_button = QPushButton("Send Message")
        self.relay_button.setStyleSheet("background-color: red")
        self.relay_button.clicked.connect(self.on_relay_button_click)

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Broker IP:", self.ip_input)
        form_layout.addRow("Broker Port:", self.port_input)
        form_layout.addRow("Client ID:", self.client_id_input)
        form_layout.addRow("", self.connect_button)
        form_layout.addRow("Relay Button:", self.relay_button)

        container = QWidget()
        container.setLayout(form_layout)
        self.setCentralWidget(container)
        self.setWindowTitle("MQTT Relay Button")
        self.setGeometry(100, 100, 300, 200)

    def on_connected(self):
        self.connect_button.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        # Validate inputs
        client_id = self.client_id_input.text().strip()
        if not client_id:
            QMessageBox.warning(self, "Error", "Client ID cannot be empty!")
            return

        # Set broker, port, and Client ID
        self.mc.broker = self.ip_input.text()
        self.mc.port = self.port_input.text()
        self.mc.client_name = client_id
        self.mc.connect_to()

    def on_relay_button_click(self):
        # Generate a random kWh value
        random_kwh = round(random.uniform(0.1, 2.0), 2)
        message = f"kWh:{random_kwh}"
        self.mc.publish_to(button_topic, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    app.aboutToQuit.connect(mainwin.mc.disconnect_from)  # Ensure clean disconnection
    sys.exit(app.exec_())