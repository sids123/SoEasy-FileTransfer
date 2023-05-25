from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Window3(QWidget):
    all_files_have_location = pyqtSignal(dict)

    def __init__(self):
        super(Window3, self).__init__()
        self.file_location_dict = {}
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(100, 100, 900, 1500))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.label.setText("Files:")
        self.label.setFont(QFont('Arial', 15))
        self.verticalLayout.addWidget(self.label)

        self.scrollArea = QScrollArea(self.verticalLayoutWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 417, 255))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        layout = QFormLayout(self.scrollAreaWidgetContents)

        self.scrollAreaWidgetContents.setLayout(layout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.OK_button = QPushButton(self.verticalLayoutWidget)
        self.OK_button.setObjectName("OK_button")
        self.OK_button.setText("OK")
        self.OK_button.setFont(QFont('Arial', 15))
        self.OK_button.clicked.connect(self.check_all_files_have_location)
        self.verticalLayout.addWidget(self.OK_button)

    def select_directory(self, file_name):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog(self, options=options)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        file_dialog.setFixedSize(1000, 2000)
        file_dialog.show()
        try:
            if file_dialog.exec_():
                directory = file_dialog.selectedFiles()[0]
            self.file_location_dict[file_name] = directory
        except:
            pass

    def check_all_files_have_location(self):
        files_have_location = True
        for location in self.file_location_dict.values():
            if location == None:
                files_have_location = False
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)

                # setting message for Message Box
                msg.setText("Not All Files Have Location")

                # setting Message box window title
                msg.setWindowTitle("Critical MessageBox")

                # declaring buttons on Message Box
                msg.setStandardButtons(QMessageBox.Cancel)

                # start the app
                retval = msg.exec_()
        if files_have_location:
            self.all_files_have_location.emit(self.file_location_dict)

    def add_files(self, files):
        for file in files:
            file = file.split("/")[-1]
            self.file_location_dict[file] = None
            label = QLabel(file)
            button = QPushButton()
            button.clicked.connect(self.create_select_directory_function(label.text()))
            button.setText("Choose Location")
            self.scrollAreaWidgetContents.layout().addRow(label, button)

    def create_select_directory_function(self, label_text):
        return lambda: self.select_directory(label_text)