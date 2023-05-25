from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class MessageWindow(QWidget):
    def __init__(self, message):
        super(MessageWindow, self).__init__()
        self.message = message
        self.setupUI()

    def setupUI(self):
        self.message_label = QLabel(self)
        self.message_label.setText(self.message)
        self.message_label.setFont(QFont('Arial', 10))
        self.message_label.setGeometry(QRect(300, 300, 700, 100))

    def change_message(self, message):
        self.message_label.setText(message)