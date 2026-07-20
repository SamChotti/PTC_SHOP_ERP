from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from modules.dashboard import DashboardPage
from modules.freight import FreightPage
from modules.sales import SalesPage


class MainWindow(QMainWindow):
    logout_clicked = Signal()  # Logout ku signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PTC SHOP ERP Pro | v2.0")

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        font = QFont("Segoe UI", 10)
        font.setHintingPreference(QFont.PreferFullHinting)
        QApplication.setFont(font)

        self.setStyleSheet(self.load_stylesheet())

        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self.create_sidebar()
        self.create_main_area()

        self.btn_dashboard.setChecked(True)
        self.show_dashboard()

    def load_stylesheet(self):
        return """
            QMainWindow { background-color: #0F172A; }
            QFrame#Sidebar { background-color: #1E293B; border-right: 1px solid #334155; }

            QPushButton#MenuButton { 
                color: #CBD5E1; background: transparent; text-align: left; 
                padding: 12px 20px; border: none; font-size: 14px; font-weight: 500;
                border-radius: 8px; margin: 2px 10px;
            }
            QPushButton#MenuButton:hover { background-color: #334155; }
            QPushButton#MenuButton:checked { background-color: #2563EB; color: white; }

            QFrame#TopBar { background-color: #1E293B; border: none; } /* Border remove panniten */
            QPushButton#TopBtn {
                background: #334155; color: white; border: none; padding: 8px 16px;
                border-radius: 8px; font-weight: 500; font-size: 14px;
                }
            QPushButton#TopBtn:hover { background: #475569; }
            QPushButton#TopBtn::menu-indicator { image: none; } /* Arrow remove */

            QLabel { color: #E2E8F0; }
            QLabel#PageTitle { font-size: 22px; font-weight: bold; color: white; } /* Module name ku */
            QLabel#BrandLabel { 
                color: #94A3B8; font-size: 12px; padding: 15px; qproperty-alignment: AlignCenter;
                border-top: 1px solid #334155;
            }
            QLabel#Signature { font-family: 'Segoe Script'; color: #60A5FA; font-size: 14px; font-weight: bold;} /* Ashik mattum */
        """

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(10, 20, 10, 10)

        title = QLabel("PTC SHOP ERP")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; padding: 10px;")
        side_layout.addWidget(title)

        self.btn_dashboard = QPushButton("🏠  Dashboard")
        self.btn_freight = QPushButton("🚚  Freight")
        self.btn_sales = QPushButton("💰  Sales")

        for btn in [self.btn_dashboard, self.btn_freight, self.btn_sales]:
            btn.setObjectName("MenuButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            side_layout.addWidget(btn)

        self.btn_dashboard.clicked.connect(self.show_dashboard)
        self.btn_freight.clicked.connect(self.show_freight)
        self.btn_sales.clicked.connect(self.show_sales)

        side_layout.addStretch()

        # 1. POWERED BY normal, ASHIK signature
        brand_layout = QHBoxLayout()
        brand_layout.setAlignment(Qt.AlignCenter)
        brand1 = QLabel("Powered by ")
        brand1.setObjectName("BrandLabel")
        brand1.setStyleSheet("border:none; padding:0;")
        brand2 = QLabel("Ashik")
        brand2.setObjectName("Signature")
        brand2.setStyleSheet("border:none; padding:0;")
        brand_layout.addWidget(brand1)
        brand_layout.addWidget(brand2)

        brand_widget = QWidget()
        brand_widget.setLayout(brand_layout)
        brand_widget.setStyleSheet("border-top: 1px solid #334155;")
        side_layout.addWidget(brand_widget)

        self.main_layout.addWidget(sidebar)

    def create_main_area(self):
        self.main_area = QVBoxLayout()
        self.create_topbar()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 10, 20, 20)
        self.main_area.addLayout(self.content_layout)
        self.main_layout.addLayout(self.main_area)

    def create_topbar(self):
        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar.setFixedHeight(60)
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(20, 10, 20, 10)

        # Module Name
        self.page_title = QLabel("DASHBOARD OVERVIEW")
        self.page_title.setObjectName("PageTitle")
        top_layout.addWidget(self.page_title)

        top_layout.addStretch()  # Push to right

        # PROFILE MENU BUTTON
        self.profile_btn = QPushButton("👤 Admin")
        self.profile_btn.setObjectName("TopBtn")
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        top_layout.addWidget(self.profile_btn)

        # DROPDOWN MENU
        self.profile_menu = QMenu(self)
        self.profile_menu.setStyleSheet("""
            QMenu {
                background-color: #1E293B; color: white; border: 1px solid #334155;
                border-radius: 8px; padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px; border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #334155;
            }
        """)

        # Menu Items
        profile_action = QAction("👤  My Profile", self)
        role_action = QAction("🛡️  Role: Administrator", self)
        role_action.setEnabled(False)  # Click panna mudiyadhu
        logout_action = QAction("🚪  Logout", self)
        logout_action.triggered.connect(self.logout_clicked.emit)  # Logout signal

        self.profile_menu.addAction(profile_action)
        self.profile_menu.addAction(role_action)
        self.profile_menu.addSeparator()
        self.profile_menu.addAction(logout_action)

        # Button click panna menu open aagum
        self.profile_btn.clicked.connect(self.show_profile_menu)

        self.main_area.addWidget(topbar)

    def show_profile_menu(self):
        # Button keela menu open aagum
        self.profile_menu.exec(self.profile_btn.mapToGlobal(QPoint(0, self.profile_btn.height())))

    def clear_content(self):
        for i in reversed(range(self.content_layout.count())):
            w = self.content_layout.itemAt(i).widget()
            if w: w.setParent(None)

    def set_active_btn(self, active_btn, title):
        for btn in [self.btn_dashboard, self.btn_freight, self.btn_sales]:
            btn.setChecked(btn == active_btn)
        self.page_title.setText(title)  # Mela module name maarum

    def show_dashboard(self):
        self.set_active_btn(self.btn_dashboard, "DASHBOARD OVERVIEW")
        self.clear_content()
        self.content_layout.addWidget(DashboardPage())

    def show_freight(self):
        self.set_active_btn(self.btn_freight, "FREIGHT MANAGEMENT")
        self.clear_content()
        self.content_layout.addWidget(FreightPage())

    def show_sales(self):
        self.set_active_btn(self.btn_sales, "SALES MODULE")
        self.clear_content()
        self.content_layout.addWidget(SalesPage())