import time

from cryptography.fernet import Fernet
import socket

key = Fernet.generate_key()
print(key)
encrypting_object = Fernet(key)

sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_socket.connect(("10.100.102.14", 6744))

sending_socket.send(key)
time.sleep(1)

try:
    with open("C:/Users/shamr/Documents/Study/cyber_project/ability1.drawio (1).png", "rb") as f:
        while True:
            bytes_read = f.read(1024)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transmission in
            # busy networks
            encrypted_bytes = encrypting_object.encrypt(bytes_read)
            sending_socket.sendall(encrypted_bytes)
            print(encrypted_bytes)

except Exception as exception:
    print(exception)

