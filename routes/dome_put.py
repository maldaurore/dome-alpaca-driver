from controller import AlpacaException, controller
from helpers import alpaca_endpoint, alpaca_response
from flask import Flask, Response, request
from routes.dome_get import SUPPORTED_ACTIONS

def handle_method_not_implemented(request, client_id, server_id):
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
        return Response("Parámetro obligatorio faltante: Action", status=400, mimetype="text/plain")
        
    if parameters is None:
        return Response("Parámetro obligatorio faltante: Parameters", status=400, mimetype="text/plain")
    
    action = action.lower()
    if action not in SUPPORTED_ACTIONS:
        raise AlpacaException(
            number=1036,
            message=f"Acción '{action}' no reconocida."
        )

    if action == 'openwithoutflap':
        controller.open_without_flap()
        return alpaca_response(client_id=client_id, server_id=server_id, value='Abriendo cortina sin gajo.')

    if action == 'getflapstatus':
        flap_status = controller.get_flap_status()
        return alpaca_response(client_id=client_id, server_id=server_id, value=flap_status)
    
def handle_connect(request, client_id, server_id):
    controller.connect()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_disconnect(request, client_id, server_id):
    controller.disconnect()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_connected(request, client_id, server_id):
    connected = request.form.get('Connected')

    if connected is None:
        return Response("Parámetro obligatorio faltante: Connected", status=400, mimetype="text/plain")
    
    connected = connected.lower()
    if connected not in ['true', 'false']:
        return Response("Valor inválido para parámetro: Connected. Debe de ser booleano.", status=400, mimetype="text/plain")
    
    if connected == 'true':
        return handle_connect(request, client_id, server_id)
    else:
        return handle_disconnect(request, client_id, server_id)

def handle_slaved(request, client_id, server_id):
    slaved = request.form.get('Slaved')

    if slaved is None:
        return Response("Parámetro obligatorio faltante: Slaved", status=400, mimetype="text/plain")
    
    slaved = slaved.lower()
    if slaved not in ['true', 'false']:
        return Response("Valor inválido para: Slaved. Debe de ser un booleano.", status=400, mimetype="text/plain")
    
    # TO DO: implementar lógica real de configuración de slaved
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_abort_slew(request, client_id, server_id):
    controller.abort_slew()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_close_shutter(request, client_id, server_id):
    controller.close_shutter()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_find_home(request, client_id, server_id):
    controller.find_home()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_open_shutter(request, client_id, server_id):
    controller.open_shutter()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_park(request, client_id, server_id):
    controller.park()
    return alpaca_response(client_id=client_id, server_id=server_id)

def handle_slew_to_azimuth(request, client_id, server_id):
    azimuth = request.form.get('Azimuth')

    if azimuth is None:
        return Response("Parámetro obligatorio faltante: Azimuth", status=400, mimetype="text/plain")
    
    try:
        azimuth_value = float(azimuth)
        controller.slew_to_azimuth(azimuth_value)
        return alpaca_response(client_id=client_id, server_id=server_id)

    except ValueError:
        return alpaca_response(
            error_number=1025, 
            error_message="Valor de azimut inválido. Debe ser un float.",
            client_id=client_id,
            server_id=server_id
        )

COMMANDS = {
    "action": handle_action,
    "commandblind": handle_method_not_implemented,
    "commandbool": handle_method_not_implemented,
    "commandstring": handle_method_not_implemented,
    "connect": handle_connect,
    "connected": handle_connected,
    "slaved": handle_slaved,
    "disconnect": handle_disconnect,
    "abortslew": handle_abort_slew,
    "closeshutter": handle_close_shutter,
    "findhome": handle_find_home,
    "openshutter": handle_open_shutter,
    "park": handle_park,
    "setpark": handle_method_not_implemented,
    # El domo no soporta movimiento vertical
    "slewtoaltitude": handle_method_not_implemented,
    "slewtoazimuth": handle_slew_to_azimuth,
    "synctoazimuth": handle_method_not_implemented,
}

def register_dome_put_routes(app):
    @app.route('/api/v1/dome/0/<action>', methods=['PUT'])
    @alpaca_endpoint
    def dome_put_action(action, client_id, server_id):
        try:
            handler = COMMANDS.get(action.lower())
            print(handler)
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
