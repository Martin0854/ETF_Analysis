from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget, 
                             QPushButton, QHBoxLayout, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ETF Search")
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or ticker...")
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.select_item)
        layout.addWidget(self.list_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.select_item)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.all_items = []
        self.load_data()
        
    def load_data(self):
        try:
            from data.etf_data import ETFDataFetcher
            fetcher = ETFDataFetcher()
            self.all_items = fetcher.get_all_etf_list()
            self.update_list(self.all_items)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load ETF list: {e}")
            
    def update_list(self, items):
        self.list_widget.clear()
        self.list_widget.addItems(items)
        
    def filter_list(self, text):
        filtered = [item for item in self.all_items if text.lower() in item.lower()]
        self.update_list(filtered)
        
    def select_item(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            # Format is "Ticker | Name"
            self.selected_ticker = current_item.text()
            self.accept()
        else:
            # If nothing selected but user clicked Select, maybe select top item?
            # Or just do nothing
            pass
            
    def get_selected_ticker(self):
        if hasattr(self, 'selected_ticker'):
            return self.selected_ticker
        return None
