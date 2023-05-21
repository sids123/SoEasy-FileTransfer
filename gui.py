from window1 import *
from window2 import *
from window3 import *
from message_win import *


class MainWindow(QMainWindow):
    # this is the window that supervises the GUI
    def __init__(self, path):
        super(MainWindow, self).__init__()
        self.path = path
        self.setGeometry(100, 100, 1300, 700)
        self.setWindowTitle("project")
        self.setup_ui()

    def setup_ui(self):
        self.current_win = 0

        # here i create the windows
        self.window1 = Window1(self.path)
        self.window2 = Window2()
        self.window3 = Window3()
        self.message_win = MessageWindow("")

        # and add them to the stack
        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, 1300, 700)
        self.stack.addWidget(self.window1)
        self.stack.addWidget(self.window2)
        self.stack.addWidget(self.window3)
        self.stack.addWidget(self.message_win)

        # with the stack i can replace which window is being presented to the user

        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.stack)

        self.stack.setCurrentIndex(self.current_win)

    def change_win(self):
        # this function changes the window to the next one
        self.current_win += 1
        self.stack.setCurrentIndex(self.current_win)

    def change_to_message_win(self, message):
        # this function changes the window to the message window
        self.message_win.change_message(message)
        self.stack.setCurrentIndex(3)