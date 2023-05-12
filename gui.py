from window1 import *
from window2 import *
from window3 import *
from message_win import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.path = "qr.png"
        self.setGeometry(100, 100, 1300, 700)
        self.setWindowTitle("project")
        self.setup_ui()

    def setup_ui(self):
        self.current_win = 0

        self.window1 = Window1(self.path)
        self.window2 = Window2()
        self.window3 = Window3()
        self.message_win = MessageWindow("")

        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, 1300, 700)
        self.stack.addWidget(self.window1)
        self.stack.addWidget(self.window2)
        self.stack.addWidget(self.window3)
        self.stack.addWidget(self.message_win)

        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.stack)

        self.stack.setCurrentIndex(self.current_win)

    def change_win(self):
        self.current_win += 1
        self.stack.setCurrentIndex(self.current_win)

    def change_to_message_win(self, message):
        self.message_win.change_message(message)
        self.stack.setCurrentIndex(3)