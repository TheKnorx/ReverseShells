# Handler for sending and receiving in en/decrypted form
from EnDeCrypt import encryptStringSymmetrical, decryptStringSymmetrical

key = "null"
client = "null"


def send(text) -> None:
    text = text.encode() if type(text) != bytes else text
    client.send(encryptStringSymmetrical(str(len(text)).zfill(10), key))
    client.send(text)


def recv() -> str:
    buffer = int(decryptStringSymmetrical(client.recv(100), key))
    encrypted_text = client.recv(buffer)
    return decryptStringSymmetrical(encrypted_text, key)