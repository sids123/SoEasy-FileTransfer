from gui import *
from connection import *
import qrcode
from threading import Thread
import sys

class Project:
    def __init__(self):
        self.ip = str(socket.gethostbyname(socket.gethostname()))
        self.port = 6744
        self.phone_port = 6745
        self.g_port = 6746
        self.path = "qr.png"
        self.qr_image = qrcode.make(f"{self.ip} {str(self.port)}")
        self.qr_image.save(self.path)
        self.main_window = MainWindow()
        self.main_receiving_socket = MainReceivingSocket(self.ip, self.port)
        self.got_files = False
        self.finished_window2 = False
        self.ready_for_the_files = False
        self.is_phone_ready_for_the_files = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        self.main_receiving_socket.connection_made.connect(self.handle_connection)
        self.main_receiving_socket.got_file_list_from_phone.connect(self.handle_files)
        self.main_receiving_socket.ready_for_files.connect(self.phone_ready_for_files)
        self.main_window.window2.finished_choosing_files.connect(self.win2_finished)
        self.main_window.window3.all_files_have_location.connect(self.finished_window3)
        self.main_receiving_socket.receive.connect(self.received_message)
        self.main_receiving_socket.exception_rose.connect(self.exception_rose)

        self.main_receiving_socket.start()

    def exception_rose(self, error_message):
        self.main_window.change_to_message_win(error_message)

    def handle_connection(self, address):
        self.phone_ip = address[0]
        self.main_sending_socket = MainSendingSocket(self.phone_ip, self.phone_port)
        self.main_sending_socket.exception_rose.connect(self.exception_rose)
        self.main_sending_socket.start()
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
        for file in self.files:
            self.condition.wait(self.mutex)
            sock = FileSendingSocket(self.phone_ip, self.g_port, file)
            self.g_port +=1
            sock.start()
            self.file_sending_sockets.append(sock)
            self.main_sending_socket.send_massage.emit("connected")

        for file in self.files_and_paths:
            sock = FileReceivingSocket(self.ip, self.g_port, self.files_and_paths)
            self.g_port +=1
            sock.start()
            self.file_recving_sockets.append(sock)
            self.main_sending_socket.send_massage.emit("socket opened")
            self.condition.wait(self.mutex)

        self.main_sending_socket.done_signal.emit()
        self.main_receiving_socket.done_signal.emit()

        self.mutex.unlock()

        self.main_window.change_to_message_win("success")

    def win2_finished(self, files):
        self.files = files
        self.finished_window2 = True
        if (self.got_files):
            self.main_window.change_win()
        else:
            self.main_window.change_to_message_win("waiting for phone")
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

    def received_message(self, message):
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


