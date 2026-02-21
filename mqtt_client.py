import json
import paho.mqtt.client as mqtt

class MqttClient:
    def __init__(self):
        self.on_event = None 
        self.client = mqtt.Client(
            client_id="controller",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1
        )

        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect

    def connect(self):
        self.client.connect("localhost")
        self.client.loop_start()

    def publish(self, payload, topic):
        self.client.publish(
            topic,
            json.dumps(payload),
            qos=1
        )

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("dome/events")

    def _on_message(self, client, userdata, msg):
        if not self.on_event:
            return

        raw = msg.payload.decode()
        try:
            event = json.loads(raw)
        except Exception as e:
            print("JSON ERROR:", e)
            return
        self.on_event(event)
