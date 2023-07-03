import math
import time
import requests
import os
import shutil
import datetime

global oldX, oldY, oldGPSTime
global oldGyro
global oldTime

runOption = True
updateGPS = False

oldX, oldY = 0, 0
oldGPSTime = 0
currX, currY = 0, 0
oldGyro = 0
oldShipHeading = 0
oldTime = 0
oldGPSHeading = 0
gpsHeading, velocity, betweenDistance,diffGPSAngle,delta_time =0,0,0,0,0 
LT, RT, CT = 1500, 1500, 1500
#targetList = [[7,13],[5,10],[5.5,4]]
targetList = [[5,7]]

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

def checkUpdateGPS(updateGPS, currX, currY):
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

def initTime():
    global initialTime
    hour = datetime.datetime.now().strftime('%H')
    minute = datetime.datetime.now().strftime('%M')
    sec = datetime.datetime.now().strftime('%S.%f')
    initialTime = float(hour) * 3600 + float(minute) * 60 + float(sec)

def initThruster():
    #PostPWMData(1500, 1500, 1500)
    LT=1500
    RT=1500
    CT=1500
    print('LEFT ::', LT, ' | RIGHT :: ', RT, ' | CENTER :: ', CT)
    print('#############################################################')

def getDT():
    global oldTime
    hour = datetime.datetime.now().strftime('%H')
    minute = datetime.datetime.now().strftime('%M')
    sec = datetime.datetime.now().strftime('%S.%f')
    currTime = float(hour) * 3600 + float(minute) * 60 + float(sec)
    if oldTime:
        deltaTime = currTime - oldTime
    else:
        deltaTime = 0
    oldTime = currTime
    return deltaTime

def correctionGPSTerm(estimatedX, estimatedY, shipHeading, LT, RT, CT, deltaTime):
    advance = (((LT + RT + CT)/3) - 1500) / 1000
    if advance >= 0.05:
        velocity = -1072.7*advance**4 + 767.07*advance**3 - 173.17*advance**2 + 22.976*advance + 0.0071
    else:
        velocity = 0

    velocityX = round(velocity * math.cos(math.radians(shipHeading)), 4)
    velocityY = round(velocity * math.sin(math.radians(shipHeading)), 4)
    estimatedX += velocityX * deltaTime
    estimatedY += velocityY * deltaTime

    return estimatedX, estimatedY

def calcPositionFromTarget(targetCoor, currX, currY, shipHeading):
    targetChange = False
    dFromTarget = math.sqrt(math.pow(targetCoor[0] - currX, 2) + math.pow(targetCoor[1] - currY, 2))
    aFromTarget = math.degrees(math.atan2(targetCoor[1]-currY, targetCoor[0]-currX))
    diffAngle = shipHeading - aFromTarget
    if abs(diffAngle)>180:
        if diffAngle>0:
            diffAngle -= 360
        else:
            diffAngle += 360
    if dFromTarget <= 0.5:
        targetChange = True
    return targetChange, dFromTarget, aFromTarget, diffAngle

def calcPWM(dFromTarget, diffAngle):
    advanceMax = 1850
    advanceMin = 1550
    rotationMax = 150
    rotationDir = (diffAngle + 0.00000001) / abs(diffAngle + 0.00000001)

    if dFromTarget > 5:
        LT = advanceMax
        RT = advanceMax
        CT = advanceMax
    elif 3 <= dFromTarget <= 5:
        LT = int(max(advanceMax-75 - 50 * (4 - dFromTarget), advanceMin))
        RT = int(max(advanceMax-75 - 50 * (4 - dFromTarget), advanceMin))
        CT = int(max(advanceMax-75 - 50 * (4 - dFromTarget), advanceMin))
    elif 1.5 <= dFromTarget < 3:
        LT = int(max(advanceMax-130 - (50/3) * (3 - dFromTarget), advanceMin))
        RT = int(max(advanceMax-130 - (50/3) * (3 - dFromTarget), advanceMin))
        CT = int(max(advanceMax-130 - (50/3) * (3 - dFromTarget), advanceMin))
    else:
        LT = advanceMin
        RT = advanceMin
        CT = advanceMin

    if 30 <= abs(diffAngle):
        if dFromTarget >= 4:
            LT = int(LT + (rotationMax - 30) * rotationDir)
            RT = int(RT - (rotationMax - 30) * rotationDir)
        elif 2 <= dFromTarget < 4:
            LT = int(LT + (rotationMax - 15) * rotationDir)
            RT = int(RT - (rotationMax - 15) * rotationDir)
        elif dFromTarget < 2:
            LT = int(LT + rotationMax * rotationDir)
            RT = int(RT - rotationMax * rotationDir)
    elif 20 <= abs(diffAngle) < 30:
        if dFromTarget >= 4:
            rotation = 0.5 * (300 - (30 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif 2 <= dFromTarget < 4:
            rotation = 0.5 * (350 - (30 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 2:
            rotation = 0.5 * (370 - (30 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
    elif 10 <= abs(diffAngle) < 20:
        if dFromTarget >= 4:
            rotation = 0.5 * (200 - (20 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif 2.5 <= dFromTarget < 4:
            rotation = 0.5 * (200 - (20 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 2.5:
            rotation = 0.5 * (250 - (20 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
    if LT >= 1850:
        residual = LT - 1850
        LT = 1850
        RT -= residual
    if RT >= 1850:
        residual = RT - 1850
        RT = 1850
        LT -= residual
    if LT <= 1150:
        residual = LT + 1150
        LT = 1150
        RT += residual
    if RT <= 1150:
        residual = RT + 1150
        RT = 1150
        LT += residual
    '''
    if 1720 <= CT < 1750:
        if LT+60 >= 1850:
            residual = LT + 60 - 1850
            LT = 1850
            RT = RT - 60 - residual
        elif RT-60 <= 1150:
            residual = RT - 60 + 1150
            RT = 1150
            LT = LT + 60 - residual
        else:
            LT += 60
            RT -= 60
    elif 1750 <= CT:
        if LT+75 >= 1850:
            residual = LT + 75 - 1850
            LT = 1850
            RT = RT - 75 - residual
        elif RT-75 <= 1150:
            residual = RT - 75 + 1150
            RT = 1150
            LT = LT + 75 - residual
        else:
            LT += 75
            RT -= 75
    '''
    if LT < 1500:
        LT = max(LT, 1200)
    elif LT > 1500:
        LT = min(LT, 1850)
    if RT < 1500:
        RT = max(RT, 1200)
    elif RT > 1500:
        RT = min(RT, 1850)
    CT = int(CT)
    return LT, RT, CT

def calcNextTargetPosition(targetPosition, currX, currY):
    distanceFromTarget=math.sqrt((currX-targetPosition[0])**2+(currY-targetPosition[1])**2)
    angleFromTarget = math.degrees(math.atan2(targetPosition[1]-currY, targetPosition[0]-currX))
    print("Server :: Distance from next target :", distanceFromTarget)
    print("Server :: Next target Angle (Recommend for Initial Ship Angle) :", angleFromTarget)
    return distanceFromTarget, angleFromTarget

def rotatingMotion(CT,currX,currY,shipHeading,diffAngle,targetCoor,targetChange):
    #print("::::::::::::: ROTATING MOTION ACTIVATED :::::::::::::")
    #rotationLevel = 250
    if CT>=1780:
        rotationLevel = 250
        while abs(diffAngle) > 50:
            print("::::::::::::: ROTATING MOTION ACTIVATED :::::::::::::")
            print('HEADING ::', shipHeading, ' | DIff :: ', diffAngle)
            LT = 1500 + rotationLevel*(diffAngle/abs(diffAngle))
            RT = 1500 + rotationLevel*(-diffAngle/abs(diffAngle))
            #PostPWMData(int(LT), int(RT), 1500)
            shipHeading = getGyroData()
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetCoor, currX, currY, shipHeading)
    else:
        rotationLevel = 250
        while abs(diffAngle) > 35:
            print("::::::::::::: ROTATING MOTION ACTIVATED :::::::::::::")
            print('HEADING ::', shipHeading, ' | DIff :: ', diffAngle)
            LT = 1500 + rotationLevel*(diffAngle/abs(diffAngle))
            RT = 1500 + rotationLevel*(-diffAngle/abs(diffAngle))
            #PostPWMData(int(LT), int(RT), 1500)
            shipHeading = getGyroData()
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetCoor, currX, currY, shipHeading)
    return diffAngle

def PostPWMData(LT, RT, CT):
    print('LEFT ::', LT, ' | RIGHT :: ', RT, ' | CENTER :: ', CT)
    print('#############################################################')
    UNAME = 'Thruster'
    URL = 'http://192.168.2.16:9016/Thruster'
    with open('/home/opencfd/OpenDEP/Send/Thruster/thruster.dat','w') as ThrusterFile:
        ThrusterFile.write(str(LT)+' '+str(RT)+' '+str(CT)+'\n')
    ThrusterFile_req = open('/home/opencfd/OpenDEP/Send/Thruster/thruster.dat','rb')
    ThrusterFile = {'ThrusterFile':ThrusterFile_req}
    reqData = {'uname':UNAME, 'fileName':ThrusterFile}
    try:
        res = requests.post(URL, files=ThrusterFile, data=reqData)
        ThrusterFile_req.close()
    except requests.exceptions.Timeout:
        PostThrusterData(ThrusterFileName, ThrusterFilePath)

def PostSimulator(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, updateGPS, LT,RT,CT,diffAngle):
    UNAME = 'Simulator'
    URL = 'http://192.168.2.3:9020/Simulator'
    cwData1 = str(deltaTime)+' '+str(currX) +' '+ str(currY) +' '+str(targetCoor[0])+' '+str(targetCoor[1])+' '+ str(aFromTarget) +' '+ str(dFromTarget)+' '+str(shipHeading)+' '+str(updateGPS)+' '+str(LT)+' '+str(RT)+' '+str(CT)+' '+str(diffAngle)
    for i in range(201):
        if i==0:
            cwData2 = str(8)+' '
        else:
            cwData2 += str(8)+' '
    with open('/home/opencfd/OpenDEP/Send/Simulator/realTimeShipData.dat', 'w') as SimulatorFile:
        SimulatorFile.write(cwData1+'\n'+cwData2+'\n'+'eof')
    SimulatorFile_req = open('/home/opencfd/OpenDEP/Send/Simulator/realTimeShipData.dat','rb')
    SimulatorFile = {'simulatorFile':SimulatorFile_req}
    reqData = {'uname':UNAME, 'fileName':SimulatorFile}
    try:
        res = requests.post(URL, files=SimulatorFile, data=reqData)
        SimulatorFile_req.close()
    except requests.exceptions.Timeout:
        pass
        #PostThrusterData(SimulatorFileName, SimulatorFilePath)

def writeHopping(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, updateGPS, LT,RT,CT,diffAngle):
    Data1 = str(deltaTime)+' '+str(currX) +' '+ str(currY) +' '+str(targetCoor[0])+' '+str(targetCoor[1])+' '+ str(aFromTarget) +' '+ str(dFromTarget)+' '+str(shipHeading)+' '+str(updateGPS)+' '+str(LT)+' '+str(RT)+' '+str(CT)+' '+str(diffAngle)
    with open('/home/opencfd/OpenDEP/Script/jbAnData/hopping.dat', 'a') as hoppingFile:
        hoppingFile.write(Data1+'\n')

def Backup(fileNum, saveFilePath ,backupPath, backupFileName):
    if not os.path.exists(backupPath):
        os.makedirs(backupPath)
    shutil.copyfile(saveFilePath + backupFileName +'.dat', backupPath + backupFileName + str(fileNum) + '.dat')
    fileNum += 1
    return fileNum

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
        SBLeeData = str(LT) + ' ' + str(RT) + ' ' + str(CT) + ' ' + str(currX) + ' ' + str(currY) + ' ' + str(gpsHeading) + ' ' + str(shipHeading) + ' ' + str(velocity) + ' ' + str(betweenDistance) + ' ' + str(diffGPSAngle) + ' ' + str(delta_time) + '\n'
        with open('./jbAnData/SBLEE_1.dat', 'a') as SBLeeFile:
            SBLeeFile.write(SBLeeData)

fileNum = 0
saveFilePath = '/home/opencfd/OpenDEP/Send/Simulator/'
backupPath = '/home/opencfd/OpenDEP/Send/Simulator/backup/'
backupFileName = 'realTimeShipData'
previousData = []

initThruster()
input("Press")
currX, currY, gpsDataTime = getGPSData()
shipHeading = getGyroData()
print('GPS :: initial Coordinate :',currX,',',currY)
print("Gyro :: initial HeadAngle :",shipHeading)
input("Press")
if len(targetList):
    distanceFromTarget, angleFromTarget = calcNextTargetPosition(targetList[0], currX, currY)
    shipHeading = float(input("input Initial shipAngle : "))
    oldShipHeading = shipHeading
    diffAngle = shipHeading - angleFromTarget
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
initTime()

while runOption:
    deltaTime = getDT()
    try:
        updateGPS, currX, currY, gpsDataTime = checkUpdateGPS(updateGPS, currX, currY)
        if updateGPS:
            print('GPS :: Updated | X : ', round(currX, 3), ' Y : ', round(currY, 3))
        else:
            currX, currY = correctionGPSTerm(currX, currY, shipHeading, LT, RT, CT, deltaTime)
            print('ESTIMATED :: | X : ', round(currX, 3), ' Y : ', round(currY, 3))
        shipHeading = getGyroData()
        print('shipHeading : ', round(shipHeading, 3))
        if len(targetList):
            print('TARGET COORDINATE ::', targetList[0][0], ',', targetList[0][1])
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetList[0], currX, currY, shipHeading)
            print(1)
            PostSimulator(deltaTime, currX, currY, targetList[0], aFromTarget, dFromTarget, shipHeading, updateGPS, LT,RT,CT,diffAngle)
            #writeHopping(deltaTime, currX, currY, targetList[0], aFromTarget, dFromTarget, shipHeading, updateGPS, LT,RT,CT,diffAngle)
            print(2)
            fileNum = Backup(fileNum, saveFilePath, backupPath, backupFileName)
            print('dfromT :', round(dFromTarget, 3), '| afromT :', round(aFromTarget, 3), ' | diffA :', round(diffAngle, 3))
            if targetChange:
                targetList.pop(0)
                print('::::::::::::   Target Change   ::::::::::::')
                if len(targetList) == 0:
                    print('::::::::::::: HOPPING MISSION END :::::::::::::')
                    initThruster()
                    runOption = False
                    break
                elif len(targetList) != 0 and abs(diffAngle) > 70:
                    LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                    #diffAngle = rotatingMotion(CT, currX,currY,shipHeading,diffAngle,targetList[0],targetChange)
                    initThruster()
                    shipHeading = getGyroData()
                    oldShipHeading = shipHeading
                else:
                    LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                    #PostPWMData(LT, RT, CT)
            else:
                if abs(diffAngle) > 60:
                    LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                    #diffAngle = rotatingMotion(CT, currX, currY, shipHeading, diffAngle, targetList[0], targetChange)
                    initThruster()
                    shipHeading = getGyroData()
                else:
                    LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                    #PostPWMData(LT, RT, CT)
                shipHeading = getGyroData()
                oldShipHeading = shipHeading
        SBLEE(updateGPS, currX, currY, gpsDataTime, LT, RT, CT, shipHeading)
    except KeyboardInterrupt:
        initThruster()
        runOption = False
        break
