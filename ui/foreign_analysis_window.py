from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import pandas as pd
import datetime

class ForeignAnalysisWorker(QThread):
    finished = pyqtSignal(str, float, object, object) # ticker, total_return, price_df, holdings_df
    error = pyqtSignal(str)

    def __init__(self, ticker, start_date, end_date):
        super().__init__()
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            from data.foreign_data import ForeignDataFetcher
            fetcher = ForeignDataFetcher()
            
            # 1. Fetch Price History
            df = fetcher.get_price_history(self.ticker, self.start_date, self.end_date)
            
            if df.empty:
                self.error.emit("No data found for this ticker/period.")
                return

            # Calculate Total Return
            start_price = df['Close'].iloc[0]
            end_price = df['Close'].iloc[-1]
            total_return = (end_price - start_price) / start_price * 100
            
            # 2. Fetch Top Holdings
            holdings = fetcher.get_top_holdings(self.ticker)
            
            # 3. Calculate Contribution for Top Holdings
            if not holdings.empty:
                holdings['Return'] = 0.0
                holdings['Contribution'] = 0.0
                
                # Iterate over holdings
                for symbol, row in holdings.iterrows():
                    # Fetch stock history
                    stock_df = fetcher.get_price_history(str(symbol), self.start_date, self.end_date)
                    if not stock_df.empty:
                        s_start = stock_df['Close'].iloc[0]
                        s_end = stock_df['Close'].iloc[-1]
                        s_ret = (s_end - s_start) / s_start * 100
                        
                        holdings.loc[symbol, 'Return'] = s_ret
                        # Weight is decimal (e.g. 0.07), so Contribution = Return * Weight
                        # Check if weight is 'Holding Percent' or 'Weight'
                        weight_col = 'Holding Percent' if 'Holding Percent' in holdings.columns else 'Weight'
                        if weight_col in holdings.columns:
                            weight = row[weight_col]
                            holdings.loc[symbol, 'Contribution'] = s_ret * weight
            
            self.finished.emit(self.ticker, total_return, df, holdings)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))

class ForeignAnalysisWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("외국 지수 분석 (yfinance)")
        self.resize(1000, 800)
        
        layout = QVBoxLayout(self)
        
        # --- Input Section ---
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("Ticker:"))
        self.ticker_input = QLineEdit("SPY")
        self.ticker_input.setFixedWidth(100)
        input_layout.addWidget(self.ticker_input)
        
        # Search Button (Magnifying Glass)
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedWidth(30)
        self.search_btn.clicked.connect(self.open_search_dialog)
        input_layout.addWidget(self.search_btn)
        
        input_layout.addWidget(QLabel("Start:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        input_layout.addWidget(self.start_date)
        
        input_layout.addWidget(QLabel("End:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        input_layout.addWidget(self.end_date)
        
        self.run_btn = QPushButton("분석")
        self.run_btn.clicked.connect(self.run_analysis)
        self.run_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;")
        input_layout.addWidget(self.run_btn)
        
        layout.addLayout(input_layout)
        
        # --- Result Section ---
        
        # Summary Label
        self.summary_label = QLabel("분석 준비 완료")
        self.summary_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(self.summary_label)
        
        # Chart
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.web_view, stretch=1)
        
        # Table
        layout.addWidget(QLabel("상위 구성 종목 성과 (Top Holdings)"))
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Symbol", "Name", "Weight", "Return (%)", "Contrib (%)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, stretch=1)
        
    def open_search_dialog(self):
        # Simple dialog for now since yfinance doesn't have easy search
        # Or we can create a simple dialog that lets user type and maybe we show some popular ones?
        # For now, let's use a simple input dialog or a custom dialog if we had a list.
        # Since we don't have a list of all US ETFs, we'll just show a message or a simple input.
        # Actually, let's reuse SearchDialog but maybe with a different mode?
        # But SearchDialog uses ETFDataFetcher which is for Korean ETFs.
        
        # Let's create a simple custom dialog here or just use QInputDialog for now?
        # User asked for "Magnifying glass to open search window".
        # Let's create a simple dialog that lists some popular US ETFs and allows typing.
        
        from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Foreign ETF Search")
        dialog.resize(300, 400)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Popular ETFs:"))
        list_widget = QListWidget()
        popular_etfs = [
            "SPY - S&P 500", "QQQ - Nasdaq 100", "DIA - Dow Jones", 
            "IWM - Russell 2000", "VTI - Total Stock Market",
            "VOO - S&P 500 (Vanguard)", "IVV - S&P 500 (iShares)",
            "SOXX - Semiconductor", "SMH - Semiconductor",
            "XLK - Technology", "XLF - Financials", "XLE - Energy",
            "GLD - Gold", "SLV - Silver", "TLT - 20+ Year Treasury"
        ]
        list_widget.addItems(popular_etfs)
        layout.addWidget(list_widget)
        
        def on_item_clicked(item):
            # Extract ticker
            text = item.text()
            ticker = text.split(" - ")[0]
            self.ticker_input.setText(ticker)
            dialog.accept()
            
        list_widget.itemClicked.connect(on_item_clicked)
        
        dialog.exec()

    def run_analysis(self):
        ticker = self.ticker_input.text().strip()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        if not ticker:
            QMessageBox.warning(self, "Error", "Ticker is required.")
            return
            
        self.run_btn.setEnabled(False)
        self.run_btn.setText("분석 중...")
        self.summary_label.setText(f"Fetching data for {ticker}...")
        
        self.worker = ForeignAnalysisWorker(ticker, start, end)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_finished(self, ticker, total_return, price_df, holdings_df):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("분석")
        self.summary_label.setText(f"{ticker} Period Return: {total_return:.2f}%")
        
        # Update Chart
        self.update_chart(ticker, price_df)
        
        # Update Table
        self.update_table(holdings_df)
        
    def on_error(self, msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("분석")
        QMessageBox.critical(self, "Error", msg)
        self.summary_label.setText("Error occurred.")
        
    def update_chart(self, ticker, df):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines', name=ticker,
            hovertemplate='%{x|%Y-%m-%d}<br>%{y:,.2f}<extra></extra>'
        ))
        fig.update_layout(
            title=f"{ticker} Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        self.web_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
        
    def update_table(self, df):
        self.table.setRowCount(0)
        if df.empty:
            return
            
        # Sort by Weight (Holding Percent)
        weight_col = 'Holding Percent' if 'Holding Percent' in df.columns else 'Weight'
        if weight_col in df.columns:
            df = df.sort_values(by=weight_col, ascending=False)
            
        self.table.setRowCount(len(df))
        
        for i, (symbol, row) in enumerate(df.iterrows()):
            # Symbol
            self.table.setItem(i, 0, QTableWidgetItem(str(symbol)))
            
            # Name
            name = row.get('Name', '')
            self.table.setItem(i, 1, QTableWidgetItem(str(name)))
            
            # Weight
            weight = row.get(weight_col, 0)
            self.table.setItem(i, 2, QTableWidgetItem(f"{weight:.2%}"))
            
            # Return
            ret = row.get('Return', 0.0)
            ret_item = QTableWidgetItem(f"{ret:.2f}")
            if ret > 0: ret_item.setForeground(QColor("red"))
            elif ret < 0: ret_item.setForeground(QColor("blue"))
            self.table.setItem(i, 3, ret_item)
            
            # Contribution
            contrib = row.get('Contribution', 0.0)
            contrib_item = QTableWidgetItem(f"{contrib:.2f}")
            if contrib > 0.5:
                contrib_item.setBackground(QColor("#e6ffe6"))
                contrib_item.setForeground(QColor("red"))
            elif contrib < -0.5:
                contrib_item.setBackground(QColor("#ffe6e6"))
                contrib_item.setForeground(QColor("blue"))
            self.table.setItem(i, 4, contrib_item)
