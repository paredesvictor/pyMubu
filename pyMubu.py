from dataclasses import dataclass, field
from types import DynamicClassAttribute
import argparse
from pythonosc import dispatcher, osc_server, udp_client
from copy import deepcopy

@dataclass
class Buffer:
    name: str = ''
    max_size: int = 256
    size: int = 0
    sample_rate: float = 1000.0
    sample_offset: float = 0.0
    mx_rows: int = 1
    mx_cols: int = 1
    mx_data: list[float] = field(default_factory=list)
    timeTags: list[float] = field(default_factory=list)
    info: list[str] = field(default_factory = lambda: [''])

@dataclass
class Track:
    name: str = ''
    mx_cols: int = 1
    mx_rows: int = 1
    has_var_rows: bool = False
    mx_col_names: list[str] = field(default_factory = lambda: [''])
    has_time_tags: bool = False
    non_num_types: str = 'none'
    max_size: str = 256
    buffers: list[Buffer] = field(default_factory = lambda: [Buffer()])

    def updateNumBuffer(self, num_buffer):
        buffer_diff = num_buffer - len(self.buffers)
        buffer = deepcopy(self.buffers[-1])
        self.buffers += [buffer for i in range(buffer_diff)]

@dataclass
class Container:
    num_buffer: int = 1
    num_tracks: int = 0
    buffer_names: list[str] = field(default_factory = lambda: [''])
    tracks: list[Track] = field(default_factory = list)

    def addTrack(self):
        track = Track()
        track.updateNumBuffer(self.num_buffer)

    def addBuffer(self):
        self.numBuffer += 1
        for track in self.tracks:
            track.updateNumBuffer(self.numBuffer)

class MubuLink:

    def __init__(self, listening_port, sending_port, ip='127.0.0.1'):
        parser_client = argparse.ArgumentParser()
        parser_client.add_argument('--ip', default='127.0.0.1')
        parser_client.add_argument('--port', type=int, default=sending_port)
        args_client = parser_client.parse_args()

        parser_server = argparse.ArgumentParser()
        parser_server.add_argument('--ip', default='127.0.0.1')
        parser_server.add_argument('--port', type=int, default=listening_port)
        args_server = parser_server.parse_args()
        dispatch = self.generateDispatcher()
    
        self.client = udp_client.SimpleUDPClient(args_client.ip, args_client.port)
        self.server = osc_server.ThreadingOSCUDPServer(
            (args_server.ip, args_server.port), 
            dispatch
            )
        
        self.container = Container()
    
    def generateDispatcher(self):
        methods = tuple([ m for m in dir(self) if not m.startswith('__') or m == ''])
        dispatch = dispatcher.Dispatcher()
        for method in methods:
            if method != 'generateDispatcher':
                address = ''.join(('/', method))
                eval('dispatch.map("{}", self.{})'.format(address, method))

    def addTrack(self, addrs, *unused):
        self.container.addTrack()
    
    def addBuffer(self, addrs, *unused):
        self.container.addBuffer()

if __name__ == '__main__':
    mubu = MubuLink(8011, 8012)