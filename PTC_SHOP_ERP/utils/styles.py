from PySide6.QtCore import Qt

STYLES = {
    "light": """
        QMainWindow { background-color: #f4f7f9; }
        QTabBar::tab { padding: 12px 20px; font-weight: bold; font-size: 14px; }
        QTabBar::tab:selected { background: #0056b3; color: white; }
        QGroupBox { border: 1px solid #d1e0f0; border-radius: 8px; margin-top: 10px; padding-top: 15px; background: white;}
        QPushButton { background-color: #0056b3; color: white; padding: 10px 15px; border-radius: 6px; font-weight: bold; }
        QPushButton:hover { background-color: #004494; }
        QTableWidget { background: white; gridline-color: #d1e0f0; }
        QHeaderView::section { background-color: #0056b3; color: white; padding: 5px; font-weight: bold; }
    """
}

FREIGHT_COLS = ["DATE", "DRIVER NAME", "CUSTOMER NAME", "BILL NO", "QTY/BAGS", "PER BAG COOLIE", "COOLIE",
           "PER BAG FREIGHT", "FREIGHT", "TRUCK NO", "BRAND", "REMARK 1", "REMARK 2"]
SALES_COLS = ["DATE", "BILL NO", "CUSTOMER", "ITEM", "QTY", "RATE", "TOTAL", "PAYMENT TYPE", "PAID", "BALANCE"]
DRIVER_MASTER_COLS = ["DRIVER NAME", "PHONE", "TRUCK NO", "LICENSE NO", "ADDRESS", "VEHICLE TYPE"] # ITHU NEW