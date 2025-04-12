import os
from time import sleep


dest11 = "ClientInControl/EnDeCrypt.py"
dest12 = "ClientSlave/EnDeCrypt.py"
dest13 = "Agent/EnDeCrypt.py"

dest21 = "ClientInControl/sock_op_handler.py"
dest22 = "ClientSlave/sock_op_handler.py"
dest23 = "Agent/sock_op_handler.py"

dest31 = "ClientInControl/sock_status_codes.py"
dest32 = "ClientSlave/sock_status_codes.py"
dest33 = "Agent/sock_status_codes.py"

file1 = "pubFiles/EnDeCrypt.py"
file2 = "pubFiles/sock_op_handler.py"
file3 = "pubFiles/sock_status_codes.py"

f1Destinations = [dest11, dest12, dest13]
f2Destinations = [dest21, dest22, dest23]
f3Destinations = [dest31, dest32, dest33]

update_list = [[file1, f1Destinations], [file2, f2Destinations], [file3, f3Destinations]]

pyAgent = "Agent/Agent.py"
pyClientSlave = "ClientSlave/ClientSlave.py"
pyInControl = "ClientInControl/ClientInControl.py"

pyFiles = [pyAgent, pyClientSlave, pyInControl]


def update_files():
    for update_instr in update_list:
        file = update_instr[0]
        print(f"Updating {file}")
        destinations = update_instr[1]
        with open(file, "r") as iFile:
            code = iFile.read()
            for dest in destinations:
                with open(dest, "w") as oFile:
                    oFile.write(code)
    print("-- Done --")


def exec_():
    print("-- EXECUTING --")
    exit()
    for pyFile in pyFiles:
        os.system(f"python {pyFile}")
        sleep(1.5)


if __name__ == '__main__':
    update_files()
    exec_()
