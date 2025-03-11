import sys
import os
import socket as sock
import ipaddress as checker

import time
import concurrent.futures

from tkinter import filedialog
from PyQt5.QtWidgets import *
from PyQt5 import uic

import asyncio


Start_port = 1
End_port = 81
FilePath = ""

success_port = list()
fail_port = list()

Current_PortRMode = "Range"

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
        self.StopScan.clicked.connect(self._StopScan)

        self.Executor = None
        self.TreadIsRunning = False
        self.temp_tree = None

    async def send_packet(self, target, port):
        newPort = QTreeWidgetItem(self.temp_tree)
        newPort.setText(1, f"Port {port}")
        newPort.setText(2, "None")

        print("wejl\n")

        if not self.TreadIsRunning:
            return

        global success_port, fail_port

        session = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        session.settimeout(0.5)

        try:
            connect = session.connect_ex((target, port))
            if connect == 0:
                newPort.setText(3, "Open")
            else:
                newPort.setText(3, "Closed")

        except sock.timeout:
            return
        except OSError:
            self.TreadIsRunning = False
            self.Executor.shutdown(wait=False, cancel_futures=True)
        finally:
            session.close()
        
    
    async def scan(self):
        self.temp_tree = QTreeWidgetItem(self.MainTree)
        self.Scan.setEnabled(False)

        # get Setting Part
        target = self.Target.text()
        TimeOut_sec = self.ScanDelay.value()
        isShowClosePort = self.ClosePort.isChecked()

        self.temp_tree.setText(0,target)
        # end Setting Part

        global success_port
        global fail_port
        self.TreadIsRunning = True

        start_time = time.time()

        self.Executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)

        try:
            self.Executor.map(self.send_packet, [target]* (End_port+1-Start_port),range(Start_port,End_port+1))
        except Exception as e:
            print("exception")
            self.Executor.shutdown(wait=False,cancel_futures=True)
            self.TreadIsRunning = False
            

        success_port.sort()
        fail_port.sort()

        for i in success_port:
            print(f"Port {i} is Open")

        print("==================================== line ====================================")
        for i in fail_port:
            print(f"Port {i} is Closed")
            
        end_time = time.time()

        success_port.clear()
        fail_port.clear()

        print(f"Time Passed : {end_time - start_time:.2f}s")

        self.temp_tree = None
        self.Scan.setEnabled(True)

    
    def Range_input(self):
        text = self.PortRange.text()

        if len(text) == 0:
            self.PortRange.setText("Please Input Port Range")
            return
        elif text.count('~') != 1:
            self.PortRange.setText("Invalid Format")
            return
        

        splited = text.split('~')
        if splited[0].isdigit() and splited[1].isdigit():
            if int(splited[0]) < 0 or int(splited[1]) > 65535:
                self.PortRange.setText("Invalid Port Range")
                return
        else:
            self.PortRange.setText("Invalid Format")
            return
        
        global Start_port
        global End_port

        Start_port = int(splited[0])
        End_port = int(splited[1])

    def File_input(self):
        filepath = filedialog.askopenfilename(
            title="Select Port Range File",
            filetypes=[("Text files"," *.txt")],
        )

        if filepath == "":
            return
        
        global FilePath
        FilePath = filepath

        self.FileName.setText(filepath)


    # UI Function
    def Change_File(self):
        global Current_PortRMode

        self.FileMode.show()
        self.RangeMode.hide()

        Current_PortRMode = "File"
    
    def Change_range(self):
        global Current_PortRMode

        self.FileMode.hide()
        self.RangeMode.show()

        Current_PortRMode = "Range"
    
    def _StopScan(self):
        self.Executor.shutdown(wait=False,cancel_futures=True)
        self.TreadIsRunning = False


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

"""

Port File Format

형식 1) Number1 ~ Number2 : Number 부터 Number까지
형식 2) Number1, Number2, Number3 : Number1, Number2, Number3 사용
형식 3) !Number1, !Number2, !Number3 : Number1, Number2, Number3 제외

같은 줄에는 같은 형식만 사용가능
여러 줄에 다양한 형식 사용가능

"""