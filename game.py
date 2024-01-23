import paho.mqtt.client as mqtt
import time
import random
import rospy
from std_msgs.msg import String

class MQTTListener:
    def __init__(self, game):
        self.game = game
        self.client = self.connect_mqtt()
        self.microwave = False

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe("#")

    def on_message(self, client, userdata, msg):
        if ('OpenCloseMicrowave' in msg.topic and msg.payload == b'OPEN'):
            if self.microwave:
                print(f"{msg.topic}: {msg.payload}")
                self.game.handle_window_opened(msg.topic, msg.payload)

            self.microwave = True

        if ('OpenCloseMicrowave' in msg.topic and msg.payload == b'CLOSED'):
            self.microwave = False

        if ('OpenCloseCupboard' in msg.topic and msg.payload == b'OPEN') or ('OpenCloseDrawer' in msg.topic and msg.payload == b'OPEN') or  ('OpenCloseFridge' in msg.topic and msg.payload == b'OPEN'):
            
            print(f"{msg.topic}: {msg.payload}")
            self.game.handle_window_opened(msg.topic, msg.payload)

        if 'PushButtonWardRoom1_SceneNumber' in msg.topic and msg.payload == b'1.0':
            if self.game.points != 0:
                self.game.restart()

    def on_publish(self, client, userdata, mid):
        print(f"Publish: mid {mid}")

    def connect_mqtt(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_publish = self.on_publish
        client.tls_set(ca_certs="cobotmakerspace.org.crt")
        client.connect("10.0.10.12", 1883, 60)
        client.loop_start()
        return client

class Game:

    def __init__(self):

        rospy.init_node('xmasgame')
        self.speech = rospy.Publisher("/speech", String, queue_size=1)
    
       
        self.hidden_objects = []
        self.points = 0
        self.turns = 3
        self.score = 0
        self.game_over_flag = False

        self.windows = [
                "instrumentation/OpenCloseCupboardA_SensorDoor/state", 
                "instrumentation/OpenCloseCupboardB_SensorDoor/state",  
                "instrumentation/OpenCloseCupboardC_SensorDoor/state",  
                "instrumentation/OpenCloseCupboardD_SensorDoor/state",  
                "instrumentation/OpenCloseCupboardE_SensorDoor/state",  
                "instrumentation/OpenCloseCupboardF_SensorDoor/state",   
                "instrumentation/OpenCloseCupboardG_SensorDoor/state",
                "instrumentation/OpenCloseDrawerD_SensorDoor/state",
                "instrumentation/OpenCloseDrawerC_SensorDoor/state",
                "instrumentation/OpenCloseDrawerB_SensorDoor/state",
                "instrumentation/OpenCloseFridge_SensorDoor/state",
                "instrumentation/OpenCloseMicrowave_DoorWindowStatus/state",
            ]
    
        self.objects_dict = {
            "instrumentation/OpenCloseCupboardA_SensorDoor/state": "Santa Stocking ",
            "instrumentation/OpenCloseCupboardB_SensorDoor/state": "Christmas Cat",
            "instrumentation/OpenCloseCupboardC_SensorDoor/state": "Reindeer Ears",
            "instrumentation/OpenCloseCupboardD_SensorDoor/state": "Christmas Boots",
            "instrumentation/OpenCloseCupboardE_SensorDoor/state": "Santa",
            "instrumentation/OpenCloseCupboardF_SensorDoor/state": "Dancing Elf",
            "instrumentation/OpenCloseCupboardG_SensorDoor/state": "Christmas Lights",
            "instrumentation/OpenCloseDrawerB_SensorDoor/state": "Pinecone",
            "instrumentation/OpenCloseDrawerC_SensorDoor/state": "Elf Hat",
            "instrumentation/OpenCloseDrawerD_SensorDoor/state": "Snowman", 
            "instrumentation/OpenCloseFridge_SensorDoor/state": "Frozen Angel",
            "instrumentation/OpenCloseMicrowave_DoorWindowStatus/state": "Warm Reindeer",

        }

    def pick_hidden_object(self):
        self.points = 10
        if not self.hidden_objects:
            
            self.hidden_objects = random.sample(self.windows, len(self.windows))

        self.hidden_object = self.hidden_objects.pop(0)

        #DO NOT HAVE BOT SAY THIS, THIS IS FOR TESTING PURPOSES.
        #This statment tells us which window or drawer is the correct answer.
        self.speak(f"Hidden object is behind window {self.hidden_object}")

       
        #Yes robot says this
        self.speak(f"Find the {self.objects_dict.get(self.hidden_object, 'Unknown')}")

    def handle_window_opened(self, topic, payload):
        if not self.hidden_objects:
            #dont say this, its error code
            print("Error: Hidden object not picked. Make sure to call pick_hidden_object before starting the game.")
            return

        opened_window = topic.split("/")[1].split("_")[0]

        if opened_window.upper() == self.hidden_object.split("/")[1].split("_")[0].upper():
            self.score += self.points
            #Yes robot says this
            self.speak("Well Done.")
            self.turns -= 1
            #self.speak(f"Points: {self.score}")

            if self.turns > 0:
                self.pick_hidden_object()
            else:
                self.game_over()
        else:
            self.points -= 1
            #Yes robot says this
            print(f"{opened_window}")
            self.speak(f"Not that one. Try again.")

    def speak(self, message):
        self.speech.publish(message)
        rospy.sleep(1.5)

    def game_over(self):
        #Yes robot says this
        self.speak(f"Game Over. Your final score was {self.score}. Thanks for playing!")
        self.game_over_flag = True

    def restart(self):
        #Yes robot says this
        self.speak("Restarting the game...")
        self.speak("Starting")
        self.hidden_objects = []
        self.turns = 3
        self.score = 0
        self.game_over_flag = False
        self.start()

    def wait_for_restart(self):
        #no robot doesnt say this.
        print("Waiting for reset signal...")
        while not self.game_over_flag:
            time.sleep(1)

    def start(self):
        self.points = 10
        #Yes robot says this
        self.speak("Game started!")
        self.pick_hidden_object()

# Instantiate the Game class
game = Game()

# Instantiate the MQTTListener class with a reference to the Game instance
mqtt_listener = MQTTListener(game)

# Wait for a while to allow MQTT listener to receive messages
time.sleep(2)

# Start the game
game.start()
rospy.spin()

# Continue running the MQTT listener in the background
# while True:
#     pass


#more drawers
#instrumentation/OpenCloseDrawerD_SensorDoor/state: b'OPEN'
#instrumentation/OpenCloseDrawerC_SensorDoor/state: b'OPEN'
#instrumentation/OpenCloseDrawerB_SensorDoor/state: b'OPEN'
#instrumentation/OpenCloseDrawerA_SensorDoor/state: b'OPEN'
#instrumentation/OpenCloseCupboardG_SensorDoor/state: b'OPEN'