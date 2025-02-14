# IoT Project
# ID 3164XXXXX

# main_gui.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import paho.mqtt.client as mqtt

# MQTT Client Class
class MqttClient:
    def __init__(self):
        # Broker settings
        self.broker = '127.0.0.1'
        self.port = 1884
        self.client_name = "pr/home/id3164/sts"
        self.username = ''
        self.password = ''
        self.subscribe_topic = ''
        self.publish_topic = ''
        self.on_connected_to_form = None
        self.client = None

    def connect_to(self):
        try:
            if self.client:  # Check if already connected
                print("Already connected to broker.")
                return
            # Initialize MQTT client
            self.client = mqtt.Client(client_id=self.client_name, clean_session=True)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            print(f"Connecting to broker {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
        except Exception as e:
            print(f"Connection failed: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected OK")
            if self.on_connected_to_form:
                self.on_connected_to_form()
        else:
            print(f"Bad connection. Returned code={rc}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(f"Message received: {payload}")
        main_window.update_subscriber_data(payload)

    def disconnect_from(self):
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                self.client = None  # Reset the client object
                print("Disconnected from broker.")
            except Exception as e:
                print(f"Disconnection failed: {e}")
        else:
            print("No active connection to disconnect.")

    def subscribe_to(self, topic):
        if self.client:
            try:
                self.client.subscribe(topic, qos=2)
                print(f"Subscribed to {topic}")
            except Exception as e:
                print(f"Subscription failed: {e}")
        else:
            print("Cannot subscribe. MQTT client is not initialized.")

    def publish_to(self, topic, message):
        if self.client:
            try:
                self.client.publish(topic, message)
                print(f"Published to {topic}: {message}")
            except Exception as e:
                print(f"Publishing failed: {e}")
        else:
            print("Cannot publish. MQTT client is not initialized.")


# Main GUI Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Electric Current Reading")
        self.setGeometry(100, 100, 800, 600)

        # MQTT Client
        self.mqtt_client = MqttClient()

        # Broker Connection Section
        self.ip_input = QLineEdit()
        self.ip_input.setInputMask('000.000.000.000')  # Only integers allowed
        self.ip_input.setText("127.0.0.1")
        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator())  # Only integers allowed
        self.port_input.setMaxLength(5)
        self.port_input.setText("1884")
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_broker)

        # Disconnect Button
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_from_broker)

        # Left Side: Appliance Selection and Estimated Usage
        self.appliance_combo = QComboBox()
        self.appliance_combo.addItems(["Oven", "Kettle", "Refrigerator", "Washing Machine"])
        self.estimated_usage = QLineEdit("00.00")
        self.estimated_usage.setValidator(QDoubleValidator(0.0, 999.99, 2))  # Float/Double only
        self.estimated_usage.setMaxLength(6)

        # Publish Button
        self.publish_button = QPushButton("Publish Selected Appliance")
        self.publish_button.clicked.connect(self.publish_selected_appliance)

        # Right Side: Subscriber Data
        self.subscriber_topic = QLineEdit("pr/home/id3164/sts")
        self.subscriber_data = QTextEdit()
        self.subscribe_button = QPushButton("Subscribe")
        self.subscribe_button.clicked.connect(self.subscribe_to_topic)

        # Layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Select Appliance:"))
        left_layout.addWidget(self.appliance_combo)
        left_layout.addWidget(QLabel("Estimated Usage (kWh):"))
        left_layout.addWidget(self.estimated_usage)
        left_layout.addWidget(self.publish_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Subscriber Topic:"))
        right_layout.addWidget(self.subscriber_topic)
        right_layout.addWidget(self.subscribe_button)
        right_layout.addWidget(QLabel("Subscriber Data:"))
        right_layout.addWidget(self.subscriber_data)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        top_layout = QVBoxLayout()
        top_layout.addWidget(QLabel("Broker IP:"))
        top_layout.addWidget(self.ip_input)
        top_layout.addWidget(QLabel("Broker Port:"))
        top_layout.addWidget(self.port_input)
        top_layout.addWidget(self.connect_button)
        top_layout.addWidget(self.disconnect_button)  # Add Disconnect Button

        container_layout = QVBoxLayout()
        container_layout.addLayout(top_layout)
        container_layout.addLayout(main_layout)

        container = QWidget()
        container.setLayout(container_layout)
        self.setCentralWidget(container)

    def connect_to_broker(self):
        # Validate inputs
        broker_ip = self.ip_input.text().strip()
        broker_port = self.port_input.text().strip()
        if not broker_ip or not broker_port:
            QMessageBox.warning(self, "Error", "Broker IP and Port cannot be empty!")
            return

        # Set broker and port
        self.mqtt_client.broker = broker_ip
        self.mqtt_client.port = int(broker_port)
        self.mqtt_client.connect_to()

    def disconnect_from_broker(self):
        self.mqtt_client.disconnect_from()

    def subscribe_to_topic(self):
        topic = self.subscriber_topic.text().strip()
        if not topic:
            QMessageBox.warning(self, "Error", "Subscriber Topic cannot be empty!")
            return

        # Subscribe to the topic
        self.mqtt_client.subscribe_to(topic)

    def update_subscriber_data(self, message):
        self.subscriber_data.append(message)

    def publish_selected_appliance(self):
        selected_appliance = self.appliance_combo.currentText().lower()  # Get selected appliance
        if not selected_appliance:
            QMessageBox.warning(self, "Error", "No appliance selected!")
            return

        # Publish the selected appliance to the Publisher
        command_topic = "pr/home/id3164/cmd"
        self.mqtt_client.publish_to(command_topic, selected_appliance)


# Run Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # Ensure clean disconnection
    def clean_disconnect():
        if main_window.mqtt_client.client:
            main_window.mqtt_client.disconnect_from()

    app.aboutToQuit.connect(clean_disconnect)  # Call disconnect safely
    sys.exit(app.exec_())
