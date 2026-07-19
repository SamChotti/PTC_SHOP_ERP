from PySide6.QtWidgets import *
class DeliveryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Delivery Schedule - Calendar View Coming Soon", styleSheet="font-size: 20px;"))