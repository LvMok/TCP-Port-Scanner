import sys
import socket as sock
import ipaddress as checker

from PyQt5.QtWidgets import *
from PyQt5 import uic

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Scanner_ui.ui",self)
        self.ui.show()
    
    def run(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = uic.loadUi('main.ui')
    window.show()
    sys.exit(app.exec_())