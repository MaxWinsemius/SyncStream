#!/usr/bin/env python
import socket
import sys
import struct

path = "/run/syncstream/virt-1"
magic = "TESLAN"
data = []
for i in range(25):
    data.extend([5, 0, 15])

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
    print("connecting")
    sock.connect(path)
    print("connected")
    s = struct.pack(f"={len(magic)}sII{len(data)}I", bytes(magic, "utf-8"), len(data), 1, *data)
    #s.append(struct.pack(f"={len(data)}I", *data))
    sock.sendall(s)
    print("send, waiting for recv")
    print("recvd")

print(f"Snet:     {data}")
print(f"Received: Not applicable")

print()
print(f"Snet:     getinfo")
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
    sock.connect(path)
    sock.sendall(struct.pack(f"={len(magic)}sII", bytes(magic, "utf-8"), 0, 0))
    r = sock.recv(8096)
    sock.sendall(struct.pack(f"={len(magic)}sII", bytes(magic, "utf-8"), 0, 0))
    r = sock.recv(8096)

struct_type = f"={len(magic)}sII"
msg_magic, msg_length, msg_type = struct.unpack(struct_type, r[:struct.calcsize(struct_type)])
_, _, _, yml = struct.unpack(f"={len(magic)}sII{msg_length}s", r)
received = str(yml, "utf-8")
print(f"Received: {received}")
