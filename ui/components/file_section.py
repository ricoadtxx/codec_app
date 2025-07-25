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
        self.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        self.setStyleSheet(FILE_SECTION_STYLE)
        
        self.fileLayout = QtWidgets.QVBoxLayout(self)
        self.fileLayout.setContentsMargins(15, 15, 15, 15)
        self.fileLayout.setSpacing(8)
        
        self.btnBrowse = QtWidgets.QPushButton("📂 Pilih Citra")
        self.btnBrowse.setCursor(Qt.PointingHandCursor)
        self.btnBrowse.setFixedHeight(40)
        self.btnBrowse.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.btnBrowse.setStyleSheet(FILE_BUTTON_STYLE)
        
        self.labelPath = QtWidgets.QLabel("Belum ada file dipilih")
        self.labelPath.setFont(QtGui.QFont("Segoe UI", 9))
        self.labelPath.setFixedHeight(35)
        self.labelPath.setAlignment(Qt.AlignCenter)
        self.labelPath.setWordWrap(True)
        self.labelPath.setStyleSheet(PATH_LABEL_STYLE)
        
        self.btnClear = QtWidgets.QPushButton("🗑 Hapus File")
        self.btnClear.setCursor(Qt.PointingHandCursor)
        self.btnClear.setFixedHeight(35)
        self.btnClear.setFont(QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold))
        self.btnClear.setStyleSheet(CLEAR_BUTTON_STYLE)
        self.btnClear.setEnabled(False)
        
        self.labelBandInfo = QtWidgets.QLabel("")
        font_band = QtGui.QFont("Segoe UI", 9)
        font_band.setItalic(True)
        self.labelBandInfo.setFont(font_band)
        self.labelBandInfo.setAlignment(Qt.AlignCenter)
        self.labelBandInfo.setFixedHeight(20)
        self.labelBandInfo.setStyleSheet(BAND_INFO_STYLE)
        self.labelBandInfo.setVisible(False)
        
        self.fileLayout.addWidget(self.btnBrowse)
        self.fileLayout.addWidget(self.labelPath)
        self.fileLayout.addWidget(self.btnClear)
        self.fileLayout.addWidget(self.labelBandInfo)
    
    def connectSignals(self):
        pass
    
    def setFilePath(self, path):
        filename = os.path.basename(path)
        self.labelPath.setText(filename)
        self.btnClear.setEnabled(bool(path))

    def setBandInfo(self, info):
        self.labelBandInfo.setText(info)
        self.labelBandInfo.setVisible(bool(info))
    
    def clearFile(self):
        self.labelPath.setText("Belum ada file dipilih")
        self.btnClear.setEnabled(False)
        self.labelBandInfo.setVisible(False)
        self.labelBandInfo.setText("")