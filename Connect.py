# IoT Project
# Connect Button

# connect_button
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
        self.subscribe_topic = ''
        self.on_connected_to_form = None
        self.on_disconnected_from_form = None  # New callback for disconnection
        self.client = None

    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def set_on_disconnected_from_form(self, on_disconnected_from_form):
        self.on_disconnected_from_form = on_disconnected_from_form

    def connect_to(self):
         try:
            # Check if the client is already connected
            if self.client and self.client.is_connected():
                print("Client is already connected. Skipping reconnection.")
                return

            # Initialize MQTT client only if it hasn't been created yet
            if not self.client:
                self.client = mqtt.Client(client_id=self.client_name, clean_session=True)
                self.client.on_connect = self.on_connect
                self.client.on_disconnect = self.on_disconnect
                self.client.on_message = self.on_message

            # Attempt to connect to the broker
            print(f"Connecting to broker {self.broker}:{self.port}")
            self.client.connect(self.broker, int(self.port))
            self.client.loop_start()
         except Exception as e:
             print(f"Connection failed: {e}")

    def disconnect_from(self):
          try:
              if self.client:
                  self.client.loop_stop()  # Stop the loop to prevent further callbacks
                  self.client.disconnect()
                  self.client = None  # Reset the client to allow reinitialization
                  print("Disconnected from broker.")
          except Exception as e:
              print(f"Disconnection failed: {e}")

    def subscribe_to(self, topic):
        if self.client:
            self.client.subscribe(topic)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected OK")
            if self.on_connected_to_form:
                self.on_connected_to_form()
        else:
            print(f"Bad connection. Returned code={rc}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected. Result code={rc}")
        if self.on_disconnected_from_form:
            self.on_disconnected_from_form()  # Trigger disconnection callback

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8", "ignore")
        print(f"Message received from topic {topic}: {payload}")
        mainwin.update_status_label("Message Received")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mc = MqttClient()
        self.mc.set_on_connected_to_form(self.on_connected)
        self.mc.set_on_disconnected_from_form(self.on_disconnected)  # Set disconnection callback

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

        # Replace the unpressable button with a QLabel
        self.status_label = QLabel("Not Connected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Broker IP:", self.ip_input)
        form_layout.addRow("Broker Port:", self.port_input)
        form_layout.addRow("Client ID:", self.client_id_input)
        form_layout.addRow("", self.connect_button)
        form_layout.addRow("Status:", self.status_label)

        container = QWidget()
        container.setLayout(form_layout)
        self.setCentralWidget(container)
        self.setWindowTitle("MQTT Connect Button")
        self.setGeometry(100, 100, 300, 200)

    def on_connected(self):
        self.connect_button.setStyleSheet("background-color: green")
        self.update_status_label("Connected")

    def on_disconnected(self):
        self.connect_button.setStyleSheet("background-color: gray")
        self.update_status_label("Not Connected")

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
        self.mc.subscribe_to(button_topic)

    def update_status_label(self, status):
        if status == "Connected":
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status == "Message Received":
            self.status_label.setText("Message Received")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.status_label.setText("Not Connected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    app.aboutToQuit.connect(mainwin.mc.disconnect_from)  # Ensure clean disconnection
    sys.exit(app.exec_())
