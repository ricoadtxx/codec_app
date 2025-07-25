import sys
import os
from PyQt5.QtWidgets import QApplication,  QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from utils.helper import resource_path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        
        pixmap = QPixmap(resource_path('assets/codec.png'))
        
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
    print("➡️ Starting app...")

    app = QApplication(sys.argv)
    print("✅ QApplication dibuat")

    from ui.main_window import MainWindow
    print("✅ MainWindow berhasil diimport")

    app.setWindowIcon(QIcon(resource_path("assets/codec.png")))
    print("✅ Icon berhasil di-set")

    splash = SplashScreen()
    splash.show_splash(3000)
    print("✅ Splash screen ditampilkan")

    app.processEvents()

    window = MainWindow()
    print("✅ Main window instance dibuat")

    def show_main_window():
        print("🪟 Menampilkan main window")
        splash.close()
        window.show()

    QTimer.singleShot(3000, show_main_window)

    print("🌀 Menjalankan event loop")
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())