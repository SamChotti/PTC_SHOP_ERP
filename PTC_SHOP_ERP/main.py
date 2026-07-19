import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import QSize
import qtawesome as qta

from styles import STYLES
from db import Database
from login import LoginWindow
from dashboard import Dashboard
from sales import SalesTab
from freight import FreightTab
from delivery import DeliveryTab
from reports import ReportsTab
from updater import check_for_update

class MainWindow(QMainWindow):
    def __init__(self, username, logout_callback): # 1. logout_callback add
        super().__init__()
        self.username = username
        self.logout_callback = logout_callback # 2. save pannikalam
        self.setWindowTitle(f"PTC SHOP ERP Pro | Welcome {username}")
        self.showMaximized()
        self.setStyleSheet(STYLES["light"])
        self.db = Database()

        check_for_update(self)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setIconSize(QSize(24, 24))
        self.setCentralWidget(self.tabs)

        self.dashboard = Dashboard(self.db)
        self.sales_tab = SalesTab(self.db)
        self.freight_tab = FreightTab(self.db)
        self.reports_tab = ReportsTab(self.db)

        self.tabs.addTab(self.dashboard, qta.icon('fa5s.tachometer-alt'), "Dashboard")
        self.tabs.addTab(self.sales_tab, qta.icon('fa5s.cash-register'), "Sales")
        self.tabs.addTab(self.freight_tab, qta.icon('fa5s.truck'), "Freight Management")
        self.tabs.addTab(self.reports_tab, qta.icon('fa5s.chart-bar'), "Reports")
        self.tabs.addTab(DeliveryTab(), qta.icon('fa5s.calendar-alt'), "Delivery Schedule")

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        toolbar.addAction(qta.icon('fa5s.plus'), "Add Entry").triggered.connect(self.add_entry)
        toolbar.addAction(qta.icon('fa5s.print'), "Print PDF").triggered.connect(lambda: QMessageBox.information(self,"Print","Coming Soon"))
        toolbar.addAction(qta.icon('fa5s.file-excel'), "Export Excel").triggered.connect(lambda: QMessageBox.information(self,"Export","Coming Soon"))

        toolbar.addSeparator()
        toolbar.addAction(qta.icon('fa5s.sign-out-alt'), "Logout").triggered.connect(self.logout)

    def add_entry(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            QMessageBox.warning(self, "Select Tab", "Please select Sales or Freight Tab")
        elif idx == 1:
            self.sales_tab.add_entry()
        elif idx == 2:
            self.freight_tab.add_entry()
        else:
            QMessageBox.warning(self, "Select Tab", "Please select Sales or Freight Tab")

    def logout(self):
        reply = QMessageBox.question(self, "Logout", "Logout aagava?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            self.logout_callback()

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login = LoginWindow()
        self.main_window = None
        self.login.login_success.connect(self.show_main) # self.login. IMPORTANT
        self.login.show()

    def show_main(self, username):
        self.main_window = MainWindow(username, self.show_login)
        self.main_window.show()
        self.login.close()

    def show_login(self):
        self.login = LoginWindow()
        self.login.login_success.connect(self.show_main) # ingayum self.login.
        self.login.show()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = MainApp()
    app.run()