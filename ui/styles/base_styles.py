"""Base application styles"""

MAIN_WINDOW_STYLE = """
    QMainWindow {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #f0f2f5, stop: 1 #e8eef7);
    }
"""

PANEL_STYLE = """
    QFrame {
        background-color: white;
        border-radius: 15px;
        border: 1px solid #e0e6ed;
    }
"""

GROUP_BOX_BASE = """
    QGroupBox {
        font-weight: bold;
        color: #2c3e50;
        border-radius: 10px;
        margin: 10px 0;
        padding-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 10px 0 10px;
        background-color: white;
    }
"""

BUTTON_BASE = """
    QPushButton {
        border: none;
        border-radius: 6px;
        font-weight: bold;
    }
    QPushButton:disabled {
        background-color: rgba(150, 150, 150, 0.5);
        color: rgba(255, 255, 255, 0.5);
    }
"""