from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class LoginWindow(QMainWindow):
    login_success = Signal()  # MainWindow ah open panna signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PTC SHOP ERP Pro | Login")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QMainWindow { background-color: #0F172A; }
            QLabel { color: white; font-size: 14px; }
            QLineEdit { 
                background-color: #1E293B; color: white; padding: 10px; 
                border: 1px solid #334155; border-radius: 6px; font-size: 14px;
            }
            QPushButton {
                background-color: #2563EB; color: white; padding: 12px;
                border-radius: 6px; font-weight: bold; font-size: 15px;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("PTC SHOP ERP")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        # ENTER press panna login aaguradhu ku
        self.password.returnPressed.connect(self.handle_login)
        self.username.returnPressed.connect(lambda: self.password.setFocus())

        login_btn = QPushButton("LOGIN")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        brand = QLabel("Powered by Ashik")
        brand.setStyleSheet("color: #94A3B8; font-family: 'Brush Script MT'; font-size: 12px;")
        brand.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(brand)

    def handle_login(self):
        user = self.username.text()
        pwd = self.password.text()

        # Ipo ku dummy check. Aprom db la irundhu check pannalam
        if user == "admin" and pwd == "admin":
            self.login_success.emit()  # Signal anupuvom
            self.close()  # Ipo dhan close pannanum
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid Username or Password")