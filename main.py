import sys
import os
from PyQt5.QtWidgets import QApplication,  QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        
        pixmap = QPixmap('assets/codec.png')
        
        if not pixmap.isNull():
            pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            pixmap = QPixmap(500, 500)
            pixmap.fill(Qt.white)
        
        self.setPixmap(pixmap)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.showMessage('<font color="white" size="5"><b>Loading CoDec App...</b></font>', 
                        Qt.AlignBottom | Qt.AlignCenter)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.close_splash)
        
    def show_splash(self, duration=3000):
        self.show()
        self.timer.start(duration)
        
    def close_splash(self):
        self.timer.stop()
        self.close()

def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("CoDec App")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CoDec Development")
    
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app.setWindowIcon(QIcon('assets/codec.png'))
    
    splash = SplashScreen()
    splash.show_splash(3000)
    
    app.processEvents()
    
    window = MainWindow()
    
    def show_main_window():
        splash.close()
        window.show()
    
    QTimer.singleShot(3000, show_main_window)
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())