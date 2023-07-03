import math
import time
import requests
import os
import shutil
import datetime

global oldX, oldY, oldGPSTime
global oldGyro
global oldLT,oldRT,oldCT
global oldTime

runOption = True
updateGPS = False
headingByGPS = False
oldHeadingByGPS = False

oldX, oldY = 0, 0
oldGPSTime = 0
currX, currY = 0, 0
oldGyro = 0
oldShipHeading = 0
oldTime = 0
oldGPSHeading = 0
gpsHeading, velocity, betweenDistance,diffGPSAngle,delta_time =0,0,0,0,0
oldLT,oldRT,oldCT=1500,1500,1500
LT, RT, CT = 1500, 1500, 1500

def getGPSData():
    global oldX, oldY, oldGPSTime
    try:
        with open('/home/opencfd/OpenDEP/Receive/GPS/gpsData.dat', 'r') as gpsFile:
            gpsData = gpsFile.readline().strip('\n').split(' ')
            status = int(gpsData[0])
            gpsX = float(gpsData[1])
            gpsY = float(gpsData[2])
            gpsDataTime = time.time()
    except:
        gpsX = oldX
        gpsY = oldY
        gpsDataTime = oldGPSTime
    return gpsX, gpsY, gpsDataTime

def checkUpdateGPS(currX, currY):
    global oldX, oldY
    gpsX, gpsY, gpsDataTime = getGPSData()
    if oldX != gpsX or oldY != gpsY:
        currX = gpsX
        currY = gpsY
        updateGPS = True
    else:
        updateGPS = False
    oldX = gpsX
    oldY = gpsY
    return updateGPS, currX, currY, gpsDataTime

def getGyroData():
    global oldGyro
    try:
        with open('/home/opencfd/OpenDEP/Receive/Gyro/gyroData.dat', 'r') as gyroFile:
            gyroData = gyroFile.readline()
            gyroHeadAngle = float(gyroData)
    except:
        gyroHeadAngle = oldGyro
    oldGyro = gyroHeadAngle
    return gyroHeadAngle

def getRCData():
    global oldLT,oldRT,oldCT
    try:
        with open('/home/opencfd/OpenDEP/Receive/Thruster/ThrusterData.dat', 'r') as thrusterFile:
            thrusterData = thrusterFile.readline().strip('\n').split(' ')
            LT = int(thrusterData[0])
            RT = int(thrusterData[1])
            CT = int(thrusterData[2])
    except:
        LT=oldLT
        RT=oldRT
        CT=oldCT
    oldLT=LT
    oldRT=RT
    oldCT=CT
    return LT,RT,CT

def SBLEE(updateGPS,currX,currY,gpsDataTime,LT,RT,CT,shipHeading):
    global oldGPSHeading, gpsHeading, velocity, betweenDistance,diffGPSAngle,delta_time 
    if updateGPS:
        previousData.append([currX, currY, gpsDataTime])
        if len(previousData) >= 2:
            gpsHeading = math.degrees(math.atan2(previousData[-1][1] - previousData[-2][1], previousData[-1][0] - previousData[-2][0]))
            betweenDistance = math.sqrt(math.pow(previousData[-1][0] - previousData[-2][0], 2) + math.pow(previousData[-1][1] - previousData[-2][1], 2))
            delta_time = previousData[-1][2] - previousData[-2][2]
            velocity = betweenDistance / delta_time
            if gpsHeading > 0 and oldGPSHeading < 0:
                diffGPSAngle = -1*(gpsHeading + abs(oldGPSHeading))
            elif gpsHeading < 0 and oldGPSHeading > 0:
                diffGPSAngle = (abs(gpsHeading) + oldGPSHeading)
            else:
                diffGPSAngle = oldGPSHeading - gpsHeading
            if diffGPSAngle >= 180:
                diffGPSAngle -= 360
            elif diffGPSAngle <= -180:
                diffGPSAngle += 360
            oldGPSHeading = gpsHeading
            previousData.pop(0)
        SBLeeData = str(LT) + ' ' + str(RT) + ' ' + str(CT) + ' ' + str(currX) + ' ' + str(currY) + ' ' + str(gpsHeading) + ' ' + str(shipHeading) + ' ' + str(velocity) + ' ' + str(betweenDistance) + ' ' + str(diffGPSAngle) + ' ' + str(delta_time) + '\n'
        with open('./jbAnData/SBLEE_1.dat', 'a') as SBLeeFile:
            SBLeeFile.write(SBLeeData)

previousData = []

input("Press")
currX, currY, gpsDataTime = getGPSData()
shipHeading = getGyroData()
print('GPS :: initial Coordinate :',currX,',',currY)
print("Gyro :: initial HeadAngle :",shipHeading)

while runOption:
    try:
        updateGPS, currX, currY, gpsDataTime = checkUpdateGPS(currX, currY)
        if updateGPS:
            print('GPS :: Updated | X : ', round(currX, 3), ' Y : ', round(currY, 3))
        shipHeading = getGyroData()
        LT,RT,CT=getRCData()
        SBLEE(updateGPS, currX, currY, gpsDataTime, LT, RT, CT, shipHeading)
    except KeyboardInterrupt:
        runOption = False
        break
