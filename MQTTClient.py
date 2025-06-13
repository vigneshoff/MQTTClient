import os
from paho.mqtt import client as mqtt_client
import logging
import json
import os
from enum import Enum
import ssl
import time
import threading
import queue

from Logger.Logger import Logger

class ConnectionMethod(Enum):
    """
    Methods supported by MQTTClient connection method. Json CONNECTION_METHOD should contain any one Enum value of this class.
    """
    BASIC = 0
    BASIC_WITH_USER_CREDENTIAL = 1
    BASIC_TLS = 2
    BASIC_TLS_WITH_USER_CREDENTIAL = 3
    MTLS = 4
    MTLS_WITH_USER_CRDENTIAL = 5
    THINGSBOARD = 6

class MQTTClient:
    """
    A mqtt client program which supports multiple connection methods.
    Handles reconnection if the connection is broken from the broker (if not externally closed by mqtt_disconnect).
    Provides external callback for on_message (on_message_cb).
    clients_info can be accessed externally.
    connect, disconnect, publish externally.
    _mqtt_json_data holds all the device information.
    _clients_status holds the current client statis (connected/disconnected to the broker).
    """
    def __init__(self, mqtt_json_data):
        self._log = Logger(name="MQTT Client", module_name="MQTTClient", level=logging.INFO)

        self._on_message_cb = None
        self._client_list_connected = {}
        self._client_list_disconnected = {}
        self._clients_status = {}
        self._mqtt_json_data = mqtt_json_data
        devices = mqtt_json_data.get("DEVICE", [])

        self._stop_event = threading.Event()

        self._safe_connect_queue = queue.Queue()
        self._safe_connect_thread = threading.Thread(target=self.__safe_connect)
        self._safe_connect_thread.start()

        self._reconnect_thread = threading.Thread(target=self.__reconnect)
        self._reconnect_thread.start()

        for device in devices:
            if not device.get("STATUS"):
                continue
            self._mqtt_conn = self.__mqtt_connect(device)

        self._log.info("MQTTClient init done...")

    def __mqtt_connect(self, device):
        dev_type = device.get("DEV_TYPE")
        is_server = device.get("IS_SERVER")
        dev_id = device.get("DEV_ID")
        client_id = device.get("CLIENT_ID")
        endpoint = device.get("ENDPOINT")
        port = device.get("PORT")
        connection_method = device.get("CONNECTION_METHOD")
        sub_topic = device.get("SUBSCRIBE_TOPIC")
        pub_topic = device.get("PUBLISH_TOPIC")
        username = device.get("USERNAME")
        password = device.get("PASSWORD")
        certs_dir = device.get("CERT_DIR")
        client_cert = certs_dir + device.get("CLIENT_CERT")
        client_key = certs_dir + device.get("CLIENT_KEY")
        ca_cert = certs_dir + device.get("CA_CERT")
        access_token = device.get("ACCESS_TOKEN")

        client = mqtt_client.Client(client_id=client_id)
        # client = mqtt_client.Client()
        client.connection_flag = False
        client.manual_disconnect = False
        client.is_server = is_server
        client.dev_id = dev_id
        client.dev_type = dev_type
        client.endpoint = endpoint
        client.port = port
        client.sub_topic = sub_topic
        client.pub_topic = pub_topic
        client.on_connect = self.__on_connect
        client.on_message = self.__on_message
        client.on_publish = self.__on_publish
        client.on_disconnect = self.__on_disconnect
        client.on_subscribe = self.__on_subscribe

        # Have all the clients with the status of False in this list. The status will be changed to true once the connection estabilished.
        self._client_list_connected[dev_id] = client
        self._clients_status[dev_id] = "DISCONNECTED"

        # Method 0
        if connection_method == ConnectionMethod.BASIC.value:
            self._log.info("ConnectionMethod is BASIC")
            pass

        # Method 1
        elif connection_method == ConnectionMethod.BASIC_WITH_USER_CREDENTIAL.value:
            self._log.info("ConnectionMethod is BASIC_WITH_USER_CREDENTIAL")
            # The below can be enabled if the server uses 8883 with tls, but not verifying the ca certificate.
            # client.tls_set(cert_reqs=ssl.CERT_NONE)
            # client.tls_insecure_set(True)
            if username and password:
                client.username_pw_set(
                    username=username,
                    password=password
                )
            else:
                self._log.error("ConnectionMethod BASIC_WITH_USER_CREDENTIAL is selected but no usernmae and password is provided")
                client = None
                return None

        # Method 2
        elif connection_method == ConnectionMethod.BASIC_TLS.value:
            self._log.info("ConnectionMethod is BASIC_TLS")
            if ca_cert and os.path.isfile(ca_cert):
                try:
                    client.tls_set(
                        ca_certs=ca_cert,
                        cert_reqs=ssl.CERT_REQUIRED,
                        tls_version=ssl.PROTOCOL_TLSv1_2
                    )
                    client.tls_insecure_set(False)
                except Exception as e:
                    self._log.error(f"{e}")
                    client = None
                    return None
            else:
                self._log.error("ConnectionMethod BASIC_TLS is selected but no ca_cert is provided")
                client = None
                return None

        # Method 3
        elif connection_method == ConnectionMethod.BASIC_TLS_WITH_USER_CREDENTIAL.value:
            self._log.info("ConnectionMethod is BASIC_TLS_WITH_USER_CREDENTIAL")
            if username and password:
                client.username_pw_set(
                    username=username,
                    password=password
                )
            else:
                self._log.error("ConnectionMethod BASIC_WITH_USER_CREDENTIAL is selected but no usernmae and password is provided")
                client = None
                return None

            if ca_cert and os.path.isfile(ca_cert):
                try:
                    client.tls_set(
                        ca_certs=ca_cert,
                        cert_reqs=ssl.CERT_REQUIRED,
                        tls_version=ssl.PROTOCOL_TLSv1_2
                    )
                    client.tls_insecure_set(False)
                except Exception as e:
                    self._log.error(f"{e}")
                    client = None
                    return None
            else:
                self._log.error("ConnectionMethod BASIC_TLS is selected but no ca_cert is provided")
                client = None
                return None

        # Method 4
        elif connection_method == ConnectionMethod.MTLS.value:
            self._log.info("ConnectionMethod is MTLS")
            if ca_cert and client_cert and client_key and os.path.isfile(ca_cert) and os.path.isfile(client_cert) and os.path.isfile(client_key):
                try:
                    client.tls_set(
                        ca_certs=ca_cert,
                        certfile=client_cert,
                        keyfile=client_key
                    )
                except Exception as e:
                    self._log.error(f"{e}")
                    client = None
                    return None
            else:
                self._log.error("ConnectionMethod MTLS is selected but missing certificates")
                client = None
                return None

        # Method 5
        elif connection_method == ConnectionMethod.MTLS_WITH_USER_CRDENTIAL.value:
            self._log.info("ConnectionMethod is MTLS_WITH_USER_CRDENTIAL")
            if username and password:
                client.username_pw_set(
                    username=username,
                    password=password
                )
            else:
                self._log.error("ConnectionMethod BASIC_WITH_USER_CREDENTIAL is selected but no usernmae and password is provided")
                client = None
                return None

            if ca_cert and client_cert and client_key and os.path.isfile(ca_cert):
                try:
                    client.tls_set(
                        ca_certs=ca_cert,
                        certfile=client_cert,
                        keyfile=client_key
                    )
                except Exception as e:
                    self._log.error(f"{e}")
                    client = None
                    return None
            else:
                self._log.error("ConnectionMethod MTLS is selected but missing certificates")
                client = None
                return None

        # Method 6
        elif connection_method == ConnectionMethod.THINGSBOARD.value:
            self._log.info("ConnectionMethod is THINGSBOARD")
            if access_token:
                client.username_pw_set(access_token)
            else:
                self._log.error("ConnectionMethod THINGSBOARD is selected but no access_token is provided")
                client = None
                return None
        else:
            self._log.error("No ConnectionMethod is providec... Exiting")
            return None

        self._safe_connect_queue.put(client)

    def __safe_connect(self):
        """
        Connecting the clients to mqtt brokers from _safe_connect_queue.
        Update _client_list_connected, _client_list_disconnected, _clients_status.
        """
        while not self._stop_event.is_set():
            try:
                client = self._safe_connect_queue.get(timeout=1)
                self._log.info(f"From queue dev_id: {client.dev_id} retrived")
            except queue.Empty:
                time.sleep(3)
                continue
            self._log.info(f"Safe Connecting: Dev ID: {client.dev_id}, Dev Type: {client.dev_type}")
            for attempt in range(0, 3):
                if not self._stop_event.is_set():
                    try:
                        if not client.connection_flag:
                            client.connect(client.endpoint, client.port, keepalive=60)
                            client.loop_start()
                            self._log.info(f"Dev ID: {client.dev_id}, Dev Type: {client.dev_type}, Attempt:{attempt} Success...")
                            self._client_list_connected[client.dev_id] = client
                            self._client_list_disconnected.pop(client.dev_id, None)
                            self._clients_status[client.dev_id] = "CONNECTED"
                            break
                    except Exception as e:
                        self._log.error(f"Dev ID: {client.dev_id}, Dev Type: {client.dev_type}, Attempt:{attempt} Failed... error: {e}")
                        if not self._stop_event.is_set():
                            time.sleep(3)
            else:
                if self._stop_event.is_set():
                    self._log.error(f"stop_event is set, skipping remaining tries for Dev ID: {client.dev_id}, Dev Type: {client.dev_type}")
                self._log.error(f"Dev ID: {client.dev_id}, Dev Type: {client.dev_type}, All Attempts Failed...")
                self._client_list_disconnected[client.dev_id] = client
                self._clients_status[client.dev_id] = "DISCONNECTED"

    def __disconnect(self):
        self._disconnect_thread = threading.Thread(target=self.__disconnect_thread)
        self._disconnect_thread.start()

    def __disconnect_thread(self):
        """
        Disconnect the clients frm _client_list_connected.
        """
        self._log.critical("Disconnecting All clients from MQTT broker...")
        for client in self._client_list_connected.values():
            try:
                client.manual_disconnect = True
                client.connection_flag = False
                # self._client_list_connected[client.dev_id] = client
                client.loop_stop()
                client.disconnect()
            except Exception as error:
                self._log.error(f"Error disconnecting {client.dev_type} client: {error}")

        print("All disconnection done...")
        self._log.critical("All disconnection done...")

    def __reconnect(self):
        """
        Attempt to reconnect the clients in _client_list_disconnected.
        """
        while not self._stop_event.is_set():
            if not self._client_list_disconnected:
                # Check the _client_list_disconnected for every 2 seconds.
                time.sleep(2)
                continue
            for dev_id, client in list(self._client_list_disconnected.items()):
                if not self._stop_event.is_set():
                    self._log.warning(f"Reconnecting to dev_id: {dev_id}")
                    matched_device = next(
                        (device for device in self._mqtt_json_data.get("DEVICE", []) if device.get("DEV_ID") == dev_id),
                        None
                    )
                    if matched_device:
                        if matched_device.get("STATUS"):
                            try:
                                self.__mqtt_connect(matched_device)
                                del self._client_list_disconnected[dev_id]
                            except:
                                self._log.info(f"Reconnection failed dev_id: {dev_id}")
                        else:
                            self._log.warning("matched_device status set to FALSE. Not trying to reconnect")
                    else:
                        self._log.error(f"No matched_device found for dev_id: {dev_id}")

            # Wait for some more time.
            if not self._stop_event.is_set():
                time.sleep(5)

            #TODO !!!. If the device is keep failing. Don't connect it to the broker. Instead send some warning.

    def __on_connect(self, client, userdata, flags, rc):
        """
        On connect subscribe to the topic.
        Update _client_list_connected, _client_list_disconnected, _clients_status.
        """
        if rc == 0:
            self._log.info(f"Dev ID: {client.dev_id}, Dev Type: {client.dev_type}, Connected to MQTT Broker Successfully!")
            client.connection_flag = True
            self._client_list_connected[client.dev_id] = client
            self._client_list_disconnected.pop(client.dev_id, None)
            self._clients_status[client.dev_id] = "CONNECTED"
            self.__subscribe(client)
            self._log.debug(f"__on_connect: rc==0, self._client_list_connected is: {self._client_list_connected}")
            self._log.debug(f"__on_connect: rc==0, self._client_list_disconnected is: {self._client_list_disconnected}")
        else:
            self._log.error(f"Dev ID: {client.dev_id}, Dev Type: {client.dev_type}, Failed to connect to MQTT Broker, return code {rc}")
            client.connection_flag = False
            self._client_list_connected.pop(client.dev_id, None)
            self._client_list_disconnected[client.dev_id] = client
            self._clients_status[client.dev_id] = "DISCONNECTED"
            self._log.debug(f"__on_connect: rc!=0, rc: {rc}, self._client_list_connected is: {self._client_list_connected}")
            self._log.debug(f"__on_connect: rc!=0, rc: {rc}, self._client_list_disconnected is: {self._client_list_disconnected}")

    def __on_message(self, client, userdata, msg):
        """
        If the callback is registered, call it with client and message.
        """
        msg_decoded = msg.payload.decode()
        self._log.debug(f"Message has been received: Device ID: {client.dev_id}, Topic: {client.sub_topic} \n{msg_decoded.replace('\r\n', '\n')}")
        if self._on_message_cb:
            self._on_message_cb(client, msg_decoded)

    def __on_publish(self, client, userdata, mid):
        self._log.debug(f"Message {mid} has been published. Device ID: {client.dev_id}, Topic: {client.pub_topic}")

    def __on_disconnect(self, client, userdata, rc):
        """
        The manually/Externally disconnected clients are not added to _client_list_disconnected for the reconnection.
        Update _client_list_connected, _client_list_disconnected, _clients_status.
        Stop the loop to handle the reconnection manually instead of paho auto reconnection.
        """
        self._log.critical(f"Disconnected... Device ID: {client.dev_id}, Is Manual/External disconnection: {client.manual_disconnect}")
        client.connection_flag = False

        if not self._stop_event.is_set():
            self._client_list_connected.pop(client.dev_id, None)

            if client.manual_disconnect == False:
                # The manually disconnected clients are not added to the _client_list_disconnected for the reconnection.
                self._client_list_disconnected[client.dev_id] = client
            else:
                # Clear the record in _clients_status if the device is manually disconnected (ie, deleted)
                self._clients_status.pop(client.dev_id, None)

            # If paho handles the reconnection, don't use loop_stop()
            client.loop_stop()
            self._log.debug(f"__on_disconnect: self._client_list_connected is: {self._client_list_connected}")
            self._log.debug(f"__on_disconnect: self._client_list_disconnected is: {self._client_list_disconnected}")
        if rc != 0:
            self._log.critical(f"Unexpected disconnection with result code {rc}, attempting to reconnect. Device ID: {client.dev_id}")

    def __on_subscribe(self, client, userdata, mid, granted_qos):
        self._log.info(f"Subscribed to topic with mid: {mid}, granted QoS: {granted_qos}, Device ID: {client.dev_id}, Topic: {client.sub_topic}")

    def __subscribe(self, client):
        if client.sub_topic:
            result, _ = client.subscribe(client.sub_topic)
            if result == mqtt_client.MQTT_ERR_SUCCESS:
                self._log.info(f"Subscribed to topic: {client.sub_topic}")
            else:
                self._log.error(f"Failed to subscribe the topic: {client.sub_topic}")
        else:
            self._log.warning(f"No SUBSCRIBE_TOPIC in client. Check the device information.")

####################################################################################################
#########################                     External Calls               #########################
####################################################################################################
    def on_message_cb (self, cb):
        self._on_message_cb = cb

    def publish(self, dev_id, message):
        """
        dev_id -> string
        message -> string or dictionary
        Called externally with dev_id and message.
        """
        if dev_id in self._client_list_connected:
            client = self._client_list_connected.get(dev_id)
            if client:
                if isinstance(message, str):
                    message_str = message
                else:
                    message_str = json.dumps(message, indent=4)
                result = client.publish(client.pub_topic, message_str)
                if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                    self._log.debug(f"External Message published successfully: Device ID: {dev_id} topic: {client.pub_topic} \n{message_str}")
                else:
                    self._log.error(f"Failed to publish external message:  Device ID: {dev_id} topic: {client.pub_topic} \n{message_str}")
            else:
                self._log.debug(f"No client available for dev_id: {dev_id}")
        else:
            self._log.debug(f"dev_id: {dev_id} is not in _client_list_connected")

    def clients_info(self):
        """
        Return the current client status. Both connected and disconnected.
        """
        return self._clients_status

    def start(self):
        pass

    def stop(self):
        """
        Call __disconnect to disconnect the clients in a thread.
        """
        self._stop_event.set()
        self.__disconnect()

    def mqtt_connect(self, device):
        """
        device -> dictionary
        Called externally to connect the device to the broker if not connected.
        Adds the device information to _mqtt_json_data
        """
        self.__add_device(device)

        dev_id = device.get("DEV_ID")
        matched_device = next(
            (device for device in self._mqtt_json_data.get("DEVICE", []) if device.get("DEV_ID") == dev_id),
            None
        )
        # matched_device_client_info = self._clients_status.get(dev_id)
        is_in_client_list_connected = self._client_list_connected.get(dev_id)
        is_in_client_list_disconnected = self._client_list_disconnected.get(dev_id)

        # The client associated with the dev_id should not be in _client_list_connected.
        # The client associated with the dev_id should not be in _client_list_disconnected too. Because it may be in reconnect state.
        # The device should not be in _mqtt_json_data.
        # Example scenario:
        # Assume if the device status is set to False during init then the _mqtt_json_data will have the device state as False.
        # If the device state is changed during runtime to True
        # The device will be deleted first, so the entry will be removed from _mqtt_json_data. Then it will be added by calling this function)

        # if not matched_device or matched_device_client_info != "CONNECTED":
        if not matched_device or (not is_in_client_list_connected and not is_in_client_list_disconnected):
            if not is_in_client_list_connected and not is_in_client_list_disconnected:
                self._log.info(f"Adding dev_id: {dev_id} to dev _mqtt_json_data")
                self._mqtt_json_data.get("DEVICE").append(device)
                if device.get("STATUS"):
                    self.__mqtt_connect(device)
                else:
                    self._clients_status[dev_id] = "DISCONNECTED"
                    self._log.warning("matched_device status set to FALSE. Not connecting to broker")
            else:
                self._log.critical("CRITICAL ERROR...")
                self._log.critical(f"the device is not in _mqtt_json_data, but it is in either _client_list_connected or _client_list_disconnected")
        else:
            self._log.info(f"dev_id {dev_id} is already exist in _mqtt_json_data, Not doing anything")

    def mqtt_disconnect(self, dev_id):
        """
        dev_id -> string
        Called externally to disconnect the client from the broker if connected.
        Removes the entry from _mqtt_json_data.
        Sets the client.manual_disconnect to avoid reconnecting, as the client is about to disconnected externally.
        """

        # Remove the device from _mqtt_json_data regardless of the device is connected to the broker or not.
        self.__remove_device(dev_id)
        if dev_id in self._client_list_connected:
            self._log.critical(f"Disconnecting request received for client with dev_id: {dev_id} from MQTT broker...")
            client = self._client_list_connected.get(dev_id)
            if client:
                try:
                    client.manual_disconnect = True
                    client.connection_flag = False
                    client.loop_stop()
                    client.disconnect()
                except Exception as error:
                    self._log.error(f"Error disconnecting dev_id: {dev_id}, type: {client.dev_type} error: {error}")
            else:
                self._log.warning(f"The client object is None for dev_id: {dev_id}")
        else:
            self._log.warning(f"dev_id: {dev_id} is not in _client_list_connected. Not disconnecting...")

    def __remove_device(self, dev_id):
        """
        Remove the device from _mqtt_json_data when called externally by mqtt_disconnect.
        Assume in runtime, the device info is deleted from the actual json file. (Maybe by some other modules).
        """
        devices = self._mqtt_json_data.get("DEVICE", [])
        for i, device in enumerate(devices):
            if device.get("DEV_ID") == dev_id:
                devices.pop(i)
                self._log.warning(f"Removed the device with dev_id: {dev_id} from _mqtt_json_data")
                break
        else:
            self._log.warning("dev_id is not in _mqtt_json_data, not removing")

    def __add_device(self, device_to_add):
        """
        Add or update the device info in _mqtt_json_data.
        Called externally by mqtt_connect during runtime.
        Assume in runtime, the device info is alredy stored in the actual json file. (Maybe by some other modules).
        """
        dev_id = device_to_add.get("DEV_ID", None)
        if dev_id is None:
            self._log.warning(f"device_to_add does not contain DEV_ID. dev_id: {dev_id}. Skipping.")
            return

        devices = self._mqtt_json_data.get("DEVICE", [])
        # Overwrite the device if existed. Else add.
        for i, device in enumerate(devices):
            if device.get("DEV_ID") == dev_id:
                devices[i] = device_to_add
                self._log.info(f"dev_id: {dev_id} is already present in _mqtt_json_data. Overwriting the device info")
                return
        devices.append(device_to_add)
        self._log.info(f"dev_id: {dev_id} is not present in _mqtt_json_data. Added as new device")
