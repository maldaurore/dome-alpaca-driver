from state import DomeState
import threading
import datetime
import time

BASE_COMMANDS_TOPIC = "dome/base/commands"
SHUTTER_COMMANDS_TOPIC = "dome/shutter/commands"
HEARTBEAT_TIMEOUT = 5

class Errors:
    DEVICES_NOT_RESPONDING = 1280
    SHUTTER_ERROR = 1281
    DOME_STALL_ERROR = 1282
    FIND_HOME_ERROR = 1283

class AlpacaException(Exception):
    def __init__(self, number, message, value = None):
        self.number = number
        self.message = message
        self.value = value

class DomeController:
    def __init__(self):
        self.state = DomeState()
        self.send_command = None
        self.last_shutter_update = None
        self.last_base_update = None
        self._watchdog_running = True

        threading.Thread(target=self._heartbeat_watchdog, daemon=True).start()

    def start_hardware_init(self):
        print("Verificando estado de los dispositivos...")
        self.send_command(
            {"cmd": "get_state"},
            BASE_COMMANDS_TOPIC
        )
        self.send_command(
            {"cmd": "get_state"},
            SHUTTER_COMMANDS_TOPIC
        )

        threading.Timer(5.0, self.finish_connect).start()

    def finish_connect(self):
        if not self.state.base_online:
            self.state.error = Errors.DEVICES_NOT_RESPONDING
            self.state.error_message = "Los dispositivos no responden."
            print("Error:", self.state.error_message)
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
        self.send_command(
            {"cmd": "abortslew"},
            BASE_COMMANDS_TOPIC
        )
        self.send_command(
            {"cmd": "abortslew"},
            SHUTTER_COMMANDS_TOPIC
        )
        return
        
    def get_flap_status(self):
        return self.state.flap_status
    
    # TO DO: borrar flags de error
    def connect(self):
        self.state = DomeState()
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
        if self.state.error and self.state.error == Errors.SHUTTER_ERROR:
            raise AlpacaException(Errors.SHUTTER_ERROR, self.state.error_message)
        # Si el gajo está arriba y la cortina está abierta, abriéndose o cerrándose, levantar error.
        if self.state.flap_status == 0 and (self.state.shutter_status == 0 or self.state.shutter_status == 2 or self.state.shutter_status == 3):
            raise AlpacaException(1035, "La cortina no está cerrada. Debe estar cerrada para abrir sin gajo.")
        
        # Enviar comando solo si el gajo está abajo y cortina está cerrada o cerrándose. Cuando la cortina está abriéndose o
        # está abierta y el gajo está abajo, se asume que se está abriedo o está abierta sin gajo y no se hace nada.
        if (self.state.flap_status == 1 and self.state.shutter_status == 1) or (self.state.flap_status == 1 and self.state.shutter_status == 3):
            print("Abriendo domo sin gajo")
            self.send_command(
                {"cmd": "open_without_flap"},
                SHUTTER_COMMANDS_TOPIC
            )
            return

    def close_shutter(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.shutter_online:
            raise AlpacaException(1035, "Cortina no conectada. Mueva el domo a Home para energizar la cortina.")
        if self.state.error and self.state.error == Errors.SHUTTER_ERROR:
            raise AlpacaException(Errors.SHUTTER_ERROR, self.state.error_message)
        if self.state.shutter_status == 0 or 2:
            self.send_command(
                {"cmd": "closeshutter"},
                SHUTTER_COMMANDS_TOPIC
            )
            return
    
    def find_home(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if self.state.slaved:
            raise AlpacaException(1033, "Operación inválida cuando el domo está slaved.")
        if self.state.error and self.state.error == Errors.FIND_HOME_ERROR:
            raise AlpacaException(Errors.FIND_HOME_ERROR, self.state.error_message)
        self.send_command(
            {"cmd": "findhome"},
            BASE_COMMANDS_TOPIC
        )
        return

    def open_shutter(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.shutter_online:
            raise AlpacaException(1035, "Cortina no conectada. Mueva el domo a Home para energizar la cortina")
        if self.state.error and self.state.error == Errors.SHUTTER_ERROR:
            raise AlpacaException(Errors.SHUTTER_ERROR, self.state.error_message)
        if self.state.shutter_status == 1 or 3:
            self.send_command(
                {"cmd": "openshutter"},
                SHUTTER_COMMANDS_TOPIC
            )
            return
        
    def park(self):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
        if not self.state.base_online:
            raise AlpacaException(1031, "Controlador de domo no disponible. Revise el hardware o conexión MQTT.")
        if self.state.error and self.state.error == Errors.FIND_HOME_ERROR:
            raise AlpacaException(Errors.FIND_HOME_ERROR, self.state.error_message)
        if not self.state.at_park:
            self.send_command(
                {"cmd": "park"},
                BASE_COMMANDS_TOPIC
            )

    def slew_to_azimuth(self, az):
        if not self.state.connected:
            raise AlpacaException(1031, "El dispositivo no está conectado.")
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
        if self.state.error and self.state.error == Errors.DOME_STALL_ERROR:
            raise AlpacaException(Errors.DOME_STALL_ERROR, self.state.error_message)
        if az > 360 or az < 0:
            raise AlpacaException(
                number=1025,
                message="Valor de azimut inválido. Debe ser entre 0 y 360."
            ) 

        self.send_command(
            {
            "cmd": "slewtoazimuth",
            "azimuth": az
            },
            BASE_COMMANDS_TOPIC
        )

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
        if self.state.error and self.state.error == Errors.DOME_STALL_ERROR:
            raise AlpacaException(Errors.FIND_HOME_ERROR, self.state.error_message)
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
            self.last_base_update = datetime.datetime.now()
        if "shutter_online" in event:
            self.state.shutter_online = event["shutter_online"]
            self.last_shutter_update = datetime.datetime.now()
        if "azimuth" in event:
            self.state.azimuth = event["azimuth"]
        if "dome_slewing" in event:
            self.state.dome_slewing = event["dome_slewing"]
        if "at_home" in event:
            self.state.at_home = event["at_home"]
        if "at_park" in event:
            self.state.at_park = event["at_park"]
        if "shutter_status" in event:
            # Evitar que se actualice el estado del shutter si hubo un error
            if not self.state.error and not self.state.error == Errors.SHUTTER_ERROR:
                self.state.shutter_status = event["shutter_status"]
        if "flap_status" in event:
            self.state.flap_status = event["flap_status"]
        if "slaved" in event:
            self.state.slaved = event["slaved"]
        if self.state.shutter_status in [2, 3] or self.state.dome_slewing:
            self.state.slewing = True
        else:
            self.state.slewing = False
        if "error" in event:
            error = event["error"]
            print(f"Error: {error}")
            match error:
                case Errors.SHUTTER_ERROR:
                    self.state.error = Errors.SHUTTER_ERROR
                    self.state.error_message = event["message"]
                    self.state.shutter_status = 4
                case Errors.DOME_STALL_ERROR:
                    self.state.error = Errors.DOME_STALL_ERROR
                    self.state.error_message = "No se detectó movimiento del domo. Revise cableado y motor."
                case Errors.FIND_HOME_ERROR:
                    self.state.error = Errors.FIND_HOME_ERROR
                    self.state.error_message = event["message"]

        #print("Dome state updated:", self.state)

    def get_connected(self):
        return self.state.connected
    
    def _heartbeat_watchdog(self):
        while self._watchdog_running:
            now = datetime.datetime.now()

            if self.last_base_update:
                delta = (now - self.last_base_update).total_seconds()
                if delta > HEARTBEAT_TIMEOUT:
                    if self.state.base_online:
                        print("Base perdido")
                    self.state.base_online = False
                    self.state.error = Errors.DEVICES_NOT_RESPONDING
                    self.state.error_message = "Se perdió la conexión con la base."
            else:
                self.state.base_online = False

            if self.last_shutter_update:
                delta = (now - self.last_shutter_update).total_seconds()
                if delta > HEARTBEAT_TIMEOUT:
                    if self.state.shutter_online:
                        print("Shutter perdido")
                    self.state.shutter_online = False
            else:
                self.state.shutter_online = False
            
            time.sleep(1)

controller = DomeController()