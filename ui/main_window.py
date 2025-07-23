from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, LEFT_PANEL_WIDTH, APP_NAME
from .styles.base_styles import MAIN_WINDOW_STYLE, PANEL_STYLE
from .components.headers import HeaderComponent
from .components.file_section import FileSectionComponent
from .components.model_section import ModelSectionComponent
from .components.process_section import ProcessSectionComponent
from .components.output_panel import OutputPanelComponent
from core.file_handler import FileHandler
from core.controller import AppController


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.current_detector = None
        self.input_image_path = None
        self.input_image_array = None
        self.detection_thread = None
        self.file_handler = FileHandler()
        self.outputPanelComponent.set_file_handler(self.file_handler)
        self.controller = AppController(self)  # Pasang controller
        self.connectSignals()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle(APP_NAME)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)
        self.mainLayout.setSpacing(25)

        self.headerComponent = HeaderComponent()
        self.mainLayout.addWidget(self.headerComponent)

        self.contentHorizontalLayout = QtWidgets.QHBoxLayout()
        self.contentHorizontalLayout.setSpacing(20)

        self.leftPanel = QtWidgets.QFrame()
        self.leftPanel.setFixedWidth(LEFT_PANEL_WIDTH)
        self.leftPanel.setStyleSheet(PANEL_STYLE)
        left_shadow = QGraphicsDropShadowEffect()
        left_shadow.setBlurRadius(15)
        left_shadow.setColor(QtGui.QColor(0, 0, 0, 30))
        left_shadow.setOffset(0, 3)
        self.leftPanel.setGraphicsEffect(left_shadow)

        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(30, 25, 30, 25)
        self.leftLayout.setSpacing(20)

        self.fileSectionComponent = FileSectionComponent()
        self.modelSectionComponent = ModelSectionComponent()
        self.processSectionComponent = ProcessSectionComponent()

        self.leftLayout.addWidget(self.fileSectionComponent)
        self.leftLayout.addWidget(self.modelSectionComponent)
        self.leftLayout.addWidget(self.processSectionComponent)
        self.leftLayout.addStretch()

        self.outputPanelComponent = OutputPanelComponent()

        self.contentHorizontalLayout.addWidget(self.leftPanel)
        self.contentHorizontalLayout.addWidget(self.outputPanelComponent, 1)

        self.mainLayout.addLayout(self.contentHorizontalLayout, 1)

        self.footerLabel = QtWidgets.QLabel("© 2024 CoDec App - Advanced Coastline Analysis Tool")
        self.footerLabel.setAlignment(Qt.AlignCenter)
        self.footerLabel.setFont(QtGui.QFont("Segoe UI", 9))
        self.mainLayout.addWidget(self.footerLabel)

        QtCore.QMetaObject.connectSlotsByName(self)

    def connectSignals(self):
        self.fileSectionComponent.btnBrowse.clicked.connect(self.controller.browseFile)
        self.fileSectionComponent.btnClear.clicked.connect(self.controller.clearFile)
        self.modelSectionComponent.btnSelectType.currentTextChanged.connect(self.controller.onModelChanged)
        self.processSectionComponent.btnRun.clicked.connect(self.controller.runDetection)
