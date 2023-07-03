import math
import time
import requests
import os
import shutil
import random

global oldX, oldY
global oldGyro
global oldTime

runOption = True

oldX, oldY = 0, 0
oldGyro = 0
oldTime = 0
LT, RT, CT = 1500, 1500, 1500
targetList = [[-7,8],[-1,16],[-1,0]]

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

saveFilePath = '/home/opencfd/OpenDEP/Script/simulation/'
backupPath = '/home/opencfd/OpenDEP/Script/simulation/backup/'
backupFileName = 'realTimeShipData'

while runOption:
    print('#############################################################')
    PostPWMData(1500, 1600, 1700)
