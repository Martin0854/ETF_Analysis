from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class MarketItem(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")
        
        layout = QGridLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.title_label, 0, 0, 1, 2)
        
        self.value_label = QLabel("-")
        self.value_label.setStyleSheet("font-size: 16px; color: #000;")
        layout.addWidget(self.value_label, 1, 0)
        
        self.delta_label = QLabel("-")
        self.delta_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.delta_label, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
    def update_data(self, value, delta, precision=2):
        if isinstance(value, (int, float)):
            self.value_label.setText(f"{value:,.{precision}f}")
        else:
            self.value_label.setText(str(value))
        
        if isinstance(delta, (int, float)):
            self.delta_label.setText(f"{delta:+.{precision}f}")
            if delta > 0:
                self.delta_label.setStyleSheet("font-size: 12px; color: red;")
            elif delta < 0:
                self.delta_label.setStyleSheet("font-size: 12px; color: blue;")
            else:
                self.delta_label.setStyleSheet("font-size: 12px; color: #666;")
        else:
            self.delta_label.setText(str(delta))
            self.delta_label.setStyleSheet("font-size: 12px; color: #666;")

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        layout.setSpacing(10)
        
        self.items = {}
        indices = ["KOSPI", "KOSDAQ", "USD/KRW", "Gov Bond 3Y", "Corp Bond AA-"]
        
        # Grid layout: 2 rows
        # Grid layout: 2 rows
        for i, name in enumerate(indices):
            item = MarketItem(name)
            self.items[name] = item
            row = i // 3
            col = i % 3
            layout.addWidget(item, row, col)
            
        # Date Label
        self.date_label = QLabel("Reference: -")
        self.date_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.date_label, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignRight)
            
    def update_market_data(self, data, ref_date=None):
        # data is a dict: {name: (value, delta)}
        for name, (value, delta) in data.items():
            if name in self.items:
                precision = 3 if "Bond" in name else 2
                self.items[name].update_data(value, delta, precision)

                
        if ref_date:
            self.date_label.setText(f"Reference: {ref_date}")
