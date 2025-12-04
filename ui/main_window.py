from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QStackedWidget, 
                             QLabel, QHBoxLayout, QMessageBox, QPushButton)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ui.dashboard import DashboardWidget
from ui.input_form import InputFormWidget
from ui.controls import ControlButtonWidget
from ui.result_view import ResultViewWidget
from ui.foreign_analysis_window import ForeignAnalysisWindow

# Worker for Market Data
class MarketDataWorker(QThread):
    data_loaded = pyqtSignal(dict, str)
    
    def run(self):
        try:
            from data.market_data import MarketDataFetcher
            fetcher = MarketDataFetcher()
            data, ref_date = fetcher.get_market_indices()
            self.data_loaded.emit(data, ref_date)
        except Exception as e:
            print(f"Market data error: {e}")
            self.data_loaded.emit({}, "")

# Worker for ETF Analysis
class AnalysisWorker(QThread):
    finished = pyqtSignal(str, str, float, object, object, dict) # ticker, name, return, price_df, pdf_df, metrics
    error = pyqtSignal(str)
    
    def __init__(self, ticker, start_date, end_date):
        super().__init__()
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        
    def run(self):
        try:
            from data.etf_data import ETFDataFetcher
            import pandas as pd
            import numpy as np
            
            etf_fetcher = ETFDataFetcher()
            
            # Use Ticker as Name
            name = self.ticker
            
            # 1. Fetch Price History
            df = etf_fetcher.get_etf_price_history(self.ticker, self.start_date, self.end_date)
            
            if df.empty:
                self.error.emit("No data found for this ticker/period.")
                return
                
            # Calculate Returns
            start_price = df['NAV'].iloc[0] if 'NAV' in df.columns else df['종가'].iloc[0]
            end_price = df['NAV'].iloc[-1] if 'NAV' in df.columns else df['종가'].iloc[-1]
            total_return = (end_price - start_price) / start_price * 100
            
            # 2. Fetch Benchmark (KOSPI)
            bm_df = etf_fetcher.get_benchmark_data(self.start_date, self.end_date)
            
            # Calculate Daily Returns for Sharpe/IR
            # Use '종가' for daily return calculation
            etf_daily_ret = df['종가'].pct_change().dropna()
            metrics = {
                'sharpe': 'N/A',
                'treynor': 'N/A',
                'excess_return': 'N/A',
                'alpha': 'N/A'
            }
            
            if not bm_df.empty:
                bm_daily_ret = bm_df['종가'].pct_change().dropna()
                
                # Align dates
                combined = pd.concat([etf_daily_ret, bm_daily_ret], axis=1, join='inner')
                combined.columns = ['etf', 'bm']
                
                if not combined.empty:
                    # Excess Return (Total)
                    bm_total_return = (bm_df['종가'].iloc[-1] - bm_df['종가'].iloc[0]) / bm_df['종가'].iloc[0] * 100
                    metrics['excess_return'] = total_return - bm_total_return
                    
                    # Sharpe Ratio (assuming risk-free rate = 0 for simplicity, annualized)
                    # Daily Sharpe * sqrt(252)
                    std = combined['etf'].std()
                    if std != 0:
                        metrics['sharpe'] = (combined['etf'].mean() / std) * np.sqrt(252)
                        
                    # Treynor Ratio (Portfolio Return / Beta)
                    # Beta = Cov(ETF, BM) / Var(BM)
                    cov_matrix = combined.cov()
                    if not cov_matrix.empty:
                        beta = cov_matrix.loc['etf', 'bm'] / cov_matrix.loc['bm', 'bm']
                        if beta != 0:
                            metrics['treynor'] = (combined['etf'].mean() * 252) / beta

            # 3. Attribution Analysis (Top 10 Holdings at Start)
            # We use start_date PDF to see what contributed to the performance
            pdf = etf_fetcher.get_etf_pdf(self.ticker, self.start_date)
            
            # If start_date PDF is empty (e.g. holiday), try next few days? 
            # For now, if empty, try end_date just to show something (though attribution logic is flawed then)
            if pdf.empty:
                pdf = etf_fetcher.get_etf_pdf(self.ticker, self.end_date)
                
            # Add 'Return' and 'Contribution' columns to PDF
            pdf['Return'] = 0.0
            pdf['Contribution'] = 0.0
            
            if not pdf.empty:
                # Find weight column
                weight_col = None
                for col in ['비중', 'Weight', 'weight']:
                    if col in pdf.columns:
                        weight_col = col
                        break
                
                if weight_col:
                    # Sort by weight and take top 50
                    top_constituents = pdf.sort_values(by=weight_col, ascending=False).head(50)
                    print(f"DEBUG: Calculating returns for {len(top_constituents)} constituents...")
                    
                    for ticker, row in top_constituents.iterrows():
                        # Fetch stock history
                        stock_df = etf_fetcher.get_stock_price_history(str(ticker), self.start_date, self.end_date)
                        if not stock_df.empty:
                            s_start = stock_df['종가'].iloc[0]
                            s_end = stock_df['종가'].iloc[-1]
                            s_ret = (s_end - s_start) / s_start * 100
                            
                            # Update PDF DataFrame
                            pdf.loc[ticker, 'Return'] = s_ret
                            pdf.loc[ticker, 'Contribution'] = s_ret * (row[weight_col] / 100)
                            
                    # Fetch Names for All Constituents
                    pdf['Name'] = pdf.index # Default to ticker
                    for ticker in pdf.index:
                        name = etf_fetcher.get_stock_name(str(ticker))
                        pdf.loc[ticker, 'Name'] = name

            self.finished.emit(self.ticker, name, total_return, df, pdf, metrics)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETF 분석기")
        self.resize(1000, 700)
        
        self.foreign_window = None
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Stacked Widget for Screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Screen 1: Input & Dashboard
        self.input_screen = QWidget()
        self.setup_input_screen()
        self.stacked_widget.addWidget(self.input_screen)
        
        # Screen 2: Results
        self.result_screen = ResultViewWidget(self.go_back)
        self.stacked_widget.addWidget(self.result_screen)
        
        # Set initial screen
        self.stacked_widget.setCurrentIndex(0)

    def setup_input_screen(self):
        layout = QVBoxLayout(self.input_screen)
        
        # Top Section: Dashboard
        top_layout = QHBoxLayout()
        
        title_label = QLabel("ETF 성과 분석기")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        top_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        top_layout.addStretch()
        
        self.dashboard = DashboardWidget()
        top_layout.addWidget(self.dashboard, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(top_layout)
        
        # Load Market Data
        self.load_market_data()
        
        layout.addStretch()
        
        # Notice Section
        notice_layout = QVBoxLayout()
        notice_layout.setSpacing(5)
        
        notice_title = QLabel("⚠️ 주의사항")
        notice_title.setStyleSheet("font-weight: bold; color: #d32f2f; font-size: 14px;")
        notice_layout.addWidget(notice_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        notices = [
            "1. 해외 지수 추종 국내 ETF는 분석 불가입니다!",
            "2. 코스피, 코스닥, 코넥스 등 국내 주식시장에 상장된 종목을 담은 ETF에 한해서 분석 가능합니다.",
            "3. 외국 지수(S&P500 등) 추종 ETF를 확인하려면 우 하단의 외국 지수 분석을 확인하세요."
        ]
        
        for notice in notices:
            lbl = QLabel(notice)
            lbl.setStyleSheet("color: #555; font-size: 12px;")
            notice_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            
        layout.addLayout(notice_layout)
        
        layout.addStretch()
        
        # Middle Section: Input Form
        self.input_form = InputFormWidget()
        layout.addWidget(self.input_form, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        # Bottom Section: Controls
        self.controls = ControlButtonWidget(self.run_analysis, self.close, self.open_foreign_analysis)
        layout.addWidget(self.controls, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

    def load_market_data(self):
        self.market_worker = MarketDataWorker()
        self.market_worker.data_loaded.connect(self.dashboard.update_market_data)
        self.market_worker.start()

    def run_analysis(self):
        # Get data from input form
        ticker = self.input_form.get_ticker()
        start_date = self.input_form.get_start_date()
        end_date = self.input_form.get_end_date()
        
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a ticker.")
            return

        # Disable button to prevent double click
        self.controls.run_btn.setEnabled(False)
        self.controls.run_btn.setText("분석 중...")
        
        # Start Worker
        self.analysis_worker = AnalysisWorker(ticker, start_date, end_date)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.start()
        
    def on_analysis_finished(self, ticker, name, total_return, df, pdf, metrics):
        # Re-enable button
        self.controls.run_btn.setEnabled(True)
        self.controls.run_btn.setText("분석하기")
        
        # Update Result Screen
        self.result_screen.display_results(ticker, name, total_return, df, pdf, metrics)
        
        # Switch to Result Screen
        self.stacked_widget.setCurrentIndex(1)
        
    def on_analysis_error(self, error_msg):
        self.controls.run_btn.setEnabled(True)
        self.controls.run_btn.setText("분석하기")
        QMessageBox.critical(self, "Analysis Failed", f"Error: {error_msg}")
        
    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)

    def open_foreign_analysis(self):
        if self.foreign_window is None:
            self.foreign_window = ForeignAnalysisWindow()
        self.foreign_window.show()
        self.foreign_window.raise_()