import os
from paho.mqtt import client as mqtt_client
import logging
import json
import time
from enum import Enum
import ssl

from Logger.Logger import Logger

class Security(Enum):
    NO_SECURITY = 0
    IOT_CORE = 1
    USER_NAME_PASS = 2


class MQTTClient():
    def __init__(self, mqtt_data, with_secure=0):
        self._log = Logger(name="MQTT Client", module_name="MQTTClient", level=logging.INFO)

        self._with_secure = with_secure

        self._mqtt_info = mqtt_data["INFO"]
        self._dev_id = self._mqtt_info["DEV_ID"]
        self._client_id = self._mqtt_info["CLIENT_ID"]
        self._endpoint = self._mqtt_info["ENDPOINT"]
        self._port = self._mqtt_info["PORT"]
        self._sub_topic = self._mqtt_info["SUBSCRIBE_TOPIC"]
        self._pub_topic = self._mqtt_info["PUBLISH_TOPIC"]
        if self._with_secure == Security.IOT_CORE:
            self._certs_dir = self._mqtt_info["CERT_DIR"]
            self._certfile = self._certs_dir + self._mqtt_info["CERTFILE"]
            self._keyfile = self._certs_dir + self._mqtt_info["KEYFILE"]
            self._cacerts = self._certs_dir + self._mqtt_info["CACERTS"]
            self._username = self._password = ""
        elif self._with_secure == Security.USER_NAME_PASS:
            self._username = self._mqtt_info["USERNAME"]
            self._password = self._mqtt_info["PASSWORD"]
            self._certfile = self._keyfile = self._cacerts = self._certs_dir = ""
        else:
            self._certfile = self._keyfile = self._cacerts = self._certs_dir = ""
            self._username = self._password = ""

        self._log.info(f"DEV_ID={self._dev_id}, CLIENT_ID={self._client_id} \
            ENDPOINT={self._endpoint}, PORT={self._port} \
            SUBSCRIBE_TOPIC={self._sub_topic}, PUBLISH_TOPIC={self._pub_topic} \
            CERTFILE={self._certfile}, KEYFILE={self._keyfile} \
            CACERTS={self._cacerts}, CERTS_DIR={self._certs_dir}")

        if self._with_secure == Security.IOT_CORE:
            self.__validate_certs()

        self._mqtt_conn = self.__mqtt_connect()

        self._log.info("MQTTClient Started...")
        print("MQTTClient Started...")


    def __mqtt_connect(self):
        self._client = mqtt_client.Client(client_id=self._client_id)
        # client = mqtt_client.Client()
        if self._with_secure == Security.IOT_CORE:
            self._client.tls_set(
                ca_certs=self._cacerts,
                certfile=self._certfile,
                keyfile=self._keyfile
            )
        elif self._with_secure == Security.USER_NAME_PASS:
            self._client.tls_set(cert_reqs=ssl.CERT_NONE)
            self._client.username_pw_set(
                username=self._username,
                password=self._password
            )

        self._client.on_connect = self.__on_connect
        self._client.on_message = self.__on_message
        self._client.on_publish = self.__on_publish
        self._client.on_disconnect = self.__on_disconnect
        self._client.on_subscribe = self.__on_subscribe

        try:
            self._client.connect(self._endpoint, self._port, keepalive=60)
            self._client.loop_start()
            return self._client
        except Exception as e:
            self._log.error(f"Failed to connect to MQTT Broker: {e}")
            exit(1)


    def __reconnect(self):
        # while True:
        #     try:
        #         time.sleep(5)
        #         self._log.warning("Attempting to reconnect...")
        #         self.__mqtt_connect()
        #         break
        #     except Exception as e:
        #         self._log.error(f"Reconnection failed: {e}")
        #         time.sleep(5)

        #TODO!!!
        pass


    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._log.info("Connected to MQTT Broker Successfully!")
            self.subscribe(self._sub_topic)
        else:
            self._log.error(f"Failed to connect to MQTT Broker, return code {rc}")


    def __on_message(self, client, userdata, msg):
        self._log.info(f"Received message on {msg.topic}:\n{msg.payload.decode()}")


    def __on_publish(self, client, userdata, mid):
        self._log.info(f"Message {mid} has been published.")


    def __on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self._log.warning(f"Unexpected disconnection with result code {rc}, attempting to reconnect")
            self.__reconnect()


    def __on_subscribe(self, client, userdata, mid, granted_qos):
        self._log.info(f"Subscribed to topic with mid: {mid}, granted QoS: {granted_qos}")


    def publish(self, message):
        message_str = json.dumps(message, indent=4)
        result = self._mqtt_conn.publish(self._pub_topic, message_str)
        if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
            self._log.info(f"Message published successfully: {message_str}")
        else:
            self._log.error("Failed to publish message")


    def subscribe(self, topic):
        self._mqtt_conn.subscribe(topic)
        self._log.info(f"Subscribed to topic: {topic}")


    def __validate_certs(self):
        for cert_path, cert_name in [
            (self._certfile, "Device Certificate"),
            (self._keyfile, "Private Key"),
            (self._cacerts, "Root CA 1")
        ]:
            if not os.path.exists(cert_path):
                self._log.error(f"{cert_name} is not in {cert_path}")
                exit(1)


class JSONPublishData():
    def __init__ (self, mqtt_data):
        self._publish_data = mqtt_data["PUBLISH"]

        self._options = list(self._publish_data.keys())
        for i, key in enumerate(self._options, start=1):
            print(f"{i}. {key}")


    def get_message(self, choice):
        if 1 <= choice <= len(self._options):
            key = self._options[choice - 1]
            return {key: self._publish_data[key]}
        else:
            print("Invalid choice!")
            return None


if __name__ == '__main__':
    try:
        with open('mqtt.json', 'r') as file:
            mqtt_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error Loading config file: {e}")
        exit(1)

    mqttclient = MQTTClient(mqtt_data, with_secure=Security.USER_NAME_PASS)

    json_publish = JSONPublishData(mqtt_data)

    while True:
        try:
            choice = input("\nEnter The Option To Publish: ")
            if choice.lower() == 'q':
                print("Exiting...")
                break

            choice = int(choice)
            message = json_publish.get_message(choice)
            if message:
                print(f"message: {message}")
                mqttclient.publish(message)
            time.sleep(1)

        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nInterrupted! Exiting...")
            break
