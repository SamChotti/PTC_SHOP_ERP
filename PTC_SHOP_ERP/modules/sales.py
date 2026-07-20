from PySide6.QtWidgets import *

class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("SALES MODULE COMING SOON")
        label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(label)