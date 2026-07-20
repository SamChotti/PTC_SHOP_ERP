import sys
from PySide6.QtWidgets import QApplication
from auth.login import LoginWindow
from main_window import MainWindow

main_window = None


def launch_main():
    global main_window
    main_window = MainWindow()
    main_window.logout_clicked.connect(show_login)  # Logout signal
    main_window.showMaximized()


def show_login():
    global main_window
    main_window.close()
    login.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PTC SHOP ERP Pro")

    login = LoginWindow()
    login.login_success.connect(launch_main)
    login.show()

    sys.exit(app.exec())