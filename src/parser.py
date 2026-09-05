import queue
from transport import Transport

class TelemParser():
    def __init__(self, transport: Transport):
        self._transport = transport
        self._queue = queue.Queue

    def _parse(self):
        packet_start = 0
        packet_end = 0

    
        