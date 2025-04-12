# Agent that operates like a bridge and transfers data from one to another client_connection
# without being able to see the plain traffic, because its peer-to-peer encrypted.

import socket
from time import sleep
import sock_op_handler
from threading import Thread
from datetime import datetime
import sock_status_codes as codes


bind_ip = "127.0.0.1"
bind_port = 4444
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_errors = (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ValueError)  # == ConnectionError.__class__


def log(text: (str, bytes)):
    print(str(datetime.now().strftime("%H:%M:%S")) + " ->", repr(text).strip("''"))


def __init_server__():
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((bind_ip, bind_port))
    log(f"Bound on {bind_ip}:{bind_port}")
    server_socket.listen(2)
    log(f"Listening for 2 connection on {bind_ip}:{bind_port}")


class client_handler:
    connected = False
    client_connection = socket.socket()
    address = None
    connection_thread = None
    public_key = None

    def __init__(self):
        self.connection_thread = Thread(target=self.getConnection)

    def run(self):
        self.connection_thread.start()

    def getConnection(self):
        while True:
            sleep(2)
            while not self.connected:
                try:
                    self.client_connection, self.address = server_socket.accept()
                    self.connected = True
                except connection_errors:
                    log("E  |  Lost connection to client_connection")
                    self.connected = False

    def send(self, text):
        sock_op_handler.send(text)

    def recv(self):
        return sock_op_handler.recv()


def exchange_keys():
    client1_code = client1.client_connection.recv(1)
    client2_code = client1.client_connection.recv(1)
    if client1_code == codes.sending:





if __name__ == '__main__':
    client1 = client_handler()
    client2 = client_handler()
    client1.run()
    client2.run()


