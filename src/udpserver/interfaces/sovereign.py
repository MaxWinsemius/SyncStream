"""
@author Max Winsemius
@date 15-01-2022

TODO:
- Finish layers
    - implement send_buffer to actually collect data and send it to a layer
    - implement smashing layers together
    - Implement alpha values to be send to the animation layers
    - Implement delete_layer
"""

from . import common
import os
import socket
import socketserver
import struct
import yaml

DEBUG = False

def deb_print(txt):
    if DEBUG:
        print(txt)

class Command:
    GET_INFO = 0
    SEND_BUFFER = 1

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        deb_print("entering while loop")
        while True:
            deb_print("exec while loop")
            data = self.request.recv(Socket._chunk_size).strip()
            deb_print("recv data")

            # Get headers
            msg_magic, msg_length, msg_type = Socket._unpack_header(Socket, data)

            if str(msg_magic, 'utf-8') != Socket._MAGIC:
                print("OH NO FUCK THAT AINT NO MAGIC")
                return

            # Execute command
            response = self.server._exec_cmd(msg_length, msg_type, data)
            deb_print("command exec'd")
            deb_print(f"resonse: {response}")

            if response:
                deb_print("returning request data")
                self.request.sendall(response)

            deb_print("exiting while loop")

class Socket(socketserver.ForkingMixIn, socketserver.UnixStreamServer):
    _MAGIC = 'TESLAN'
    _MAGIC_LEN = len(bytes(_MAGIC, 'utf-8'))
    _chunk_size = 8096
    _struct_header = f"={_MAGIC_LEN}sII"
    _struct_header_size = struct.calcsize(_struct_header)

    def __init__(self, root, path):
        self.root = root
        self.path = path

        if os.path.exists(path):
            os.remove(path)

        print(f"Socket served at {path}")
        socketserver.UnixStreamServer.__init__(self, path, Handler, True)

    def _unpack_header(self, data):
        return struct.unpack(self._struct_header, data[:self._struct_header_size])

    def _exec_cmd(self, msg_length, msg_type, data):
        if msg_type == Command.GET_INFO:
            return self.root.get_info()

        if msg_type == Command.SEND_BUFFER:
            return self.root.send_buffer(msg_length, data, self)

class Layer:
    def set_buffer(self, framebuffer):
        self.framebuffer = framebuffer

class Root:
    _CMD_ID_GET_INFO = 0
    _CMD_ID_SEND_BUFFER = 1

    def __init__(self, iface, path):
        self.iface = iface
        self.layers = []
        self.insert_layer(path, 0)

    def insert_layer(self, path, index, authorative = True):
        layer = Layer()
        layer.path = f"{path}-{len(self.layers)}"
        layer.socket = Socket(self, layer.path)
        layer.authorative = authorative
        self.layers.insert(index, layer)
        layer.socket.serve_forever()

    # TODO
    def delete_layer(self, index):
        pass

    def get_info(self):
        yaml_dat = yaml.dump({
            'num_leds': self.iface.length #TODO Add layer info here
        })
        yaml_bytes = bytes(yaml_dat, 'utf-8')

        return struct.pack(Socket._struct_header + f"{len(yaml_bytes)}s",
                           bytes(Socket._MAGIC, 'utf-8'),
                           len(yaml_bytes),
                           Command.GET_INFO,
                           yaml_bytes)

    def send_buffer(self, msg_length, data, socket):
        if msg_length % 3 != 0:
            print(f"received inconsistend buffer of length {msg_length} % 3 = {msg_length % 3}")
            return

        if msg_length / 3 != self.iface.length:
            print(f"Received buffer length of {msg_length} whilst interface is of length {self.iface.length}")
            return

        framebuffer = struct.unpack(f"={msg_length}I", data[Socket._struct_header_size:])

        self.iface.set_rgb_array(0, self.iface.length, framebuffer)
        self.iface.send_udp_framebuffer()
