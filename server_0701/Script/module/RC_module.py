import Config
import serial
import requests
import math
import time
import numpy as np 
import os
import datetime 

ArduinoPort="/dev/ttyACM0"
Commu=serial.Serial(ArduinoPort,9600)

Pwm_Switch=[]
for i in range(0,3):
    Pwm_Switch.insert(i,0)


def correctThrusterPWM(LT,RT,correction_Factor):
    correct_RT = 0 
    if RT > 1500:
        correct_RT = RT + correction_Factor
    elif RT < 1500:
        correct_RT = RT - correction_Factor
    else:
        correct_RT = 1500

    return LT, correct_RT 
     


def ALL_SetPwmValue(Fmax,Bmax,Diff,FB,LR):
    try:
        upperLimit= 360
        FB_=FB
        LR_=LR
        FB = (FB - 1500) / (400)
        LR = (LR - 1500) / (400 * 2)
        Left_Thruster_Offset = max(FB, 0) * Fmax + min(FB, 0) * Bmax + np.sign(FB+0.00001)*(max(LR, 0) + min(LR, 0)) * Diff
        Right_Thruster_Offset = max(FB, 0) * Fmax + min(FB, 0) * Bmax - np.sign(FB+0.00001)*(max(LR, 0) + min(LR, 0)) * Diff
        Left_Thruster_Corrector = upperLimit - max(Right_Thruster_Offset, upperLimit)
        Right_Thruster_Corrector = upperLimit - max(Left_Thruster_Offset, upperLimit)
        Left_Thruster_Offset = min(Left_Thruster_Offset, upperLimit)
        Right_Thruster_Offset = min(Right_Thruster_Offset, upperLimit)
        Left_Thruster = int(1500 + Left_Thruster_Offset)# + Left_Thruster_Corrector)
        Right_Thruster = int(1500 + Right_Thruster_Offset)# + Right_Thruster_Corrector)
        #if Left_Thruster<1540: 
            #Left_Thruster=1500
        #if Right_Thruster<1540:
            #Right_Thruster=1500
    except:
        FB_, LR_ = 1500, 1500
        Left_Thruster = 1500
        Right_Thruster = 1500
    return FB_, LR_, Left_Thruster, Right_Thruster


def ALL_postToRC(Index,LT, RT, mode):
    URL = 'http://192.168.2.10:9021/Thruster'
    UNAME= 'Thruster'
    with open('./data/Thruster.dat','w') as lightFile:
        lightFile.write(str(LT) + " " + str(RT))
    LightFile_req = open('./data/Thruster.dat', "rb")
    LightFile = {'thrusterFile': LightFile_req}
    reqdata = {'uname': UNAME, 'fileName': "Thruster.dat"}
    try:
        res = requests.post(URL, files=LightFile, data=reqdata,timeout=0.1)
        LightFile_req.close()
        if res.status_code == 200:
            os.remove('./data/Thruster.dat')
    except requests.exceptions.Timeout:
        ALL_postToRC(Index,LT,RT,mode)
    except requests.exceptions.ConnectionError:
        ALL_postToRC(Index,LT,RT,mode)
        


def reciving_arduino(running, mode):
    forceQuit = 2000
    try:
    #    forceQuit = 2000
        Parsing=Commu.readline().decode().split(" ")
        if Parsing[0]!='' and len(Parsing)==3:
            Pwm_Switch[0]=int(Parsing[0].strip("\n").strip("\r"))
            Pwm_Switch[1]=int(Parsing[1].strip("\n").strip("\r"))
            Pwm_Switch[2]=int(Parsing[2].strip("\n").strip("\r"))
            LR=Pwm_Switch[0]
            FB=Pwm_Switch[1]
            forceQuit = Pwm_Switch[2]
            if (int(Pwm_Switch[0]) != 1500 or int(Pwm_Switch[1]) != 1500):
                mode = "RC"
            if int(Pwm_Switch[0]) >= 1100 and int(Pwm_Switch[0]) <= 1900:
                if (int(Pwm_Switch[1]) >= 1100 and int(Pwm_Switch[1]) <= 1900):
                    return LR, FB , forceQuit
                else:
                    return 1500, 1500 , forceQuit
            else: 
                return 1500, 1500 , forceQuit
        else:
            return 1500, 1500, forceQuit
    except KeyboardInterrupt:
        running = false
    except:
        print("please excute again")
        return 1500, 1500, forceQuit


def postToLED(mode):
    with open(Config.filePathForLED, 'w') as LEDFile:
        LEDFile.write(mode)
    LEDFile_requests = open(Config.filePathForLED, 'rb')
    LEDFile = {'LEDFile': LEDFile_requests}
    requests_data = {'uname':Config.unameForLED,  'fileName':Config.fileNameForLED}
    try:
        poster = requests.post((Config.urlForLED), files=LEDFile, data=requests_data, timeout=0.1)
        LEDFile_requests.close()
    except requests.exceptions.Timeout:
        postToLED(mode)
    except requests.exceptions.ConnectionError:
        postToLED(mode)


