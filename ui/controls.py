from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class ControlButtonWidget(QWidget):
    def __init__(self, run_callback, exit_callback, foreign_callback=None):
        super().__init__()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.run_btn = QPushButton("분석하기")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px; 
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: black;
            }
        """)
        self.run_btn.clicked.connect(run_callback)
        layout.addWidget(self.run_btn)
        
        if foreign_callback:
            self.foreign_btn = QPushButton("외국 지수 분석")
            self.foreign_btn.setMinimumHeight(40)
            self.foreign_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3; 
                    color: white; 
                    font-weight: bold; 
                    border-radius: 5px; 
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.foreign_btn.clicked.connect(foreign_callback)
            layout.addWidget(self.foreign_btn)
        
        self.exit_btn = QPushButton("종료")
        self.exit_btn.setMinimumHeight(40)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px; 
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.exit_btn.clicked.connect(exit_callback)
        layout.addWidget(self.exit_btn)
