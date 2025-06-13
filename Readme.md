# MQTTClient

This module provides an MQTT client application that connects to MQTT brokers.


# Simple test method, just fill the json and start the MQTTClient.
mqtt.json
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_0",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_0",
            "ENDPOINT": "localhost",
            "PORT": 1883,
            "CONNECTION_METHOD": 0,
            "PUBLISH_TOPIC": "DEV/DEV_0/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_0/TO",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "",
            "CA_CERT": "",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```

main.py

```python
import json
from MQTTClient import MQTTClient

if __name__ == '__main__':
    try:
        with open ("mqtt.json", 'r') as conf_file:
            json_data = json.load(conf_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        json_data = {}

    mqtt_client = MQTTClient(json_data)

    while True:
        choice = input("\nEnter q to exit...: ")
        if choice.lower() == 'q':
            print("Exiting...")
            mqtt_client.stop()
            break
```

```shell
# python3 main.py
symlink created .\MQTTClient\Logs\2025-06-13\MQTTClient\19.27.06.log .\MQTTClient\Logs\2025-06-13\MQTTClient\log.log

Enter q to exit...: q
Exiting...
All disconnection done...
```

## Notes:
The logs will be stored in Logs directory.

To enable the detailed log, init the Logger with DEBUG in MQTTClient.py

```self._log = Logger(name="MQTT Client", module_name="MQTTClient", level=logging.DEBUG)```

#
#
#
# Explanation:

### Supported methods:
*  **Code - Method**
* **0 - No security**
* **1 - With only Username and Password**
* **2 - Basic TLS**
* **3 - Basic TLS with Username and Password**
* **4 - Mutual TLS (mTLS)**
* **5 - mTLS with Username and Password**
* **6 - Thingsboard**

### Features:
- Supports JSON payloads and custom messages
- Supports Publish and Subscribe
- Automatic Reconnection
- Support external on_message callback
- Support external connect, disconnect, publish and provides client status
- Logs

## Initializing the Module
Keep all the information in the `MQTTClient.json` and init the MQTTClient class. All the operations are handled automatically. Refer MQTTTest.py for overview.

### Example `MQTTClient.json`
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "",
            "IS_SERVER": ,
            "DEV_ID": "",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "",
            "ENDPOINT": "",
            "PORT": ,
            "CONNECTION_METHOD": ,
            "PUBLISH_TOPIC": "",
            "SUBSCRIBE_TOPIC": "",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "",
            "CA_CERT": "",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```

### JSON Explanation:
- **DEV_TYPE**
    *   Type: String (DEV, SERVER)
    *   Priority: High
    *   Ex: IOT_DEV, IOT_SERVER, TEMP_SENSOR
    *   Helps to identify  the client type and handle the incoming / outgoing messages.
- **IS_SERVER**
    *   Type: Boolean (true / false)
    *   Priority: Low
    *   Helps to find the client is device / server. To forward the messages between server & client.
- **DEV_ID**
    *   Type: String (DEV_01)
    *   Priority: High
    *   Must for the internal handling.
- **MAPPED_TO_DEV_OR_SERVER**
    *   Type: String (DEV_02)
    *   Priority: Low
    *   Helps to find the client is for device or server. To forward the messages between server & client.
- **CLIENT_ID**
    *   Type: String (TEST_CLIENT_DEV_01)
    *   Priority: High
    *   Must for the internal handling.
- **ENDPOINT**
    *   Type: String (localhost, test.mosquitto.org)
    *   Priority: High
    *   Broker address
- **PORT**
    *   Type: Integer (1883, 8883)
    *   Priority: High
    *   Port
- **CONNECTION_METHOD**
    *   Type: Integer (0-6)
    *   Priority: High
    *   The connection method from (Supported methods code)
- **PUBLISH_TOPIC**
    *   Type: String (DEV/DEV_0/FROM)
    *   Priority: High
    *   Publish topic for the mqtt messages to the broker.
- **SUBSCRIBE_TOPIC**
    *   Type: String (DEV/DEV_0/TO)
    *   Priority: High
    *   Subscribe topic to receive message from the broker.
- **USERNAME**
    *   Type: String (vignesh)
    *   Priority: High
    *   Credentials for the connection if enabled in the broker.
- **PASSWORD**
    *   Type: String (vignesh)
    *   Priority: High
    *   Credentials for the connection if enabled in the broker.
- **CERT_DIR**
    *   Type: String (./certs/)
    *   Priority: High
    *   Location where the certificates are kept.
- **CA_CERT**
    *   Type: String (ca.crt)
    *   Priority: High
    *   CA certificate.
- **CLIENT_CERT**
    *   Type: String (client.crt)
    *   Priority: High
    *   Client certificate.
- **CLIENT_KEY**
    *   Type: String (client.key)
    *   Priority: High
    *   Client private key.
- **ACCESS_TOKEN**
    *   Type: String (xhdfndfdhcne)
    *   Priority: High
    *   Thingsboard access token.
- **STATUS**
    *   Type: Boolean (true / false)
    *   Priority: High
    *   If the status must be true to connect to the broker.

## Example `MQTTClient.json` for Method 0 - No security
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_0",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_0",
            "ENDPOINT": "localhost",
            "PORT": 1883,
            "CONNECTION_METHOD": 0,
            "PUBLISH_TOPIC": "DEV/DEV_0/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_0/TO",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "",
            "CA_CERT": "",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```
## Example `MQTTClient.json` for Method 1 - With only Username and Password
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_1",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_1",
            "ENDPOINT": "localhost",
            "PORT": 1883,
            "CONNECTION_METHOD": 1,
            "PUBLISH_TOPIC": "DEV/DEV_1/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_1/TO",
            "USERNAME": "vignesh",
            "PASSWORD": "password",
            "CERT_DIR": "",
            "CA_CERT": "",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```
## Example `MQTTClient.json` for Method 2 - Basic TLS
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_2",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_2",
            "ENDPOINT": "localhost",
            "PORT": 8883,
            "CONNECTION_METHOD": 2,
            "PUBLISH_TOPIC": "DEV/DEV_2/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_2/TO",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "./certs/",
            "CA_CERT": "ca.crt",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```
## Example `MQTTClient.json` for Method 3 - Basic TLS with Username and Password
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_3",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_3",
            "ENDPOINT": "localhost",
            "PORT": 8883,
            "CONNECTION_METHOD": 3,
            "PUBLISH_TOPIC": "DEV/DEV_3/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_3/TO",
            "USERNAME": "vignesh",
            "PASSWORD": "password",
            "CERT_DIR": "./certs/",
            "CA_CERT": "ca.crt",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": false
        }
    ]
}
```
## Example `MQTTClient.json` for Method 4 - Mutual TLS (mTLS)
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_4",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_4",
            "ENDPOINT": "localhost",
            "PORT": 8883,
            "CONNECTION_METHOD": 4,
            "PUBLISH_TOPIC": "DEV/DEV_4/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_4/TO",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "./certs/",
            "CA_CERT": "ca.crt",
            "CLIENT_CERT": "client.crt",
            "CLIENT_KEY": "client.key",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```
## Example `MQTTClient.json` for Method 5 - Mutual TLS (mTLS) with Username and Password
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_5",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_5",
            "ENDPOINT": "localhost",
            "PORT": 8883,
            "CONNECTION_METHOD": 5,
            "PUBLISH_TOPIC": "DEV/DEV_5/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_5/TO",
            "USERNAME": "vignesh",
            "PASSWORD": "password",
            "CERT_DIR": "./certs/",
            "CA_CERT": "ca.crt",
            "CLIENT_CERT": "client.crt",
            "CLIENT_KEY": "client.key",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ]
}
```
## Example `MQTTClient.json` for Method 6 - Thingsboard
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV_TB",
            "IS_SERVER": false,
            "DEV_ID": "DEV_6",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_6",
            "ENDPOINT": "thingsboard.cloud",
            "PORT": 1883,
            "CONNECTION_METHOD": 6,
            "PUBLISH_TOPIC": "v1/devices/me/telemetry",
            "SUBSCRIBE_TOPIC": "DEV/DEV_6/TO",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "",
            "CA_CERT": "",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "REdfddfdfVEddfdfy7hd",
            "STATUS": true
        }
    ]
}
```
#
#
#
# Example with publish:
### Example `MQTTClient.json` for Method 0 - No security
```json
{
    "DEVICE": [
        {
            "DEV_TYPE": "DEV",
            "IS_SERVER": false,
            "DEV_ID": "DEV_0",
            "MAPPED_TO_DEV_OR_SERVER": "",
            "CLIENT_ID": "TEST_CLIENT_DEV_0",
            "ENDPOINT": "localhost",
            "PORT": 1883,
            "CONNECTION_METHOD": 0,
            "PUBLISH_TOPIC": "DEV/DEV_0/FROM",
            "SUBSCRIBE_TOPIC": "DEV/DEV_0/TO",
            "USERNAME": "",
            "PASSWORD": "",
            "CERT_DIR": "",
            "CA_CERT": "",
            "CLIENT_CERT": "",
            "CLIENT_KEY": "",
            "ACCESS_TOKEN": "",
            "STATUS": true
        }
    ],
    "PUBLISH": {
        "VEHILCLE_INFO": {
            "REG_NO": 1234,
            "ENGINE_NO": 9876
        },
        "LOCATION": {
            "LAT": 123.4,
            "LONG": 567.8
        },
        "Temperature": 34
    }
}
```
The payloads inside "PUBLISH" shall be published to the connected device's publish topic.



### Sample Output - get the connected devices:
Lets try to connect two mqtt brokers. One listening on port 1883 (Basic method) and another on port 8883 (mTLS, Username and Password).

In the attached `MQTTClient.json` DEV_0 and DEV_5.

```shell
# python3 MQTTTest.py
symlink created .\MQTTClient\Logs\2025-06-13\MQTTClient\19.27.06.log .\MQTTClient\Logs\2025-06-13\MQTTClient\log.log

Enter m for options, q to Exit: m
Help menu
m -> menu
q -> exit
g -> get the client details
p -> enter into publish mode
a -> add / connect new device
d -> delete / disconnect the device


Enter m for options, q to Exit: g

device details:
dev_id          Status
DEV_0           CONNECTED
DEV_5           CONNECTED

Enter m for options, q to Exit: q

Exiting...
All disconnection done...
```

### Sample Output - Sending LOCATION to DEV_0
The `PUBLISH` node in the JSON configuration allows publishing various data without altering the code. The dev_id and message_id will be displayed in the console. Select an option to publish the corresponding data to the `PUBLISH_TOPIC`.

ex: DEV_0 1
```shell
Enter m for options, q to Exit: p

device details:
dev_id          Status
DEV_0           CONNECTED
DEV_5           CONNECTED


Available messages:
message_id      Description
0               VEHILCLE_INFO
1               LOCATION
2               Temperature


For custom messages Enter dev_id with c
Enter dev_id message_id: DEV_0 1

msg_to_publish: {'LOCATION': {'LAT': 123.4, 'LONG': 567.8}}
```

### Sample Output - Sending custom message to DEV_5
ex: DEV_5 c

Then enter the message, once entered press ctrl+z then press enter.
```shell
Enter m for options, q to Exit: p

device details:
dev_id          Status
DEV_0           CONNECTED
DEV_5           CONNECTED


Available messages:
message_id      Description
0               VEHILCLE_INFO
1               LOCATION
2               Temperature


For custom messages Enter dev_id with c
Enter dev_id message_id: DEV_5 c
Enter custom message to publish. Press CTRL+Z then Press Enter

{"CustomMessage": "Hello World..."}
^Z

```
