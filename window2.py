from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Window2(QWidget):
    finished_choosing_files = pyqtSignal(list)

    def __init__(self):
        super(Window2, self).__init__()
        self.setup_ui()

    def setup_ui(self):
        self.files = []
        self.setObjectName("Form")

        self.vertical_layout_widget = QWidget(self)
        self.vertical_layout_widget.setGeometry(QRect(200, 100, 900, 500))
        self.vertical_layout_widget.setObjectName("verticalLayoutWidget")

        self.vertical_layout = QVBoxLayout(self.vertical_layout_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setObjectName("verticalLayout")

        self.push_button = QPushButton(self.vertical_layout_widget)
        self.push_button.setObjectName("pushButton")
        self.push_button.setText("+")
        self.push_button.setFont(QFont('Arial', 15))
        self.push_button.clicked.connect(self.get_file_path)
        self.vertical_layout.addWidget(self.push_button)

        self.title_label = QLabel(self.vertical_layout_widget)
        self.title_label.setText("files:")
        self.title_label.setFont(QFont('Arial', 15))
        self.vertical_layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea(self.vertical_layout_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")

        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_widget_contents.setGeometry(QRect(0, 0, 287, 153))
        self.scroll_area_widget_contents.setObjectName("scrollAreaWidgetContents")

        layout = QVBoxLayout(self.scroll_area_widget_contents)
        layout.addStretch()

        self.scroll_area_widget_contents.setLayout(layout)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.vertical_layout.addWidget(self.scroll_area)

        self.ok_button = QPushButton(self.vertical_layout_widget)
        self.ok_button.setObjectName("okButton")
        self.ok_button.setText("OK")
        self.ok_button.setFont(QFont('Arial', 15))
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.vertical_layout.addWidget(self.ok_button)

    def add_file(self, file_path):
        self.files.append(file_path)
        self.label = QLabel(file_path, self.scroll_area_widget_contents)
        self.scroll_area_widget_contents.layout().addWidget(self.label)

    def get_file_path(self):
        file_app = QFileDialog(self)
        file_app.fileSelected.connect(self.add_file)
        file_app.setFixedSize(1300, 700)
        file_app.show()

    def ok_button_clicked(self):
        self.finished_choosing_files.emit(self.files)