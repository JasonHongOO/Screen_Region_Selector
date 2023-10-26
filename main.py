import sys
import json

from RegionSelector import ScreenCapture
from ScreenBox import ScreenBox
from PyQt5.QtWidgets import QApplication


def main():
    print("Selection Range : ")
    print(f"選取的區域座標: (Top, Left, Width, Height)")
    app = QApplication(sys.argv)
    window = ScreenCapture()
    app.exec_()
    if window.begin and window.end:
        left, top = window.begin.x(), window.begin.y()
        right, down = window.end.x(), window.end.y()

        width = right - left + 1
        height = down - top + 1
        print(f"選取的區域座標: ({top}, {left}, {width}, {height})")
    
    window = ScreenBox(left, top, width, height)
    window.show()
    app.exec_()

    with open("Coordination.json", "r") as json_file:
        data = json.load(json_file)
        left = data['left']
        top = data['top']
        width = data['width']
        height = data['height']

    print(f"選取的區域座標: ({top}, {left}, {width}, {height})")

    # 設定視窗大小
    screen_size = {"top": top, "left": left, "width": width, "height": height}
    print(f"Top : {screen_size['top']}")
    print(f"Left : {screen_size['left']}")
    print(f"Width : {screen_size['width']}")
    print(f"Height : {screen_size['height']}")

if __name__ == "__main__":
    main()

    # print("OK")