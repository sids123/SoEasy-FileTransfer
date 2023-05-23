from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from GUI_phone import *
from Connection_phone import *
import netifaces
from threading import Thread
import time
from cryptography.fernet import Fernet


class Project:
    def __init__(self):
# Get a list of network interfaces on the device
        interfaces = netifaces.interfaces()
        # Loop through the interfaces and find the one that is active and has an IP address
        for iface in interfaces:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                self.ip = addrs[netifaces.AF_INET][0]['addr']
                if self.ip != '127.0.0.1':
                    break
        # we set all the important stuff here
        self.port = 6745
        self.g_port = 6746
        self.main_window = MainWindow()
        self.main_receiving_socket = MainReceivingSocket(self.ip, self.port)
        self.got_files = False
        self.is_window2_finished = False
        self.ready_for_the_files = False
        self.is_phone_ready_for_the_files = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.files_received = []

        # here we connect all the signals from the sockets and windows
        self.main_receiving_socket.receive.connect(self.received_message)
        self.main_receiving_socket.connection_made.connect(self.handle_connection)
        self.main_receiving_socket.got_file_list_from_phone.connect(self.handle_files)
        self.main_receiving_socket.ready_for_files.connect(self.computer_ready_for_files)

        self.main_window.window1.CameraThread.got_data.connect(self.handle_data)
        self.main_window.window2.finished.connect(self.finished_window2)
        self.main_window.window3.all_files_have_location.connect(self.finished_window3)

        self.main_receiving_socket.exception_rose.connect(self.exception_rose)

        self.main_receiving_socket.start()

    def exception_rose(self, error_message):
        # this function gets called in case of an exception
        if error_message == "":
            self.main_window.change_to_message_win("error")
        else:
            self.main_window.change_to_message_win(error_message)

    def handle_data(self, data):
        # scan the qr code and we need to connect the the computer
        # the data we get is from the qr code
        data = data.split()
        self.computer_ip = data[0]
        self.computer_port = int(data[1])
        self.key = data[2].encode()
        self.main_receiving_socket.add_encrypting_object(self.key)
        # we start the sending socket so it will connect to the computer
        self.main_sending_socket = MainSendingSocket(self.computer_ip, self.computer_port, self.key)
        self.main_sending_socket.exception_rose.connect(self.exception_rose)
        self.main_sending_socket.start()

    def handle_connection(self):
        self.main_window.change_win()

    def handle_files(self, list_of_files):
        # this handles the file list from the computer and adds it to the GUI
        self.files_from_computer = list_of_files
        self.main_window.window3.add_files(self.files_from_computer)
        self.got_files = True
        if (self.is_window2_finished):
            self.main_window.change_win()

    def computer_ready_for_files(self):
        # this gets called when the computer sends a message that it is read to send the files
        self.is_phone_ready_for_the_files = True
        if self.ready_for_the_files:
            # if we are also ready to send the files the file sending starts
            self.main_window.change_to_message_win("transferring files")
            thread = Thread(target=self.send_files)
            thread.start()
        else:
            pass

    def send_files(self):
        self.file_sending_sockets = []
        self.file_recving_sockets = []
        self.mutex.lock()
        i=0
        # receiving the files
        self.sockets = ["" for f in self.files_and_paths.keys()]
        for file in self.files_and_paths:
            time.sleep(1)
            # opening a listening socket
            self.sockets[i] = FileReceivingSocket(self.ip, self.g_port, self.files_and_paths, self.key)
            self.g_port+=1
            self.sockets[i].start()
            self.file_recving_sockets.append(self.sockets[i])
            # telling the other device we opened a socket and he can connect to it
            self.main_sending_socket.send_massage.emit("socket opened")
            # waiting for the other device to tell us he opened connected to our socket
            self.condition.wait(self.mutex)
            i += 1
            
        # sending the files
        for file in self.files:
            # waiting for the other device to tell us he opened a socket and is listening on it
            self.condition.wait(self.mutex)
            # connecting to that socket
            sock = FileSendingSocket(self.computer_ip, self.g_port, file, self.key)
            self.g_port+=1
            sock.start()
            self.file_sending_sockets.append(sock)
            # telling the other device we connected to the socket and he can open another one
            self.main_sending_socket.send_massage.emit("connected")
            time.sleep(1)
        
        # emitting to the main sockets that we finished transferring so they can close 
        self.main_sending_socket.done_signal.emit()
        self.main_receiving_socket.done_signal.emit()
        

        # making sure all receiving socket have finished
        all_socket_finished = True
        while True:
            for socket in self.sockets:
                # going through each socket and making sure it's finished
                if not socket.finished:
                    all_socket_finished = False
            if all_socket_finished:
                break
            all_socket_finished = True

        # updating the GUI that file transfer went well
        self.main_window.change_to_message_win("all files received successfully")

        self.mutex.unlock()

    def finished_window2(self, files):
        # this happens when the second window finishes. it updates the files
        self.files = files
        self.is_window2_finished = True
        # if the computer already sent the file than we can move to the next window and if not we wait for him
        if (self.got_files):
            self.main_window.change_win()
        else:
            self.main_window.change_to_message_win("waiting for computer")
        # sending to the computer the files we chose
        self.main_sending_socket.got_files(self.files)

    def finished_window3(self, files_and_paths):
        # this happens when the third window is finished
        # we update the locations of the files the computer sent
        self.files_and_paths = files_and_paths
        # sending that we are ready to send the files
        self.main_sending_socket.ready_to_send_files()
        self.ready_for_the_files = True
        # if the computer already sent that he is ready to send files we start sending files
        # if not we wait for it
        if self.is_phone_ready_for_the_files:
            self.main_window.change_to_message_win("transferring files")
            thread = Thread(target=self.send_files)
            thread.start()
        else:
            self.main_window.change_to_message_win("waiting for computer")

    def received_message(self, message):
        # this get called when we receive a message during the file sending
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

def main():
    app = QApplication(sys.argv)
    project = Project()
    project.main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()