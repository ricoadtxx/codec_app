"""Model configuration component"""
from PyQt5 import QtCore, QtGui, QtWidgets
from ..styles.component_styles import MODEL_SECTION_STYLE, COMBO_BOX_STYLE
from config.settings import MODEL_TYPES

class ModelSectionComponent(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__("🤖 Model Configuration")
        self.setupUi()
    
    def setupUi(self):
        """Setup model configuration UI components"""
        self.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        self.setStyleSheet(MODEL_SECTION_STYLE)
        
        # Layout
        self.modelLayout = QtWidgets.QVBoxLayout(self)
        self.modelLayout.setContentsMargins(15, 15, 15, 15)
        self.modelLayout.setSpacing(10)
        
        # Model label
        self.labelModel = QtWidgets.QLabel("Tipe Model:")
        self.labelModel.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.labelModel.setStyleSheet("color: #000; border: none;")
        
        # Model dropdown
        self.btnSelectType = QtWidgets.QComboBox()
        self.btnSelectType.setFixedHeight(40)
        self.btnSelectType.setFont(QtGui.QFont("Segoe UI", 10))
        self.btnSelectType.addItems(MODEL_TYPES)
        self.btnSelectType.setStyleSheet(COMBO_BOX_STYLE)
        
        self.modelLayout.addWidget(self.labelModel)
        self.modelLayout.addWidget(self.btnSelectType)
    
    def getCurrentModel(self):
        """Get the currently selected model"""
        return self.btnSelectType.currentText()
    
    def setCurrentModel(self, model):
        """Set the current model selection"""
        index = self.btnSelectType.findText(model)
        if index >= 0:
            self.btnSelectType.setCurrentIndex(index)