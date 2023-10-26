import sys
import os
from os import path
import json

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QEvent, QObject, QCoreApplication, QTimer
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import win32gui
import win32ui
import win32con

import io
import win32clipboard
from PIL import Image


class ScreenBox(QMainWindow):
    def __init__(self, left=0, top=0, width=0, height=0) -> None:
        super(ScreenBox, self).__init__()

        # Class Instance Variables.
        self.mouse_relative_position_x = 0
        self.mouse_relative_position_y = 0
        self.button_window_height = 10
        self.region_x_pos = 0
        self.region_y_pos = 0
        self.region_width = 0
        self.region_height = 0
        self.screen_shoot_path = ""
        self.callback_function = 0

        # Set the flags 
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create ButtonWindow.
        self.button_window = ButtonWindow()
        self.button_window.button_close.clicked.connect(self.close_window)
        self.button_window.button_save.clicked.connect(self.get_screen_region_and_open_save_file_dialog)
        self.button_window.button_clipboard.clicked.connect(self.get_screen_region_and_hide_windows)

        self.timer = QTimer(self)
        self.mouse_mode = 0
        widget_stylesheet = "QWidget#central_widget{" \
                            "border-color: rgba(135, 206, 250, 1);" \
                            "border-left-color: rgba(135, 206, 250, 1);" \
                            "border-right-color: rgba(135, 206, 250, 1);" \
                            "border-bottom-color: rgba(135, 206, 250, 1);" \
                            "border-style: solid;" \
                            "border-top-width: 4px;" \
                            "border-left-width: 4px;" \
                            "border-right-width: 4px;" \
                            "border-bottom-width: 4px;" \
                            "border-radius: 4px;" \
                            "background-color: rgba(255, 255, 255, 2);" \
                            "}"

        # Create the central widget.
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet(widget_stylesheet)
        self.central_widget.setMouseTracking(True)
        self.central_widget.installEventFilter(self)
        self.central_widget.setObjectName("central_widget")

        # Set the central widget for the main window.
        self.setCentralWidget(self.central_widget)

        # Define the initial geometry for the window.
        # screen_width = QApplication.primaryScreen().size().width()
        # screen_height = QApplication.primaryScreen().size().height()
        # self.setGeometry(int(screen_width / 2) - int(self.geometry().width() / 2),  # x position
        #                  int(screen_height / 2) - int(self.geometry().height() / 2),  # y position
        #                  400,  # width
        #                  300)  # height
        
        self.setGeometry(left,  # x position
                         top,  # y position
                         width,  # width
                         height)  # height

        # Set an icon for this window.
        file_name = os.path.dirname(os.path.realpath(__file__)) + "\\Images\\capture.ico"
        if path.exists(file_name):
            self.setWindowIcon(QIcon(file_name))

        # set windows minimum size.
        self.setMinimumSize(300, 100)

    def close_window(self) -> None:
        data = {}
        data['left'] = self.x()
        data['top'] = self.y()
        data['width'] = self.width()
        data['height'] = self.height()
        with open("coordination.json", "w") as json_file:
            json.dump(data, json_file)
        self.close()

    def open_save_file_dialog(self) -> str:
        current_directory = os.path.dirname(os.path.realpath(__file__))
        filter = "text files (*.jpg *.JPG)"
        # filter = "text files (*.bmp *.BMP)"
        path_file_name = QFileDialog.getSaveFileName(self, 'Save Path', current_directory, filter)[0]
        return path_file_name

    @QtCore.pyqtSlot()
    def get_screen_region_and_open_save_file_dialog(self) -> None:
        self.region_x_pos = self.x()
        self.region_y_pos = self.y()
        self.region_width = self.width()
        self.region_height = self.height()
        self.screen_shoot_path = self.open_save_file_dialog()
        self.hide()
        self.button_window.hide()
        self.timer.singleShot(500, self.save_screen_region_to_file_and_show_windows)

    @QtCore.pyqtSlot()
    def save_screen_region_to_file_and_show_windows(self) -> None:
        if len(self.screen_shoot_path) > 0:
            self.save_screen_region_to_file(self.region_x_pos, self.region_y_pos,
                                            self.region_width, self.region_height, self.screen_shoot_path)
        self.show()
        self.button_window.show()
        self.button_window.activateWindow()
        self.button_window.raise_()

    @staticmethod
    def save_screen_region_to_file(x: int, y: int, width: int, height: int, full_path_and_image: str):
        desktop_window = win32gui.GetDesktopWindow()
        window_device_context = win32gui.GetWindowDC(desktop_window)
        img_dc = win32ui.CreateDCFromHandle(window_device_context)
        mem_dc = img_dc.CreateCompatibleDC()
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (x, y), win32con.SRCCOPY)
        screenshot.SaveBitmapFile(mem_dc, full_path_and_image)
        img_dc.DeleteDC()
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())

    @staticmethod
    def copy_image_from_file_to_clipboard(full_path_and_image: str) -> None:
        image = Image.open(full_path_and_image)
        output = io.BytesIO()
        image.convert(mode="RGB").save(output, format="BMP")
        data = output.getvalue()[14:]
        output.close()

        # Copy image to clipboard.
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    @QtCore.pyqtSlot()
    def get_screen_region_and_hide_windows(self) -> None:
        self.region_x_pos = self.x()
        self.region_y_pos = self.y()
        self.region_width = self.width()
        self.region_height = self.height()
        self.hide()
        self.button_window.hide()
        self.timer.singleShot(500, self.copy_screen_region_to_clipboard_and_show_windows)

    @QtCore.pyqtSlot()
    def copy_screen_region_to_clipboard_and_show_windows(self) -> None:
        self.copy_screen_region_to_clipboard(self.region_x_pos, self.region_y_pos, self.region_width, self.region_height)
        self.show()
        self.button_window.show()
        self.button_window.activateWindow()
        self.button_window.raise_()

    @staticmethod
    def copy_screen_region_to_clipboard(x: int, y: int, width: int, height: int) -> None:
        desktop_window = win32gui.GetDesktopWindow()
        window_device_context = win32gui.GetWindowDC(desktop_window)
        img_dc = win32ui.CreateDCFromHandle(window_device_context)
        mem_dc = img_dc.CreateCompatibleDC()
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (x, y), win32con.SRCCOPY)

        # Load into PIL image.
        bmpinfo = screenshot.GetInfo()
        bmpstr = screenshot.GetBitmapBits(True)
        screenshot_image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        img_dc.DeleteDC()
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        output = io.BytesIO()
        screenshot_image.convert(mode="RGB").save(output, format="BMP")
        data = output.getvalue()[14:]
        output.close()

        # Copy image to clipboard.
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_relative_position_x = event.pos().x()
            self.mouse_relative_position_y = event.pos().y()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mouse_mode = 0
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.button_window.setGeometry(self.x(),  # x position
                                       self.y() + self.height(),  # y position
                                       self.width(),  # width
                                       self.button_window_height)  # height
        QMainWindow.resizeEvent(self, event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            self.button_window.show()
            self.button_window.activateWindow()
            self.button_window.raise_()

            if event.buttons() == Qt.NoButton:
                # Change the mouse cursor when pointer reach the bottom-right corner.
                if pos.x() > self.width() - 5 and pos.y() > self.height() - 5:
                    QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                # Change the mouse cursor when pointer reach the top-left corner.
                elif pos.x() < 5 and pos.y() < 5:
                    QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                # Change the mouse cursor when pointer reach the top-right corner.
                elif pos.x() > self.width() - 5 and pos.y() < 5:
                    QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                # Change the mouse cursor when pointer reach the bottom-left corner.
                elif pos.x() < 5 and pos.y() > self.height() - 5:
                    QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                # Change the mouse cursor when pointer reach the left and right border.
                elif pos.x() > self.width() - 5 or pos.x() < 5:
                    QApplication.setOverrideCursor(Qt.SizeHorCursor)
                # Change the mouse cursor when pointer reach the top and bottom border.
                elif pos.y() > self.height() - 5 or pos.y() < 5:
                    QApplication.setOverrideCursor(Qt.SizeVerCursor)
                # Change the mouse cursor to the standard arrow cursor.
                else:
                    QApplication.setOverrideCursor(Qt.ArrowCursor)


            if event.buttons() & Qt.LeftButton:

                # When the mouse is in the bottom-right corner.
                # If the X mouse position is greater than the window width - 10,
                # and if the Y mouse position is greater than the window height - 10,
                # then adjust window geometry.
                if pos.x() > self.width() - 10 and pos.y() > self.height() - 10 \
                        and (self.mouse_mode == 0 or self.mouse_mode == 1):
                    self.mouse_mode = 1
                    QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                    self.setGeometry(self.x(), self.y(), pos.x(), pos.y())

                # When the mouse is in the top-left corner.
                # If the X mouse position is less than 10,
                # and if the Y mouse position is less than 10,
                # then adjust window geometry.
                elif pos.x() < 10 and pos.y() < 10 \
                        and (self.mouse_mode == 0 or self.mouse_mode == 2):
                    self.mouse_mode = 2
                    QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                    self.setGeometry(self.x() + pos.x(), self.y() + pos.y(),
                                     self.width() - pos.x(), self.height() - pos.y())

                # When the mouse is in the top-right corner.
                # If the X mouse position is greater than the window width - 10,
                # and if the Y mouse position is less than 10,
                # then adjust window geometry.
                elif pos.x() > self.width() - 10 and pos.y() < 10 \
                        and (self.mouse_mode == 0 or self.mouse_mode == 3):
                    self.mouse_mode = 3
                    QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    self.setGeometry(self.x(), self.y() + pos.y(),
                                     pos.x(), self.height() - pos.y())

                # When the mouse is in the bottom-left corner.
                # If the X mouse position is less than 10,
                # and if the Y mouse position is greater than height - 10,
                # then adjust window geometry.
                elif pos.x() < 10 and pos.y() > self.height() - 10 \
                        and (self.mouse_mode == 0 or self.mouse_mode == 4):
                    self.mouse_mode = 4
                    QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    self.setGeometry(self.x() + pos.x(), self.y(),
                                     self.width() - pos.x(), pos.y())

                # When the mouse is on the window right border.
                # If the X mouse position is greater than the window width - 5,
                # then adjust window geometry.
                elif pos.x() > self.width() - 5 and 0 < pos.y() < self.height() \
                        and (self.mouse_mode == 0 or self.mouse_mode == 5):
                    self.mouse_mode = 5
                    QApplication.setOverrideCursor(Qt.SizeHorCursor)
                    self.setGeometry(self.x(), self.y(), pos.x(), self.height())

                # When the mouse is on the window left border.
                # If the X mouse position is less than 5,
                # then adjust window geometry.
                elif pos.x() < 5 and 0 < pos.y() < self.height() \
                        and (self.mouse_mode == 0 or self.mouse_mode == 6):
                    self.mouse_mode = 6
                    QApplication.setOverrideCursor(Qt.SizeHorCursor)
                    if self.width() - pos.x() > self.minimumWidth():
                        self.setGeometry(self.x() + pos.x(), self.y(), self.width() - pos.x(), self.height())

                # When the mouse is on the window bottom border.
                # If the Y mouse position is greater than the window height,
                # then adjust window geometry.
                elif pos.y() > self.height() - 5 and 0 < pos.x() < self.width() \
                        and (self.mouse_mode == 0 or self.mouse_mode == 7):
                    self.mouse_mode = 7
                    QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    self.setGeometry(self.x(), self.y(), self.width(), pos.y())

                # When the mouse is on the window top border.
                # If the Y mouse position is less than 5,
                # then adjust window geometry.
                elif pos.y() < 5 and 0 < pos.x() < self.width() \
                        and (self.mouse_mode == 0 or self.mouse_mode == 8):
                    self.mouse_mode = 8
                    QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    if self.height() - pos.y() > self.minimumHeight():
                        self.setGeometry(self.x(), self.y() + pos.y(), self.width(), self.height() - pos.y())

                # If the X mouse position is greater than 10 and less than window width
                # and the Y mouse position is greater than 10 and less than window height.
                # Then move window to a new position.
                elif 10 < pos.x() < self.width() - 10 and 10 < pos.y() < self.height() - 10 \
                        and (self.mouse_mode == 0 or self.mouse_mode == 9):
                    self.mouse_mode = 9
                    # Change the mouse cursor to cursor used for elements that are used to
                    # resize top-level windows in any direction.
                    QApplication.setOverrideCursor(Qt.SizeAllCursor)
                    # Move the widget when the mouse is dragged.
                    self.move(event.globalPos().x() - self.mouse_relative_position_x,
                              event.globalPos().y() - self.mouse_relative_position_y)
                    # Set geometry for the button_window.
                    self.button_window.setGeometry(self.x(),  # x position
                                                   self.y() + self.height(),  # y position
                                                   self.width(),  # width
                                                   self.button_window_height)  # height
                else:
                    QApplication.setOverrideCursor(Qt.ArrowCursor)

        elif event.type() == QEvent.Show:
            self.button_window.setGeometry(self.x(),  # x position
                                           self.y() + self.height(),  # y position
                                           self.width(),  # width
                                           self.button_window_height)  # height
            self.button_window.show()

        else:
            return False

        self.central_widget.update()
        QCoreApplication.processEvents()
        return True


class ButtonWindow(QWidget):
    def __init__(self) -> None:
        super(ButtonWindow, self).__init__()

        # Set the flags 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        widget_stylesheet = "QWidget#button_window {" \
                            "background-color: rgba(255, 255, 255, 2);" \
                            "}"

        button_stylesheet = """
                            QPushButton {
                                background-color: #4CAF50; /* 背景顏色 */
                                border: none; /* 移除按鈕邊框 */
                                color: white; /* 文字顏色 */
                                padding: 0px 0px; /* 內邊距，控制按鈕大小 */
                                text-align: center; /* 文字置中 */
                                text-decoration: none;
                                font-size: 16px;
                                margin: 0px 0px;
                                border-radius: 5px; /* 圓角 */
                            }
                            
                            QPushButton:hover {
                                background-color: #45a049; /* 滑鼠懸停時的背景顏色 */
                            }
                        """

        self.button_save = QPushButton("Save")
        self.button_save.setFixedSize(85, 30)
        self.button_save.setMouseTracking(True)
        self.button_save.installEventFilter(self)
        self.button_save.setStyleSheet(button_stylesheet)

        self.button_clipboard = QPushButton("Copy")
        self.button_clipboard.setFixedSize(85, 30)
        self.button_clipboard.setMouseTracking(True)
        self.button_clipboard.installEventFilter(self)
        self.button_clipboard.setStyleSheet(button_stylesheet)

        self.button_close = QPushButton("Close")
        self.button_close.setFixedSize(85, 30)
        self.button_close.setMouseTracking(True)
        self.button_close.installEventFilter(self)
        self.button_close.setStyleSheet(button_stylesheet)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(self.button_save)
        horizontal_layout.addWidget(self.button_clipboard)
        horizontal_layout.addWidget(self.button_close)
        vert_layout = QVBoxLayout()
        vert_layout.addLayout(horizontal_layout)

        self.setLayout(vert_layout)
        self.setStyleSheet(widget_stylesheet)
        self.setObjectName("button_window")

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseMove:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            return True
        else:
            return False


if __name__ == '__main__':
    app = QApplication([])
    window = ScreenBox()
    window.show()
    sys.exit(app.exec_())