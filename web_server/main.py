import socket
import time
import re
import threading
import select

HOST = '127.0.0.1'
PORT = 1337


class HttpHandler():
    def __init__(self):
        self.handlers = {}
    
    def add_handler(self, path, method, fun):
        '''
            Add handler, single route could have multiple handler to handle different method
            TODO: Update path to regex
        '''
        if path in self.handlers:      #Route already exist
            self.handlers[path][method] = fun      
        else:                          #Route doesn't exist
            self.handlers[path] = {}
            self.handlers[path][method] = fun
    
    def handle(self, conn):
        '''
            Execute handler based on method type and path
        '''
        return ConnectionHandlerThread(conn, self.handlers)

    @staticmethod
    def is_valid(path, handlers):
        for pattern in handlers.keys():
            if re.fullmatch(pattern, path):
                return pattern
        return False
    
    @staticmethod
    def parse_url_params(pattern, path):
        return re.fullmatch(pattern, path).groups()

    @staticmethod
    def parse_body_params(body):
        gr = re.findall('([A-Za-z0-9%.]+=[A-Za-z0-9%.]+)', body)
        args = {}
        for item in gr:
            [k, v] = item.split('=')
            args[k] = v
        return args
        

class ConnectionHandlerThread(threading.Thread):
    RES_404 = b'HTTP/1.0 404 Not Found\nConnection: close\nContent-Length: 0\n\n'
    RES_501 = b'HTTP/1.0 500 Not Implemented\nConnection: close\nContent-Length: 0\n\n'
    HEAD_200 = b'HTTP/1.0 200 OK\nConnection: close\nContent-Length: '

    def __init__(self, conn, handlers):
        super(ConnectionHandlerThread, self).__init__()
        data = conn.recv(2048)
        data_split = data.decode().split(' ')

        self.method = data_split[0]
        self.path = data_split[1]
        if (self.method == 'POST'):
            print(data)
            self.body = data.decode().split('\r\n\r\n')[1]
        else:
            self.body = None

        self.handlers = handlers
        self.conn = conn

    def run(self):
        re_path = HttpHandler.is_valid(self.path, self.handlers)
        if re_path:
            if self.method in self.handlers[re_path]:
                if self.method == 'POST':
                    params = HttpHandler.parse_body_params(self.body)
                    result = self.handlers[re_path]['POST'](**params)
                    header = self.HEAD_200 + str(len(result)).encode() + b'\n\n'
                    response = header + result
                    print(f'[+] Respond 200: {response.decode()}')
                    self.conn.sendall(response)
                else:
                    params = HttpHandler.parse_url_params(re_path, self.path)
                    result = self.handlers[re_path][self.method](*params)
                    header = self.HEAD_200 + str(len(result)).encode() + b'\n\n'
                    response = header + result
                    print(f'[+] Respond 200: {response.decode()}')
                    self.conn.sendall(response)
                return
            else:
                print('[-] Respond 501')
                self.conn.sendall(self.RES_501)
        else:
            print('[-] Respond 404')
            self.conn.sendall(self.RES_404)

def sleep(*args, **kwargs):
    if len(args) > 0:
        time.sleep(int(args[0])/1000)
        res = str(time.time())
        return res.encode()
    elif 'duration' in kwargs.keys():
        time.sleep(int(kwargs['duration'])/1000)
        res = str(time.time())
        return res.encode()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(10)
    sock.setblocking(False)
    read_list = [sock]
    
    # Init Handler
    httpHandler = HttpHandler()
    httpHandler.add_handler('/execute/([0-9]*)', 'GET', sleep)
    httpHandler.add_handler('/execute', 'POST', sleep)

    print(f'[*] Started listening on port {PORT}')

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
                    connThread = httpHandler.handle(el)
                    connThread.start()
                except Exception as e:
                    print(e)
                read_list.remove(el)