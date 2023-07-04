import serial
import math
import time
import pigpio as gpio
import numpy as np
import os
import requests


def PostThrusterData(LeftThruster, RightThruster, CenterThruster):
    UNAME = 'Thruster'
    URL = 'http://192.168.2.2:9016/Thruster'
    with open("./data/ThrusterData.dat","w") as ThrusterFile:
        ThrusterFile.write(str(LeftThruster)+' '+str(RightThruster)+' '+str(CenterThruster)+'\n')
    ThrusterFile_req = open('./data/ThrusterData.dat','rb')
    ThrusterFile = {'ThrusterFile':ThrusterFile_req}
    reqData = {'uname':UNAME, 'fileName':ThrusterFile}
    try:
        res = requests.post(URL, files=ThrusterFile, data=reqData)
        ThrusterFile_req.close()
    except requests.exceptions.Timeout:
        PostThrusterData(ThrusterFileName, ThrusterFilePath)


def ALL_SetPwmValue(Fmax,Bmax,Diff,FB,LR):
    print("read ALL_SetPwmValue")
    try:
        upperLimit=350
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
        Left_Thruster = int(1500 + Left_Thruster_Offset + Left_Thruster_Corrector)
        Right_Thruster = int(1500 + Right_Thruster_Offset + Right_Thruster_Corrector)
        #Center_Thruster = min(Fmax,FB_)
    except:
        FB_, LR_ = 1500, 1500
        Left_Thruster = 1500
        Right_Thruster = 1500
        print("read out ALL_SetPwmValue")
    return Left_Thruster, Right_Thruster


def ThrusterOperation(Left_Thruster,Right_Thruster,Center_Thruster):
    try:
        print("Left : ",Left_Thruster, " Right : ",Right_Thruster,"Center : ", Center_Thruster)
        print('####################################################')
        pi_connect.set_servo_pulsewidth(19,Left_Thruster)
        pi_connect.set_servo_pulsewidth(20,Right_Thruster)
        pi_connect.set_servo_pulsewidth(5,Center_Thruster)
    except KeyboardInterrupt:
        print("error1")
        pi_connect.set_servo_pulsewidth(19,1500)
        pi_connect.set_servo_pulsewidth(20,1500)
        pi_connect.set_servo_pulsewidth(5,1500)
    except:
        print("error2")
        pi_connect.set_servo_pulsewidth(19,1500)
        pi_connect.set_servo_pulsewidth(20,1500)
        pi_connect.set_servo_pulsewidth(5,1500)

RCmode = False

arduinoPort = "/dev/ttyACM0"
reception = serial.Serial(arduinoPort,9600)
pi_connect= gpio.pi()

LT = RT = CT = FB = LR = 1500

#############################################
maxF = 350
maxB = 350
maxR = 700
#############################################

LL = int(input('Input Left >>> '))
RR = int(input('Input Right >>> '))
CC = int(input('Input Center >>> '))

while RCmode == False:
    rawRC = reception.readline().decode('utf-8', errors='ignore').split(" ")
    if len(rawRC) == 2 and rawRC[0]!='' and 1100 <= int(rawRC[0]) <= 1900:
        FB = int(rawRC[0])
    ThrusterOperation(LL,RR,CC)
    if 1600 < FB or 1400 > FB:
        RCmode = True

while RCmode:
    try:
        rawRC = reception.readline().decode('utf-8', errors='ignore').split(" ")
        if len(rawRC) == 2 and rawRC[0]!='' and 1100 <= int(rawRC[0]) <= 1900:
            FB = int(rawRC[0])
            LR = int(rawRC[1].strip("\n").strip("\r"))
            print(FB, LR)
            if 1100 <= LR <= 1900:
                LT, RT = ALL_SetPwmValue(maxF, maxB, maxR, FB, LR)
                CT = int((LT+RT)/2)
                ThrusterOperation(LT, RT, CT)
                #PostThrusterData(LeftThruster,RightThruster,CenterThruster)
    except KeyboardInterrupt:
        LT = RT = CT = FB = LR = 1500
        pi_connect.set_servo_pulsewidth(19,1500)
        pi_connect.set_servo_pulsewidth(20,1500)
        pi_connect.set_servo_pulsewidth(5,1500)
        Running = False
        break
