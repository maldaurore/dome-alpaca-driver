from state import DomeState
import threading
from helpers import alpaca_response
import datetime

class AlpacaException(Exception):
    def __init__(self, number, message):
        self.number = number
        self.message = message

class DomeController:
    def __init__(self):
        self.state = DomeState()
        self.send_command = None

    def start_hardware_init(self):
        print("Verificando estado de los dispositivos...")
        self.send_command(
            {"cmd": "get_state"},
        )

        threading.Timer(5.0, self.finish_connect).start()

    def finish_connect(self):
        if not self.state.base_online:
            self.state.fatal_error = True
            self.state.fatal_error_message = "Los dispositivos no responden."
            print("Error fatal:", self.state.fatal_error_message)
        else:
            print("Dispositivos conectados correctamente.")

    def _response(self, error_number=0, error_message='', value=None):
        return {
            "error_number": error_number,
            "error_message": error_message,
            "value": value
        }
    
    def abort_slew(self):
        if not self.state.connected:
            raise AlpacaException(1031, 'El dispositivo no está conectado.')
        self.send_command({
            "cmd": "abortslew"
        })
        return
        
    def get_flap_status(self):
        return self.state.flap_status
    
    def connect(self):
        self.state.connected = True
        return
    
    def disconnect(self):
        self.state.connected = False
        return

    def open_without_flap(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.shutter_online:
            raise AlpacaException(1035, "Cortina no conectada. Mueva el domo a Home para energizar la cortina.")
        # Si el gajo está arriba y la cortina está abierta, abriéndose o cerrándose, levantar error.
        if self.state.flap_status == 0 and (self.state.shutter_status == 0 or self.state.shutter_status == 2 or self.state.shutter_status == 3):
            raise AlpacaException(1035, "La cortina no está cerrada. Debe estar cerrada para abrir sin gajo.")
        
        # Enviar comando solo si el gajo está abajo y cortina está cerrada o cerrándose. Cuando la cortina está abriéndose o
        # está abierta y el gajo está abajo, se asume que se está abriedo o está abierta sin gajo y no se hace nada.
        if (self.state.flap_status == 1 and self.state.shutter_status == 1) or (self.state.flap_status == 1 and self.state.shutter_status == 3):
            print("Abriendo domo sin gajo")
            self.send_command({
                "cmd": "open_without_flap"
            })
            return

    def close_shutter(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.shutter_online:
            raise AlpacaException(1035, "Cortina no conectada. Mueva el domo a Home para energizar la cortina.")
        if self.state.shutter_status == 4:  # Error
            raise AlpacaException(1035, self.state.fatal_error_message)
        if self.state.shutter_status == 0 or 2:
            self.send_command({
                "cmd": "closeshutter"
            })
            return
    
    def find_home(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if self.state.slaved:
            raise AlpacaException(1033, "Operación inválida cuando el domo está slaved.")
        self.send_command({
            "cmd": "findhome"
        })
        return

    def open_shutter(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.shutter_online:
            raise AlpacaException(1035, "Cortina no conectada. Mueva el domo a Home para energizar la cortina")
        if self.state.shutter_status == 4:  # Error
            raise AlpacaException(1035, self.state.fatal_error_message)
        if self.state.shutter_status == 1 or 3:
            self.send_command({
                "cmd": "openshutter"
            })
            return
        
    def park(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(1031, "Controlador de domo no disponible. Revise el hardware o conexión MQTT.")
        if not self.state.at_park:
            self.send_command({
                "cmd": "park"
            })

    def slew_to_azimuth(self, az):
        if not self.state.base_online:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        if self.state.slaved:
            raise AlpacaException(
                number=1033,
                message="Operación inválida mientras el domo está slaved."
            )
        if az > 360 or az < 0:
            raise AlpacaException(
                number=1025,
                message="Valor de azimut inválido. Debe ser entre 0 y 360."
            ) 

        self.send_command({
            "cmd": "slewtoazimuth",
            "azimuth": az
        })

    def get_at_home(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        return self.state.at_home
    
    def get_at_park(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        return self.state.at_park
    
    def get_azimuth(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        return self.state.azimuth

    def get_shutter_status(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        return self.state.shutter_status
    
    def get_slaved(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        return self.state.slaved
    
    def get_slewing(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        return self.state.slewing
    
    def get_device_state(self):
        if not self.state.connected:
            raise AlpacaException(
                number=1031,
                message="Controlador de domo no disponible. Revise el hardware o conexión MQTT."
            )
        device_state = [
            {"Name": "AtHome", "Value": self.state.at_home},
            {"Name": "AtPark", "Value": self.state.at_park},
            {"Name": "Azimuth", "Value": self.state.azimuth},
            {"Name": "ShutterStatus", "Value": self.state.shutter_status},
            {"Name": "Slewing", "Value": self.state.slewing},
            {"Name": "TimeStamp", "Value": datetime.datetime.now()}
        ]
        return device_state

    def on_hardware_event(self, event):
        if "base_online" in event:
            self.state.base_online = event["base_online"]
        if "shutter_online" in event:
            self.state.shutter_online = event["shutter_online"]
        if "azimuth" in event:
            self.state.azimuth = event["azimuth"]
        if "dome_slewing" in event:
            self.state.dome_slewing = event["dome_slewing"]
        if "at_home" in event:
            self.state.at_home = event["at_home"]
        if "at_park" in event:
            self.state.at_park = event["at_park"]
        if "shutter_status" in event:
            self.state.shutter_status = event["shutter_status"]
        if "flap_status" in event:
            self.state.flap_status = event["flap_status"]
        if "slaved" in event:
            self.state.slaved = event["slaved"]
        if self.state.shutter_status in [2, 3] or self.state.dome_slewing:
            self.state.slewing = True
        else:
            self.state.slewing = False

        print("Dome state updated:", self.state)

    def get_connected(self):
        return self.state.connected

controller = DomeController()