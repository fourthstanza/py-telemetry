import serial
import queue
import threading
import tomllib
from abc import ABC, abstractmethod

class Transport(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_bytes(self, timeout) -> bytes | None:
        pass

class SerialReader(Transport):
    def __init__(
            self,
            port: str, 
            queuelength: int = 4096, 
            baudrate: int = 115200, 
            bytesize: str = "EIGHTBITS", 
            parity: str = "PARITY_NONE", 
            stopbits = serial.STOPBITS_ONE, 
            timeout: float | None = 0.1,
            chunklength: int = 1
        ):
        
        self._port = port
        self._queuelength = queuelength
        self._queue = queue.Queue(maxsize = self._queuelength)
        self._baudrate = baudrate
        self._timeout = timeout
        self._running: bool = True
        self._thread = None
        self._chunklength = chunklength

        match bytesize:
            case("FIVEBITS" | "5"):
                self._bytesize = serial.FIVEBITS
            case("SIXBITS" | "6"):
                self._bytesize = serial.SIXBITS
            case("SEVENBITS" | "7"):
                self._bytesize = serial.SEVENBITS
            case("EIGHTBITS" | "8"):
                self._bytesize = serial.EIGHTBITS
            case _:
                print("Unknown bytesize, defaulting to eight bits")
                self._bytesize = serial.EIGHTBITS

        match parity:
            case("PARITY_NONE"):
                self._parity = serial.PARITY_NONE
            case("PARITY_EVEN"):
                self._parity = serial.PARITY_EVEN
            case("PARITY_ODD"):
                self._parity = serial.PARITY_ODD
            case("PARITY_MARK"):
                self._parity = serial.PARITY_MARK
            case("PARITY_SPACE"):
                self._parity = serial.PARITY_SPACE
            case _:
                print("Unknown parity, defaulting to none")
                self._parity = serial.PARITY_NONE

        match stopbits:
            case("STOPBITS_ONE" | "1"):
                self._stopbits = serial.STOPBITS_ONE
            case("STOPBITS_ONE_POINT_FIVE" | "1.5"):
                self._stopbits = serial.STOPBITS_ONE_POINT_FIVE
            case("STOPBITS_TWO" | "2"):
                self._stopbits = serial.STOPBITS_TWO
            case _:
                print("Unknown stop bits, defaulting to one")
                self._stopbits = serial.STOPBITS_ONE

        self._reader = serial.Serial(
            self._port, 
            self._baudrate, 
            self._bytesize, 
            self._parity, 
            self._stopbits, 
            self._timeout
        )

    def start(self)  -> None:
        if not self._reader.is_open:
            self._reader.open()
        if self._running == False:
            self._thread = threading.Thread(
                target=self._read_loop,
                daemon=True
            )
            self._running = True
            self._thread.start

    def stop(self) -> None:
        self._running = False
        self._reader.close()

    def _read_loop(self):
        while self._running:
            byte = self._reader.read(self._chunklength)
            if byte:
                self._queue.put(byte, block=False)

    def get_bytes(self, timeout) -> bytes | None:
        try:
            return self._queue.get(timeout = timeout)
        except queue.ShutDown:
            return None
