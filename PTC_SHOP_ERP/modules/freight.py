from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from db.db import db
import datetime
import pandas as pd

class AnimatedCard(QFrame):
    def __init__(self, title, value, color, icon):
        super().__init__()
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}, stop:1 #1E293B);
                border-radius: 14px;
                border: 1px solid #334155;
            }}
            QLabel {{background: transparent; color: white;}}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; font-weight: 600; opacity: 0.8;")
        top.addWidget(icon_lbl)
        top.addStretch()
        top.addWidget(title_lbl)

        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet("font-size: 28px; font-weight: bold;")

        layout.addLayout(top)
        layout.addWidget(value_lbl)

class DynamicForm(QFrame):
    data_saved = Signal()

    def __init__(self, title, columns, file_type, parent=None):
        super().__init__(parent)
        self.file_type = file_type
        self.parent = parent
        self.is_closing = False # CRASH FIX FLAG

        form_width = int(parent.width() * 0.35)
        if form_width > 500: form_width = 500
        if form_width < 380: form_width = 380
        self.setFixedWidth(form_width)
        self.setFixedHeight(parent.height() - 40)
        self.move(parent.width(), 20)

        self.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 16px;
                border: 1px solid #2563EB;
            }
            QLabel.field-label {color: #60A5FA; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;}
            QLabel {background: transparent; color: #CBD5E1;}
            QScrollBar:vertical {background: #1E293B; width: 8px; border-radius: 4px;}
            QScrollBar::handle:vertical {background: #2563EB; border-radius: 4px;}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(37, 99, 235, 100))
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("background: #EF4444; color: white; border-radius: 16px; font-weight: bold; font-size: 16px;")
        close_btn.clicked.connect(self.cancel_with_confirm)
        header.addWidget(title_lbl)
        header.addStretch()
        header.addWidget(close_btn)
        main_layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea {border: none; background: transparent;}")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        self.inputs = {}
        driver_names = db.get_driver_names()

        for col in columns:
            if col == 'ID': continue

            field_container = QVBoxLayout()
            field_container.setSpacing(6)

            label = QLabel(col.replace("_", " ").title())
            label.setProperty("class", "field-label")

            if col.lower() == "driver name":
                widget = QComboBox()
                widget.addItems(["Select Driver"] + driver_names)
                widget.setEditable(True)
            elif "amount" in col.lower() or "rate" in col.lower() or "weight" in col.lower():
                widget = QDoubleSpinBox()
                widget.setMaximum(999999)
                widget.setDecimals(2)
            elif "date" in col.lower():
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {col.replace('_', ' ')}")

            widget.setFixedHeight(42)
            widget.setStyleSheet("""
                QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                    background:#1E293B; color:#F8FAFC; padding:8px 12px;
                    border:2px solid #334155; border-radius:10px; font-size: 14px;
                }
                QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                    border: 2px solid #3B82F6; background: #0F172A;
                }
                QComboBox QAbstractItemView {background: #1E293B; color: white; selection-background-color: #2563EB;}
            """)
            self.inputs[col] = widget
            field_container.addWidget(label)
            field_container.addWidget(widget)
            scroll_layout.addLayout(field_container)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        save_btn = QPushButton("💾 Save Data")
        save_btn.setFixedHeight(46)
        save_btn.setStyleSheet("background: #2563EB; color: white; border-radius: 10px; font-weight: bold; font-size: 15px;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(46)
        cancel_btn.setStyleSheet("background: #334155; color: white; border-radius: 10px; font-weight: bold; font-size: 15px;")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        save_btn.clicked.connect(self.save_with_confirm)
        cancel_btn.clicked.connect(self.cancel_with_confirm)

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(350)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setStartValue(QPoint(parent.width(), 20))
        self.anim.setEndValue(QPoint(parent.width() - self.width() - 20, 20))
        self.anim.start()

    def slide_out(self):
        if self.is_closing: return # already closing na return
        self.is_closing = True
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(280)
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(self.parent.width(), 20))
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()

    def save_with_confirm(self):
        reply = QMessageBox.question(self, 'Confirm Save', "Do you want to save this data?", QMessageBox.Save | QMessageBox.Cancel, QMessageBox.Save)
        if reply == QMessageBox.Save:
            data = {}
            for key, widget in self.inputs.items():
                if isinstance(widget, QComboBox): val = widget.currentText()
                elif isinstance(widget, QDateEdit): val = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QDoubleSpinBox): val = widget.value()
                else: val = widget.text()
                if val == "Select Driver": val = ""
                data[key] = val
            db.add_data(data, self.file_type)
            self.data_saved.emit()
            QMessageBox.information(self, "Success", "✅ Data Saved Successfully!")
            self.slide_out()

    def cancel_with_confirm(self):
        reply = QMessageBox.question(self, 'Confirm Cancel', "Are you sure? Data will not be saved.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.slide_out()

class ReportFilterDialog(QDialog):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setStyleSheet("background-color: #1E293B; color: white;")
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.addItems(["All"] + db.get_driver_names())
        layout.addWidget(self.driver_combo)

        layout.addWidget(QLabel("From Date:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        layout.addWidget(self.date_from)

        layout.addWidget(QLabel("To Date:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        layout.addWidget(self.date_to)

        layout.addWidget(QLabel("Report Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Driver Individual", "Driver Multi", "Custom Summary"])
        layout.addWidget(self.type_combo)

        btn = QPushButton("📊 Generate & Print")
        btn.setFixedHeight(42)
        btn.setStyleSheet("background-color: #2563EB; color: white; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 14px;")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_filters(self):
        return {
            'driver': self.driver_combo.currentText(),
            'date_from': self.date_from.date().toString("yyyy-MM-dd"),
            'date_to': self.date_to.date().toString("yyyy-MM-dd"),
            'type': self.type_combo.currentText()
        }

class FreightPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_type = "freight"
        self.updating = False
        self.form = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15,15,15,15)
        main_layout.setSpacing(15)

        dashboard = QGridLayout()
        dashboard.setSpacing(12)
        cards = [
            AnimatedCard("Total Freight", 0, "#2563EB", "📦"),
            AnimatedCard("Total Drivers", 0, "#059669", "🚛"),
            AnimatedCard("This Month", 0, "#D97706", "📈"),
            AnimatedCard("Revenue", "₹0", "#DC2626", "💰")
        ]
        for i, card in enumerate(cards):
            dashboard.addWidget(card, 0, i)
        main_layout.addLayout(dashboard)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)
        for name, icon in [("New", "🆕"), ("Import", "📥"), ("+ Freight", "➕"), ("+ Driver", "👤"), ("🔄", ""), ("Export", "📤"), ("Print", "🖨️"), ("Report", "📊")]:
            btn = QPushButton(f"{icon} {name}")
            btn.setFixedHeight(40)
            btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 600; font-size: 13px;")
            action_bar.addWidget(btn)
            if "Freight" in name: self.add_btn = btn
            if "Driver" in name: self.driver_btn = btn
            if "🔄" in name: self.refresh_btn = btn
            if "Export" in name: self.export_btn = btn
            if "Print" in name: self.print_btn = btn
            if "Report" in name: self.report_btn = btn

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search...")
        self.search_box.setFixedHeight(40)
        self.search_box.setMinimumWidth(180)
        self.search_box.setStyleSheet("background:#1E293B; color:white; border:2px solid #334155; border-radius:8px; padding:0 10px;")
        self.search_box.textChanged.connect(self.filter_table)
        action_bar.addWidget(self.search_box)
        action_bar.addStretch()
        main_layout.addLayout(action_bar)

        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {background-color: #1E293B; color: white; border-radius: 10px; gridline-color: #334155; border: 1px solid #334155;}
            QHeaderView::section {background-color: #0F172A; color: white; padding: 10px; border: none; font-weight: bold; font-size: 12px;}
            QTableWidget::item:selected {background-color: #2563EB;}
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.itemChanged.connect(self.cell_edited)
        main_layout.addWidget(self.table)

        self.add_btn.clicked.connect(lambda: self.show_form("Add New Freight", db.get_columns("freight"), "freight"))
        self.driver_btn.clicked.connect(lambda: self.show_form("Add Driver Details", db.get_columns("driver"), "driver"))
        self.refresh_btn.clicked.connect(self.load_data)
        self.export_btn.clicked.connect(self.export_excel)
        self.print_btn.clicked.connect(self.print_driver_copy)
        self.report_btn.clicked.connect(self.generate_report)
        self.load_data()

    def resizeEvent(self, event):
        if self.form and not self.form.is_closing:
            self.form.setFixedHeight(self.height() - 40)
            new_width = int(self.width() * 0.35)
            if new_width > 500: new_width = 500
            if new_width < 380: new_width = 380
            self.form.setFixedWidth(new_width)
            self.form.move(self.width() - self.form.width() - 15, 20)
        super().resizeEvent(event)

    def show_form(self, title, columns, file_type):
        # CRASH PROOF LOGIC
        if self.form:
            if not self.form.is_closing:
                self.form.slide_out()
            return # pudhu form open pannadhu

        self.current_type = file_type
        self.form = DynamicForm(title, columns, file_type, self)
        self.form.data_saved.connect(self.load_data)
        self.form.data_saved.connect(lambda: setattr(self, 'form', None)) # Save aana piragu clear
        self.form.destroyed.connect(lambda: setattr(self, 'form', None)) # Delete aana piragu clear
        self.form.show()
        self.form.raise_()

    def load_data(self):
        self.updating = True
        data = db.load_excel(self.current_type)
        cols = db.get_columns(self.current_type)
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels([c.replace("_"," ").title() for c in cols])
        self.table.setRowCount(len(data))
        for r, row_data in enumerate(data):
            for c, col in enumerate(cols):
                item = QTableWidgetItem(str(row_data.get(col,'')))
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.updating = False

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def cell_edited(self, item):
        if self.updating: return
        row = item.row()
        col = item.column()
        new_value = item.text()
        try:
            db.update_cell(row, col, new_value, self.current_type)
            item.setBackground(QColor("#22C55E"))
            QTimer.singleShot(400, lambda: item.setBackground(QColor("transparent")))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Invalid value: {e}")
            self.load_data()

    def export_excel(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export Excel", f"{self.current_type}_{datetime.date.today()}.xlsx", "Excel Files (*.xlsx)")
        if file:
            df = db.get_df(self.current_type)
            df.to_excel(file, index=False, engine='openpyxl')
            QMessageBox.information(self, "Exported", f"✅ Exported to {file}")

    def print_driver_copy(self):
        dialog = ReportFilterDialog("Print Driver Copy")
        if dialog.exec():
            filters = dialog.get_filters()
            self.generate_and_print(filters, "driver_copy")

    def generate_report(self):
        dialog = ReportFilterDialog("Generate Report")
        if dialog.exec():
            filters = dialog.get_filters()
            self.generate_and_print(filters, "report")

    def generate_and_print(self, filters, mode):
        df = db.get_df(self.current_type)
        if filters['driver']!= "All" and 'Driver Name' in df.columns:
            df = df[df['Driver Name'] == filters['driver']]
        if 'Date' in df.columns:
            if filters['date_from']:
                df = df[pd.to_datetime(df['Date']) >= pd.to_datetime(filters['date_from'])]
            if filters['date_to']:
                df = df[pd.to_datetime(df['Date']) <= pd.to_datetime(filters['date_to'])]

        if df.empty:
            QMessageBox.warning(self, "No Data", "Selected filters ku data illa")
            return

        report_file = f"data/{mode}_{datetime.date.today()}.xlsx"
        df.to_excel(report_file, index=False, engine='openpyxl')
        QMessageBox.information(self, "Success", f"✅ {mode.title()} Generated\nFile: {report_file}\nRows: {len(df)}")