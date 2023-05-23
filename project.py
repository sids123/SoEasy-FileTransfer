import time
from cryptography.fernet import Fernet
from gui import *
from connection import *
import qrcode
from threading import Thread
import sys

class Project:
    def __init__(self):
        # we set all the important stuff here
        self.key = Fernet.generate_key()
        print(self.key)
        self.ip = str(socket.gethostbyname(socket.gethostname()))
        self.port = 6744
        self.phone_port = 6745
        self.sending_port = 6746
        self.path = "qr.png"
        self.qr_image = qrcode.make(f"{self.ip} {str(self.port)} {self.key.decode()}")
        self.qr_image.save(self.path)
        self.main_window = MainWindow(self.path)
        self.main_receiving_socket = MainReceivingSocket(self.ip, self.port, self.key)
        self.got_files = False
        self.is_window2_finished = False
        self.ready_for_the_files = False
        self.is_phone_ready_for_the_files = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.files_received = []

        # here we connect all the signals from the sockets and windows
        self.main_receiving_socket.connection_made.connect(self.handle_connection)
        self.main_receiving_socket.got_file_list_from_phone.connect(self.handle_files)
        self.main_receiving_socket.ready_for_files.connect(self.phone_ready_for_files)
        self.main_window.window2.finished_choosing_files.connect(self.finished_window2)
        self.main_window.window3.all_files_have_location.connect(self.finished_window3)
        self.main_receiving_socket.receive.connect(self.received_message)
        self.main_receiving_socket.exception_rose.connect(self.exception_rose)

        self.main_receiving_socket.start()

    def exception_rose(self, error_message):
        # this function gets called in case of an exception
        if error_message == "":
            self.main_window.change_to_message_win("error")
        else:
            self.main_window.change_to_message_win(error_message)

    def handle_connection(self, address):
        # this gets called when the phone connected and now we need to connect to the phone
        self.phone_ip = address[0]
        self.main_sending_socket = MainSendingSocket(self.phone_ip, self.phone_port, self.key)
        self.main_sending_socket.exception_rose.connect(self.exception_rose)
        self.main_sending_socket.start()
        self.main_window.change_win()

    def handle_files(self, list_of_files):
        # this handles the file list from the phone and adds it to the GUI
        self.files_from_phone = list_of_files
        self.main_window.window3.add_files(self.files_from_phone)
        self.got_files = True
        if (self.is_window2_finished):
            self.main_window.change_win()

    def phone_ready_for_files(self):
        # this gets called when the phone sends a message that it is read to send the files
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

        # sending the files
        self.mutex.lock()
        for file in self.files:
            # waiting for the other device to tell us he opened a socket and is listening on it
            self.condition.wait(self.mutex)
            # connecting to that socket
            sock = FileSendingSocket(self.phone_ip, self.sending_port, file, self.key)
            self.sending_port +=1
            sock.start()
            self.file_sending_sockets.append(sock)
            # telling the other device we connected to the socket and he can open another one
            self.main_sending_socket.send_massage.emit("connected")
            time.sleep(1)
        i=0
        self.sockets = ["" for f in self.files_and_paths.keys()]

        # receiving the files
        for file in self.files_and_paths:
            # opening a listening socket
            self.sockets[i] = FileReceivingSocket(self.ip, self.sending_port, self.files_and_paths, self.key)
            self.sending_port +=1
            self.sockets[i].start()
            self.file_recving_sockets.append(self.sockets[i])
            # telling the other device we opened a socket and he can connect to it
            self.main_sending_socket.send_massage.emit("socket opened")
            time.sleep(1)
            # waiting for the other device to tell us he opened connected to our socket
            self.condition.wait(self.mutex)
            i+=1
            
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
        # if the phone already sent the file than we can move to the next window and if not we wait for him
        if (self.got_files):
            self.main_window.change_win()
        else:
            self.main_window.change_to_message_win("waiting for phone")
        # sending to the phone the files we chose
        self.main_sending_socket.got_files(self.files)

    def finished_window3(self, files_and_paths):
        # this happens when the third window is finished
        # we update the locations of the files the phone sent
        self.files_and_paths = files_and_paths
        # sending that we are ready to send the files
        self.main_sending_socket.ready_to_send_files()
        self.ready_for_the_files = True
        # if the phone already sent that he is ready to send files we start sending files
        # if not we wait for it
        if self.is_phone_ready_for_the_files:
            self.main_window.change_to_message_win("transferring files")
            thread = Thread(target=self.send_files)
            thread.start()
        else:
            self.main_window.change_to_message_win("waiting for phone")

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


