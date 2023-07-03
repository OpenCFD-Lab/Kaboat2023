import math
import time

runOption = True

previousData = []
oldX = 0
oldY = 0
oldGyro = 0
oldLT = 0
oldRT = 0
oldCT = 0
oldHeading = 0
velocity = 0
betweenDistance = 0
diffAngle = 0
deltaTime = 0

while runOption:
    try:
        with open('/home/opencfd/OpenDEP/Receive/GPS/gpsData.dat', 'r') as gpsFile:
            gpsData = gpsFile.readline().strip('\n').split(' ')
            if len(gpsData) == 3:
                status = int(gpsData[0])
                gpsX = float(gpsData[1])
                gpsY = float(gpsData[2])
                dataTime = time.time()


        with open('/home/opencfd/OpenDEP/Receive/Gyro/gyroData.dat', 'r') as gyroFile:
            gyroData = gyroFile.readline()
            gyroHeadAngle = float(gyroData)

        with open('/home/opencfd/OpenDEP/Receive/Thruster/ThrusterData.dat', 'r') as thrusterFile:
            thrusterData = thrusterFile.readline().strip('\n').split(' ')
            if len(thrusterData) == 3:
                LT = int(thrusterData[0])
                RT = int(thrusterData[1])
                CT = int(thrusterData[2])

        if oldX != gpsX or oldY != gpsY:
            currX = gpsX
            currY = gpsY
            updateGPS = True
        else:
            updateGPS = False
        oldX = gpsX
        oldY = gpsY

        if oldGyro != gyroHeadAngle:
            currGyro = gyroHeadAngle
            updateGyro = True
        else:
            updateGyro = False
        oldGyro = gyroHeadAngle

        if oldLT != LT or oldRT != RT or oldCT != CT:
            currLT = LT
            currRT = RT
            currCT = CT
            updateThruster = True
        else:
            updateThruster = False
        oldLT = LT
        oldRT = RT
        oldCT = CT
        
        if updateThruster:
            ThrusterData = str(currLT) + ' ' + str(currRT) + ' ' + str(currCT) + '\n'
            print(ThrusterData)
            with open('./jbAnData/RC1850.dat', 'a') as RCFile:
                RCFile.write(ThrusterData)

        if updateGPS:
            previousData.append([gpsX, gpsY, dataTime])
            if len(previousData) >= 2:
                gpsHeading = math.degrees(math.atan2(previousData[-1][1] - previousData[-2][1], previousData[-1][0] - previousData[-2][0]))
                betweenDistance = math.sqrt(math.pow(previousData[-1][0] - previousData[-2][0], 2) + math.pow(previousData[-1][1] - previousData[-2][1], 2))
                deltaTime = previousData[-1][2] - previousData[-2][2]
                velocity = betweenDistance / deltaTime
                if gpsHeading > 0 and oldHeading < 0:
                    diffAngle = gpsHeading - abs(oldHeading)
                elif gpsHeading < 0 and oldHeading > 0:
                    diffAngle = -1*(abs(gpsHeading) - oldHeading)
                else:
                    #diffAngle = gpsHeading - oldHeading
                    diffAngle = oldHeading - gpsHeading
                oldHeading = gpsHeading
            if len(previousData) > 3:
                previousData.pop(0)
            if len(previousData) == 2:
                diffAngle = 0

            SBLeeData = str(currLT) + ' ' + str(currRT) + ' ' + str(currCT) + ' ' + str(gpsX) + ' ' + str(gpsY) + ' ' + str(gpsHeading) + ' ' + str(currGyro) + ' ' + str(velocity) + ' ' + str(betweenDistance) + ' ' + str(diffAngle) + ' ' + str(deltaTime) + '\n'
            #with open('./jbAnData/SBLEE_1.dat', 'a') as SBLeeFile:
            #    SBLeeFile.write(SBLeeData)
            print('LT : ', currLT, ' | RT : ', currRT, ' | CT : ', currCT, ' | V : ', round(velocity,4))
            print('X : ', round(gpsX, 4), ' | Y : ', round(gpsY, 4), ' | gpsHeading : ', round(gpsHeading, 4),  ' | gyroHeading : ', round(currGyro, 4))
            print('D : ', round(betweenDistance,4), ' | angle : ', round(diffAngle,4), ' | dT : ', round(deltaTime,4))
            print('########################################################')
            '''
            headingData = str(status)+' '+str(currX)+' '+str(currY)+' '+str(gpsHeading)+' '+str(currGyro) + '\n'
            with open('./jbAnData/heading.dat', 'a') as headingFile:
                headingFile.write(headingData)
            '''
    except KeyboardInterrupt:
        runOption = False
        break
