from http.server import HTTPServer, BaseHTTPRequestHandler
from time import sleep
from threading import Thread
from datetime import datetime

import urllib.parse
import pathlib
import mimetypes
import socket
import threading
import json


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)
                
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        self.save_data_to_json(data_dict)
        print(f'Received: {data_dict}')
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
            
    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())
            
    def socket_client(data):
        host = socket.gethostname()
        port = 5000
        with socket.socket() as s:
            while True:
                try:
                    s.connect((host, port))
                    s.sendall(b'Hello, world')
                    data = s.recv(1024)
                    break
                except ConnectionRefusedError:
                    sleep(0.5)
                    
    def save_data_to_json(self, data):
        json_file = pathlib.Path() / 'storage' / 'data.json'
        date = str(datetime.now()).split('.')[0]
        
        with open(json_file, 'r+') as f:
            data_json = json.load(f)
            data_json[date] = data
            f.seek(0)
            json.dump(data_json, f, indent=4)
            f.truncate()
       


def echo_server():
    host = socket.gethostname()
    port = 5000
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
        s.bind((host, port))
        s.listen(2)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                print(f'From client: {data}')
                if not data:
                    break
                
                
def socket_client(data):
    host = socket.gethostname()
    port = 5000
    with socket.socket() as s:
        while True:
            try:
                s.connect((host, port))
                s.sendall(b'Hello, world')
                data = s.recv(1024)
                print(f'From server: {data}')
                break
            except ConnectionRefusedError:
                sleep(0.5)

def run(server_class=HTTPServer, handler_class=HttpHandler):
    print('Start server')
    server_address = ('', 3000)
    
    http = server_class(server_address, handler_class)
    try:
        socket_server = Thread(target=echo_server)
        print('Sockt server start')
        socket_server.start()
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
