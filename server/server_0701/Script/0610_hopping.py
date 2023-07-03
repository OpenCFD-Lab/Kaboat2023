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
headingByGPS = False
oldHeadingByGPS = False

oldX, oldY = 0, 0
oldGPSTime = 0
currX, currY = 0, 0
oldGyro = 0
oldShipHeading = 0
oldTime = 0
oldGPSHeading = 0
gpsHeading, velocity, betweenDistance,diffGPSAngle,delta_time=0,0,0,0,0

LT, RT, CT = 1500, 1500, 1500
targetList = [[5.5,12],[5.5,5],[5.5,12],[5.5,5],[5.5,12],[5.5,5],[5.5,12],[5.5,5],[5.5,12],[5.5,5]]
#targetList = [[5.5,12],[5.5,5],[5.5,12],[5.5,5],[5.5,12],[5.5,5]]
fileNum = 0
saveFilePath = '/home/opencfd/OpenDEP/Send/Simulator/'
backupPath = '/home/opencfd/OpenDEP/Send/Simulator/backup/'
backupFileName = 'realTimeShipData'
previousGPS = []
lidarDist=[]
oldLidar=[]
for i in range(201):
    lidarDist.append(0)

def getLidarData():
    global oldLidar
    with open('/home/opencfd/OpenDEP/Receive/Lidar/Lidar.dat', 'r') as lidarFile:
        tempDist = lidarFile.readline().strip(' ').split(' ')
        if len(tempDist)==201:
            for di in range(len(tempDist)):
                lidarDist[di]=float(tempDist[di])
    return lidarDist

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
    PostPWMData(1500, 1500, 1500)
    '''
    LT=1500
    RT=1500
    CT=1500
    print('LEFT ::', LT, ' | RIGHT :: ', RT, ' | CENTER :: ', CT)
    print('#############################################################')
    '''

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
    print('ESTIMATED :: | X : ', round(estimatedX, 3), ' Y : ', round(estimatedY, 3))
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
    print('TARGET COORDINATE ::', round(targetCoor[0],3), ',', round(targetCoor[1],3))
    print('dfromT :', round(dFromTarget, 3), '| afromT :', round(aFromTarget, 3), ' | diffA :', round(diffAngle, 3))
    return targetChange, dFromTarget, aFromTarget, diffAngle

def lowSpeedMode(dFromTarget, diffAngle):
    lowSpeedMax = 1700
    lowSpeedMin = 1600
    rotationMax = 150
    rotationDir = (diffAngle + 0.00000001) / abs(diffAngle + 0.00000001)

    if dFromTarget >= 2.5:
        LT = int(max(lowSpeedMax - 50 * (2.5 - dFromTarget), lowSpeedMin))
        RT = int(max(lowSpeedMax - 50 * (2.5 - dFromTarget), lowSpeedMin))
        CT = int(max(lowSpeedMax - 50 * (2.5 - dFromTarget), lowSpeedMin))
    elif 1.5 <= dFromTarget < 2.5:
        LT = int(max(lowSpeedMax - 50 - (50 / 1.5) * (2.5 - dFromTarget), lowSpeedMin))
        RT = int(max(lowSpeedMax - 50 - (50 / 1.5) * (2.5 - dFromTarget), lowSpeedMin))
        CT = int(max(lowSpeedMax - 50 - (50 / 1.5) * (2.5 - dFromTarget), lowSpeedMin))
    else:
        LT = lowSpeedMin
        RT = lowSpeedMin
        CT = lowSpeedMin

    if 30 <= abs(diffAngle):
        if 2 <= dFromTarget:
            LT = int(LT + (rotationMax - 15) * rotationDir)
            RT = int(RT - (rotationMax - 15) * rotationDir)
        elif dFromTarget < 2:
            LT = int(LT + rotationMax * rotationDir)
            RT = int(RT - rotationMax * rotationDir)
    elif 20 <= abs(diffAngle) < 30:
        if 2 <= dFromTarget:
            rotation = 0.5 * (250 - (30 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 2:
            rotation = 0.5 * (300 - (30 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
    elif 10 <= abs(diffAngle) < 20:
        if 2.5 <= dFromTarget:
            rotation = 0.5 * (150 - (20 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 2.5:
            rotation = 0.5 * (250 - (20 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
    return LT,RT,CT

def highSpeedMode(dFromTarget, diffAngle):
    highSpeedMax = 1850
    highSpeedMin = 1700
    rotationDir = (diffAngle + 0.00000001) / abs(diffAngle + 0.00000001)

    if dFromTarget > 4:
        LT = highSpeedMax
        RT = highSpeedMax
        CT = highSpeedMax
    else:
        LT = int(max(highSpeedMax - 200*(4 - dFromTarget), highSpeedMin))
        RT = int(max(highSpeedMax - 200*(4 - dFromTarget), highSpeedMin))
        CT = int(max(highSpeedMax - 200*(4 - dFromTarget), highSpeedMin))

    if 30 <= abs(diffAngle):
        rotation = 0.5 * (400 - (30 - abs(diffAngle)) * 10)
        LT = int(LT + (rotation * rotationDir))
        RT = int(RT - (rotation * rotationDir))
    elif 20 <= abs(diffAngle) < 30:
        rotation = 0.5 * (370 - (30 - abs(diffAngle)) * 10)
        LT = int(LT + (rotation * rotationDir))
        RT = int(RT - (rotation * rotationDir))
    elif 5 <= abs(diffAngle) < 20:
        rotation = 0.5 * (250 - (20 - abs(diffAngle)) * 10)
        LT = int(LT + (rotation * rotationDir))
        RT = int(RT - (rotation * rotationDir))
    return LT,RT,CT

def calcPWM(dFromTarget, diffAngle):
    if dFromTarget > 3:
        LT,RT,CT = highSpeedMode(dFromTarget,diffAngle)
        print(':::::: HIGH SPEED ::::::')
    else:
        LT,RT,CT = lowSpeedMode(dFromTarget,diffAngle)
        print(':::::: LOW SPEED ::::::')

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

    if LT < 1500:
        LT = max(LT, 1150)
    elif LT > 1500:
        LT = min(LT, 1850)
    if RT < 1500:
        RT = max(RT, 1150)
    elif RT > 1500:
        RT = min(RT, 1850)
    return LT, RT, int(CT)

def calcNextTargetPosition(targetPosition, currX, currY):
    distanceFromTarget=math.sqrt((currX-targetPosition[0])**2+(currY-targetPosition[1])**2)
    angleFromTarget = math.degrees(math.atan2(targetPosition[1]-currY, targetPosition[0]-currX))
    print("Server :: Distance from next target :", distanceFromTarget)
    print("Server :: Next target Angle (Recommend for Initial Ship Angle) :", angleFromTarget)
    return distanceFromTarget, angleFromTarget

def rotatingMotion(CT,currX,currY,shipHeading,diffAngle,targetCoor,deltaTime,updateGPS):
    global fileNum, saveFilePath, backupPath, backupFileName
    if CT>=1780:
        rotationLevel = 250
        while abs(diffAngle) > 50:
            print("::::::::::::: ROTATING MOTION ACTIVATED :::::::::::::")
            print('HEADING ::', round(shipHeading,3), ' | DIff :: ', round(diffAngle,3))
            LT = 1500 + rotationLevel*(diffAngle/abs(diffAngle))
            RT = 1500 + rotationLevel*(-diffAngle/abs(diffAngle))
            #print(LT,RT,1500)
            PostPWMData(int(LT), int(RT), 1500)
            shipHeading = getGyroData()
            lidarDist = getLidarData()
            deltaTime = getDT()
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetCoor, currX, currY, shipHeading)
            #PostSimulator(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, lidarDist, updateGPS, LT, RT, CT, diffAngle)
            writeHopping(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, updateGPS, LT, RT, CT, diffAngle)
            fileNum = Backup(fileNum, saveFilePath, backupPath, backupFileName)
    else:
        rotationLevel = 250
        while abs(diffAngle) > 35:
            print("::::::::::::: ROTATING MOTION ACTIVATED :::::::::::::")
            print('HEADING ::', round(shipHeading,3), ' | DIff :: ', round(diffAngle,3))
            LT = 1500 + rotationLevel*(diffAngle/abs(diffAngle))
            RT = 1500 + rotationLevel*(-diffAngle/abs(diffAngle))
            #print(LT,RT,1500)
            PostPWMData(int(LT), int(RT), 1500)
            deltaTime = getDT()
            shipHeading = getGyroData()
            lidarDist = getLidarData()
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetCoor, currX, currY, shipHeading)
            #PostSimulator(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, lidarDist, updateGPS, LT, RT, CT, diffAngle)
            writeHopping(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, updateGPS, LT,RT, CT, diffAngle)
            fileNum = Backup(fileNum, saveFilePath, backupPath, backupFileName)
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
        res = requests.post(URL, files=ThrusterFile, data=reqData, timeout=0.1)
        ThrusterFile_req.close()
    except requests.exceptions.Timeout:
        PostPWMData(LT, RT, CT)

def PostSimulator(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, lidarDist, updateGPS, LT,RT,CT,diffAngle):
    UNAME = 'simulator'
    URL = 'http://192.168.2.3:9020/simulator'
    cwData1 = str(deltaTime)+' '+str(currX) +' '+ str(currY) +' '+str(targetCoor[0])+' '+str(targetCoor[1])+' '+ str(aFromTarget) +' '+ str(dFromTarget)+' '+str(shipHeading)+' '+str(updateGPS)+' '+str(LT)+' '+str(RT)+' '+str(CT)+' '+str(diffAngle)
    with open('/home/opencfd/OpenDEP/Send/Simulator/realTimeShipData.dat', 'w') as SimulatorFile:
        SimulatorFile.write(cwData1+'\n')
        for i in range(201):
            SimulatorFile.write(str(lidarDist[i])+' ')
        SimulatorFile.write('\n'+'eof')
    SimulatorFile_req = open('/home/opencfd/OpenDEP/Send/Simulator/realTimeShipData.dat','rb')
    SimulatorFile = {'simulatorFile':SimulatorFile_req}
    reqData = {'uname':UNAME, 'fileName':SimulatorFile}
    try:
        res = requests.post(URL, files=SimulatorFile, data=reqData, timeout=0.1)
        SimulatorFile_req.close()
    except requests.exceptions.Timeout:
        PostSimulator(deltaTime, currX, currY, targetCoor, aFromTarget, dFromTarget, shipHeading, lidarDist, updateGPS, LT,RT,CT,diffAngle)

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

def calcVelocity(updateGPS,currX,currY,gpsDataTime):
    global velocity, gpsHeading
    if updateGPS:
        previousGPS.append([currX, currY, gpsDataTime])
        if len(previousGPS) >= 2:
            gpsHeading = math.degrees(math.atan2(previousGPS[-1][1] - previousGPS[-2][1], previousGPS[-1][0] - previousGPS[-2][0]))
            betweenDistance = math.sqrt(math.pow(previousGPS[-1][0] - previousGPS[-2][0], 2) + math.pow(previousGPS[-1][1] - previousGPS[-2][1], 2))
            gpsDT = previousGPS[-1][2] - previousGPS[-2][2]
            velocity = betweenDistance / gpsDT
    return velocity, gpsHeading

def getHeading(updateGPS,currX,currY,gpsDataTime):
    global oldHeadingByGPS, oldShipHeading
    velocity, gpsHeading = calcVelocity(updateGPS,currX,currY,gpsDataTime)
    print(':::::: Current Velocity',round(velocity,3),'[m/s] ::::::')
    if velocity >= 1.5:
        shipHeading = gpsHeading
        headingByGPS = True
    else:
        shipHeading = getGyroData()
        headingByGPS = False
    if oldHeadingByGPS != headingByGPS:
        shipHeading = 0.5*shipHeading + 0.5*oldShipHeading
    oldShipHeading = shipHeading
    oldHeadingByGPS = headingByGPS
    print('shipHeading : ', round(shipHeading, 3))
    return shipHeading

########################################################################

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
        lidarDist = getLidarData()
        shipHeading = getHeading(updateGPS, currX, currY, gpsDataTime)
        if len(targetList):
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetList[0], currX, currY, shipHeading)
            if targetChange:
                targetList.pop(0)
                print('::::::::::::   Target Change   ::::::::::::')
                if len(targetList) == 0:
                    print('::::::::::::: HOPPING MISSION END :::::::::::::')
                    initThruster()
                    runOption = False
                    break
                elif len(targetList) != 0 and abs(diffAngle) > 70:
                    diffAngle = rotatingMotion(CT, currX, currY, shipHeading, diffAngle, targetList[0], deltaTime, updateGPS)
                    initThruster()
                    shipHeading = getGyroData()
                    oldShipHeading = shipHeading
                else:
                    LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                    PostPWMData(LT, RT, CT)
                    #print(LT,RT,CT)
            else:
                if abs(diffAngle) > 60:
                    diffAngle = rotatingMotion(CT, currX, currY, shipHeading, diffAngle, targetList[0], deltaTime, updateGPS)
                    initThruster()
                    shipHeading = getGyroData()
                    oldShipHeading = shipHeading
                else:
                    LT, RT, CT = calcPWM(dFromTarget, diffAngle)
                    PostPWMData(LT, RT, CT)
                    #print(LT,RT,CT)
            print('###################################################')
            #PostSimulator(deltaTime, currX, currY, targetList[0], aFromTarget, dFromTarget, shipHeading, lidarDist, updateGPS, LT,RT, CT, diffAngle)
            writeHopping(deltaTime, currX, currY, targetList[0], aFromTarget, dFromTarget, shipHeading, updateGPS, LT,RT, CT, diffAngle)
            fileNum = Backup(fileNum, saveFilePath, backupPath, backupFileName)
    except KeyboardInterrupt:
        initThruster()
        runOption = False
        break
