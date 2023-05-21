
import socket
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class Window1(QWidget):
    # this is window where we display the camera
    def __init__(self):
        super(Window1, self).__init__()
        self.initUI()

    def initUI(self):
        self.VBL = QVBoxLayout()

        # this is the label that will display the camera
        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        # starting the camera
        self.CameraThread = CameraThread()

        self.CameraThread.start()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setLayout(self.VBL)


    def ImageUpdateSlot(self, Image):
        # this will change the image displayed
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    got_data = pyqtSignal(str)
    def run(self):
        # this is the object to capture an image
        Capture = cv2.VideoCapture(0)
        # this is the object to decode the qr code
        detector = cv2.QRCodeDetector()
        while True:
            # it reads from the camera
            ret, frame = Capture.read()
            if ret:
                # it's converting it to an image
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1440, 2960, Qt.KeepAspectRatio)
                # updating the GUI with the new image
                self.ImageUpdate.emit(Pic)
                data, bbox, _ = detector.detectAndDecode(Image)
                if data:
                    # if it decoded the qr code it emits the data to the project object
                    self.got_data.emit(str(data))
                    break
