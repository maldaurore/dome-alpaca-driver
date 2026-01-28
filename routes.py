from flask import Flask, jsonify, render_template, request, Response
from datetime import datetime, timezone
import requests
from utils import dome_address, shutter_address, get_initialized, initialize, track_initialize_to_park, track_initialize_to_slew, abortSlew, track_shutter_to_action, get_shutter_initialized
import threading

server_transaction_id = 0

def get_next_transaction_id():
    global server_transaction_id
    server_transaction_id += 1
    return server_transaction_id

def setup_route(app):
  @app.route('/setup', methods=['GET'])
  def setup():
    return render_template('setup.html')
  
  @app.route('/setup/v1/dome/0/setup')
  def setup_dome():
    return render_template('dome-setup.html')
  
  @app.route('/management/apiversions', methods=['GET'])
  def api_versions():
    ServerTransactionID = get_next_transaction_id()
    normalized_args = {key.lower(): value for key, value in request.args.items()}
    ClientTransactionID = normalized_args.get('clienttransactionid') or 0

    response = {
       "Value": [1],
       "ClientTransactionID": int(ClientTransactionID),
       "ServerTransactionID": int(ServerTransactionID)
    }
    return jsonify(response)
  
  @app.route('/management/v1/<option>', methods=['GET'])
  def management_options(option):
    ServerTransactionID = get_next_transaction_id()
    normalized_args = {key.lower(): value for key, value in request.args.items()}
    ClientTransactionID = normalized_args.get('clienttransactionid') or 0

    try:
      if option == 'description':
        response = {
          "Value": {
            "ServerName": "ASCOM Alpaca Dome Controller",
            "Manufacturer": "Gael Sánchez - UABC - IAENS",
            "ManufacturerVersion": "1.0",
            "Location": "Instituto de Astronomía, Ensenada, Baja California, México",
          },
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID
        }
        return jsonify(response)
      elif option == 'configureddevices':
        response = {
          "Value": [
            {
              "DeviceName": "Domo",
              "DeviceType": "Dome",
              "DeviceNumber": 0,
              "UniqueID": "123e4567-e89b-12d3-a456-426614174000"
            }
          ],
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
        }
        return jsonify(response)
      else:
        response = { "error": "Unknown command" }
        return jsonify(response), 400
      
    except Exception as e:
      return Response(f"Internal server error: {str(e)}", status=500, mimetype="text/plain")
  
  ## RUTAS PUT
  @app.route('/api/v1/dome/0/<action>', methods=['PUT'])
  def dome_action(action):
    ServerTransactionID = get_next_transaction_id()
    normalized_args = {key.lower(): value for key, value in request.args.items()}
    ClientTransactionID = normalized_args.get('clienttransactionid') or 0

    try:
      ## DEVICE
      if action == 'action':
        action = request.form.get('Action')
        parameters = request.form.get('Parameters')

        print(parameters)

        if action is None:
          return Response("Missing required parameter: Action", status=400, mimetype="text/plain")
        
        if parameters is None:
          return Response("Missing required parameter: Parameters", status=400, mimetype="text/plain")
        
        ## DEVICE (Cortina, listo)
        if action == 'openWithoutFlap':
          print("Verificando estado de athome en hilo principal")
          dome_response = requests.get(dome_address + '/athome')
          if dome_response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from dome",
              "Value": None
            })
        
          dome_data = dome_response.json()
          error = dome_data['ErrorNumber']
          if error != 0:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": error,
              "ErrorMessage": dome_data['Message'],
              "Value": None
            })
          at_home = dome_data['Value']
          print("Athome: ", at_home)
          if not at_home:
            print ("No en home, enviando a home")
            dome_response = requests.put(dome_address + '/findhome')
            if dome_response.status_code != 200:
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": 1037,
                "ErrorMessage": "Failed to get response from dome",
                "Value": None
              })
            dome_data = dome_response.json()
            error = dome_data['ErrorNumber']
            if error != 0:
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": error,
                "ErrorMessage": dome_data['Message'],
                "Value": None
              })
            threading.Thread(target=track_shutter_to_action, args=('openwithoutflap', True, True,), daemon=True).start()
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 0,
              "ErrorMessage": '',
            })
          
          else:
            print("En home, obteniendo inicializacion de cortina")
            try:
              shutter_initialized = get_shutter_initialized()
            except Exception as e:
              shutter_initialized = {'Initialized': False, 'Error': False}
            print("Shutter initialized: ", shutter_initialized)
            if shutter_initialized['Error']:
              print("Error")
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": 1037,
                "ErrorMessage": shutter_initialized['Message'],
                "Value": None
              })
            if not shutter_initialized['Initialized']:
              # Monitorear inicializacion
              print("Cortina no inicializada, entrando en hilo de monitoreo de inicializacion")
              threading.Thread(target=track_shutter_to_action, args=('openwithoutflap', True, False,), daemon=True).start()
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": 0,
                "ErrorMessage": '',
              })
            else:
              # Enviar comando
              print("Cortina inicializada, enviando comando para abrir sin gajo")
              shutter_response = requests.put(shutter_address + '/openwithoutflap')
              if shutter_response.status_code != 200:
                return jsonify({
                  "ClientTransactionID": ClientTransactionID,
                  "ServerTransactionID": ServerTransactionID,
                  "ErrorNumber": 1037,
                  "ErrorMessage": "Failed to get response from shutter",
                  "Value": None
                })
              shutter_data = shutter_response.json()
              error = shutter_data['ErrorNumber']
              if error != 0:
                return jsonify({
                  "ClientTransactionID": ClientTransactionID,
                  "ServerTransactionID": ServerTransactionID,
                  "ErrorNumber": error,
                  "ErrorMessage": shutter_data['Message'],
                  "Value": None
                })
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": 0,
                "ErrorMessage": '',
              })


        else:
          response = {
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1036,
            "ErrorMessage": "Action not implemented",
            "Value": None
          }
          return jsonify(response)
      
      if action == 'commandblind':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 1036,
          "ErrorMessage": 'Action not implemented',
          "Value": None
        }
        return jsonify(response)

      if action == 'commandbool':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 1036,
          "ErrorMessage": 'Action not implemented',
          "Value": None
        }
        return jsonify(response)
      
      if action == 'commandstring':
        command = request.form['Command']
        raw = request.form['Raw']

        if not command:
          return Response("Missing required parameter: Command", status=400, mimetype="text/plain")
        if not raw:
          return Response("Missing required parameter: Raw", status=400, mimetype="text/plain")
        
        ## DEVICE (Cortina)
        if command == 'flapStatus':
            
          try:
            shutter_response = requests.get(shutter_address + '/flapstatus')
          except Exception as e:
            # RETORNAR ULTIMO ESTADO OBTENIDO
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Cortina no disponible. ",
              "Value": None
            })
          if shutter_response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from shutter",
              "Value": None
            })
          response = {
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 0,
            "ErrorMessage": '',
            "Value": '0'
          }
          return jsonify(response)
        else:
          response = {
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1036,
            "ErrorMessage": "Action not implemented",
            "Value": None
          }
          return jsonify(response)
      
      if action == 'connect':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": None
        }
        return jsonify(response)
      
      if action == 'connected':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 1036,
          "ErrorMessage": 'Action not implemented',
          "Value": None
        }
        return jsonify(response)
      
      if action == 'disconnect':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 1036,
          "ErrorMessage": 'Action not implemented',
          "Value": None
        }
        return jsonify(response)
      
      ## DEVICE (Domo, listo)
      if action == 'slaved':
        slaved = request.form.get('Slaved')

        if slaved == None:
          response = {
            "error": "Slaved parameter is required"
          }
          return jsonify(response), 400
        
        response = requests.put(dome_address + '/slaved', data={'Slaved': slaved})
        if response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        
        dome_data = response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
          
        return jsonify({
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
        })
    
      ## DEVICE (Domo y cortina, listo)
      if action == 'abortslew':
        dome_response = requests.put(dome_address + '/abortslew')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        try:
          shutter_response = requests.put(shutter_address + '/abortslew')
          if shutter_response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from shutter",
              "Value": None
            })
          shutter_data = shutter_response.json()
          error = shutter_data['ErrorNumber']
          if error != 0:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": error,
              "ErrorMessage": shutter_data['Message'],
              "Value": None
            })
        except Exception as e:
          pass

        abortSlew()
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
        }
        return jsonify(response)
      
      ## DEVICE (Cortina, listo)
      if action == 'closeshutter':
        print("Verificando estado de athome en hilo principal")
        dome_response = requests.get(dome_address + '/athome')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        at_home = dome_data['Value']
        print("Athome: ", at_home)
        if not at_home:
          print ("No en home, enviando a home")
          dome_response = requests.put(dome_address + '/findhome')
          if dome_response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from dome",
              "Value": None
            })
          dome_data = dome_response.json()
          error = dome_data['ErrorNumber']
          if error != 0:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": error,
              "ErrorMessage": dome_data['Message'],
              "Value": None
            })
          threading.Thread(target=track_shutter_to_action, args=('close', True, True,), daemon=True).start()
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 0,
            "ErrorMessage": '',
          })
          
        else:
          print("En home, obteniendo inicializacion de cortina")
          try:
            shutter_initialized = get_shutter_initialized()
          except Exception as e:
            shutter_initialized = {'Initialized': False, 'Error': False}
          print("Shutter initialized: ", shutter_initialized)
          if shutter_initialized['Error']:
            print("Error")
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": shutter_initialized['Message'],
              "Value": None
            })
          if not shutter_initialized['Initialized']:
            # Monitorear inicializacion
            print("Cortina no inicializada, entrando en hilo de monitoreo de inicializacion")
            threading.Thread(target=track_shutter_to_action, args=('close', True, False,), daemon=True).start()
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 0,
              "ErrorMessage": '',
            })
          else:
            # Enviar comando
            print("Cortina inicializada, enviando comando para abrir sin gajo")
            shutter_response = requests.put(shutter_address + '/close')
            if shutter_response.status_code != 200:
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": 1037,
                "ErrorMessage": "Failed to get response from shutter",
                "Value": None
              })
            shutter_data = shutter_response.json()
            error = shutter_data['ErrorNumber']
            if error != 0:
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": error,
                "ErrorMessage": shutter_data['Message'],
                "Value": None
              })
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 0,
              "ErrorMessage": '',
            })
        
      ## DEVICE (Domo, listo)
      if action == 'findhome':
        response = requests.put(dome_address + '/findhome')
        if response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        dome_data = response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        
        return jsonify({
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
        })
        
      ## DEVICE (Cortina)
      if action == 'openshutter':
        print("Verificando estado de athome en hilo principal")
        dome_response = requests.get(dome_address + '/athome')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        at_home = dome_data['Value']
        print("Athome: ", at_home)
        if not at_home:
          print ("No en home, enviando a home")
          dome_response = requests.put(dome_address + '/findhome')
          if dome_response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from dome",
              "Value": None
            })
          dome_data = dome_response.json()
          error = dome_data['ErrorNumber']
          if error != 0:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": error,
              "ErrorMessage": dome_data['Message'],
              "Value": None
            })
          threading.Thread(target=track_shutter_to_action, args=('open', True, True,), daemon=True).start()
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 0,
            "ErrorMessage": '',
          })
          
        else:
          print("En home, obteniendo inicializacion de cortina")
          try:
            shutter_initialized = get_shutter_initialized()
          except Exception as e:
            shutter_initialized = {'Initialized': False, 'Error': False}
          print("Shutter initialized: ", shutter_initialized)
          if shutter_initialized['Error']:
            print("Error")
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": shutter_initialized['Message'],
              "Value": None
            })
          if not shutter_initialized['Initialized']:
            # Monitorear inicializacion
            print("Cortina no inicializada, entrando en hilo de monitoreo de inicializacion")
            threading.Thread(target=track_shutter_to_action, args=('open', True, False,), daemon=True).start()
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 0,
              "ErrorMessage": '',
            })
          else:
            # Enviar comando
            print("Cortina inicializada, enviando comando para abrir sin gajo")
            shutter_response = requests.put(shutter_address + '/open')
            if shutter_response.status_code != 200:
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": 1037,
                "ErrorMessage": "Failed to get response from shutter",
                "Value": None
              })
            shutter_data = shutter_response.json()
            error = shutter_data['ErrorNumber']
            if error != 0:
              return jsonify({
                "ClientTransactionID": ClientTransactionID,
                "ServerTransactionID": ServerTransactionID,
                "ErrorNumber": error,
                "ErrorMessage": shutter_data['Message'],
                "Value": None
              })
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 0,
              "ErrorMessage": '',
            })
        
      ## DEVICE (Domo, listo)
      if action == 'park':

        initialized = get_initialized()

        if initialized['Error']:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": initialized['Message'],
            "Value": None
          })
        
        if initialized['Initialized']:
          response = requests.put(dome_address + '/park')
          if response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from dome",
              "Value": None
            })
          dome_data = response.json()
          error = dome_data['ErrorNumber']
          if error != 0:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": error,
              "ErrorMessage": dome_data['Message'],
              "Value": None
            })
          
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 0,
            "ErrorMessage": '',
          })
        
        else:
          initialize_response = initialize()

          if initialize_response['Error']:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": initialize_response['Message'],
              "Value": None
            })
          else:
            threading.Thread(target=track_initialize_to_park, daemon=True).start()
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 0,
              "ErrorMessage": '',
            })
      
      ## DEVICE (Domo)
      if action == 'setpark':
        
        initialized = get_initialized()
        if initialized['Error']:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": initialized['Message'],
            "Value": None
          })
        if not initialized['Initialized']:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Dome is not initialized",
            "Value": None
          })
        
        device_response = requests.put(dome_address + '/setpark')
        if device_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        dome_data = device_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        return jsonify({
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
        })
        
      if action == 'slewtoaltitude':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 1036,
          "ErrorMessage": 'Action not implemented',
          "Value": None
        }
        return jsonify(response)

      ## DEVICE (Domo)
      if action == 'slewtoazimuth':

        azimuth = request.form.get('Azimuth')
        if azimuth == None:
          response = {
            "error": "Azimuth parameter is required"
          }
          return jsonify(response), 400

        initialized = get_initialized()
        if initialized['Error']:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": initialized['Message'],
            "Value": None
          })
        if not initialized['Initialized']:

          device_response = requests.put(dome_address + '/findhome')
          if device_response.status_code != 200:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": 1037,
              "ErrorMessage": "Failed to get response from dome",
              "Value": None
            })
          dome_data = device_response.json()
          error = dome_data['ErrorNumber']
          if error != 0:
            return jsonify({
              "ClientTransactionID": ClientTransactionID,
              "ServerTransactionID": ServerTransactionID,
              "ErrorNumber": error,
              "ErrorMessage": dome_data['Message'],
              "Value": None
            })
          threading.Thread(target=track_initialize_to_slew, args=(azimuth,), daemon=True).start()
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 0,
            "ErrorMessage": '',
          })
        
        dome_response = requests.put(dome_address + '/slewtoazimuth', data={'Azimuth': azimuth})
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
          })
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        return jsonify({
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
        })
        
      if action == 'synctoazimuth':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 1036,
          "ErrorMessage": 'Action not implemented',
          "Value": None
        }
        return jsonify(response)
    
      else:
        response = {"error": "Unknown command" }  
        return jsonify(response), 400
    
    except Exception as e:
      print(e)
      response = { "error": str(e) }
      return jsonify(response), 500

  @app.route('/api/v1/dome/0/<action>', methods=['GET'])
  def dome_action_get(action):
    ServerTransactionID = get_next_transaction_id()
    normalized_args = {key.lower(): value for key, value in request.args.items()}
    ClientTransactionID = normalized_args.get('clienttransactionid') or 0

    try:
      if action == 'connected':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'connecting':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": False
        }
        return jsonify(response)
      
      if action == 'description':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": 'Dome for the 14 inch telescope at IAE'
        }
        return jsonify(response)
      
      ## DEVICE (Domo y cortina)
      if action == 'devicestate':
        dome_response = requests.get(dome_address + '/devicestate')
        dome_error = ''
        if dome_response.status_code != 200:
          dome_error = "Failed to get response from dome"
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          dome_error = dome_data['Message']
        
        # Consulta a cortina
          
        if dome_error:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": dome_error,
            "Value": None
          })
        
        slewing = dome_data['Slewing'] or False
        
        return jsonify({
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": [
            {"Name": "Altitude", "Value": 90.0},
            {"Name": "AtHome", "Value": dome_data['AtHome']},
            {"Name": "AtPark", "Value": dome_data['AtPark']},
            {"Name": "Azimuth", "Value": dome_data['Azimuth']},
            {"Name": "ShutterStatus", "Value": 0},
            {"Name": "Slewing", "Value": slewing},
            {"Name": "TimeStamp", "Value": datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')}
          ]
        })
      
      if action == 'driverinfo':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": "ASCOM Alpaca Dome Driver v1.0 - Controls a rotating dome with motorized shutter. Developed by Gael Sánchez (UABC). Supports optional flap exclusion for zenith visibility. Implements dome rotation, shutter control, and slaving support."
        }
        return jsonify(response)
      
      if action == 'driverversion':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": "1.0"
        }
        return jsonify(response)
      
      if action == 'interfaceversion':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": 3
        }
        return jsonify(response)
      
      if action == 'name':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": 'Dome for the 14 inch telescope at IAENS'
        }
        return jsonify(response)
      
      if action == 'supportedactions':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": ['openWithoutFlap']
        }
        return jsonify(response)
      
      if action == 'altitude':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": 90.0
        }
        return jsonify(response)
      
      ## DEVICE (Domo, listo)
      if action == 'athome':
        dome_response = requests.get(dome_address + '/athome')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
            })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        at_home = dome_data['Value']
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": at_home
        }
        return jsonify(response)
      
      ## DEVICE (Domo, listo)
      if action == 'atpark':
        dome_response = requests.get(dome_address + '/atpark')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
            })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        at_park = dome_data['Value']
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": at_park
        }
        return jsonify(response)
      
      ## DEVICE (Domo, listo)
      if action == 'azimuth':
        dome_response = requests.get(dome_address + '/azimuth')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get azimuth from dome",
            "Value": None
            })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        dome_azimuth = dome_data['Value']
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": dome_azimuth
        }
        return jsonify(response)
      
      if action == 'canfindhome':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'canpark':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'cansetaltitude':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": False
        }
        return jsonify(response)
      
      if action == 'cansetazimuth':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'cansetpark':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'cansetshutter':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'canslave':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": True
        }
        return jsonify(response)
      
      if action == 'cansynctoazimuth':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": False
        }
        return jsonify(response)
      
      ## DEVICE (Cortina)
      if action == 'shutterstatus':
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": 0
        }
        return jsonify(response)
      
      ## DEVICE (Domo, listo)
      if action == 'slaved':
        dome_response = requests.get(dome_address + '/slaved')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
            })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        slaved = dome_data['Value']
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": slaved
        }
        print(response)
        return jsonify(response)
      
      # Domo y cortina
      if action == 'slewing':
        dome_response = requests.get(dome_address + '/slewing')
        if dome_response.status_code != 200:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": 1037,
            "ErrorMessage": "Failed to get response from dome",
            "Value": None
            })
        
        dome_data = dome_response.json()
        error = dome_data['ErrorNumber']
        if error != 0:
          return jsonify({
            "ClientTransactionID": ClientTransactionID,
            "ServerTransactionID": ServerTransactionID,
            "ErrorNumber": error,
            "ErrorMessage": dome_data['Message'],
            "Value": None
          })
        dome_slewing = dome_data['Value']

        # Consulta a la cortina
        shutter_slewing = False
        response = {
          "ClientTransactionID": ClientTransactionID,
          "ServerTransactionID": ServerTransactionID,
          "ErrorNumber": 0,
          "ErrorMessage": '',
          "Value": dome_slewing or shutter_slewing
        }
        return jsonify(response)
      
      else:
        response = {"error": "Unknown command" }  
        return jsonify(response), 400

    except Exception as e:
      response = { "error": str(e) }
      return jsonify(response), 500
    
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

  return app
