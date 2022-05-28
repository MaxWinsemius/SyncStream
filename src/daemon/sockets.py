import socketserver
from . import commands

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        log(LogLevel.debug, "entering while loop")
        while True:
            log(LogLevel.ddebug, "exec while loop")
            data = self.request.recv(Socket._chunk_size).strip()
            log(LogLevel.ddebug, "recv data")

            # Get headers
            msg_magic, msg_length, msg_type = Socket._unpack_header(Socket, data)

            if str(msg_magic, 'utf-8') != Socket._MAGIC:
                print("OH NO FUCK THAT AINT NO MAGIC")
                return

            # Execute command
            response = self.server._exec_cmd(msg_length, msg_type, data)
            log(LogLevel.ddebug, "command exec'd")
            log(LogLevel.ddebug, f"resonse: {response}")

            if response:
                log(LogLevel.ddebug, "returning request data")
                self.request.sendall(response)

            log(LogLevel.ddebug, "exiting while loop")

class Socket(socketserver.UnixStreamServer):
    _MAGIC = 'TESLAN'
    _MAGIC_LEN = len(bytes(_MAGIC, 'utf-8'))
    _chunk_size = 8096
    _struct_header = f"={_MAGIC_LEN}sII"
    _struct_header_size = struct.calcsize(_struct_header)

    def __init__(self, path, animation_path):
        self.path = path
        # TODO: Create animation handler
        self.animation_path = animation_path

        if os.path.exists(path):
            os.remove(path)

        print(f"Socket served at {path}")
        socketserver.UnixStreamServer.__init__(self, path, Handler, True)

    def _unpack_header(self, data):
        return struct.unpack(self._struct_header, data[:self._struct_header_size])

    def _exec_cmd(self, msg_length, msg_type, data):
        if msg_type == commands.EXIT:
            # TODO: finish animation handler
            #self.animations.exit()
            exit(0)

        #if msg_type == Command.GET_INFO:
        #    return self.root.get_info()

        #if msg_type == Command.SEND_BUFFER:
        #    return self.root.send_buffer(msg_length, data, self)
