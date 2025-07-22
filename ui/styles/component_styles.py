from .base_styles import GROUP_BOX_BASE, BUTTON_BASE

HEADER_STYLE = """
    QFrame {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                  stop: 0 #667eea, stop: 1 #764ba2);
    }
"""

TITLE_STYLE = "color: white; background: transparent;"
SUBTITLE_STYLE = "color: rgba(255, 255, 255, 200); background: transparent;"

FILE_SECTION_STYLE = GROUP_BOX_BASE + """
    QGroupBox {
        border: 2px solid #3498db;
    }
"""

FILE_BUTTON_STYLE = BUTTON_BASE + """
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #6c5fb3, stop: 1 #229954);
        color: white;
        height: 40px;
    }
    QPushButton:hover:enabled {
        background-color: #310cf5;
    }
    QPushButton:pressed:enabled {
        background-color: #922b21;
    }
"""

CLEAR_BUTTON_STYLE = BUTTON_BASE + """
    QPushButton {
        background-color: #c0392b;
        color: white;
        height: 35px;
    }
    QPushButton:hover:enabled {
        background-color: #e74c3c;
    }
    QPushButton:pressed:enabled {
        background-color: #922b21;
    }
"""

PATH_LABEL_STYLE = """
    QLabel {
        color: #7f8c8d;
        background-color: #f8f9fa;
        padding: 6px 10px;
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
"""

BAND_INFO_STYLE = """
    QLabel {
        color: #6c757d;
        background: transparent;
        padding: 0px;
        margin: 0px;
    }
"""

MODEL_SECTION_STYLE = GROUP_BOX_BASE + """
    QGroupBox {
        border: 2px solid #e74c3c;
    }
"""

COMBO_BOX_STYLE = """
    QComboBox {
        background-color: white;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        padding: 8px;
        color: #2c3e50;
        height: 40px;
    }
    QComboBox:hover {
        border: 2px solid #e74c3c;
    }
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 8px solid #7f8c8d;
        margin-right: 10px;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 5px;
        selection-background-color: #e74c3c;
        selection-color: white;
    }
"""

PROCESS_SECTION_STYLE = GROUP_BOX_BASE + """
    QGroupBox {
        border: 2px solid #27ae60;
    }
"""

RUN_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #27ae60, stop: 1 #229954);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px;
        height: 50px;
        font-weight: bold;
    }
    QPushButton:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #2ecc71, stop: 1 #27ae60);
    }
    QPushButton:pressed {
        background: #1e8449;
    }
    QPushButton:disabled {
        background: #bdc3c7;
        color: #7f8c8d;
    }
"""

OUTPUT_HEADER_STYLE = """
    QLabel {
        color: white;
        padding: 10px;
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                  stop: 0 #f39c12, stop: 1 #e67e22);
        border-radius: 8px;
    }
"""

TAB_WIDGET_STYLE = """
    QTabWidget::pane {
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
    QTabWidget::tab-bar {
        alignment: center;
    }
    QTabBar::tab {
        background-color: #ecf0f1;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        color: #2c3e50;
        font-weight: bold;
        min-width: 120px;
        max-width: 160px;
    }
    QTabBar::tab:selected {
        background-color: #f39c12;
        color: white;
    }
    QTabBar::tab:hover {
        background-color: #d5dbdb;
    }
"""

PREVIEW_LABEL_STYLE = """
    QLabel {
        color: #7f8c8d;
        background-color: #ecf0f1;
        border: 2px dashed #bdc3c7;
        border-radius: 8px;
        padding: 20px;
        font-size: 12px;
    }
"""

INPUT_PREVIEW_LABEL_STYLE = """
    QLabel {
        color: #7f8c8d;
        background-color: #ecf0f1;
        border: 2px dashed #3498db;
        border-radius: 8px;
        padding: 20px;
        font-size: 12px;
    }
"""

TEXT_EDIT_STYLE = """
    QTextEdit {
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        padding: 10px;
        background-color: #f8f9fa;
        color: #2c3e50;
        font-family: 'Consolas', monospace;
        font-size: 10px;
    }
"""

INFO_LABEL_STYLE = """
    QLabel {
        color: #5d4037;
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 6px;
        border-left: 3px solid #f39c12;
    }
"""

FOOTER_STYLE = "color: #7f8c8d; background: transparent; padding: 10px;"