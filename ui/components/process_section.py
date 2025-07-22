from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from ..styles.component_styles import PROCESS_SECTION_STYLE, RUN_BUTTON_STYLE

class ProcessSectionComponent(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__("⚡ Processing")
        self.setupUi()
    
    def setupUi(self):
        self.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        self.setStyleSheet(PROCESS_SECTION_STYLE)
        
        self.processLayout = QtWidgets.QVBoxLayout(self)
        self.processLayout.setContentsMargins(15, 15, 15, 15)
        
        self.btnRun = QtWidgets.QPushButton("🚀 Jalankan")
        self.btnRun.setFixedHeight(50)
        self.btnRun.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.btnRun.setStyleSheet(RUN_BUTTON_STYLE)
        
        run_shadow = QGraphicsDropShadowEffect()
        run_shadow.setBlurRadius(10)
        run_shadow.setColor(QtGui.QColor(39, 174, 96, 100))
        run_shadow.setOffset(0, 3)
        self.btnRun.setGraphicsEffect(run_shadow)
        
        self.processLayout.addWidget(self.btnRun)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setFixedHeight(20)
        self.progressBar.hide()
        self.processLayout.addWidget(self.progressBar)
    
    def setProcessingState(self, processing):
        if processing:
            self.btnRun.setText("⏳ Memproses...")
            self.btnRun.setEnabled(False)
            self.progressBar.show()
        else:
            self.btnRun.setText("🚀 Jalankan")
            self.btnRun.setEnabled(True)
            self.progressBar.hide()
