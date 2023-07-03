import math
import time
import requests
import os
import shutil

global oldX, oldY, currX, currY
global oldGyro
global oldTime

runOption = True

oldX, oldY = 0, 0
currX, currY = 0, 0
gpsX, gpsY = 0, 0
gpsDataTime = 0
oldGyro = 0
oldTime = 0
LT, RT, CT = 1500, 1500, 1500
targetList = [[7,13],[5,10],[5.5,4]]

def getGPSData():
    global oldX, oldY, currX, currY, gpsX, gpsY, gpsDataTime
    with open('/home/opencfd/OpenDEP/Receive/GPS/gpsData.dat', 'r') as gpsFile:
        gpsData = gpsFile.readline().strip('\n').split(' ')
        if len(gpsData) == 3:
            status = int(gpsData[0])
            gpsX = float(gpsData[1])
            gpsY = float(gpsData[2])
            gpsDataTime = time.time()
    if oldX != gpsX or oldY != gpsY:
        #if math.sqrt(math.pow(gpsX-oldX, 2) + math.pow(gpsY-oldY, 2)) >= 0.08:
        currX = gpsX
        currY = gpsY
        updateGPS = True
    else:
        updateGPS = False
    oldX = gpsX
    oldY = gpsY

    return updateGPS, currX, currY, gpsDataTime


def getGyroData():
    global oldGyro, currGyro
    try:
        with open('/home/opencfd/OpenDEP/Receive/Gyro/gyroData.dat', 'r') as gyroFile:
            gyroData = gyroFile.readline()
            gyroHeadAngle = float(gyroData)

        if oldGyro != gyroHeadAngle:
            currGyro = gyroHeadAngle
            updateGyro = True
        else:
            updateGyro = False
        oldGyro = gyroHeadAngle
    except ValueError:
        pass

    return updateGyro, currGyro

def getDT():
    global oldTime, deltaTime
    currTime = time.time()

    if oldTime != currTime:
        deltaTime = currTime - oldTime
    oldTime = currTime

    return deltaTime


def correctionGPSTerm(estimatedX, estimatedY, shipHeading, LT, RT, CT, deltaTime):
    advance = (((LT + RT + CT)/3) - 1500) / 1000
    if advance >= 0.03:
        velocity = -1080.3*math.pow(advance, 4) + 773.38*math.pow(advance, 3) - 174.97*math.pow(advance, 2) + 23.176*advance + 0.0002
    else:
        velocity = 0

    velocityX = round(velocity * math.cos(math.radians(shipHeading)), 4)
    velocityY = round(velocity * math.sin(math.radians(shipHeading)), 4)
    estimatedX += velocityX * deltaTime
    estimatedY += velocityY * deltaTime

    return estimatedX, estimatedY


def calcPositionFromTarget(targetX, targetY, currX, currY, shipHeading):
    targetChange = False
    dFromTarget = math.sqrt(math.pow(targetX - currX, 2) + math.pow(targetY - currY, 2))
    aFromTarget = math.degrees(math.atan2(targetY-currY, targetX-currX))
    diffAngle = shipHeading - aFromTarget
    if abs(diffAngle)>180:
        if diffAngle>0:
            diffAngle -= 360
        else:
            diffAngle += 360
    if dFromTarget <= 1.0:
        targetChange = True
        print('::::::::::::   Target Change   ::::::::::::')

    return targetChange, dFromTarget, aFromTarget, diffAngle


def calcPWM(dFromTarget, diffAngle):
    advanceMax = 1600
    advanceMin = 1550
    rotationMax = 250
    rotationDir = (diffAngle + 0.00000001) / abs(diffAngle + 0.00000001)

    if dFromTarget > 5:
        LT = advanceMax
        RT = advanceMax
        CT = advanceMax
    elif 3 <= dFromTarget <= 5:
        LT = int(max(advanceMax-50 - 50 * (4 - dFromTarget), advanceMin))
        RT = int(max(advanceMax-50 - 50 * (4 - dFromTarget), advanceMin))
        CT = int(max(advanceMax-50 - 50 * (4 - dFromTarget), advanceMin))
    elif 1.5 <= dFromTarget < 3:
        LT = int(max(advanceMax-100 - (50/3) * (3 - dFromTarget), advanceMin))
        RT = int(max(advanceMax-100 - (50/3) * (3 - dFromTarget), advanceMin))
        CT = int(max(advanceMax-100 - (50/3) * (3 - dFromTarget), advanceMin))
    else:
        LT = advanceMin
        RT = advanceMin
        CT = advanceMin

    if 50 <= abs(diffAngle):
        LT = int(1500 + rotationMax * rotationDir)
        RT = int(1500 - rotationMax * rotationDir)
        CT = (LT+RT)/2
    elif 30 <= abs(diffAngle) < 50:
        if dFromTarget > 4:
            LT = int(LT + (4*rotationMax/5 - 40) * rotationDir)
            RT = int(RT - (4*rotationMax/5 - 40) * rotationDir)
        if 2.5 <= dFromTarget <= 4:
            LT = int(LT + (4*rotationMax/5 - 20) * rotationDir)
            RT = int(RT - (4*rotationMax/5 - 20) * rotationDir)
        elif dFromTarget < 2.5:
            LT = int(LT + (4*rotationMax/5) * rotationDir)
            RT = int(RT - (4*rotationMax/5) * rotationDir)
    elif 20 <= abs(diffAngle) < 30:
        if dFromTarget > 4:
            rotation = 0.5 * (150 - (30 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        if 2.5 <= dFromTarget <= 4:
            rotation = 0.5 * (250 - (30 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 2.5:
            rotation = 0.5 * (350 - (30 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
    elif 10 <= abs(diffAngle) < 20:
        if dFromTarget > 4:
            rotation = 0.5 * (100 - (20 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        if 2.5 <= dFromTarget <= 4:
            rotation = 0.5 * (150 - (20 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 2.5:
            rotation = 0.5 * (250 - (20 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))

    if 1720 <= CT < 1750:
        if RT+60 >= 1850:
            residual = RT + 60 - 1850
            RT = 1850
            LT = LT - 60 - residual
        elif LT-60 <= 1150:
            residual = LT - 60 + 1150
            LT = 1150
            RT = RT + 60 - residual
        else:
            LT -= 60
            RT += 60
    elif 1750 <= CT:
        if RT+75 >= 1850:
            residual = RT + 75 - 1850
            RT = 1850
            LT = LT - 75 - residual
        elif LT-75 <= 1150:
            residual = LT - 75 + 1150
            LT = 1150
            RT = RT + 75 - residual
        else:
            LT -= 75
            RT += 75

    if LT < 1500:
        LT = max(LT, 1200)
    elif LT > 1500:
        LT = min(LT, 1800)
    if RT < 1500:
        RT = max(RT, 1200)
    elif RT > 1500:
        RT = min(RT, 1800)
    CT = int(CT)
    return LT, RT, CT

def calcNextTargetPosition(targetPosition, currX, currY):
    distanceFromTarget=math.sqrt((currX-targetPosition[0])**2+(currY-targetPosition[1])**2)
    angleFromTarget = math.degrees(math.atan2(targetPosition[1]-currY, targetPosition[0]-currX))
    print("Server :: Distance from next target :", distanceFromTarget)
    print("Server :: Next target Angle (Recommend for Initial Ship Angle) :", angleFromTarget)
    return distanceFromTarget, angleFromTarget

def PostPWMData(LT, RT, CT):
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

def PostSimulator(deltaTime, currX, currY, targetX, targetY, aFromTarget, dFromTarget):
    UNAME = 'Simulator'
    URL = 'http://192.168.2.9:9020/Simulator'
    cwData1 = str(deltaTime)+' '+str(currX) +' '+ str(currY) +' '+str(targetX)+' '+str(targetY)+' '+ str(aFromTarget) +' '+ str(dFromTarget)
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
        PostThrusterData(SimulatorFileName, SimulatorFilePath)

def Backup(fileNum, saveFilePath ,backupPath, backupFileName):
    if not os.path.exists(backupPath):
        os.makedirs(backupPath)
    shutil.copyfile(saveFilePath + backupFileName +'.dat', backupPath + backupFileName + str(fileNum) + '.dat')
    fileNum += 1

    return fileNum
updateGPS = False
fileNum = 0
saveFilePath = '/home/opencfd/OpenDEP/Send/Simulator/'
backupPath = '/home/opencfd/OpenDEP/Send/Simulator/backup/'
backupFileName = 'realTimeShipData'
previousData = []

input("Press")
updateGPS, currX, currY, gpsDataTime = getGPSData()
print('GPS :: initial Coordinate :',updateGPS,currX,',',currY)
input("Press")
updateGyro, shipHeading = getGyroData()
print("Gyro :: initial HeadAngle :",shipHeading)
if len(targetList):
    distanceFromTarget, angleFromTarget = calcNextTargetPosition(targetList[0], currX, currY)
    shipHeading = float(input("input Initial shipAngle : "))
    diffAngle = shipHeading - angleFromTarget
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')


while runOption:
    deltaTime = getDT()
    try:
        updateGPS, currX, currY, gpsDataTime = getGPSData()
        if updateGPS:
            print('GPS :: Updated | X : ', round(currX, 3), ' Y : ', round(currY, 3))
        #else:
        #    currX, currY = correctionGPSTerm(currX, currY, shipHeading, LT, RT, CT, deltaTime)
        #    print('ESTIMATED :: | X : ', round(currX, 3), ' Y : ', round(currY, 3))
            updateGyro, shipHeading = getGyroData()
            print('shipHeading : ', round(shipHeading, 3))
            if len(targetList):
                targetX = targetList[0][0]
                targetY = targetList[0][1]
                print('TARGET COORDINATE ::', targetX, ',', targetY)
                targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetX, targetY, currX, currY, shipHeading)
                print('dfromT :', round(dFromTarget, 3), '| afromT :', round(aFromTarget, 3), ' | diffA :', round(diffAngle, 3))
                if targetChange:
                    targetList.pop(0)
                    if len(targetList) == 0:
                        print('::::::::::::: HOPPING MISSION DONE :::::::::::::')
                        PostPWMData(1500, 1500, 1500)
                        runOption = False
                        break
                    targetX = targetList[0][0]
                    targetY = targetList[0][1]
                    targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetX, targetY, currX, currY, shipHeading)
                PostSimulator(deltaTime, currX, currY, targetX, targetY, aFromTarget, dFromTarget)
                fileNum = Backup(fileNum, saveFilePath, backupPath, backupFileName)
                LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                with open('/home/opencfd/OpenDEP/Script/jbAnData/hopping.dat', 'a') as hoppingFile:
                    hoppingFile.write(str(deltaTime)+','+str(LT)+','+str(RT)+','+str(CT)+','+str(currX)+','+str(currY)+','+str(shipHeading)+','+
                            str(targetX)+','+str(targetY)+','+str(dFromTarget)+','+str(aFromTarget)+','+str(diffAngle)+'\n')
                print('LEFT ::', LT, ' | RIGHT :: ', RT, ' | CENTER :: ', CT)
                print('#############################################################')
                PostPWMData(LT, RT, CT)
            else:
                runOption = False
                break
        '''
        if updateGPS:
            previousData.append([currX, currY, gpsDataTime])
            if len(previousData) >= 2:
                gpsHeading = math.degrees(math.atan2(previousData[-1][1] - previousData[-2][1], previousData[-1][0] - previousData[-2][0]))
                betweenDistance = math.sqrt(math.pow(previousData[-1][0] - previousData[-2][0], 2) + math.pow(previousData[-1][1] - previousData[-2][1], 2))
                delta_time = previousData[-1][2] - previousData[-2][2]
                velocity = betweenDistance / delta_time
                if gpsHeading > 0 and oldHeading < 0:
                    diffAngle = gpsHeading - abs(oldHeading)
                elif gpsHeading < 0 and oldHeading > 0:
                    diffAngle = -1*(abs(gpsHeading) - oldHeading)
                else:
                    diffAngle = oldHeading - gpsHeading
                oldHeading = gpsHeading
            SBLeeData = str(LT) + ' ' + str(RT) + ' ' + str(CT) + ' ' + str(currX) + ' ' + str(currY) + ' ' + str(gpsHeading) + ' ' + str(shipHeading) + ' ' + str(velocity) + ' ' + str(betweenDistance) + ' ' + str(diffAngle) + ' ' + str(delta_time) + '\n'
            with open('./jbAnData/SBLEE_1.dat', 'a') as SBLeeFile:
                SBLeeFile.write(SBLeeData)
            '''
    except KeyboardInterrupt:
        runOption = False
        break
