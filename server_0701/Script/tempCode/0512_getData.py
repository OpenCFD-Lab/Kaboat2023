import math
import time
import requests

status = 0 
gpsX = 0
gpsY = 0
gpsDataTime = 0
gyroData = 0
runOption=True

while runOption:
    try:
        with open('/home/opencfd/OpenDEP/Receive/GPS/gpsData.dat', 'r') as gpsFile:
            gpsData = gpsFile.readline().strip('\n').split(' ')
        with open('/home/opencfd/OpenDEP/Receive/Gyro/gyroData.dat', 'r') as gyroFile:
            gyroData = gyroFile.readline()
            try:
                gyroHeadAngle = float(gyroData)
            except ValueError:
                pass
        if len(gpsData) == 3:
            status = int(gpsData[0])
            gpsX = float(gpsData[1])
            gpsY = float(gpsData[2])
            gpsDataTime = time.time()
            with open('/home/opencfd/OpenDEP/Script/jbAnData/rawGPS.dat', 'a') as rawGPS:
                rawGPS.write(str(status)+','+str(gpsX)+','+str(gpsY)+','+str(gyroHeadAngle)+','+str(gpsDataTime)+'\n')
            print(status, gpsX, gpsY, gyroHeadAngle, gpsDataTime)
    except KeyboardInterrupt:
        runOption = False
        break
