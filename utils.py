import requests
import time
import threading

dome_address = 'http://192.168.1.75'
shutter_address = 'http://192.168.1.76'
detener_hilos = threading.Event()


def get_initialized():
  """Check if the dome is initialized."""
  print('verificando estado de domo...')
  response = requests.get(dome_address + '/initialized')
  if response.status_code != 200:
    return {'Error': True, 'Message': 'Ocurrió un error al obtener la respuesta del dispositivo'}
  
  data = response.json()
  error = data['ErrorNumber']
  if error != 0:
    return {'Error': True, 'Message': data['Message']}
  return {'Error': False, 'Initialized': data['Value']}

def get_at_home():
  """Check if the dome is at home position."""
  print('verificando estado de domo...')
  response = requests.get(dome_address + '/athome')
  if response.status_code != 200:
    return {'Error': True, 'Message': 'Ocurrió un error al obtener la respuesta del dispositivo'}
  
  data = response.json()
  error = data['ErrorNumber']
  if error != 0:
    return {'Error': True, 'Message': data['Message']}
  return {'Error': False, 'AtHome': data['Value']}

def get_shutter_initialized():
  """Check if the shutter is initialized."""
  print('verificando estado de obturador...')
  response = requests.get(shutter_address + '/initialized')
  print("Respuesta obtenida")
  if response.status_code != 200:
    print("Error en la respuesta")
    return {'Error': True, 'Message': 'Ocurrió un error al obtener la respuesta del dispositivo'}
  
  data = response.json()
  print("Datos obtenidos: ", data)
  error = data['ErrorNumber']
  if error != 0:
    return {'Error': True, 'Message': data['Message']}
  return {'Error': False, 'Initialized': data['Initialized']}

def initialize():
  print('inicializando domo...')
  dome_response = requests.put(dome_address + '/findhome')
  if dome_response.status_code != 200:
    return {'Error': True, 'Message': 'Ocurrió un error al obtener la respuesta del dispositivo'}
  dome_data = dome_response.json()
  error = dome_data['ErrorNumber']
  if error != 0:
    return {'Error': True, 'Message': dome_data['Message']}
  
  return {'Error': False, 'Message': ''}

def abortSlew():
  detener_hilos.set()

def track_initialize_to_park():
  initialized = False
  error = False

  print('monitoreando estado de domo')
  while not initialized and not error and not detener_hilos.is_set():
    initialized_response = get_initialized()
    if initialized_response['Error']:
      error = True
      print('Error:', initialized_response['Message'])
      break
    else:
      initialized = initialized_response['Initialized']
      print('Initialized:', initialized)
      time.sleep(5)

  print('Saliendo de bucle')
  # If the dome is initialized, park it
  if initialized and not error and not detener_hilos.is_set():
    print('Dome initialized, parking...')
    requests.put(dome_address + '/park')

  return

def track_initialize_to_slew(azimuth):
  initialized = False
  error = False

  print('monitoreando estado de domo')
  while not initialized and not error and not detener_hilos.is_set():
    initialized_response = get_initialized()
    if initialized_response['Error']:
      error = True
      print('Error:', initialized_response['Message'])
      break
    else:
      initialized = initialized_response['Initialized']
      print('Initialized:', initialized)
      time.sleep(5)

  print('Saliendo de bucle')
  # If the dome is initialized, slew to the specified azimuth
  if initialized and not error and not detener_hilos.is_set():
    print('Dome initialized, slewing to azimuth:', azimuth)
    requests.put(dome_address + '/slewtoazimuth', data={'Azimuth': azimuth})

def track_at_home():
  at_home = False
  error = False

  print('monitoreando estado de domo')
  while not at_home and not error and not detener_hilos.is_set():
    at_home_response = get_at_home()
    if at_home_response['Error']:
      error = True
      print('Error:', at_home_response['Message'])
      raise Exception('Error al obtener el estado del domo')
    else:
      at_home = at_home_response['AtHome']
      print('AtHome:', at_home)
      time.sleep(5)

  print('Saliendo de bucle')
  return True
  
def track_shutter_initialized():
  initialized = False
  error = False

  print('monitoreando estado de obturador')
  while not initialized and not error and not detener_hilos.is_set():
    print('monitoreando estado de obturador')
    try:

      initialized_response = get_shutter_initialized()
    except Exception as e:
      print('Error:', str(e))
      initialized_response = {'Error': False, 'Initialized': False}
      
    if initialized_response['Error']:
      #error = True
      print('Error:', initialized_response['Message'])
      #raise Exception('Error al obtener el estado del obturador')
    else:
      initialized = initialized_response['Initialized']
      print('Initialized:', initialized)
    time.sleep(5)

  print('Saliendo de bucle')
  return True

def track_shutter_to_action(action, track_initialize, track_home):
  if track_home:
    track_at_home()

  if track_initialize:
    track_shutter_initialized()

  action_response = requests.put(shutter_address + '/' + action)
  if action_response.status_code != 200:
    raise Exception('Error al obtener la respuesta del dispositivo')
  action_data = action_response.json()
  error = action_data['ErrorNumber']
  if error != 0:
    raise Exception(action_data['Message'])
  
  return True