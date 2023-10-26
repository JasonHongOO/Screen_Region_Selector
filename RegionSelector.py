import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, \
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QEvent, QObject, QCoreApplication, QTimer, QRect
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from PyQt5 import QtCore

class ScreenCapture(QMainWindow):
    def __init__(self):
        super().__init__()

        self.begin = None
        self.end = None
        self.painter = QPainter()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.5)
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())

        self.label = QLabel(self)
        self.label.setGeometry(QRect(0, 0, 0, 0))
        # self.label.setStyleSheet("border: 4px solid red;")
        self.pixmap = QPixmap(self.size())
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.showFullScreen()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_capture_box)
        self.timer.start(10)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.begin is not None:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end = event.pos()
            self.close()

    def paintEvent(self, event):
        painter = QPainter(self.pixmap)
        painter.drawPixmap(0, 0, self.pixmap)
        if self.begin and self.end:
            rect = QRect(self.begin, self.end)
            painter.setBrush(QBrush(QColor(0, 0, 255, 100)))  # 設定填充顏色為淺藍色 (0, 0, 255)，並設定透明度為 100
            painter.drawRect(rect)
    
    def update_capture_box(self):
        if self.begin and self.end:
            self.label.setGeometry(QRect(self.begin, self.end))

            # self.painter = QPainter(self.pixmap)
            # self.painter.drawPixmap(0, 0, self.pixmap)
            # rect = QRect(self.begin, self.end)
            # self.painter.setBrush(QBrush(QColor(0, 0, 255, 100)))  # 設定填充顏色為淺藍色 (0, 0, 255)，並設定透明度為 100
            # self.painter.drawRect(rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenCapture()
    app.exec_()
    if window.begin and window.end:
        x1, y1 = window.begin.x(), window.begin.y()
        x2, y2 = window.end.x(), window.end.y()
        print(f"選取的區域座標: ({x1}, {y1}) - ({x2}, {y2})")
