from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Window1(QWidget):
    def __init__(self, path):
        super(Window1, self).__init__()
        self.path = path
        self.window1_ui()

    def window1_ui(self):
        self.photo = QLabel(self)
        self.photo.setPixmap(QPixmap(self.path))
        self.photo.setScaledContents(True)
        self.photo.setGeometry(QRect(300, 0, 700, 700))




