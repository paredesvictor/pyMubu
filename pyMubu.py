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
    max_size: int = 256
    buffers: list[Buffer] = field(default_factory = lambda: [Buffer()])

    def updateNumBuffer(self, num_buffer):
        buffer_diff = num_buffer - len(self.buffers)
        buffer = deepcopy(self.buffers[-1])
        self.buffers += [buffer for i in range(buffer_diff)]

    def setInfo(self, attribute, value):
        return
        
@dataclass
class Container:
    num_buffer: int = 1
    num_tracks: int = 0
    buffer_names: list[str] = field(default_factory = lambda: [''])
    tracks: list[Track] = field(default_factory = list)

    def addTrack(self):
        track = Track()
        track.updateNumBuffer(self.num_buffer)
        self.tracks.append(track)
        self.num_tracks += 1

    def addBuffer(self):
        self.numBuffer += 1
        for track in self.tracks:
            track.updateNumBuffer(self.numBuffer)

    def setTrackInfo(self, info):
        self.tracks[track_idx].setInfo(attribute, value)


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
        self.server = osc_server.BlockingOSCUDPServer(
            (args_server.ip, args_server.port), 
            dispatch
            )
        
        self.container = Container()
    
    def generateDispatcher(self):
        methods = tuple([ m for m in dir(self) if not m.startswith('__') or m == ''])
        dispatch = dispatcher.Dispatcher()
        for method in methods:
            if method not in ('generateDispatcher', 'connect'):
                address = ''.join(('/', method))
                eval('dispatch.map("{}", self.{})'.format(address, method))
        return dispatch

    def connect(self):
        print('serving...')
        self.server.serve_forever()

    def addTrack(self, addrs):
        self.container.addTrack()
    
    def addBuffer(self, addrs):
        self.container.addBuffer()

    def setTrackInfo(self, addrs, *info):
        track_idx = info[0] - 1
        att_name = info[1]
        value = info[2:]
        if att_name == 'name':
            attribute = 'name'
            value = str(value[0])
        if att_name == 'maxsize':
            attribute = 'max_size'
            value = int(value[0])
        if att_name == 'matrixrows':
            attribute = 'mx_rows'
            value = int(value[0])
        if att_name == 'matrixcols':
            attribute = 'mx_cols'
            value = int(value[0])
        if att_name == 'matrixvarrows':
            attribute = 'has_var_rows'
            value = bool(value[0])
        if att_name == 'matrixcolnames':
            attribute = 'mx_col_names'
            value = value
        if att_name == 'extradata':
            attribute = 'non_num_types'
            value = str(value[0])
        if att_name == 'timetagged':
            attribute = 'has_time_tags'
            value = bool(value[0])
        self.container.setTrackInfo(attribute, value)

if __name__ == '__main__':
    mubu = MubuLink(8011, 8012)
    mubu.connect()