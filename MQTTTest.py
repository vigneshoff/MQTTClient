import json
import sys
from MQTTClient import MQTTClient

def mqtt_on_message(client, message):
    '''
    Callback function from MQTTClient to process the message.
    '''
    print(f"\nIncomming message:\n{message}")

def display_publish_msg(mqtt_data):
    '''
    Display the available data in the PUBLISH node from the json.
    '''
    publish_data = mqtt_data.get("PUBLISH")
    print(f"Available messages:")
    print("message_id", "Description", sep="\t")
    for i, key in enumerate(publish_data):
        print(i, key, sep="\t\t")
    print("\n")

def get_publish_msg(mqtt_data, msg_id):
    '''
    return the message based on the index.
    msg_id is the index of the data in the PUBLISH node.
    '''
    msg_id = int(msg_id)
    publish_data = mqtt_data.get("PUBLISH")
    key_list = list(publish_data.keys())
    for i, key in enumerate(publish_data):
        if i == msg_id:
            return {key: publish_data[key_list[msg_id]]}

def read_multiple_lines():
    try:
        input = sys.stdin.read()
        if isinstance(input, str):
            # sometimes we can publish non json strings too...
            try:
                return json.loads(input)
            except:
                return input
    except:
        input = {}
        print("\nInvalid Entry...!!!")

    return input

if __name__ == '__main__':
    try:
        with open ("MQTTClient.json", 'r') as conf_file:
            json_data = json.load(conf_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        json_data = {}

    mqtt_client = MQTTClient(json_data)
    mqtt_client.on_message_cb(mqtt_on_message)

    '''
    Below operations demonstrates the functionalities provided by MQTTClient.
    1. Get clients info
    2. Publish the available / custom message to the particular device.
    3. Connect the device to the MQTTClient broker.
    4. Disconnect the device from the MQTTClient broker.
    '''
    while True:
        try:
            choice = input("\nEnter m for options, q to Exit: ")

            if choice.lower() == 'm':
                print(
                    "Help menu\n"
                    "m -> menu\n"
                    "q -> exit\n"
                    "g -> get the client details\n"
                    "p -> enter into publish mode\n"
                    "a -> add / connect new device\n"
                    "d -> delete / disconnect the device\n"
                )

            elif choice.lower() == 'q':
                print("\nExiting...")
                mqtt_client.stop()
                break

            elif choice.lower() == 'g':
                '''
                Get the device / clients information.
                '''
                dev_detail = mqtt_client.clients_info()
                print(f"\ndevice details:")
                print("dev_id", "Status", sep="\t\t")
                for i, key in enumerate(dev_detail):
                    print(key, dev_detail[key], sep="\t\t")
                print("\n")

            elif choice.lower() == 'p':
                '''
                Publish mode.
                '''
                dev_detail = mqtt_client.clients_info()
                print(f"\ndevice details:")
                print("dev_id", "Status", sep="\t\t")
                for i, key in enumerate(dev_detail):
                    print(key, dev_detail[key], sep="\t\t")
                print("\n")

                display_publish_msg(json_data)
                print("For custom messages Enter dev_id with c")
                p_choice = input("Enter dev_id message_id: ")
                if len(p_choice.split()) == 2:
                    dev_id, msg_id = p_choice.split()
                    if msg_id == 'c':
                        print("Enter custom message to publish. Press CTRL+Z then Press Enter\n")
                        message = read_multiple_lines()
                        mqtt_client.publish(dev_id, message)
                    else:
                        msg_to_publish = get_publish_msg(json_data, msg_id)
                        print(f"\nmsg_to_publish: {msg_to_publish}")
                        mqtt_client.publish(dev_id, msg_to_publish)
                else:
                    print("Invalid dev_id message_id.")

            elif choice.lower() == 'a':
                '''
                Create / add new device.
                '''
                print("Enter the device details:\n")
                message = read_multiple_lines()
                mqtt_client.mqtt_connect(message)

            elif choice.lower() == 'd':
                '''
                Delete or disconnect the device.
                '''
                dev_id = input("Enter the device id: ")
                mqtt_client.mqtt_disconnect(dev_id)

        except KeyboardInterrupt:
            print("\nInterrupted! Exiting...")
            mqtt_client.stop()
            break
