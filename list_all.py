import paho.mqtt.client as mqtt

class MQTTListener():

    def __init__(self) -> None:

        self.client = self.connect_mqtt()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe("#")
 
    def on_message(self, client, userdata, msg):
        # match msg.topic:
            # case "instrumentation/PushButtonWardRoom1_SceneNumber/state":
        #if ('OpenCloseCupboard' in msg.topic):
        print(f"{msg.topic}: {msg.payload}")
            # case _: 
            #     print(f"{msg.topic}: {msg.payload}")
            #     pass

        # print(f"Messaged Received: {msg.topic}")

    def on_publish(self, client, userdata, mid):
        print(f"Publish: mid {mid}")

    def connect_mqtt(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_publish = self.on_publish
        client.tls_set(ca_certs="cobotmakerspace.org.crt")
        client.connect("10.0.10.12", 1883, 60)
        client.loop_forever()

        return client
    
ml = MQTTListener()
