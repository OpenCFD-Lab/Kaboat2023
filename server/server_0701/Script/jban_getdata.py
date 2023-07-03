import math
import time
import os
import shutil
import datetime

global oldX, oldY, oldGPSTime
global oldGyro, oldGyroTime
global oldLidar, oldLidarTime

updateGPS = False
updateGyro = False
updateLidar = False

oldX, oldY = 0, 0
oldGPSTime = 0
currX, currY = 0, 0

oldGyro = 0
oldGyroTime = 0
currGyro = 0

oldLidar = []
oldLidarTime = 0
currLidar = []

dist=[]
for i in range(201):
    dist.append(0)

pGPS=[]
pGyro=[]
pLidar=[]

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
    global oldGyro, oldGyroTime
    try:
        with open('/home/opencfd/OpenDEP/Receive/Gyro/gyroData.dat', 'r') as gyroFile:
            gyroData = gyroFile.readline()
            gyroHeadAngle = float(gyroData)
            gyroDataTime = time.time()
    except:
        gyroHeadAngle = oldGyro
        gyroDataTime = oldGyroTime
    return gyroHeadAngle, gyroDataTime

def checkUpdateGyro(currGyro):
    global oldGyro
    gyroHeadAngle, gyroDataTime = getGyroData()
    if oldGyro != gyroHeadAngle:
        currGyro = gyroHeadAngle
        updateGyro = True
    else:
        updateGyro = False
    oldGyro = gyroHeadAngle
    return updateGyro, currGyro, gyroDataTime

def getLidarData():
    global dist, oldLidar, oldLidarTime
    updatedFilePath="/home/opencfd/OpenDEP/Receive/Lidar/Lidar.dat"
    try:
        with open(updatedFilePath,"r") as lidarUpdated:
            tmpDist=lidarUpdated.readline().strip(" ").split(" ")
            #if(len(tmpDist)==201):
            for di in range(len(tmpDist)):
                dist[di]=float(tmpDist[di])
            lidarDataTime = time.time()
    except:
        dist = oldLidar
        lidarDataTime = oldLidarTime
    print(dist)
    return dist, lidarDataTime

def checkUpdateLidar(currLidar):
    global oldLidar
    distance, lidarDataTime = getLidarData()
    if oldLidar != distance:
        currLidar = distance
        updateLidar = True
    else:
        updateLidar = False
    oldLidar = distance
    return updateLidar, currLidar, lidarDataTime

def wGPS(updateGPS,currX,currY,gpsDataTime):
    delta_time=0
    if updateGPS:
        pGPS.append([currX, currY, gpsDataTime])
        if len(pGPS) >= 2:
            delta_time = pGPS[-1][2] - pGPS[-2][2]
            pGPS.pop(0)
        data1 = str(pGPS[-1][0]) + ' ' + str(pGPS[-1][1]) + ' ' + str(delta_time) + '\n'
        with open('./jbAnData/0609gps.dat', 'a') as gFile:
            gFile.write(data1)

def wGyro(updateGyro,currGyro,gyroDataTime):
    delta_time=0
    if updateGyro:
        pGyro.append([currGyro, gyroDataTime])
        if len(pGyro) >= 2:
            delta_time = pGyro[-1][1] - pGyro[-2][1]
            pGyro.pop(0)
        data2 = str(pGyro[-1][0]) + ' ' + str(delta_time) + '\n'
        with open('./jbAnData/0609gyro.dat', 'a') as hFile:
            hFile.write(data2)

def wLidar(updateLidar, currLidar, lidarDataTime):
    l_time=0
    if updateLidar:
        pLidar.append([currLidar, lidarDataTime])
        if len(pLidar) >= 2:
            l_time = pLidar[-1][1] - pLidar[-2][1]
            print(l_time)
            pLidar.pop(0)
        data3 = str(pLidar[-1][0]) + ' ' + str(l_time) + '\n'
        with open('./jbAnData/0609lidar.dat', 'a') as lFile:
            lFile.write(data3)

while True:
    try:
        updateGPS, currX, currY, gpsDataTime = checkUpdateGPS(currX, currY)
        updateGyro, currGyro, gyroDataTime = checkUpdateGyro(currGyro)
        updateLidar, currLidar, lidarDataTime = checkUpdateLidar(currLidar)
        #print(updateLidar)
        wGPS(updateGPS,currX,currY,gpsDataTime)
        wGyro(updateGyro, currGyro, gyroDataTime)
        wLidar(updateLidar, currLidar, lidarDataTime)
    except KeyboardInterrupt:
        break


