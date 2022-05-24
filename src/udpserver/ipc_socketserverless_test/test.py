#!/usr/bin/python
import socket

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind('/run/syncstream/virt-1')
    while True:
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            print("Connection!")
            while True:
                data = conn.recv(8096)
                if not data:
                    break
                print(data)
                conn.sendall(data)
