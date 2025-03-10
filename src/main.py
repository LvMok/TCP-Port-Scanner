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

        RangeFrame = self.Setting_Tab.findChild(QWidget,'TargetPort').findChild(QWidget,'RangeMode')
        FileFrame = self.Setting_Tab.findChild(QWidget,'TargetPort').findChild(QWidget,'FileMode')
        
        RangeFrame.findChild(QWidget,'RangeConfirm').clicked.connect(self.Range_input)
        FileFrame.findChild(QWidget,'FileConfirm').clicked.connect(self.File_input)
        self.ChangeFile.clicked.connect(self.Change_File)
        self.ChangeRange.clicked.connect(self.Change_range)

        self.Scan.clicked.connect(self.scan)
        
    
    def scan(self):
        # get Setting Part
        target = self.Target.toPlainText()
        if self.ChangeRange.isChecked():
            print("debug")
    
    def Range_input(self):
        print("Trigg Range")
    
    def File_input(self):
        print("Trigg File")

    def Change_File(self):
        self.FileMode.show()
        self.RangeMode.hide()
    
    def Change_range(self):
        self.FileMode.hide()
        self.RangeMode.show()

def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

if __name__ == '__main__':
    os.chdir(str(os.getcwd())+'\\src')
    
    suppress_qt_warnings()

    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()