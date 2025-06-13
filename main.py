import json
from MQTTClient import MQTTClient

if __name__ == '__main__':
    try:
        with open ("main.json", 'r') as conf_file:
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