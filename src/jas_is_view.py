from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer,QDateTime, QFile, QTextStream

import sys
import json
import random
import argparse
import datetime
import os
import time
import colorsys
import traceback
import threading

from pathlib import Path
import XPlaneUdp


LISTEN_PORT = 49005
SEND_PORT = 49000
XPLANE_IP = "192.168.0.18"


# Egna  funktioner
current_milli_time = lambda: int(round(time.time() * 1000))


parser = argparse.ArgumentParser()
parser.add_argument("--nogui", help="Run without GUI", action="store_true")
parser.add_argument("--file", help="Run selected file, use with --nogui")
args = parser.parse_args()
if args.nogui:
    GUI = False
    print("GUI turned off")
else:
    GUI = True



def signal_handler(sig, frame):
        print("You pressed Ctrl+C!")
        running = False
        sys.exit(0)
        os._exit(0)


def updateLamp(self, lamp, dataref, color):
    if (self.xp.getDataref(dataref,2) >0):
        lamp.setStyleSheet("background-color: "+color)
    else:
        lamp.setStyleSheet("background-color: white")
    
def connectButton(self, button, dataref):
    button.pressed.connect(lambda: self.buttonPressed(dataref))
    button.released.connect(lambda: self.buttonReleased(dataref))

class RunGUI(QMainWindow):
    def __init__(self,):
        super(RunGUI,self).__init__()

        self.initUI()
        
        self.xp = XPlaneUdp.XPlaneUdp(XPLANE_IP,SEND_PORT)
        self.xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)

        self.xp.getDataref("JAS/autopilot/att",1)
        self.xp.getDataref("JAS/lamps/hojd",1)
        # self.xp.sendDataref("sim/cockpit/electrical/night_vision_on", 1)
        # 
        # self.xp.sendDataref("sim/cockpit/electrical/night_vision_on", 0)

        # 
        
        
    def initUI(self):
        #self.root = Tk() # for 2d drawing
        
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(current_dir, "../ui/main.ui"), self)
        print(self.ui)
        #self.setGeometry(200, 200, 300, 300)
        self.resize(640, 480)
        self.setWindowTitle("JAS IS View")
        
        connectButton(self, self.ui.button_hojd,"JAS/button/hojd")
        connectButton(self, self.ui.button_att,"JAS/button/att")
        connectButton(self, self.ui.button_spak,"JAS/button/spak")
        connectButton(self, self.ui.button_start,"JAS/button/start")
        

        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(100)



    def updateGUI(self):
        # if (self.xp.dataList["JAS/lamps/hojd"] >0):
        #     self.ui.lamps_hojd.setStyleSheet("background-color: orange")
        # else:
        #     self.ui.lamps_hojd.setStyleSheet("background-color: white")
        updateLamp(self, self.ui.lamps_hojd, "JAS/lamps/hojd", "orange")
        updateLamp(self, self.ui.lamps_att, "JAS/lamps/att", "orange")
        updateLamp(self, self.ui.lamps_spak, "JAS/lamps/spak", "orange")
        
        updateLamp(self, self.ui.lamps_master1, "JAS/lamps/master1", "red")
        updateLamp(self, self.ui.lamps_master2, "JAS/lamps/master2", "red")
        
        updateLamp(self, self.ui.lamps_airbrake, "JAS/lamps/airbrake", "green")
        
        updateLamp(self, self.ui.buttonlamp_apu, "JAS/button/apu", "green")
        updateLamp(self, self.ui.lamps_apu_gar, "JAS/lamps/apu_gar", "green")
        
        pass
            
            
    def buttonPressed(self, dataref):
        print("buttonPressed:", dataref)
        self.xp.sendDataref(dataref, 1)
        
    def buttonReleased(self, dataref):
        print("buttonReleased:", dataref)
        self.xp.sendDataref(dataref, 0)   
             
    def loop(self):
        self.xp.readData()
        self.updateGUI()
        #print("loop")
        self.timer.start(10)
        pass
        

if __name__ == "__main__":

    try:
        app = QApplication(sys.argv)
        win = RunGUI()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        print(traceback.format_exc())
        os._exit(1)
    print ("program end")
    os._exit(0)