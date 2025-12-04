from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class ControlButtonWidget(QWidget):
    def __init__(self, run_callback, exit_callback):
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
