from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QFrame, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import plotly.graph_objects as go
import pandas as pd

class ResultViewWidget(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # Top: Header & Back Button
        top_layout = QHBoxLayout()
        
        self.header_label = QLabel("분석 결과")
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        top_layout.addWidget(self.header_label)
        
        top_layout.addStretch()
        
        self.back_btn = QPushButton("뒤로")
        self.back_btn.clicked.connect(back_callback)
        top_layout.addWidget(self.back_btn)
        
        layout.addLayout(top_layout)
        
        # Status / Summary
        self.status_label = QLabel("분석 준비")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(self.status_label)
        
        # Metrics Section
        self.metrics_frame = QFrame()
        self.metrics_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 10px;")
        metrics_layout = QHBoxLayout(self.metrics_frame)
        
        self.sharpe_label = QLabel("샤프 비율: -")
        self.treynor_label = QLabel("트레이너 지수: -")
        self.excess_label = QLabel("초과 수익률: -")
        
        self.end_price_label = QLabel("종료일 가격: -")
        self.period_return_label = QLabel("기간 수익률: -")
        
        for lbl in [self.sharpe_label, self.treynor_label, self.excess_label, self.end_price_label, self.period_return_label]:
            lbl.setStyleSheet("font-size: 12px; font-weight: bold;")
            metrics_layout.addWidget(lbl)
            
        # Help Button
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(24, 24)
        self.help_btn.setStyleSheet(
            "QPushButton { "
            "border-radius: 12px; "
            "background-color: #e0e0e0; "
            "color: #333; "
            "font-weight: bold; "
            "font-size: 18px; "
            "border: 1px solid #ccc; "
            "padding: 0px; "
            "}"
            "QPushButton:hover { background-color: #d0d0d0; }"
        )
        self.help_btn.clicked.connect(self.show_metrics_help)
        metrics_layout.addWidget(self.help_btn)
            
        layout.addWidget(self.metrics_frame)
        
        # Chart Area
        self.web_view = QWebEngineView()
        # Set size policy to expand
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.web_view, stretch=1)
        
        # Constituent Analysis Area (Table)
        self.table_label = QLabel("종목 분석 (대표 포트폴리오)")
        self.table_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.table_label)
        
        self.constituent_table = QTableWidget()
        self.constituent_table.setColumnCount(5)
        self.constituent_table.setHorizontalHeaderLabels(["Name", "Weight (%)", "Amount", "Return (%)", "Contrib (%)"])
        self.constituent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.constituent_table.itemSelectionChanged.connect(self.calculate_sum)
        
        # Make Read-only
        self.constituent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Custom Sorting
        self.constituent_table.horizontalHeader().setSectionsClickable(True)
        self.constituent_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        self.sort_col = -1
        self.sort_order = 0 # 0: Default, 1: Desc, 2: Asc
        self.original_df = pd.DataFrame()
        self.current_df = pd.DataFrame()
        
        layout.addWidget(self.constituent_table, stretch=1)
        
        # Sum Label
        self.sum_label = QLabel("합계: -")
        self.sum_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333; margin-top: 5px;")
        layout.addWidget(self.sum_label, alignment=Qt.AlignmentFlag.AlignRight)
        
    def display_results(self, ticker, name, total_return, price_df, pdf_df, metrics):
        if name == ticker:
            self.status_label.setText(f"Analysis for {ticker}: Total Return {total_return:.2f}%")
        else:
            self.status_label.setText(f"Analysis for {ticker}: Total Return {total_return:.2f}%")
        
        # Update Metrics
        sharpe = metrics.get('sharpe', 'N/A')
        treynor = metrics.get('treynor', 'N/A')
        excess = metrics.get('excess_return', 'N/A')
        
        self.sharpe_label.setText(f"Sharpe Ratio: {sharpe:.2f}" if isinstance(sharpe, (int, float)) else f"Sharpe Ratio: {sharpe}")
        self.treynor_label.setText(f"Treynor Ratio: {treynor:.2f}" if isinstance(treynor, (int, float)) else f"Treynor Ratio: {treynor}")
        self.excess_label.setText(f"Excess Return: {excess:.2f}%" if isinstance(excess, (int, float)) else f"Excess Return: {excess}")
        
        # Update Price and Return
        if not price_df.empty:
            col = 'NAV' if 'NAV' in price_df.columns else '종가'
            end_price = price_df[col].iloc[-1]
            self.end_price_label.setText(f"종료일 가격: {end_price:,.0f}")
            self.period_return_label.setText(f"기간 수익률: {total_return:.2f}%")
        else:
            self.end_price_label.setText("종료일 가격: -")
            self.period_return_label.setText("기간 수익률: -")
        
        # Update Chart
        self.update_chart(ticker, name, price_df)
        
        # Update PDF Table
        self.update_constituents(pdf_df)
        
    def update_chart(self, ticker, name, price_df):
        if price_df.empty:
            self.web_view.setHtml("")
            return

        # Determine column to plot
        col = 'NAV' if 'NAV' in price_df.columns else '종가'
        
        # Create Plotly Figure
        fig = go.Figure()
        
        # Add Trace
        fig.add_trace(go.Scatter(
            x=price_df.index, 
            y=price_df[col], 
            mode='lines', 
            name=col,
            hovertemplate='%{x|%Y-%m-%d}<br>%{y:,.0f}<extra></extra>'
        ))
        
        # Update Layout
        title_text = f"{ticker} 성과"
        fig.update_layout(
            title=dict(text=title_text, x=0.5, xanchor='center'),
            xaxis_title="날짜",
            yaxis_title="가격",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        
        # Convert to HTML
        html = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html)
        
    def update_constituents(self, pdf_df):
        if pdf_df.empty:
            self.constituent_table.setRowCount(0)
            return
            
        # Check available columns
        columns = pdf_df.columns.tolist()
        
        # Try to find weight column
        self.weight_col = None
        for col in ['비중', 'Weight', 'weight']:
            if col in columns:
                self.weight_col = col
                break
                
        # Try to find amount column
        self.amount_col = None
        for col in ['금액', 'Amount', 'amount', '평가금액']:
            if col in columns:
                self.amount_col = col
                break
        
        # Initial Sort by Weight Descending
        if self.weight_col:
            pdf_df = pdf_df.sort_values(by=self.weight_col, ascending=False)
            
        # Store original DF (top 50 or all)
        self.original_df = pdf_df.head(50).copy()
        
        # Reset Sort State
        self.sort_col = -1
        self.sort_order = 0
        
        self.populate_table(self.original_df)
        
    def populate_table(self, df):
        self.current_df = df
        self.constituent_table.setRowCount(len(df))
        self.constituent_table.setSortingEnabled(False) # Disable built-in sorting
        
        for row_idx, (index, row) in enumerate(df.iterrows()):
            # Name (Index or Name column)
            name_val = row.get('Name', str(index))
            name_item = QTableWidgetItem(str(name_val))
            self.constituent_table.setItem(row_idx, 0, name_item)
            
            # Weight
            weight_val = row[self.weight_col] if self.weight_col else "N/A"
            if isinstance(weight_val, (int, float)):
                weight_str = f"{weight_val:.2f}"
                weight_item = QTableWidgetItem()
                weight_item.setData(Qt.ItemDataRole.DisplayRole, weight_val) # For proper sorting if we used built-in
                weight_item.setText(weight_str)
            else:
                weight_str = str(weight_val)
                weight_item = QTableWidgetItem(weight_str)
            self.constituent_table.setItem(row_idx, 1, weight_item)
            
            # Amount
            amount_val = row[self.amount_col] if self.amount_col else "N/A"
            if isinstance(amount_val, (int, float)):
                amount_str = f"{amount_val:,.0f}"
                amount_item = QTableWidgetItem()
                amount_item.setData(Qt.ItemDataRole.DisplayRole, amount_val)
                amount_item.setText(amount_str)
            else:
                amount_str = str(amount_val)
                amount_item = QTableWidgetItem(amount_str)
            self.constituent_table.setItem(row_idx, 2, amount_item)
            
            # Return
            ret_val = row.get('Return', 0.0)
            ret_item = QTableWidgetItem()
            ret_item.setData(Qt.ItemDataRole.DisplayRole, ret_val)
            ret_item.setText(f"{ret_val:.2f}")
            
            if ret_val > 0:
                ret_item.setForeground(QColor("red"))
            elif ret_val < 0:
                ret_item.setForeground(QColor("blue"))
            self.constituent_table.setItem(row_idx, 3, ret_item)
            
            # Contribution
            contrib_val = row.get('Contribution', 0.0)
            contrib_item = QTableWidgetItem()
            contrib_item.setData(Qt.ItemDataRole.DisplayRole, contrib_val)
            contrib_item.setText(f"{contrib_val:.2f}")
            
            # Highlight significant contribution (> 0.5% or < -0.5%)
            if contrib_val > 0.5:
                contrib_item.setBackground(QColor("#e6ffe6")) # Light Green
                contrib_item.setForeground(QColor("red"))
            elif contrib_val < -0.5:
                contrib_item.setBackground(QColor("#ffe6e6")) # Light Red
                contrib_item.setForeground(QColor("blue"))
                
            self.constituent_table.setItem(row_idx, 4, contrib_item)
            
    def on_header_clicked(self, logicalIndex):
        # Cycle: Desc (1) -> Asc (2) -> Default (0)
        if self.sort_col == logicalIndex:
            self.sort_order = (self.sort_order + 1) % 3
            if self.sort_order == 0:
                # Skip 0 if we want to toggle only, but user asked for Default.
                # 0 means Default.
                pass
        else:
            self.sort_col = logicalIndex
            self.sort_order = 1 # Start with Descending
            
        # Perform Sort
        if self.sort_order == 0:
            # Default Order
            self.populate_table(self.original_df)
            self.constituent_table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder) # Hide indicator logic if possible or just ignore
        else:
            # Determine column name to sort by
            col_name = None
            if logicalIndex == 0: # Name
                col_name = 'Name'
            elif logicalIndex == 1: # Weight
                col_name = self.weight_col
            elif logicalIndex == 2: # Amount
                col_name = self.amount_col
            elif logicalIndex == 3: # Return
                col_name = 'Return'
            elif logicalIndex == 4: # Contrib
                col_name = 'Contribution'
                
            if col_name:
                ascending = (self.sort_order == 2)
                sorted_df = self.original_df.sort_values(by=col_name, ascending=ascending)
                self.populate_table(sorted_df)
                
                # Update Header Indicator (Visual only)
                qt_order = Qt.SortOrder.AscendingOrder if ascending else Qt.SortOrder.DescendingOrder
                self.constituent_table.horizontalHeader().setSortIndicator(logicalIndex, qt_order)
            
    def calculate_sum(self):
        selected_items = self.constituent_table.selectedItems()
        if not selected_items:
            self.sum_label.setText("합계: -")
            return
            
        total_sum = 0.0
        count = 0
        
        for item in selected_items:
            text = item.text().replace(",", "").replace("%", "")
            try:
                val = float(text)
                total_sum += val
                count += 1
            except ValueError:
                pass
                
        if count > 0:
            self.sum_label.setText(f"개수: {count} | 합계: {total_sum:,.2f}")
        else:
            self.sum_label.setText("합계: -")

    def show_metrics_help(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("지표 설명")
        msg.setText(
            "<b>Sharpe Ratio (샤프 비율)</b><br>"
            "(포트폴리오 수익률 - 무위험 수익률) / 변동성<br>"
            "위험 한 단위당 초과 수익을 나타냅니다.<br><br>"
            
            "<b>Treynor Ratio (트레이너 지수)</b><br>"
            "(포트폴리오 수익률 - 무위험 수익률) / 베타<br>"
            "체계적 위험 한 단위당 초과 수익을 나타냅니다.<br><br>"
            
            "<b>Excess Return (초과 수익률)</b><br>"
            "포트폴리오 수익률 - 벤치마크 수익률<br>"
            "시장 대비 얼마나 더 수익을 냈는지 나타냅니다."
        )
        msg.exec()
