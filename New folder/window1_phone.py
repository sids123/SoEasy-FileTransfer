#
import socket
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class Window1(QWidget):
    def __init__(self):
        super(Window1, self).__init__()
        self.initUI()

    def initUI(self):
        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.CameraThread = CameraThread()

        self.CameraThread.start()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setLayout(self.VBL)


    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

class CameraThread(QThread):
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
                    self.got_data.emit(str(data))
                    break
