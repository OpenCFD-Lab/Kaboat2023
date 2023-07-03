import math
import time
import requests

global oldX, oldY
global oldGyro
global oldTime

runOption = True

previousData = []
oldX= 0
oldY=0
oldGyro = 0
oldTime = 0
LT,RT,CT=1500,1500,1500
targetList = [[5,5],[2,8]]

def getGPSData():
    global oldX, oldY, currX, currY
    with open('/home/opencfd/OpenDEP/Receive/GPS/gpsData.dat', 'r') as gpsFile:
        gpsData = gpsFile.readline().strip('\n').split(' ')
        if len(gpsData) == 3:
            status = int(gpsData[0])
            gpsX = float(gpsData[1])
            gpsY = float(gpsData[2])
            gpsDataTime = time.time()

    if oldX != gpsX or oldY != gpsY:
        if math.sqrt(math.pow(gpsX-oldX, 2) + math.pow(gpsY-oldY, 2)) >= 0.08:
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
    with open('/home/opencfd/OpenDEP/Receive/Gyro/gyroData.dat', 'r') as gyroFile:
        gyroData = gyroFile.readline()
        gyroHeadAngle = float(gyroData)

    if oldGyro != gyroHeadAngle:
        currGyro = gyroHeadAngle
        updateGyro = True
    else:
        updateGyro = False
    oldGyro = gyroHeadAngle

    return updateGyro, currGyro

def getDT():
    global oldTime
    currTime = time.time()

    if oldTime != currTime:
        deltaTime = currTime - oldTime
    oldTime = currTime

    return deltaTime


def correctionGPSTerm(currX, currY, shipHeading, LT, RT, CT, deltaTime):
    advance = (((LT + RT + CT)/3) - 1500) / 1000
    if advance >= 0.03:
        velocity = -1080.3*math.pow(advance, 4) + 773.38*math.pow(advance, 3) - 174.97*math.pow(advance, 2) + 23.176*advance + 0.0002
    else:
        velocity = 0

    velocityX = round(velocity * math.cos(math.radians(shipHeading)), 4)
    velocityY = round(velocity * math.sin(math.radians(shipHeading)), 4)
    currX += velocityX * deltaTime
    currY += velocityY * deltaTime

    return currX, currY

def calcPositionFromTarget(targetX, targetY, currX, currY, shipHeading):
    targetChange = False
    dFromTarget = math.sqrt(math.pow(targetX - currX, 2) + math.pow(targetY - currY, 2))
    aFromTarget = math.degrees(math.atan2(targetY-currY, targetX-currX))
    diffAngle = shipHeading - aFromTarget
    print("distanceFromTarget :: ", dFromTarget)
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
    advanceMax = 1700

    rotationMax = 300
    rotation = 0
    rotationDir = (diffAngle + 0.00000001) / abs(diffAngle + 0.000000001)

    if dFromTarget > 4:
        LT = advanceMax
        RT = advanceMax
        CT = advanceMax
    elif 3 <= dFromTarget <= 4:
        LT = int((advanceMax-50) - 50 * (4 - dFromTarget))
        RT = int((advanceMax-50) - 50 * (4 - dFromTarget))
        CT = int((advanceMax-50) - 50 * (4 - dFromTarget))
    elif 1.5 <= dFromTarget < 3:
        LT = int((advanceMax-100) - 50 / 3 * (3 - dFromTarget))
        RT = int((advanceMax-100) - 50 / 3 * (3 - dFromTarget))
        CT = int((advanceMax-100) - 50 / 3 * (3 - dFromTarget))
    else:
        LT = 1550
        RT = 1550
        CT = 1550
    # Set final Thruster value according to distance,angle from target
    if 75 >= abs(diffAngle):
        LT = int(LT + 220 * rotationDir)
        RT = int(RT - 220 * rotationDir)
        CT=1550
    elif 30<= abs(diffAngle) < 75:
        if dFromTarget > 4:
            LT = int(LT + 75 * rotationDir)
            RT = int(RT - 75 * rotationDir)
        if 1.5 <= dFromTarget <= 4:
            LT = int(LT + 125 * rotationDir)
            RT = int(RT - 125 * rotationDir)
        elif dFromTarget < 1.5:
            LT = int(LT + 150 * rotationDir)
            RT = int(RT - 150 * rotationDir)
    elif 20 <= abs(diffAngle) < 30:
        if dFromTarget > 4:
            rotation = 0.5 * 100
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        if 1.5 <= dFromTarget <= 4:
            rotation = 0.5 * (200 - (30 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 1.5:
            rotation = 0.5 * (350 - (30 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
    elif 5 <= abs(diffAngle) < 20:
        if dFromTarget > 4:
            rotation = 0.5 * 70
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        if 1.5 <= dFromTarget <= 4:
            rotation = 0.5 * (150 - (20 - abs(diffAngle)) * 5)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))
        elif dFromTarget < 1.5:
            rotation = 0.5 * (250 - (20 - abs(diffAngle)) * 10)
            LT = int(LT + (rotation * rotationDir))
            RT = int(RT - (rotation * rotationDir))

    # if abs(LT - RT) >= 250:
    #     if LT > RT:
    #         LT -= (30 + (abs(LT - RT) - 250) * 0.1)
    #         RT += (30 + (abs(LT - RT) - 250) * 0.1)
    #     else:
    #         LT += (30 + (abs(LT - RT) - 250) * 0.1)
    #         RT -= (30 + (abs(LT - RT) - 250) * 0.1)

    if LT < 1500:
        LT = max(LT, 1200)
    elif LT > 1500:
        LT = min(LT, 1800)
    if RT < 1500:
        RT = max(RT, 1200)
    elif RT > 1500:
        RT = min(RT, 1800)

    return LT, RT, CT

def calcNextTargetPosition(targetPosition, currX, currY):
    distanceFromTarget=math.sqrt((currX-targetPosition[0])**2+(currY-targetPosition[1])**2)
    angleFromTarget = math.degrees(math.atan2(targetPosition[1]-currY, targetPosition[0]-currX))
    print("Server :: Distance from next target :",distanceFromTarget)
    print("Server :: Next target Angle (Recommend for Initial Ship Angle) :",angleFromTarget)
    return distanceFromTarget, angleFromTarget

def PostPWMData(LT, RT, CT):
    UNAME = 'Thruster'
    URL = 'http://192.168.2.16:9026/Thruster'
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


input("Press")
updateGPS, currX, currY, gpsDataTime = getGPSData()
updateGyro, shipHeading = getGyroData()
print("Gyro :: initial HeadAngle :",shipHeading)
if len(targetList):
    distanceFromTarget,angleFromTarget=calcNextTargetPosition(targetList[0], currX, currY)
    shipHeading=float(input("input Initial shipAngle :"))
    diffAngle=shipHeading - angleFromTarget

numberingCWKIM = 0 
while runOption:
    deltaTime = getDT()
    try:
        updateGPS, currX, currY, gpsDataTime = getGPSData()
        if updateGPS:
            print('GPS :: Updated')
        else:
            currX, currY = correctionGPSTerm(currX,currY,shipHeading,LT,RT,CT,deltaTime)
        updateGyro, shipHeading = getGyroData()
        if len(targetList):
            targetX = targetList[0][0]
            targetY = targetList[0][1]
            targetChange, dFromTarget, aFromTarget, diffAngle = calcPositionFromTarget(targetX, targetY, currX, currY, shipHeading)
            if targetChange:
                targetList.pop(0)
            cwkimTime = datetime.datetime.now().strftime('%H%M%S%f')[:9]
            cwData1 = cwkimTime + str(currX) + str(currY) + str(aFromTarget) + str(dFromTarget)
            cwData2 = 'lidar'
            with open('/home/opencfd/OpenDEP/Script/CWKIM/realTimeShipData%d.dat' % numberingCWKIM,'w') as cwFile:
                cwFile.write(cwData1+'\n'+cwData2+'\n'+'eof')
            LT, RT, CT = calcPWM(dFromTarget, diffAngle)
            PostPWMData(LT,RT,CT)
            numberingCWKIM += 1 
        else:
            runOption = False
            break
    except KeyboardInterrupt:
        runOption = False
        break
