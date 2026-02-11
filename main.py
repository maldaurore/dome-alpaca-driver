from flask import Flask
# from routes.routes import setup_route
from controller import controller
from mqtt_client import MqttClient
from routes.management import register_management_routes
from routes.dome_put import register_dome_put_routes
from routes.dome_get import register_dome_get_routes
from discovery_server import start_discovery

app = Flask(__name__)
#setup_route(app)
register_management_routes(app)
register_dome_put_routes(app)
register_dome_get_routes(app)

if __name__ == "__main__":
    start_discovery()
    mqtt = MqttClient()

    controller.send_command = mqtt.publish
    mqtt.on_event = controller.on_hardware_event
    mqtt.connect()
    controller.start_hardware_init()

    app.run(host="0.0.0.0", port=5000)
