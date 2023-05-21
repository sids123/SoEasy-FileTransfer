from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Window3(QWidget):
    # this is the window where you pick locations for the files the other device chose
    all_files_have_location = pyqtSignal(dict)

    def __init__(self):
        super(Window3, self).__init__()
        self.file_location_dict = {}
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")

        # creating the vertical layout and the actual widget
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(100, 100, 900, 1500))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        # creating a label and adding it to the vertical layout
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.label.setText("Files:")
        self.label.setFont(QFont('Arial', 15))
        self.verticalLayout.addWidget(self.label)

        # creating the area where the files that the other device chose will be
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

        # creating the button that you press when you're finished choosing files and adding it to the vertical layout
        self.ok_button = QPushButton(self.verticalLayoutWidget)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setText("OK")
        self.ok_button.setFont(QFont('Arial', 15))
        self.ok_button.clicked.connect(self.check_all_files_have_location)
        self.verticalLayout.addWidget(self.ok_button)

    def select_directory(self, file_name):
        # creating the object of the file system
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog(self, options=options)
        # setting the object to a mode in which you choose a directory instead of a file
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        file_dialog.setFixedSize(1000, 2000)
        file_dialog.show()
        try:
            # it tries to see if you chose a directory or just closed the window
            # if you chose a directory it would work and if not the try except will catch it
            if file_dialog.exec_():
                directory = file_dialog.selectedFiles()[0]
            self.file_location_dict[file_name] = directory
        except:
            pass

    def check_all_files_have_location(self):
        files_have_location = True
        # it goes over each file and checking if it has a location or is it a None type
        for location in self.file_location_dict.values():
            if location == None:
                files_have_location = False
        if files_have_location:
            # if all files have a location then it emits a dictionary with the files and their location
            self.all_files_have_location.emit(self.file_location_dict)

    def add_files(self, files):
        # here you add files to this window
        for file in files:
            # for each file it extracts the file name insert it to the dict and adds a label for it in the GUI
            file = file.split("/")[-1]
            self.file_location_dict[file] = None
            label = QLabel(file)
            button = QPushButton()
            button.clicked.connect(self.create_select_directory_function(label.text()))
            button.setText("Choose Location")
            self.scrollAreaWidgetContents.layout().addRow(label, button)

    def create_select_directory_function(self, label_text):
        return lambda: self.select_directory(label_text)