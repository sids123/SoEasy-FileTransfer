import socket
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

import cv2

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.ConnectingThread = ConnectingThread()

        self.ConnectingThread.start()
        self.ConnectingThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.ConnectingThread.got_data.connect(self.change_label)
        self.setLayout(self.VBL)


    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def change_label(self, decoded_string):
        self.FeedLabel.setPixmap(QPixmap(""))
        self.FeedLabel.setText(decoded_string)

class ConnectingThread(QThread): # change
    ImageUpdate = pyqtSignal(QImage)
    got_data = pyqtSignal(str)
    def run(self):
        Capture = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        while True:
            ret, frame = Capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1440, 2960, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
                data, bbox, _ = detector.detectAndDecode(Image)
                if data:
                    ip, port = str(data).split()
                    self.got_data.emit(f"{ip} {port}")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((ip, int(port)))
                    sock.close()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())