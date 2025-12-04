from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QDateEdit, QVBoxLayout, QGroupBox, QCompleter, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QDate, Qt, QStringListModel, QThread, pyqtSignal

class InputFormWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        group_box = QGroupBox("파라미터 조정")
        group_layout = QFormLayout()
        
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("돋보기로 검색")
        
        # Search Button Layout
        ticker_layout = QHBoxLayout()
        ticker_layout.addWidget(self.ticker_input)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedWidth(30)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.open_search_dialog)
        ticker_layout.addWidget(self.search_btn)
        
        group_layout.addRow("종목명:", ticker_layout)
        
        self.listing_date_label = QLabel("")
        self.listing_date_label.setStyleSheet("color: gray; font-size: 10pt;")
        group_layout.addRow("", self.listing_date_label)
        
        # Connect editingFinished to update listing date
        self.ticker_input.editingFinished.connect(self.update_listing_date)
        
        # Completer setup
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.ticker_input.setCompleter(self.completer)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addYears(-1)) # Default 1 year ago
        group_layout.addRow("시작일 :", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        group_layout.addRow("종료일 :", self.end_date)
        
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
    def set_etf_list(self, etf_list):
        """
        Sets the list of ETFs for autocomplete.
        etf_list: List of strings "Ticker | Name"
        """
        model = QStringListModel(etf_list)
        self.completer.setModel(model)
        
    def get_ticker(self):
        text = self.ticker_input.text()
        # Extract ticker if in format "Ticker | Name"
        if "|" in text:
            return text.split("|")[0].strip()
        return text.strip()
        
    def get_start_date(self):
        return self.start_date.date().toString("yyyyMMdd")
        
    def get_end_date(self):
        return self.end_date.date().toString("yyyyMMdd")

    def open_search_dialog(self):
        from ui.search_dialog import SearchDialog
        dialog = SearchDialog(self)
        if dialog.exec():
            selected = dialog.get_selected_ticker()
            if selected:
                self.ticker_input.setText(selected)
                self.update_listing_date()

    def update_listing_date(self):
        ticker = self.get_ticker()
        if not ticker:
            self.listing_date_label.setText("")
            return
            
        # Run in a separate thread or just call it? 
        # Since it might take a second, better to be async, but for now let's try synchronous for simplicity 
        # or use a simple worker if needed. 
        # Given the user wants it "simple", let's try direct call first. 
        # If it freezes UI, we can make it async.
        
        # Actually, let's use a small worker to avoid freezing UI
        self.listing_date_label.setText("상장일 가져오는 중...")
        
        from data.etf_data import ETFDataFetcher
        # We can't easily run async without a proper thread setup in this class structure
        # Let's just do it synchronously for now, as pykrx might be fast enough for cached data or small range?
        # No, fetching 20 years might take 1-2 seconds.
        
        # Simple Thread
        self.fetch_thread = ListingDateFetcher(ticker)
        self.fetch_thread.result_ready.connect(self.on_listing_date_ready)
        self.fetch_thread.start()
        
    def on_listing_date_ready(self, date_str):
        if date_str:
            self.listing_date_label.setText(f"상장일: {date_str}")
        else:
            self.listing_date_label.setText("상장일: 알 수 없음")

class ListingDateFetcher(QThread):
    result_ready = pyqtSignal(str)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        
    def run(self):
        try:
            from data.etf_data import ETFDataFetcher
            fetcher = ETFDataFetcher()
            date = fetcher.get_listing_date(self.ticker)
            self.result_ready.emit(date if date else "")
        except:
            self.result_ready.emit("")
