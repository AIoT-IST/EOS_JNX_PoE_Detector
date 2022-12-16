from PyQt5 import QtWidgets, QtGui, QtCore
from PoE_Detector_UI import Ui_MainWindow
from subprocess import Popen, PIPE
from array import array
from PyQt5.QtCore import QTimer
import ctypes  
import os, sys
import time
import threading
import numpy as np
import cv2
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime

loadclib = ctypes.cdll.LoadLibrary   
lib = loadclib("/usr/local/lib/libAVS_SDK.so")  #Change lib here
libc = loadclib("libc.so.6") 
PoEVoltage = []
PoEPowerGood = []

PoE_CURRENT_Identifier = ctypes.c_int(0)
PoE_VOLT_Identifier = ctypes.c_int(1)
PoE_POECLASS_Identifier = ctypes.c_int(2)
PoE_POWERGOOD_Identifier = ctypes.c_int(3)
PoE_LASTPOWERSTATE_Identifier = ctypes.c_int(4)

PoE_VOLT = ctypes.c_float(0)
PowerGood = ctypes.c_float(0)

if not os.geteuid()==0:
	sys.exit("Need root privileges, please use sudo command...")

m_handle = lib.AVS_GetProductHandle(ctypes.c_int(0))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.EOS_Information()

        # Get Init state of PoE PowerGood
        for port in range(4):
                lib.AVS_PoEGetPortProperty(m_handle,ctypes.c_int(port), PoE_POWERGOOD_Identifier, ctypes.byref(PowerGood))
                PoEPowerGood.insert(port, round(PowerGood.value))

        self.EOS_PoE_Status()

        self.timer=QTimer(self) #call QTimer
        self.timer.start(1000)  #Trigger event every ? ms
        self.timer.timeout.connect(self.EOS_PoE_Status)

        self.s=0
        self.log_count=4

    def EOS_Information(self):

        versionstr = ctypes.create_string_buffer(256)
        lib.AVS_GetProductInfo(m_handle,versionstr,ctypes.sizeof(versionstr))
            
        DINums = ctypes.c_int(0)
        lib.AVS_DIOGetDINums(m_handle,ctypes.byref(DINums))
        DINumbers="\nDI Nums = " + str(DINums.value)
         
        DONums = ctypes.c_int(0)
        lib.AVS_DIOGetDONums(m_handle,ctypes.byref(DONums))
        DONumbers="  DO Nums = " + str(DONums.value)

        b=array('b', map(ord,versionstr)).tostring()
        s=b.decode() + DINumbers + DONumbers
        self.ui.label.setText(s)
             
    def EOS_PoE_Status(self):        	
        for port in range(4):
                # Get PoE voltage
                lib.AVS_PoEGetPortProperty(m_handle,ctypes.c_int(port), PoE_VOLT_Identifier, ctypes.byref(PoE_VOLT))
                PoEVoltage.insert(port, round(PoE_VOLT.value))

                # Get PoE PowerGood
                lib.AVS_PoEGetPortProperty(m_handle,ctypes.c_int(port), PoE_POWERGOOD_Identifier, ctypes.byref(PowerGood))
                # PoE PowerGood change of state
                if bool(round(PowerGood.value)) ^ bool(PoEPowerGood[port]):
                        PoEPowerGood[port]=round(PowerGood.value)
               
                        # Reset Log 
                        self.log_count-=1
                        if self.log_count < 0:
                                s=datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" Cam "+str(port+1)            
                                self.log_count=4
                        else:                
                                s=self.ui.label.text()+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" Cam "+str(port+1) 
                        
                        if round(PowerGood.value):
                                print(datetime.now().strftime("%H:%M:%S")+" camera "+str(port+1)+" plug!")
                                self.ui.label.setText(s+" plug!")
                                #QMessageBox.information(None, 'Camera Detection', "camera "+str(port+1)+" plug!   ")
                        else:
                                print(datetime.now().strftime("%H:%M:%S")+" camera "+str(port+1)+" unplug!")
                                self.ui.label.setText(s+" unplug!")
                                #QMessageBox.warning(None, 'Camera Detection', "camera "+str(port+1)+" unplug!   ")

        # PoE Voltage       
        self.ui.lcdNumber_Port1.display(PoEVoltage[0])
        self.ui.lcdNumber_Port2.display(PoEVoltage[1])
        self.ui.lcdNumber_Port3.display(PoEVoltage[2])
        self.ui.lcdNumber_Port4.display(PoEVoltage[3])


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
