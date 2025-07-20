import os
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from ..styles.component_styles import (
    FILE_SECTION_STYLE, FILE_BUTTON_STYLE, CLEAR_BUTTON_STYLE,
    PATH_LABEL_STYLE, BAND_INFO_STYLE
)

class FileSectionComponent(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__("📁 File Selection")
        self.setupUi()
        self.connectSignals()
    
    def setupUi(self):
        """Setup file selection UI components"""
        self.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        self.setStyleSheet(FILE_SECTION_STYLE)
        
        # Layout
        self.fileLayout = QtWidgets.QVBoxLayout(self)
        self.fileLayout.setContentsMargins(15, 15, 15, 15)
        self.fileLayout.setSpacing(8)
        
        # Browse button
        self.btnBrowse = QtWidgets.QPushButton("📂 Pilih Citra")
        self.btnBrowse.setFixedHeight(40)
        self.btnBrowse.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.btnBrowse.setStyleSheet(FILE_BUTTON_STYLE)
        
        # Path label
        self.labelPath = QtWidgets.QLabel("Belum ada file dipilih")
        self.labelPath.setFont(QtGui.QFont("Segoe UI", 9))
        self.labelPath.setFixedHeight(35)
        self.labelPath.setAlignment(Qt.AlignCenter)
        self.labelPath.setWordWrap(True)
        self.labelPath.setStyleSheet(PATH_LABEL_STYLE)
        
        # Clear button
        self.btnClear = QtWidgets.QPushButton("🗑 Hapus File")
        self.btnClear.setFixedHeight(35)
        self.btnClear.setFont(QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold))
        self.btnClear.setStyleSheet(CLEAR_BUTTON_STYLE)
        self.btnClear.setEnabled(False)
        
        # Band info label
        self.labelBandInfo = QtWidgets.QLabel("")
        font_band = QtGui.QFont("Segoe UI", 9)
        font_band.setItalic(True)
        self.labelBandInfo.setFont(font_band)
        self.labelBandInfo.setAlignment(Qt.AlignCenter)
        self.labelBandInfo.setFixedHeight(20)
        self.labelBandInfo.setStyleSheet(BAND_INFO_STYLE)
        self.labelBandInfo.setVisible(False)
        
        # Add widgets to layout
        self.fileLayout.addWidget(self.btnBrowse)
        self.fileLayout.addWidget(self.labelPath)
        self.fileLayout.addWidget(self.btnClear)
        self.fileLayout.addWidget(self.labelBandInfo)
    
    def connectSignals(self):
        """Connect component signals"""
        pass  # Will be connected in main window
    
    def setFilePath(self, path):
        """Set the file path display"""
        filename = os.path.basename(path)
        self.labelPath.setText(filename)
        self.btnClear.setEnabled(bool(path))

    def setBandInfo(self, info):
        """Set band information display"""
        self.labelBandInfo.setText(info)
        self.labelBandInfo.setVisible(bool(info))
    
    def clearFile(self):
        """Clear the selected file"""
        self.labelPath.setText("Belum ada file dipilih")
        self.btnClear.setEnabled(False)
        self.labelBandInfo.setVisible(False)
        self.labelBandInfo.setText("")