#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer,QDateTime, QFile, QTextStream, Qt
from PyQt5.QtGui import QFont

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


#LISTEN_PORT = 49006
SEND_PORT = 49000
XPLANE_IP = "192.168.0.18"


# Egna  funktioner
current_milli_time = lambda: int(round(time.time() * 1000))


parser = argparse.ArgumentParser()

parser.add_argument("--ip", help="Ip address of X-plane")
args = parser.parse_args()

if args.ip:
    XPLANE_IP = args.ip
print ("Connecting to ", XPLANE_IP)

def signal_handler(sig, frame):
        print("You pressed Ctrl+C!")
        running = False
        sys.exit(0)
        os._exit(0)

def updateSlider(self, lamp, dataref, type=1):
    value = self.xp.getDataref(dataref,10)
    
    if (type == 1):
        value = value*100 + 100
    if (type == 2):
        value = value*100
    #print("udpate slider", value)
    lamp.setValue(int(value))

def updateText(self, lamp, dataref):
    value = self.xp.getDataref(dataref,1)
    lamp.setText(str(int(value))+"%")

def updateLamp(self, lamp, dataref, color):
    font = QFont("Sans")
    font.setPointSize(12)
    lamp.setFont(font)
    if (self.xp.getDataref(dataref,2) >0):
        lamp.setStyleSheet("background-color: "+color)
    else:
        lamp.setStyleSheet("background-color: #AAAAAA")
    
def connectButton(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonPressed(dataref))
    button.released.connect(lambda: self.buttonReleased(dataref))
    
def connectButtonCommand(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonPressedCommand(dataref))
    
    
def connectOnButton(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonPressed(dataref))
def connectOffButton(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonReleased(dataref))


class ColorButton():
    def __init__(self, parent, button, dataref, color, type, lampDR=""):
        font = button.font()
        font.setPointSize(12)
        button.setFont(font)
        self.parent = parent
        self.button = button
        self.dataref = dataref
        self.color = color
        self.type = type
        if (lampDR==""):
            self.lampdataref = self.dataref
        else:
            self.lampdataref = lampDR
        
        if (type == 0):
            button.pressed.connect(self.onClickedToggle)
        if (type == 1):
            button.pressed.connect(self.buttonPressed)
            button.released.connect(self.buttonReleased)
        
    def onClickedToggle(self):
        prevvalue = self.parent.xp.getDataref(self.dataref, 1)
        if (prevvalue == 1):
            self.parent.xp.sendDataref(self.dataref, 0)
        else:
            self.parent.xp.sendDataref(self.dataref, 1)
            
    def buttonPressed(self):
        print("buttonPressed2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 1)
        
    def buttonReleased(self):
        print("buttonReleased2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 0)  
        
    def updateColor(self):
        if (self.parent.xp.getDataref(self.lampdataref,2) >0):
            self.button.setStyleSheet("background-color: "+self.color)
        else:
            self.button.setStyleSheet("background-color: #bbbbbb")
        

class RunGUI(QMainWindow):
    def __init__(self,):
        super(RunGUI,self).__init__()

        
        self.buttonList = []
        self.xp = XPlaneUdp.XPlaneUdp(XPLANE_IP,SEND_PORT)
        self.xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)

        self.xp.getDataref("JAS/autopilot/att",1)
        self.xp.getDataref("JAS/lamps/hojd",1)
        
        self.initUI()
        
    def initUI(self):
        #self.root = Tk() # for 2d drawing
        
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(current_dir, "../ui/main.ui"), self)
        print(self.ui)
        #self.setGeometry(200, 200, 300, 300)
        #self.resize(640, 480)
        self.setWindowTitle("JAS IS Cockpit")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        
        # connectButton(self, self.ui.button_afk,"JAS/button/afk")
        # connectButton(self, self.ui.button_hojd,"JAS/button/hojd")
        # connectButton(self, self.ui.button_att,"JAS/button/att")
        # connectButton(self, self.ui.button_spak,"JAS/button/spak")
        connectButton(self, self.ui.button_start,"JAS/io/frontpanel/di/start")
        connectButton(self, self.ui.button_master,"JAS/io/frontpanel/di/master")
        
        connectButton(self, self.ui.button_falltank,"JAS/io/vu22/di/falltank")
        connectButton(self, self.ui.button_systest,"JAS/io/vu22/di/syst")
        connectButton(self, self.ui.button_lamptest,"JAS/io/vu22/di/lampprov")
        #connectButton(self, self.ui.mot_fack,"JAS/system/mot/fack")
        #connectButton(self, self.ui.mot_rems,"JAS/system/mot/rems")
        
        

        
        connectButtonCommand(self, self.ui.button_reload_acf,"sim/operation/reload_aircraft_no_art")
        
        

        #self.buttonList.append( ColorButton(self,self.ui.buttonlamp_antikoll, "sim/cockpit/electrical/nav_lights_on", "yellow", 0) )
        
        self.buttonList.append( ColorButton(self,self.ui.button_afk, "JAS/io/frontpanel/di/afk", "orange", 1, lampDR="JAS/io/frontpanel/lo/afk") )
        self.buttonList.append( ColorButton(self,self.ui.button_hojd, "JAS/io/frontpanel/di/hojd", "orange", 1, lampDR="JAS/io/frontpanel/lo/hojd") )
        self.buttonList.append( ColorButton(self,self.ui.button_att, "JAS/io/frontpanel/di/att", "orange", 1, lampDR="JAS/io/frontpanel/lo/att") )
        self.buttonList.append( ColorButton(self,self.ui.button_spak, "JAS/io/frontpanel/di/spak", "orange", 1, lampDR="JAS/io/frontpanel/lo/spak") )
        
        self.buttonList.append( ColorButton(self,self.ui.button_apu_on, "JAS/io/vu22/di/apu", "green", 0) )
        self.buttonList.append( ColorButton(self,self.ui.button_ess_on, "JAS/io/vu22/di/ess", "green", 0) )
        self.buttonList.append( ColorButton(self,self.ui.button_hstrom_on, "JAS/io/vu22/di/hstrom", "green", 0) )
        self.buttonList.append( ColorButton(self,self.ui.button_lt_kran_on, "JAS/io/vu22/di/ltbra", "green", 0) )
        
        self.buttonList.append( ColorButton(self,self.ui.button_mkv, "JAS/io/vu22/di/mkv", "orange", 1, lampDR="JAS/io/vu22/lamp/mkv") )
        self.buttonList.append( ColorButton(self,self.ui.button_rhm, "JAS/io/vu22/di/rhm", "orange", 1, lampDR="JAS/io/vu22/lamp/rhm") )
        self.buttonList.append( ColorButton(self,self.ui.button_sand, "JAS/io/vu22/di/sand", "orange", 1, lampDR="JAS/io/vu22/lamp/sand") )
        
        
        #self.buttonList.append( ColorButton(self,self.ui.dap_button_pluv, "JAS/system/dap/lamp/pluv", "green", 0) )
        
        
        
        
        self.ui.button_tanka.clicked.connect(self.buttonTankaFull)
        self.ui.button_tanka_50.clicked.connect(self.buttonTanka50)
        
        self.ui.auto_afk_text.valueChanged.connect(self.autoAFK)
        self.ui.auto_hojd_text.valueChanged.connect(self.autoHOJD)

        font = QFont("Sans")
        font.setPointSize(12)
        self.setFont(font)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(100)



    def updateGUI(self):
        for button in self.buttonList:
            button.updateColor()
        # if (self.xp.dataList["JAS/lamps/hojd"] >0):
        #     self.ui.lamps_hojd.setStyleSheet("background-color: orange")
        # else:
        #     self.ui.lamps_hojd.setStyleSheet("background-color: white")
        
        updateLamp(self, self.ui.lamps_master1, "JAS/io/frontpanel/lo/master1", "red")
        updateLamp(self, self.ui.lamps_master2, "JAS/io/frontpanel/lo/master2", "red")
        
        
        updateLamp(self, self.ui.lamps_hojdvarn, "JAS/io/frontpanel/lo/hojdvarn", "red")
        
        updateLamp(self, self.ui.lamps_airbrake, "JAS/io/frontpanel/lo/airbrake", "green")
        updateLamp(self, self.ui.lamps_a14, "JAS/io/frontpanel/lo/a14", "orange")
        updateLamp(self, self.ui.lamps_ks, "JAS/io/frontpanel/lo/ks", "orange")
        
        # updateLamp(self, self.ui.buttonlamp_lt_kran, "JAS/button/lt_kran", "green")
        updateLamp(self, self.ui.lamps_apu_gar, "JAS/io/vu22/lo/apugar", "green")
        updateLamp(self, self.ui.lamps_apu_red, "JAS/io/vu22/lo/apured", "red")
        # updateLamp(self, self.ui.buttonlamp_apu, "JAS/button/apu", "green")
        # updateLamp(self, self.ui.buttonlamp_hstrom, "JAS/button/hstrom", "green")
        # updateLamp(self, self.ui.buttonlamp_ess, "JAS/button/ess", "green")
        
        
        updateLamp(self, self.ui.lamps_park, "sim/cockpit2/controls/parking_brake_ratio", "red")
        
        
        updateText(self, self.ui.text_fuel, "JAS/fuel")
        # updateSlider(self, self.ui.spak_roll, "sim/joystick/yoke_roll_ratio", type=2)
        # updateSlider(self, self.ui.spak_pedaler, "sim/joystick/yoke_heading_ratio", type=2)
        # updateSlider(self, self.ui.spak_pitch, "sim/joystick/yoke_pitch_ratio", type=2)
        # updateSlider(self, self.ui.spak_gas, "sim/cockpit2/engine/actuators/throttle_ratio_all", type=2)
        # 
        #self.ui.auto_afk_text.setValue(self.xp.getDataref("JAS/autopilot/afk",1))
        
        # VAT tablån
        updateLamp(self, self.ui.vat_lamp_normsty, "JAS/io/vat/lo/normsty", "orange")
        updateLamp(self, self.ui.vat_lamp_luftsys, "JAS/io/vat/lo/luftsys", "orange")
        updateLamp(self, self.ui.vat_lamp_hhp1, "JAS/io/vat/lo/hhp1", "orange")
        updateLamp(self, self.ui.vat_lamp_hgen, "JAS/io/vat/lo/hgen", "orange")
        updateLamp(self, self.ui.vat_lamp_motor, "JAS/io/vat/lo/motor", "orange")
        updateLamp(self, self.ui.vat_lamp_dragkr, "JAS/io/vat/lo/dragkr", "orange")
        updateLamp(self, self.ui.vat_lamp_oljetr, "JAS/io/vat/lo/oljetr", "orange")
        
        
        updateLamp(self, self.ui.vat_lamp_abumod, "JAS/io/vat/lo/abumod", "orange")
        updateLamp(self, self.ui.vat_lamp_primdat, "JAS/io/vat/lo/primdat", "orange")
        updateLamp(self, self.ui.vat_lamp_hydr1, "JAS/io/vat/lo/hydr1", "orange")
        updateLamp(self, self.ui.vat_lamp_resgen, "JAS/io/vat/lo/resgen", "orange")
        updateLamp(self, self.ui.vat_lamp_mobrand, "JAS/io/vat/lo/mobrand", "orange")
        updateLamp(self, self.ui.vat_lamp_apu, "JAS/io/vat/lo/apu", "orange")
        updateLamp(self, self.ui.vat_lamp_apubrnd, "JAS/io/vat/lo/apubrnd", "orange")
        
        updateLamp(self, self.ui.vat_lamp_styrsak, "JAS/io/vat/lo/styrsak", "orange")
        updateLamp(self, self.ui.vat_lamp_uppdrag, "JAS/io/vat/lo/uppdrag", "orange")
        updateLamp(self, self.ui.vat_lamp_hydr2, "JAS/io/vat/lo/hydr2", "orange")
        updateLamp(self, self.ui.vat_lamp_likstrm, "JAS/io/vat/lo/likstrm", "orange")
        updateLamp(self, self.ui.vat_lamp_landst, "JAS/io/vat/lo/landst", "orange")
        updateLamp(self, self.ui.vat_lamp_bromsar, "JAS/io/vat/lo/bromsar", "orange")
        updateLamp(self, self.ui.vat_lamp_streck1, "JAS/io/vat/lo/streck1", "orange")
        
        updateLamp(self, self.ui.vat_lamp_felinfo, "JAS/io/vat/lo/felinfo", "orange")
        updateLamp(self, self.ui.vat_lamp_dator, "JAS/io/vat/lo/dator", "orange")
        updateLamp(self, self.ui.vat_lamp_streck2, "JAS/io/vat/lo/streck2", "orange")
        updateLamp(self, self.ui.vat_lamp_brasys, "JAS/io/vat/lo/brasys", "orange")
        updateLamp(self, self.ui.vat_lamp_bramgd, "JAS/io/vat/lo/bramgd", "orange")
        updateLamp(self, self.ui.vat_lamp_oxykab, "JAS/io/vat/lo/oxykab", "orange")
        updateLamp(self, self.ui.vat_lamp_huvstol, "JAS/io/vat/lo/huvstol", "orange")
        
        # ST
        
        updateLamp(self, self.ui.st_lamp_j, "JAS/io/st/lo/J", "orange")
        updateLamp(self, self.ui.st_lamp_a, "JAS/io/st/lo/A", "orange")
        updateLamp(self, self.ui.st_lamp_s, "JAS/io/st/lo/S", "orange")
        
        
        
        
        pass
            
    def buttonPressedCommand(self, dataref):
        print("buttonPressedCommand:", dataref)
        self.xp.sendCommand(dataref)
                    
    def buttonPressed(self, dataref):
        print("buttonPressed:", dataref)
        self.xp.sendDataref(dataref, 1)
        
    def buttonReleased(self, dataref):
        print("buttonReleased:", dataref)
        self.xp.sendDataref(dataref, 0)   
             
    def buttonTankaFull(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 3000)
    def buttonTanka50(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 1500)
        
    def autoAFK(self):
        newvalue = float(self.ui.auto_afk_text.value()) / 1.85200
        self.xp.sendDataref("JAS/autopilot/afk", newvalue)
        
    def autoHOJD(self):
        newvalue = float(self.ui.auto_hojd_text.value()) / 0.3048
        self.xp.sendDataref("JAS/autopilot/alt", newvalue)
                
    def loop(self):
        self.xp.readData()
        self.updateGUI()
        
        #print(self.xp.dataList)
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
