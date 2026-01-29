from flask import Flask
# from routes.routes import setup_route
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
    app.run(host="0.0.0.0", port=5000)
