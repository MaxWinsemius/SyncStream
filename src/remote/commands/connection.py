#!/usr/bin/env python3

import struct
import socket
import os
from threading import Lock
import time

class CommandTypes:
    GET_INFO_CMD_ID    = 0
    SEND_BUFFER_CMD_ID = 1
    PING = 2
    STOP = 3
    DUMP_INTERFACES = 4 # Dump the yaml interfaces config
    LAYERS_ADD = 20
    LAYERS_DEL = 21

SEND_BUFFER_FAILED_RETRY_TIMEOUT = 3

class Connection:
    """
    Basic UNIX IPC socket connection handler
    """
    _MAGIC = 'TESLAN'
    _chunk_size = 1024  # in bytes
    _timeout = 0.5  # in seconds
    _struct_header = '=%dsII' % len(_MAGIC.encode('utf-8'))
    _struct_header_size = struct.calcsize(_struct_header)

    def __init__(self, socket_path, auto_reconnect=False):
        self._socket_path = socket_path
        self._connect()
        print(f"Connecting to socket path <{socket_path}>")
        self._cmd_lock = Lock()
        self._sub_socket = None
        self._sub_lock = Lock()
        self._auto_reconnect = auto_reconnect
        self._quitting = False

    def _connect(self):
        self._cmd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._cmd_socket.connect(self._socket_path)
    
    def _pack_string(self, msg_type, payload):
        """Packs the given message type and payload. Turns the resulting
        message into a byte string.
        """
        pb = payload.encode('utf-8')
        s = struct.pack('=II', len(pb), msg_type)
        return self._MAGIC.encode('utf-8') + s + pb

    def _pack_integers(self, msg_type, integer_iterable):
        pb = struct.pack(f'={len(integer_iterable)}I', *integer_iterable)
        s = struct.pack('=II', len(integer_iterable), msg_type)
        return self._MAGIC.encode('utf-8') + s + pb

    def _unpack(self, data):
        """Unpacks the given byte string and parses the result from JSON.
        Returns None on failure and saves data into "self.buffer".
        """
        msg_magic, msg_length, msg_type = self._unpack_header(data)
        msg_size = self._struct_header_size + msg_length
        # XXX: Message shouldn't be any longer than the data
        payload = data[self._struct_header_size:msg_size]
        return payload.decode('utf-8', 'replace')

    def _unpack_header(self, data):
        """Unpacks the header of given byte string.
        """
        return struct.unpack(self._struct_header, data[:self._struct_header_size])

    def _ipc_recv(self, sock):
        data = sock.recv(14)

        if len(data) == 0:
            return '', 0

        msg_magic, msg_length, msg_type = self._unpack_header(data)
        msg_size = self._struct_header_size + msg_length
        while len(data) < msg_size:
            data += sock.recv(msg_length)
        payload = self._unpack(data)
        return payload, msg_type

    def _ipc_send(self, sock, message_type, payload):
        """Send and receive a message from the ipc.  NOTE: this is not thread
        safe
        """
        sock.sendall(self._pack_string(message_type, payload))
        data, msg_type = self._ipc_recv(sock)
        return data

    def _wait_for_socket(self):
        # for the auto_reconnect feature only
        socket_path_exists = False
        for tries in range(0, 500):
            socket_path_exists = os.path.exists(self._socket_path)
            if socket_path_exists:
                break
            time.sleep(0.001)

        return socket_path_exists

    def _message(self, message_type, payload):
        try:
            self._cmd_lock.acquire()
            return self._ipc_send(self._cmd_socket, message_type, payload)
        except ConnectionError as e:
            if not self._auto_reconnect:
                raise e

            # XXX: can the socket path change between restarts?
            if not self._wait_for_socket():
                raise e

            self._connect()
            
            return self._ipc_send(self._cmd_socket, message_type, payload)
        finally:
            self._cmd_lock.release()

    def get_something(self, type, payload=""):
        data = self._message(type, payload)
        return data

    def send_buffer(self, buffer, failed=False):
        try:
            self._cmd_lock.acquire()
            if failed: self._connect()
                
            self._cmd_socket.sendall(self._pack_integers(CommandTypes.SEND_BUFFER_CMD_ID, [e for E in buffer for e in E]))
            if failed: print("Connection re-established!")
        except ConnectionError as e:
            if not self._auto_reconnect:
                raise e
            if not failed: print("Connection Error! I'll keep retrying...")
            time.sleep(SEND_BUFFER_FAILED_RETRY_TIMEOUT)
            self._cmd_lock.release()
            self.send_buffer(buffer, failed=True)
        finally:
            if self._cmd_lock.locked(): self._cmd_lock.release()
            

    def close(self):
        self._cmd_socket.close()
