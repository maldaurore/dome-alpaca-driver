import datetime
from helpers import alpaca_endpoint, alpaca_response
from flask import Flask, Response, request
from controller import AlpacaException, controller

SUPPORTED_ACTIONS = [ 'openwithoutflap', 'getflapstatus' ]

def handle_not_implemented(request, client_id, server_id):
    return alpaca_response(
        client_id=client_id,
        server_id=server_id,
        error_number=1024,
        error_message="This action is not implemented."
    )

def handle_get_connected(request, client_id, server_id):
    connected = controller.get_connected()
    return alpaca_response(client_id=client_id, server_id=server_id, value=connected)

def handle_get_connecting(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_get_description(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    description = "Controlador de domo para el telescopio de 14 pulgadas del IAENS. Desarrollado por Gael Sánchez."
    return alpaca_response(client_id=client_id, server_id=server_id, value=description)

def handle_get_device_state(request, client_id, server_id):
    device_state = controller.get_device_state()
    return alpaca_response(client_id=client_id, server_id=server_id, value=device_state)

def handle_get_driver_info(request, client_id, server_id):
    driver_info = "Controlador de Domo ASCOM Alpaca v1.0 - Controla un domo rotatorio con cortina motorizada. Desarrollado por Gael Sánchez (UABC). Soporta exlusión opcional de gajo para visibilidad del cenit."
    return alpaca_response(client_id=client_id, server_id=server_id, value=driver_info)

def handle_get_driverversion(request, client_id, server_id):
    version = "1.0"
    return alpaca_response(client_id=client_id, server_id=server_id, value=version)

def handle_get_interface_version(request, client_id, server_id):
    interface_version = 3
    return alpaca_response(client_id=client_id, server_id=server_id, value=interface_version)

def handle_get_name(request, client_id, server_id):
    name = "Domo del telescopio de 14 pulgadas - IAENS"
    return alpaca_response(client_id=client_id, server_id=server_id, value=name)

def handle_get_supported_actions(request, client_id, server_id):
    return alpaca_response(client_id=client_id, server_id=server_id, value=SUPPORTED_ACTIONS)

def handle_get_at_home(request, client_id, server_id):
    value = controller.get_at_home()
    return alpaca_response(client_id=client_id, server_id=server_id, value=value)

def handle_get_at_park(request, client_id, server_id):
    value = controller.get_at_park()
    return alpaca_response(client_id=client_id, server_id=server_id, value=value)


def handle_get_azimuth(request, client_id, server_id):
    value = controller.get_azimuth()
    return alpaca_response(client_id=client_id, server_id=server_id, value=value)

def handle_can_find_home(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_park(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_set_altitude(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_can_set_azimuth(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_set_park(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_can_set_shutter(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_slave(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=True)

def handle_can_sync_to_azimuth(request, client_id, server_id):
    if not controller.get_connected():
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1031,
            error_message="Dispositivo no conectado"
        )
    return alpaca_response(client_id=client_id, server_id=server_id, value=False)

def handle_get_shutter_status(request, client_id, server_id):
    shutter_status = controller.get_shutter_status()
    return alpaca_response(client_id=client_id, server_id=server_id, value=shutter_status)

def handle_get_slaved(request, client_id, server_id):
    slaved = controller.get_slaved()
    return alpaca_response(client_id=client_id, server_id=server_id, value=slaved)

def handle_get_slewing(request, client_id, server_id):
    slewing = controller.get_slewing()
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
        except AlpacaException as e:
            return alpaca_response(
                client_id=client_id,
                server_id=server_id,
                error_number=e.number,
                error_message=e.message
            )
        except Exception as e:
            return Response(f"Internal server error: {str(e)}", status=500, mimetype="text/plain")
        except Exception as e:
            print(f"Error handling dome action '{action}': {str(e)}")
            return Response(f"Internal server error: {str(e)}", status=500, mimetype="text/plain")