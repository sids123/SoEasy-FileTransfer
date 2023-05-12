import threading
import qrcode
import socket
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Window1(QWidget):
    def __init__(self, PATH, IP, PORT):
        super(Window1, self).__init__()
        self.setGeometry(100, 100, 1300, 700)
        self.setWindowTitle("project")

        self.window1UI(PATH, IP, PORT)

    def window1UI(self, PATH, IP, PORT):
        self.photo = QLabel(self)
        self.photo.setGeometry(QRect(300, 0, 700, 700))
        self.photo.setPixmap(QPixmap(PATH))
        self.photo.setScaledContents(True)
        self.ListenerThread = ListenerThread(IP, PORT)
        self.ListenerThread.connection_made.connect(self.stop_display)
        self.ListenerThread.start()

    def stop_display(self):
        self.photo.clear()

class ListenerThread(QThread):
    connection_made = pyqtSignal(socket)
    def __init__(self, IP, PORT):
        super(ListenerThread, self).__init__()
        self.IP = IP
        self.PORT = PORT
        self.sock = None

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.IP, self.PORT))
        sock.listen(1)
        phone, addr = sock.accept()
        self.connection_made.emit(phone)
        sock.close()


def main():
    COMPUTER_IP = str(socket.gethostbyname(socket.gethostname()))
    PORT = 6744
    PATH = "qr.png"
    print(PORT)
    print(COMPUTER_IP)

    qr = qrcode.make(f"{COMPUTER_IP} {str(PORT)}")
    qr.save(PATH)

    app = QApplication(sys.argv)
    win = Window1(PATH, COMPUTER_IP, PORT)
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
