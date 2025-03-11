import sys
import os

import time

from tkinter import filedialog
from PyQt5.QtWidgets import *
from PyQt5 import uic

import asyncio
import qasync

import re


Start_port = 1
End_port = 81
FilePath = ""


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Scanner_ui.ui",self)
        self.ui.show()

        RangeFrame = self.Setting_Tab.findChild(QWidget,'TargetPort').findChild(QWidget,'RangeMode')
        FileFrame = self.Setting_Tab.findChild(QWidget,'TargetPort').findChild(QWidget,'FileMode')
        self.LoadingUI = None

        RangeFrame.findChild(QWidget,'RangeConfirm').clicked.connect(self.Range_input)
        FileFrame.findChild(QWidget,'FileConfirm').clicked.connect(self.File_input)
        self.ChangeFile.clicked.connect(self.Change_File)
        self.ChangeRange.clicked.connect(self.Change_range)
        self.Delete.clicked.connect(self.delete_all_item)

        self.Scan.clicked.connect(lambda: asyncio.create_task(self.scan()))

        self.temp_tree = None
        self.current_num = 0
        self.Tasks = list()
        self.isShowClosePort = False
        self.timeout_sec = 1
        self.ScanPorts = list()
        self.CurrentPortRMode = "Range"

    def read_portfile(self):
        try:
            with open(FilePath,'r') as f:
                for line in f:
                    raw = line.strip()

                    if raw.count('~') > 0: #format 1
                        splited = raw.split('|')
                        for string in splited:
                            string = string.strip()
                            info = string.split('~')

                            for i in range(int(info[0]),int(info[1])):
                                self.ScanPorts.append(i)


                    elif raw.count(',') > 0: #format 2
                        splited = raw.split(',')
                        for string in splited:
                            string = string.strip()
                            self.ScanPorts.append(int(string))

                    elif raw.count('!') > 0: #format 3
                        self.ScanPorts = list(set(self.ScanPorts))
                        splited = raw.split('|')
                        for string in splited:
                            string = string.strip()
                            self.ScanPorts.remove(int(string.replace('!','')))

                    elif raw.isdigit():
                        self.ScanPorts.append(int(raw))
                    else:
                        continue
        except Exception as e:
            self.CurrentPortRMode = "File_Error"



    def show_loading(self):
        self.LoadingUI = QDialog(self)
        uic.loadUi("Loading_UI.ui",self.LoadingUI)
        self.LoadingUI.setModal(True)
        self.LoadingUI.show()

        self.progress_bar = self.LoadingUI.findChild(QProgressBar, "Progress")
        if self.progress_bar:
            self.progress_bar.setValue(0) 
    
    def close_loading(self):
        if self.LoadingUI:
            self.LoadingUI.close()
            self.LoadingUI = None

    async def send_packet(self, target, port):
        newPort = QTreeWidgetItem(self.temp_tree)
        newPort.setText(1, f"Port {port}")
        newPort.setText(2, "None")
        
        is_close_port = False

        self.current_num += 1

        try:
            task = asyncio.create_task(
                asyncio.open_connection(target,port=port)
            )
            self.Tasks.append(task)

            reader, writer = await asyncio.wait_for(
                task,
                self.timeout_sec
            )
            
            newPort.setText(3, "Open 🟢")
            writer.close()
            await writer.wait_closed()

        except ConnectionRefusedError:
            newPort.setText(3, "Closed 🔴")
            newPort.setText(4, "Connection Refused")
            is_close_port = True

        except asyncio.TimeoutError:
            newPort.setText(3, "Closed 🔴")
            is_close_port = True
        
        except asyncio.CancelledError:
            newPort.setText(3, "Closed 🔴")
            newPort.setText(4, "Cancelled")
            is_close_port = True
            return

        if is_close_port and not self.isShowClosePort:
            self.temp_tree.removeChild(newPort)
        
        self.LoadingUI.findChild(QProgressBar,"Progress").setValue(int(self.current_num / End_port * 100))

    
    async def scan(self):
        if self.CurrentPortRMode == "File":
            self.read_portfile()
            self.ScanPorts = list(set(self.ScanPorts))
            self.ScanPorts.sort()

        self.show_loading()

        self.temp_tree = QTreeWidgetItem(self.MainTree)
        if self.CurrentPortRMode == "File_Error":
            self.temp_tree.setText(0,"File Error")
            self.temp_tree.setText(4,"Please Check Your Port File Location")
            self.close_loading()
            return
        
        self.Scan.setEnabled(False)

        # get Setting Part
        target = self.Target.text()
        self.timeout_sec = self.ScanDelay.value()
        self.isShowClosePort = self.ClosePort.isChecked()
        self.temp_tree.setText(0,target)

        if target.count('.') == 0 or target.count('.') >= len(target) or re.search(r'[^a-zA-Z0-9.]', target):
            self.temp_tree.setText(4,"Not Vaild Host")
            self.close_loading()
            self.Scan.setEnabled(True)
            return
        
        # end Setting Part

        self.Tasks.clear()

        start_time = time.time()

        if self.CurrentPortRMode == "File":
            try:
                task = [self.send_packet(target, port) for port in self.ScanPorts]
                await asyncio.gather(*task)
            except Exception as e:
                self.temp_tree.setText(4,"Not Vaild Host")
                self._stopScan()
            
        elif self.CurrentPortRMode == "Range":
            try:
                task = [self.send_packet(target, port) for port in range(Start_port,End_port+1)]
                await asyncio.gather(*task)
            except Exception as e:
                self.temp_tree.setText(4,"Not Vaild Host")
                self._stopScan()


        end_time = time.time()
        self.temp_tree.setText(0,f"{target} ({end_time-start_time:.2f}s)")

        if self.CurrentPortRMode == "File_Error":
            self.CurrentPortRMode = "File"

        self.temp_tree = None
        self.Scan.setEnabled(True)
        self.current_num = 0
        self.close_loading()

    
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

        self.CurrentPortRMode = "File"
        self.FileName.setText(filepath)


    # UI Function
    def Change_File(self):

        self.FileMode.show()
        self.RangeMode.hide()

        self.CurrentPortRMode = "File"
    
    def Change_range(self):

        self.FileMode.hide()
        self.RangeMode.show()

        self.CurrentPortRMode = "Range"
    
    def _stopScan(self):
        self.TreadIsRunning = False  #스캔 중단 플래그 설정

        #현재 실행 중인 모든 태스크 취소
        for task in self.Tasks:
            if not task.done():  # 완료되지 않은 경우만 취소
                task.cancel()

        self.Tasks.clear()
    
    def delete_all_item(self):
        self.MainTree.clear()



def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

if __name__ == '__main__':
    os.chdir(str(os.getcwd())+'\\src')
    
    suppress_qt_warnings()

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    myWindow = Window()
    myWindow.show()

    with loop:
        loop.run_forever()

"""

Port File Format

형식 1) Number1 ~ Number2 | Number3 ~ Number4 : Number 부터 Number까지
형식 2) Number1, Number2, Number3 : Number1, Number2, Number3 사용
형식 3) !Number1 | !Number2 | !Number3 : Number1, Number2, Number3 제외

같은 줄에는 같은 형식만 사용가능
여러 줄에 다양한 형식 사용가능

"""