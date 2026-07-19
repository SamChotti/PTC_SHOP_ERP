from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from styles import STYLES

class LoginWindow(QWidget):
    login_success = Signal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PTC SHOP ERP - Login")
        self.showMaximized()
        self.setStyleSheet(STYLES["light"])
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        card = QFrame()
        card.setFixedSize(450, 400)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)

        title = QLabel("PTC SHOP ERP")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0056b3;")
        card_layout.addWidget(title)
        subtitle = QLabel("Sales | Delivery | Freight | Accounts")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        self.user_input = QLineEdit(placeholderText="Username")
        self.pass_input = QLineEdit(placeholderText="Password", echoMode=QLineEdit.Password)
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.check_login)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        card_layout.addWidget(login_btn)
        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def check_login(self):
        if self.user_input.text() == "admin" and self.pass_input.text() == "ptc123":
            self.login_success.emit("admin")
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid Username or Password")