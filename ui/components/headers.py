from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from ..styles.component_styles import HEADER_STYLE, TITLE_STYLE, SUBTITLE_STYLE

class HeaderComponent(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setupUi()
    
    def setupUi(self):
        self.setFixedHeight(120)
        self.setStyleSheet(HEADER_STYLE)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        self.headerLayout = QtWidgets.QVBoxLayout(self)
        self.headerLayout.setContentsMargins(30, 20, 30, 20)
        
        self.labelTitle = QtWidgets.QLabel("🌊 Coastline Detection & Extraction")
        font_title = QtGui.QFont("Segoe UI", 22, QtGui.QFont.Bold)
        self.labelTitle.setFont(font_title)
        self.labelTitle.setAlignment(Qt.AlignCenter)
        self.labelTitle.setStyleSheet(TITLE_STYLE)
        
        self.labelSubtitle = QtWidgets.QLabel("Advanced Satellite & UAV Imagery Processing")
        font_subtitle = QtGui.QFont("Segoe UI", 12)
        self.labelSubtitle.setFont(font_subtitle)
        self.labelSubtitle.setAlignment(Qt.AlignCenter)
        self.labelSubtitle.setStyleSheet(SUBTITLE_STYLE)
        
        self.headerLayout.addWidget(self.labelTitle)
        self.headerLayout.addWidget(self.labelSubtitle)