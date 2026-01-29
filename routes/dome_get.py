import datetime
from helpers import alpaca_endpoint, alpaca_response
from flask import Flask, Response, request
from state import DOME_STATE

def handle_not_implemented(request, client_id, server_id):
    return alpaca_response(
        client_id=client_id,
        server_id=server_id,
        error_number=1024,
        error_message="This action is not implemented."
    )

def handle_get_connected(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención de estado de conexión
    return alpaca_response(client_id=client_id, server_id=server_id, value=DOME_STATE["connected"])

def handle_get_connecting(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención de estado de conexión en progreso
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_get_description(request, client_id, server_id):
    description = "Dome driver for the 14 inch telescope at IAE"
    return alpaca_response(client_id=client_id, server_id=server_id, value=description)

def handle_get_device_state(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención del estado del dispositivo
    # MOCKED DATA
    device_state = [
        {"Name": "AtHome", "Value": True},
        {"Name": "AtPark", "Value": True},
        {"Name": "Azimuth", "Value": 0.0},
        {"Name": "ShutterStatus", "Value": 0},
        {"Name": "Slewing", "Value": False},
        {"Name": "TimeStamp", "Value": datetime.datetime.now()}
    ]
    return alpaca_response(client_id=client_id, server_id=server_id, value=device_state)

def handle_get_driver_info(request, client_id, server_id):
    driver_info = "ASCOM Alpaca Dome Driver v1.0 - Controls a rotating dome with motorized shutter. Developed by Gael Sánchez (UABC). Supports optional flap exclusion for zenith visibility. Implements dome rotation, shutter control, and slaving support."
    return alpaca_response(client_id=client_id, server_id=server_id, value=driver_info)

def handle_get_driverversion(request, client_id, server_id):
    version = "1.0"
    return alpaca_response(client_id=client_id, server_id=server_id, value=version)

def handle_get_interface_version(request, client_id, server_id):
    interface_version = 3
    return alpaca_response(client_id=client_id, server_id=server_id, value=interface_version)

def handle_get_name(request, client_id, server_id):
    name = "Dome for the 14 inch telescope at IAENS"
    return alpaca_response(client_id=client_id, server_id=server_id, value=name)

def handle_get_supported_actions(request, client_id, server_id):
    actions = [ 'openWithoutFlap' ]
    return alpaca_response(client_id=client_id, server_id=server_id, value=actions)

def handle_get_at_home(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención de estado AtHome
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_get_at_park(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención de estado AtPark
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_get_azimuth(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención de azimuth
    azimuth = DOME_STATE["azimuth"]
    return alpaca_response(client_id=client_id, server_id=server_id, value=azimuth)

def handle_can_find_home(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_park(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_set_altitude(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_can_set_azimuth(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_set_park(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_set_shutter(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_slave(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_sync_to_azimuth(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_get_shutter_status(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención del estado del obturador
    shutter_status = 0  # 0 = Closed, 1 = Open, 2 = Opening, 3 = Closing
    return alpaca_response(client_id=client_id, server_id=server_id, value=shutter_status)

def handle_get_slaved(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención del estado Slaved
    slaved = False
    return alpaca_response(client_id=client_id, server_id=server_id, value=slaved)

def handle_get_slewing(request, client_id, server_id):
    # TO DO: implementar lógica real de obtención del estado Slewing
    slewing = False
    return alpaca_response(client_id=client_id, server_id=server_id, value=slewing)

COMMANDS = {
    "connected": handle_get_connected,
    "connecting": handle_get_connecting,
    "description": handle_get_description,
    "devicestate": handle_get_device_state,
    "driverinfo": handle_get_driver_info,
    "driverversion": handle_get_driverversion,
    "interfaceversion": handle_get_interface_version,
    "name": handle_get_name,
    "supportedactions": handle_get_supported_actions,
    "altitude": handle_not_implemented,
    "athome": handle_get_at_home,
    "atpark": handle_get_at_park,
    "azimuth": handle_get_azimuth,
    "canfindhome": handle_can_find_home,
    "canpark": handle_can_park,
    "cansetaltitude": handle_can_set_altitude,
    "cansetazimuth": handle_can_set_azimuth,
    "cansetpark": handle_can_set_park,
    "cansetshutter": handle_can_set_shutter,
    "canslave": handle_can_slave,
    "cansyncazimuth": handle_can_sync_to_azimuth,
    "shutterstatus": handle_get_shutter_status,
    "slaved": handle_get_slaved,
    "slewing": handle_get_slewing
}

def register_dome_get_routes(app):
    @app.route('/api/v1/dome/0/<action>', methods=['GET'])
    @alpaca_endpoint
    def dome_get_action(action, client_id, server_id):
        try:
            handler = COMMANDS.get(action.lower())
            if not handler:
                return alpaca_response(
                    client_id=client_id,
                    server_id=server_id,
                    error_number=1035,
                    error_message=f"Action '{action}' not recognized."
                )
            return handler(request, client_id, server_id)
        except Exception as e:
            return Response(f"Internal server error: {str(e)}", status=500, mimetype="text/plain")
    return app