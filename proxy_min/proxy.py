import socket
import time
import re
import threading
import select

HOST = '127.0.0.1'
PORT = 7175

class ConnectionHandlerThread(threading.Thread):
    def __init__(self, conn, handlers):
        super(ConnectionHandlerThread, self).__init__()
        data = conn.recv(2048)
        data_split = data.decode().split(' ')

        self.method = data_split[0]
        self.path = data_split[1]
        self.data = data
        self.handlers = handlers
        self.conn = conn

    def run(self):
        '''
            Print status (connected, headers)
            Block jika termasuk blacklist
            Ubah headers menjadi dict
            Pilihan edit headers/continue
        '''
        print(self.data)
        print(self.path)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsck:
            lsck.settimeout(10)
            lsck.connect((self.path, 80))
            lsck.sendall(self.data)
            while True:
                # receive data from web server
                recv_data = lsck.recv(2048)

                if (len(recv_data) > 0):
                    print(recv_data.decode())
                    self.conn.send(recv_data)
                else:
                    return

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(10)
    sock.setblocking(False)
    read_list = [sock]

    print(f'[*] Started proxy on port {PORT}')

    while True:
        readable, writable, errored = select.select(read_list, [], [])
        for el in readable:
            if el is sock:
                conn, addr = sock.accept()
                conn.setblocking(False)
                print(f'[+] Connected by {addr}')
                read_list.append(conn)
            else:
                try:
                    connThread = ConnectionHandlerThread(el)
                    connThread.start()
                except Exception as e:
                    print(e)
                read_list.remove(el)