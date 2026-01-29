from flask import jsonify, render_template, request, Response
from helpers import alpaca_endpoint, alpaca_response

def register_management_routes(app):
    @app.route('/setup', methods=['GET'])
    def setup():
        return render_template('setup.html')
    
    @app.route('/management/apiversions', methods=['GET'])
    @alpaca_endpoint
    def api_versions(client_id, server_id):
        normalized_args = {key.lower(): value for key, value in request.args.items()}

        return alpaca_response(value=[1], client_id=client_id, server_id=server_id)
  
    @app.route('/management/v1/<option>', methods=['GET'])
    @alpaca_endpoint
    def management_options(option, client_id, server_id):
        normalized_args = {key.lower(): value for key, value in request.args.items()}

        try:
            if option == 'description':
                value = {
                    "ServerName": "ASCOM Alpaca Dome Controller",
                    "Manufacturer": "Gael Sánchez - UABC - IAENS",
                    "ManufacturerVersion": "1.0",
                    "Location": "Instituto de Astronomía, Ensenada, Baja California, México",
                }
                return alpaca_response(value=value, client_id=client_id, server_id=server_id)
            elif option == 'configureddevices':
                value = [
                    {
                    "DeviceName": "Domo IAENS",
                    "DeviceType": "Dome",
                    "DeviceNumber": 0,
                    "UniqueID": "123e4567-e89b-12d3-a456-426614174000"
                    }
                ]
                return alpaca_response(value=value, client_id=client_id, server_id=server_id)
            else:
                response = { "error": "Unknown command" }
                return jsonify(response), 400
      
        except Exception as e:
            return Response(f"Internal server error: {str(e)}", status=500, mimetype="text/plain")