import socket
import time
import re
import threading
import select

HOST = '127.0.0.1'
PORT = 7175

BLACKLIST = ['.*?google.*', 'http://www\.columbia\.edu.*']

CLOSE_CONN = b'HTTP/1.0 200 OK\r\nConnection: close\r\nContent-Length: 0\r\n\r\n'
BLOCK_CONN = b'HTTP/1.0 403 Forbidden\r\nConnection: close\r\nContent-Length: 16\r\n\r\nBlocked by proxy'

class ConnectionHandlerThread(threading.Thread):

    def __init__(self, conn):
        super(ConnectionHandlerThread, self).__init__()
        data = conn.recv(2048)
        data_split = data.split(b' ')

        self.method = data_split[0].decode()
        self.path = data_split[1].decode()
        self.base_path = re.fullmatch('https?://(.*?)/.*', self.path).groups()[0]
        
        byte_headers = data.split(b'\r\n\r\n')[0].split(b'\r\n')[1:]
        self.headers = {}
        for header in byte_headers:
            [k, v] = header.decode().split(':', 1)
            self.headers[k] = v
        
        self.data = data
        self.conn = conn
        self.raddr, self.rport = conn.getpeername()


    def run(self):
        #Block connection if listed on blaclist
        for bl_path in BLACKLIST:
            if re.fullmatch(bl_path, self.path):
                self.conn.send(BLOCK_CONN)
                print(f'[-] Blocked connection to {self.path} (Blacklist)')
                return

        while True:
            choice = input(f'[?] Choose option for {self.raddr}:{self.rport} to {self.path} (C/E/B/?): ')
            if choice == 'C':
                break
            elif choice == 'E':
                # TODO: Implement edit headers
                print('Edit Headers')
                break
            elif choice == 'B':
                self.conn.send(BLOCK_CONN)
                print(f'[-] Blocked connection to {self.path}')
                return
            else:
                print('[i] Proxy Help:\nC - Forward the connection\nE - Edit header(s), then forward the connection\nB - Block the connection')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsck:
            lsck.settimeout(30)
            lsck.connect((self.base_path, 80))
            lsck.sendall(self.data)
            while True:
                try:
                    recv_data = lsck.recv(2048)

                    if (len(recv_data) > 0):
                        self.conn.send(recv_data)
                    else:
                        self.conn.send(CLOSE_CONN)
                        lsck.shutdown(socket.SHUT_RDWR)
                        lsck.close()
                        print(f'[-] Closed connection from {self.raddr}:{self.rport}')
                        return
                except:
                    self.conn.send(CLOSE_CONN)
                    lsck.shutdown(socket.SHUT_RDWR)
                    lsck.close()
                    print(f'[-] Closed connection from {self.raddr}:{self.rport}')
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