import time

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import pickle
import os
from cryptography.fernet import Fernet



class MainSendingSocket(QThread):
    got_file_list = pyqtSignal(list)
    ready_to_send = pyqtSignal()
    send_massage = pyqtSignal(str)
    done_signal = pyqtSignal()
    exception_rose = pyqtSignal(str)

    def __init__(self, ip, port, key):
        super(MainSendingSocket, self).__init__()
        # here i set up all the important information for the connection
        self.ip = ip
        self.port = port
        self.sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encrypting_object = Fernet(key)

        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # here i connect the signals of this class to a slot
        self.got_file_list.connect(self.got_files)
        self.ready_to_send.connect(self.ready_to_send_files)
        self.send_massage.connect(self.send)
        self.done_signal.connect(self.done)
        self.done_condition = False

        self.files = []

    def run(self):
        self.mutex.lock()
        # here it connects to the phone and then waits until it has the list of files to send
        self.connect_to_phone()
        self.condition.wait(self.mutex)

        # it converts the file list to bytes and sends it
        serialized_file_list = pickle.dumps(self.files)

        try:
            self.sending_socket.send(self.encrypting_object.encrypt(serialized_file_list))

            # here it wait again until the computer is ready to start sending the files
            self.condition.wait(self.mutex)
            self.sending_socket.send(self.encrypting_object.encrypt("ready for files".encode()))

            while True:
                # here it waits until the project tells it to send a message
                # the message is that either a socket opened or that a socket connected
                self.condition.wait(self.mutex)
                self.sending_socket.send(self.encrypting_object.encrypt(self.message.encode()))
                if self.done_condition:
                    break

        except Exception as exception:
            self.exception_rose.emit(str(exception))
        self.sending_socket.close()
        print(4)
        self.mutex.unlock()

    def connect_to_phone(self):
        # this function connects to the socket on the phone
        try:
            self.sending_socket.connect((self.ip, self.port))

        except Exception as exception:
            self.exception_rose.emit(str(exception))


    def got_files(self, files):
        # when the program will have the files a signal will be emitted to this slot and this will run
        # this function sets the file list and tells the program to stop waiting and continue
        self.files = files

        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def ready_to_send_files(self):
        # when the program will be ready to send the files a signal will be emitted to this slot and this will run
        # this function tells the program to stop waiting and continue
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def send(self, message):
        # when the program needs to send a message (during the file sending) a signal will be emitted to this slot and this will run
        # this function sets the message list and tells the program to stop waiting and continue
        self.mutex.lock()
        self.message = message
        self.condition.wakeAll()
        self.mutex.unlock()

    def done(self):
        # when the program is done a signal will be emitted to this slot and this will run
        # this function sets the done condition to true list and tells the program to stop waiting and continue
        self.done_condition = True
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()


class FileSendingSocket(MainSendingSocket):
    def __init__(self, ip, port, file_path, key):
        super(FileSendingSocket, self).__init__(ip, port, key)
        self.file_path = file_path
        self.BUFFER_SIZE = 1024

    def run(self):
        self.connect_to_phone()

        # we send the socket the file name
        file_name = self.file_path.split("/")[-1]
        try:
            self.sending_socket.send(self.encrypting_object.encrypt(str(file_name).encode()))

            with open(self.file_path, "rb") as f:
                while True:
                    # we read 1024 bytes from the file
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break

                    # we encrypt the data
                    encrypted_bytes = self.encrypting_object.encrypt(bytes_read)
                    size = len(encrypted_bytes)

                    # we send the size and then the data
                    self.sending_socket.send(str(size).encode())
                    message = self.sending_socket.recv(self.BUFFER_SIZE)
                    self.sending_socket.send(encrypted_bytes)


        except Exception as exception:
            self.exception_rose.emit(str(exception))
        print(2)
        self.sending_socket.close()


class MainReceivingSocket(QThread):
    connection_made = pyqtSignal(tuple)
    got_file_list_from_phone = pyqtSignal(list)
    ready_for_files = pyqtSignal()
    receive = pyqtSignal(str)
    done_signal = pyqtSignal()
    exception_rose = pyqtSignal(str)

    def __init__(self, ip, port, key):
        super(MainReceivingSocket, self).__init__()
        # here i set up all the important information for the connection
        self.ip = ip
        self.port = port
        self.done_signal.connect(self.done)
        self.done_condition = False
        self.encrypting_object = Fernet(key)



    def run(self):
        self.handle_connection()
        try:
            # we receive the file list and emit to the project object
            serialized_file_list = self.encrypting_object.decrypt(self.receiving_socket.recv(1024))
            list_of_files = pickle.loads(serialized_file_list)

            self.got_file_list_from_phone.emit(list_of_files)

            # we wait to receive a message that the phone is ready for sending
            message = self.encrypting_object.decrypt(self.receiving_socket.recv(1024)).decode()
            if message == "ready for files":
                self.ready_for_files.emit()

            while True:
                # here it waits to receive a message
                # the message is that either a socket opened or that a socket connected
                message = self.encrypting_object.decrypt(self.receiving_socket.recv(1024)).decode()
                self.receive.emit(message)
                if self.done_condition:
                    break

        except Exception as exception:
            self.exception_rose.emit(str(exception))
        print(3)
        self.receiving_socket.close()

    def handle_connection(self):
        # here we open a socket and listen for connections on the address specified
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
        self.connection_made.emit(self.address)


    def done(self):
        self.done_condition = True

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
            # here we receive the file name form the socket
            file_name = self.encrypting_object.decrypt(self.receiving_socket.recv(self.BUFFER_SIZE)).decode()
            location = self.files_and_paths[file_name]
            self.receiving_socket.settimeout(5)
            time.sleep(1)
            error_line = 0
            bytes_arrived_well = True

            with open(f"{location}/{file_name}", "wb") as file:
                while True:
                    error_line = 0
                    # we read the size of the part from the socket

                    try:
                        if bytes_arrived_well:
                            size = self.receiving_socket.recv(1024)
                        else:
                            size = b'1464'
                            bytes_arrived_well = True
                    except:
                        size = b'1464'
                    error_line += 1
                    self.receiving_socket.send(size)
                    if size == b"":
                        # their is no next piece of data so it doesn't have a size
                        break
                    error_line += 1

                    size = int(size.decode())

                    # we receive the data and decrypt it
                    error_line += 1

                    encrypted_bytes = self.receiving_socket.recv(size)

                    if not encrypted_bytes:
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    error_line += 1

                    if encrypted_bytes.decode()[-1] != '=':
                        error_line += 1
                        rest_of_bytes = self.receiving_socket.recv(size)
                        rest_of_bytes = rest_of_bytes.split(b'=')
                        if len(rest_of_bytes) == 2:
                            if rest_of_bytes[1].isdigit():
                                bytes_arrived_well = False
                        rest_of_bytes = rest_of_bytes[0]
                        encrypted_bytes += rest_of_bytes + b'='

                    error_line += 1

                    if encrypted_bytes.decode()[-1] == '=':
                        bytes_read = self.encrypting_object.decrypt(encrypted_bytes)
                        file.write(bytes_read)
        except Exception as exception:
            self.exception_rose.emit(str(exception))
            print(str(exception) + file_name + str(error_line))
            print(1)
        print(2)
        self.finished = True
        self.receiving_socket.close()

    def handle_address(self):
        pass
