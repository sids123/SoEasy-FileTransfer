from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from GUI_phone import *
from Connection_phone import *
import netifaces
from threading import Thread
import time

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
        self.port = 6745
        self.g_port = 6746
        self.main_window = MainWindow()
        self.main_receiving_socket = MainReceivingSocket(self.ip, self.port)
        self.got_files = False
        self.finished_window2 = False
        self.ready_for_the_files = False
        self.is_phone_ready_for_the_files = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.files_received = []

        self.main_receiving_socket.receive.connect(self.socket_opened)
        self.main_receiving_socket.connection_made.connect(self.handle_connection)
        self.main_receiving_socket.got_file_list_from_phone.connect(self.handle_files)
        self.main_receiving_socket.ready_for_files.connect(self.phone_ready_for_files)

        self.main_window.window1.ConnectingThread.got_data.connect(self.handle_data)
        self.main_window.window2.finished.connect(self.win2_finished)
        self.main_window.window3.all_files_have_location.connect(self.finished_window3)

        self.main_receiving_socket.exception_rose.connect(self.exception_rose)

        self.main_receiving_socket.start()

    def exception_rose(self, error_message):
        self.main_window.change_to_message_win(error_message)

    def handle_data(self, data):
        data = data.split()
        self.computer_ip = data[0]
        self.computer_port = int(data[1])
        self.main_sending_socket = MainSendingSocket(self.computer_ip, self.computer_port)
        self.main_sending_socket.exception_rose.connect(self.exception_rose)
        self.main_sending_socket.start()

    def handle_connection(self):
        self.main_window.change_win()

    def handle_files(self, list_of_files):
        self.files_from_phone = list_of_files
        self.main_window.window3.add_files(self.files_from_phone)
        self.got_files = True
        if (self.finished_window2):
            self.main_window.change_win()

    def phone_ready_for_files(self):
        self.is_phone_ready_for_the_files = True
        if self.ready_for_the_files:
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
        self.sockets = ["" for f in self.files_and_paths.keys()]
        for file in self.files_and_paths:
            time.sleep(1)
            self.sockets[i] = FileReceivingSocket(self.ip, self.g_port, self.files_and_paths)
            self.g_port+=1
            self.sockets[i].start()
            self.file_recving_sockets.append(self.sockets[i])
            self.main_sending_socket.send_massage.emit("socket opened")
            self.condition.wait(self.mutex)
            i += 1
        for file in self.files:
            self.condition.wait(self.mutex)
            sock = FileSendingSocket(self.computer_ip, self.g_port, file)
            self.g_port+=1
            sock.start()
            self.file_sending_sockets.append(sock)
            self.main_sending_socket.send_massage.emit("connected")
            time.sleep(1)

        self.main_sending_socket.done_signal.emit()
        self.main_receiving_socket.done_signal.emit()


        files_not_received = []
        all_socket_finished = True
        while True:
            for socket in self.sockets:
                if not socket.finished:
                    all_socket_finished = False
            if all_socket_finished:
                break
            all_socket_finished = True

        self.main_window.change_to_message_win("all files received successfully")

        self.mutex.unlock()

    def win2_finished(self, files):
        self.files = files
        self.finished_window2 = True
        if (self.got_files):
            self.main_window.change_win()
        else:
            self.main_window.change_to_message_win("waiting for computer")
        self.main_sending_socket.got_files(self.files)

    def finished_window3(self, files_and_paths):
        self.files_and_paths = files_and_paths
        self.main_sending_socket.ready_to_send_files()
        self.ready_for_the_files = True
        if self.is_phone_ready_for_the_files:
            self.main_window.change_to_message_win("transferring files")
            thread = Thread(target=self.send_files)
            thread.start()
        else:
            self.main_window.change_to_message_win("waiting for phone")

    def socket_opened(self, message):
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