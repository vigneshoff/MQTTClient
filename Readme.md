# MQTTClient

This module provides an MQTT client application that connects to MQTT brokers with the following options:

1. **Without security**
2. **With Username and Password**
3. **With Certificates**

### Features:
- Supports JSON payloads
- Supports Publish and Subscribe
- Logs are created for debugging purposes

## Initializing the Module
Initialize the module with any one of the security options and edit the `mqtt.json` file accordingly.

```python
class Security(Enum):
    NO_SECURITY = 0
    IOT_CORE = 1
    USER_NAME_PASS = 2

mqttclient = MQTTClient(mqtt_data, with_secure=Security.USER_NAME_PASS)
```

## Publishing Messages
The `PUBLISH` node in the JSON configuration allows publishing various data without altering the code. The available keys will be displayed in the console. Select an option to publish the corresponding data to the `PUBLISH_TOPIC`.

### Sample Output:
```shell
# python3 MQTTClient.py
MQTTClient Started...
    1. VEHICLE_INFO
    2. LOCATION

Enter The Option To Publish: 2
message: {'LOCATION': {'LAT': 123.4, 'LONG': 567.8}}
```

## Example JSON Configurations

### Example `mqtt.json` for No Security
```json
{
    "INFO": {
        "DEV_ID": "TEST_DEV_001",
        "CLIENT_ID": "TEST_CLIENT_001",
        "ENDPOINT": "test.mosquitto.org",
        "PORT": 1883,
        "PUBLISH_TOPIC": "TEST/DEV001/PUB",
        "SUBSCRIBE_TOPIC": "TEST/DEV001/SUB",
        "CERTFILE": "",
        "KEYFILE": "",
        "CACERTS": "",
        "CERT_DIR": "./certs/",
        "USERNAME": "",
        "PASSWORD": ""
    },
    "PUBLISH": {
        "VEHICLE_INFO": {
            "REG_NO": 1234,
            "ENGINE_NO": 9876
        },
        "LOCATION": {
            "LAT": 123.4,
            "LONG": 567.8
        }
    }
}
```

### Example `mqtt.json` for IoT Core / Security
Keep the certificates under the directory specified in `CERT_DIR`
```json
{
    "INFO": {
        "DEV_ID": "TEST_DEV_001",
        "CLIENT_ID": "TEST_CLIENT_001",
        "ENDPOINT": "xxx-ats.iot.ap-southeast-2.amazonaws.com",
        "PORT": 8883,
        "PUBLISH_TOPIC": "TEST/DEV001/PUB",
        "SUBSCRIBE_TOPIC": "TEST/DEV001/SUB",
        "CERTFILE": "xxx-certificate.pem.crt",
        "KEYFILE": "xxx-private.pem.key",
        "CACERTS": "AmazonRootCA1.pem",
        "CERT_DIR": "./certs/",
        "USERNAME": "",
        "PASSWORD": ""
    },
    "PUBLISH": {
        "VEHICLE_INFO": {
            "REG_NO": 1234,
            "ENGINE_NO": 9876
        },
        "LOCATION": {
            "LAT": 123.4,
            "LONG": 567.8
        }
    }
}
```

### Example `mqtt.json` for Username & Password Authentication
```json
{
    "INFO": {
        "DEV_ID": "TEST_DEV_001",
        "CLIENT_ID": "TEST_CLIENT_001",
        "ENDPOINT": "xxx.s1.eu.hivemq.cloud",
        "PORT": 8883,
        "PUBLISH_TOPIC": "TEST/DEV001/PUB",
        "SUBSCRIBE_TOPIC": "TEST/DEV001/SUB",
        "CERTFILE": "",
        "KEYFILE": "",
        "CACERTS": "",
        "CERT_DIR": "./certs/",
        "USERNAME": "username",
        "PASSWORD": "password"
    },
    "PUBLISH": {
        "VEHICLE_INFO": {
            "REG_NO": 1234,
            "ENGINE_NO": 9876
        },
        "LOCATION": {
            "LAT": 123.4,
            "LONG": 567.8
        }
    }
}
```

