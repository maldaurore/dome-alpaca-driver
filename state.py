from dataclasses import dataclass
from enum import Enum

class ShutterStatus(Enum):
    OPEN = 0
    CLOSED = 1
    OPENING = 2
    CLOSING = 3
    ERROR = 4

class FlapStatus(Enum):
    UP = 0
    DOWN = 1
    ERROR = 2

@dataclass
class DomeState:
    # CAMBIAR 'connected' AL TERMINAR EL DESARROLLO
    connected: bool = True
    azimuth: float = None
    dome_slewing: bool = None
    slewing: bool = None
    slaved: bool = False
    at_home: bool = None
    at_park: bool = None
    base_online: bool = None
    shutter_online: bool = None
    shutter_status: ShutterStatus = None
    flap_status: FlapStatus = None
    fatal_error: bool = None
    fatal_error_message: str = ""
