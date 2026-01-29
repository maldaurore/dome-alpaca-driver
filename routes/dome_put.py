from helpers import alpaca_endpoint, alpaca_response
from flask import Flask, Response, request
from state import DOME_STATE

def handle_action_not_implemented(request, client_id, server_id):
    return alpaca_response(
        client_id=client_id,
        server_id=server_id,
        error_number=1024,
        error_message="This action is not implemented."
    )

def handle_action(request, client_id, server_id):
    action = request.form.get('Action')
    parameters = request.form.get('Parameters')

    if action is None:
        return Response("Missing required parameter: Action", status=400, mimetype="text/plain")
        
    if parameters is None:
        return Response("Missing required parameter: Parameters", status=400, mimetype="text/plain")

    if action == 'openWithoutFlap':
        return alpaca_response(client_id=client_id, server_id=server_id, value='Opening without flap exclusion')
    else:
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1024,
            error_message=f"Action '{action}' not recognized."
        )

def handle_command_string(request, client_id, server_id):
    command = request.form.get('Command')
    raw = request.form.get('Raw')

    if not command:
        return Response("Missing required parameter: Command", status=400, mimetype="text/plain")
    if raw is None:
        return Response("Missing required parameter: Raw", status=400, mimetype="text/plain")
    
    if command == 'flapStatus':
        # TO DO: implementar lógica real de obtención de estado del flap
        return alpaca_response(client_id=client_id, server_id=server_id, value="0")
    else:
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1024,
            error_message=f"Command '{command}' not recognized."
        )
    
def handle_connect(request, client_id, server_id):
    # TO DO: implementar lógica real de conexión
    DOME_STATE["connected"] = True
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_disconnect(request, client_id, server_id):
    # TO DO: implementar lógica real de desconexión
    DOME_STATE["connected"] = False
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_connected(request, client_id, server_id):
    connected = request.form.get('Connected')

    if connected is None:
        return Response("Missing required parameter: Connected", status=400, mimetype="text/plain")
    
    connected = connected.lower()
    if connected not in ['true', 'false']:
        return Response("Invalid value for parameter: Connected. Must be boolean.", status=400, mimetype="text/plain")
    
    if connected == 'true':
        return handle_connect(request, client_id, server_id)
    else:
        return handle_disconnect(request, client_id, server_id)

def handle_slaved(request, client_id, server_id):
    slaved = request.form.get('Slaved')

    if slaved is None:
        return Response("Missing required parameter: Slaved", status=400, mimetype="text/plain")
    
    slaved = slaved.lower()
    if slaved not in ['true', 'false']:
        return Response("Invalid value for parameter: Slaved. Must be 'true' or 'false'.", status=400, mimetype="text/plain")
    
    # TO DO: implementar lógica real de configuración de slaved
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_abort_slew(request, client_id, server_id):
    # TO DO: implementar lógica real de aborto de movimiento
    DOME_STATE["slewing"] = False
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_close_shutter(request, client_id, server_id):
    # TO DO: implementar lógica real de cierre del obturador
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_find_home(request, client_id, server_id):
    # TO DO: implementar lógica real de búsqueda de home
    DOME_STATE["at_home"] = True
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_open_shutter(request, client_id, server_id):
    # TO DO: implementar lógica real de apertura del obturador
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_park(request, client_id, server_id):
    # TO DO: implementar lógica real de park
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_set_park(request, client_id, server_id):
    # TO DO: implementar lógica real de configuración de park
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_slew_to_azimuth(request, client_id, server_id):
    azimuth = request.form.get('Azimuth')

    if azimuth is None:
        return Response("Missing required parameter: Azimuth", status=400, mimetype="text/plain")
    
    try:
        azimuth_value = float(azimuth)
    except ValueError:
        return Response("Invalid value for parameter: Azimuth. Must be a float.", status=400, mimetype="text/plain")
    
    if azimuth_value > 360.0 or azimuth_value < 0.0:
        return alpaca_response(
            client_id=client_id,
            server_id=server_id,
            error_number=1025,
            error_message="Azimuth out of range. Must be between 0 and 360 degrees."
        )
    # TO DO: implementar lógica real de movimiento a azimut
    DOME_STATE["at_home"] = False
    DOME_STATE["azimuth"] = azimuth_value
    return alpaca_response(client_id=client_id, server_id=server_id)

COMMANDS = {
    "action": handle_action,
    "commandblind": handle_action_not_implemented,
    "commandbool": handle_action_not_implemented,
    "commandstring": handle_command_string,
    "connect": handle_connect,
    "connected": handle_connected,
    "slaved": handle_slaved,
    "disconnect": handle_disconnect,
    "abortslew": handle_abort_slew,
    "closeshutter": handle_close_shutter,
    "findhome": handle_find_home,
    "openshutter": handle_open_shutter,
    "park": handle_park,
    "setpark": handle_set_park,
    # El domo no soporta movimiento vertical
    "slewtoaltitude": handle_action_not_implemented,
    "slewtoazimuth": handle_slew_to_azimuth,
    "synctoazimuth": handle_action_not_implemented,
}

def register_dome_put_routes(app):
    @app.route('/api/v1/dome/0/<action>', methods=['PUT'])
    @alpaca_endpoint
    def dome_put_action(action, client_id, server_id):
        try:
            handler = COMMANDS.get(action.lower())
            print(handler)
            if not handler:
                # TO DO: checar que el codigo de error sea el correcto
                return Response(f"Action '{action}' not recognized.", status=404, mimetype="text/plain")
            return handler(request, client_id, server_id)
        except Exception as e:
            print(f"Error handling dome action '{action}': {str(e)}")
            return Response(f"Internal server error: {str(e)}", status=500, mimetype="text/plain")
