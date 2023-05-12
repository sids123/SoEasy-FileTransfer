from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Window3(QWidget):
    all_files_have_location = pyqtSignal(dict)
    def __init__(self):
        super(Window3, self).__init__()
        self.file_location_dict = {}
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("Form")

        self.vertical_layout_widget = QWidget(self)
        self.vertical_layout_widget.setGeometry(QRect(200, 100, 900, 500))
        self.vertical_layout_widget.setObjectName("vertical_layout_widget")

        self.vertical_layout = QVBoxLayout(self.vertical_layout_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setObjectName("vertical_layout")

        self.title_label = QLabel(self.vertical_layout_widget)
        self.title_label.setObjectName("label")
        self.title_label.setText("Files:")
        self.title_label.setFont(QFont('Arial', 15))
        self.vertical_layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea(self.vertical_layout_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_widget_contents.setGeometry(QRect(0, 0, 417, 255))
        self.scroll_area_widget_contents.setObjectName("scroll_area_widget_contents")

        layout = QFormLayout(self.scroll_area_widget_contents)

        self.scroll_area_widget_contents.setLayout(layout)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.vertical_layout.addWidget(self.scroll_area)

        self.ok_button = QPushButton(self.vertical_layout_widget)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setText("OK")
        self.ok_button.setFont(QFont('Arial', 15))
        self.ok_button.clicked.connect(self.check_all_files_have_location)
        self.vertical_layout.addWidget(self.ok_button)

    def select_directory(self, file_name):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog(self, options=options)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        file_dialog.setFixedSize(1300, 700)
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
            self.scroll_area_widget_contents.layout().addRow(label, button)

    def create_select_directory_function(self, label_text):
        return lambda: self.select_directory(label_text)