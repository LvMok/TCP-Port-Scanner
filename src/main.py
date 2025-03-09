import sys
import os
import socket as sock
import ipaddress as checker

from PyQt5.QtWidgets import *
from PyQt5 import uic

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Scanner_ui.ui",self)
        self.ui.show()
        
        self.run()
    
    def run(self):
        pass

if __name__ == '__main__':
    os.chdir(str(os.getcwd())+'\\src')
    
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()