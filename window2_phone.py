from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class Window2(QWidget):
    # this is the window where you choose files
    finished = pyqtSignal(list)
    def __init__(self):
        super(Window2, self).__init__()
        self.i = 0
        self.setupUi()
    def setupUi(self):
        self.files = []
        self.setObjectName("Form")
        self.setGeometry(100, 100, 1300, 700)

        # creating the vertical layout and the actual widget
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(100, 200, 870, 1500))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        # creating the button that you press to add a file and adding it to the vertical layout
        self.pushButton = QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("+")
        self.pushButton.setFont(QFont('Arial', 15))
        self.pushButton.clicked.connect(self.get_file_path)
        self.verticalLayout.addWidget(self.pushButton)

        # creating a label and adding it to the vertical layout
        self.title_label = QLabel(self.verticalLayoutWidget)
        self.title_label.setText("files:")
        self.title_label.setFont(QFont('Arial', 15))
        self.verticalLayout.addWidget(self.title_label)

        # creating the area that you add the files to in the GUI
        self.scrollArea = QScrollArea(self.verticalLayoutWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 287, 153))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        layout = QVBoxLayout(self)
        layout.addStretch()

        self.scrollAreaWidgetContents.setLayout(layout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        # creating the button that you press when you're finished choosing files and adding it to the vertical layout
        self.okButton = QPushButton(self.verticalLayoutWidget)
        self.okButton.setObjectName("okButton")
        self.okButton.setText("OK")
        self.okButton.setFont(QFont('Arial', 15))
        self.okButton.clicked.connect(self.ok_button_clicked)
        self.verticalLayout.addWidget(self.okButton)

    def add_file(self, file_path):
        # adding the file to the list of files updating the GUI with the file
        self.files.append(file_path)
        self.label = QLabel(file_path)
        self.scrollAreaWidgetContents.layout().addWidget(self.label)

    def get_file_path(self):
        # opening the file system and getting the location of the file i choose
        file_app = QFileDialog(self)
        file_app.fileSelected.connect(self.add_file)
        file_app.setFixedSize(1000, 2000)
        file_app.show()
        
    def ok_button_clicked(self):
        self.finished.emit(self.files)