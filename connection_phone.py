#
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import pickle
import os
import time
from cryptography.fernet import Fernet



class MainSendingSocket(QThread):
    got_file_list = pyqtSignal(list)
    ready_to_send = pyqtSignal()
    send_massage = pyqtSignal(str)
    done_signal = pyqtSignal()
    exception_rose = pyqtSignal(str)


    def __init__(self, ip, port, key):
        super(MainSendingSocket, self).__init__()
        self.ip = ip
        self.port = port
        self.sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encrypting_object = Fernet(key)

        self.mutex = QMutex()
        self.condition = QWaitCondition()

        self.got_file_list.connect(self.got_files)
        self.ready_to_send.connect(self.ready_to_send_files)
        self.send_massage.connect(self.send)
        self.done_signal.connect(self.done)
        self.done_condition = False
        self.files = []


    def run(self):
        self.mutex.lock()
        self.connect_to_phone()
        self.condition.wait(self.mutex)

        serialized_file_list = pickle.dumps(self.files)
        try:
            self.sending_socket.send(self.encrypting_object.encrypt(serialized_file_list))

            self.condition.wait(self.mutex)
            self.sending_socket.send(self.encrypting_object.encrypt("ready for files".encode()))

            while True:
                self.condition.wait(self.mutex)
                self.sending_socket.send(self.encrypting_object.encrypt(self.message.encode()))
                if self.done_condition:
                    break

        except Exception as exception:
            self.exception_rose.emit(str(exception))

        self.mutex.unlock()
        
        self.sending_socket.close()

    def connect_to_phone(self):
        try:
            self.sending_socket.connect((self.ip, self.port))
        except Exception as exception:
            self.exception_rose.emit(str(exception))

    def got_files(self, files):
        self.files = files

        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def ready_to_send_files(self):
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def send(self, message):
        self.mutex.lock()
        self.message = message
        self.condition.wakeAll()
        self.mutex.unlock()

    def done(self):
        self.done_condition = True

class FileSendingSocket(MainSendingSocket):
    def __init__(self, ip, port, file_path, key):
        super(FileSendingSocket, self).__init__(ip, port, key)
        self.file_path = file_path
        self.BUFFER_SIZE = 1024

    def run(self):
        self.connect_to_phone()

        file_name = self.file_path.split("/")[-1]
        try:
            self.sending_socket.send(self.encrypting_object.encrypt(str(file_name).encode()))

            with open(self.file_path, "rb") as f:
                while True:
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transmission in
                    # busy networks
                    self.sending_socket.sendall(self.encrypting_object.encrypt(bytes_read))

        except Exception as exception:
                self.exception_rose.emit(str(exception))

        self.sending_socket.close()


class MainReceivingSocket(QThread):
    connection_made = pyqtSignal()
    got_file_list_from_phone = pyqtSignal(list)
    ready_for_files = pyqtSignal()
    receive = pyqtSignal(str) #wrong name
    done_signal = pyqtSignal()
    exception_rose = pyqtSignal(str)



    def __init__(self, ip, port):
        super(MainReceivingSocket, self).__init__()
        self.ip = ip
        self.port = port
        self.done_signal.connect(self.done)
        self.done_condition = False
        self.receiving_socket=None

    def run(self):
        self.handle_connection()
        try:
            serialized_file_list = self.encrypting_object.decrypt(self.receiving_socket.recv(1024))
            list_of_files = pickle.loads(serialized_file_list)

            self.got_file_list_from_phone.emit(list_of_files)

            message = self.encrypting_object.decrypt(self.receiving_socket.recv(1024)).decode()
            if message == "ready for files":
                self.ready_for_files.emit()

            while True:
                message = self.encrypting_object.decrypt(self.receiving_socket.recv(1024)).decode()
                self.receive.emit(message)  # add signal connected
                if self.done_condition:
                    break

        except Exception as exception:
            self.exception_rose.emit(str(exception))
            
        self.receiving_socket.close()

    def handle_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen()
        try:
            self.receiving_socket, self.address = sock.accept()
        except Exception as exception:
                self.exception_rose.emit(str(exception))

        sock.close()
        self.handle_address()

    def handle_address(self):
        self.connection_made.emit()

    def done(self):
        self.done_condition = True

    def add_encrypting_object(self, key):
        self.encrypting_object = Fernet(key)

class FileReceivingSocket(MainReceivingSocket):
    def __init__(self, ip, port, files_and_paths, key):
        super(FileReceivingSocket, self).__init__(ip, port, key)
        self.file = None
        self.BUFFER_SIZE = 1024
        self.files_and_paths = files_and_paths
        self.finished = False

    def run(self):
        self.handle_connection()
        try:
            file_name = self.encrypting_object.decrypt(self.receiving_socket.recv(self.BUFFER_SIZE)).decode()
            location = self.files_and_paths[file_name]
            time.sleep(1)

            with open(f"{location}/{file_name}", "wb") as file:
                while True:
                    # read 1024 bytes from the socket (receive)
                    bytes_read = self.encrypting_object.decrypt(self.receiving_socket.recv(self.BUFFER_SIZE))
                    if not bytes_read:
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    file.write(bytes_read)
            time.sleep(1)
        except Exception as exception:
            self.exception_rose.emit(str(exception))
        self.finished = True
        self.receiving_socket.close()

    def handle_address(self):
        pass