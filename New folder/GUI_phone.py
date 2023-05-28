from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from message_win import *
from window1_phone import *
from window2_phone import *
from window3_phone import *
import time


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.path = "qr.png"
        self.setGeometry(0, 0, 1050, 2000)
        self.setWindowTitle("project")
        self.setupUI()

    def setupUI(self):
        self.current_index = 0

        self.window1 = Window1()
        self.window2 = Window2()
        self.window3 = Window3()
        self.message_win = MessageWindow("")

        self.Stack = QStackedWidget(self)
        self.Stack.setGeometry(0, 0, 1050, 2000)
        self.Stack.addWidget(self.window1)
        self.Stack.addWidget(self.window2)
        self.Stack.addWidget(self.window3)
        self.Stack.addWidget(self.message_win)

        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.Stack)

        self.Stack.setCurrentIndex(self.current_index)

    def change_win(self):
        self.current_index += 1
        self.Stack.setCurrentIndex(self.current_index)

    def change_to_message_win(self, message):
        self.message_win.change_message(message)
        self.Stack.setCurrentIndex(3)