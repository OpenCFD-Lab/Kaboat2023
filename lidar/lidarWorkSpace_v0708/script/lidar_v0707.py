import os
import datetime
import copy
import config
import requests

def pigeon():
    url=config.url
    userName="Lidar"
    lidarRequest=open(config.writePath,'rb')
    lidarFile={'lidarFile':lidarRequest}
    requestData={'uname':userName, 'fileName':'Lidar.dat'}
    try:
        garaGUGU=requests.post(url,files=lidarFile,data=requestData, timeout=0.1)
    except requests.exceptions.Timeout:
        pigeon()

def getTime():
    hour= datetime.datetime.now().strftime('%H')
    minute=datetime.datetime.now().strftime('%M')
    sec=datetime.datetime.now().strftime('%S.%f')
    now=float(hour)*3600+float(minute)*60+float(sec)
    return now

def getNewFilePath():
    fileGeneratedTime=[]
    for fileName in os.listdir(config.diskPath):
        filePath=config.diskPath+fileName
        generatedTime=os.path.getctime(filePath)
        fileGeneratedTime.append((filePath,generatedTime))
    newFilePath=max(fileGeneratedTime, key=lambda x:x[1])[0]
    return newFilePath

def read(rDist):
    fileStatus=False
    newFilePath=getNewFilePath()
    isUpdated=(newFilePath!=config.errorAvoidancePath)
    if isUpdated:
        with open(newFilePath,"r") as newFile:
            rD=newFile.readline().split(" ")
            if len(rD)==360:
                fileStatus=True
                for rA in range(0,len(rD)):
                    if rA<=100: rDist[rA+100]=float(rD[rA])
                    elif rA>=260 and rA<360: rDist[rA-260]=float(rD[rA])
    return rDist,fileStatus

def write(fDist):
    with open(config.writePath,"w") as writeFile:
        for fDi in range(len(fDist)): writeFile.write(str(fDist[fDi])+" ")
    pigeon()

def forZeroPoints(rDist,zDist):
    for zDi in range(0,2):
        zDist[zDi]=rDist[zDi]
        zDist[len(zDist)-1-zDi]=zDist[len(zDist)-1-zDi]
    for rDi in range(2, len(rDist)-2):
        if rDist[rDi]==0:
            if rDist[rDi+1]==0 and rDist[rDi-1]==0: zDist[rDi]=max(rDist[rDi-2],rDist[rDi+2])
            elif rDist[rDi+1]==0 or rDist[rDi-1]==0: zDist[rDi]=max(rDist[rDi-1],rDist[rDi+1])
            else:
                leftDiff=abs(rDist[rDi]-rDist[rDi-1])
                rightDiff=abs(rDist[rDi]-rDist[rDi+1])
                if leftDiff<rightDiff: zDist[rDi]=rDist[rDi-1]
                else: zDist[rDi]=rDist[rDi+1]
        else:
            zDist[rDi]=rDist[rDi]
    return zDist

def forCollapsedPoints(zDist,cDist):
    threshold=0.6 #m
    for cDi in range(0,2):
        cDist[cDi]=zDist[cDi]
        cDist[len(cDist)-1-cDi]=zDist[len(cDist)-1-cDi] 
    for zDi in range(2, len(zDist)-2):
        leftDiff=zDist[zDi]-zDist[zDi-1]
        rightDiff=zDist[zDi]-zDist[zDi+1]
        leftPrevDiff=zDist[zDi-1]-zDist[zDi-2]
        rightNextDiff=zDist[zDi+1]-zDist[zDi+2]
        if threshold<=abs(leftDiff) or threshold <=abs(rightDiff):
            if threshold<=abs(leftDiff) and threshold<=abs(rightDiff):
                if threshold<=abs(leftPrevDiff) and threshold>abs(rightNextDiff): cDist[zDi]=zDist[zDi+1]
                elif threshold>abs(leftPrevDiff) and threshold<=abs(rightNextDiff): cDist[zDi]=zDist[zDi-1]
                elif threshold>abs(leftPrevDiff) and threshold>abs(rightNextDiff): cDist[zDi]=max(zDist[zDi+1],zDist[zDi-1])
                else: cDist[zDi]=zDist[zDi]
            elif threshold>abs(leftDiff) and threshold<=abs(rightDiff):
                if leftDiff>0 and rightDiff>0 : cDist[zDi]=zDist[zDi]
                else:
                    if threshold<=abs(leftPrevDiff) and threshold>abs(rightNextDiff): cDist[zDi]=zDist[zDi+1]
                    elif threshold>abs(leftPrevDiff) and threshold<=abs(rightNextDiff): cDist[zDi]=zDist[zDi-1]
                    else: cDist[zDi]=zDist[zDi]
            elif threshold<=abs(leftDiff) and threshold>abs(rightDiff):
                if leftDiff>0 and rightDiff>0 : cDist[zDi]=zDist[zDi]
                else:
                    if threshold>abs(leftPrevDiff) and threshold<=abs(rightNextDiff): cDist[zDi]=zDist[zDi-1]
                    elif threshold<=abs(leftPrevDiff) and threshold>abs(rightNextDiff): cDist[zDi]=zDist[zDi+1]
                    else: cDist[zDi]=zDist[zDi]
            else: cDist[zDi]=zDist[zDi] 
        else: cDist[zDi]=zDist[zDi]
    return cDist

"""
def forFiercedPoints(cDist,fDist):
    for fDi in range(0,2):
        fDist[fDi]=cDist[fDi]
        fDist[len(fDist)-1-fDi]=cDist[len(fDist)-1-fDi]
    for cDi in range(2, len(cDist)-2):
        leftDiff=abs(cDist[cDi]-cDist[cDi-1])
        rightDiff=abs(cDist[cDi]-cDist[cDi+1])
        leftPrevDiff=abs(cDist[cDi-1]-cDist[cDi-2])
        rightNextDiff=abs(cDist[cDi+1]-cDist[cDi+2])
"""

# variable for checking time-delay while excution
initTime=getTime()
elapsedTime=0
deltaTime=0

# variable for distance, angle from object detected by lidar
rAngle=copy.deepcopy(config.rAngle)
rDist=copy.deepcopy(config.rDist)
zDist=copy.deepcopy(config.rDist)
cDist=copy.deepcopy(config.rDist)
#fDist=copy.deepcopy(config.rDist)

execution=True
fileStatus=False

while execution:
    try:
        rDist,fileStatus=read(rDist)
        if fileStatus:
            os.system('rm -rf '+config.diskPath+'Lidar*')
            zDist=forZeroPoints(rDist,zDist)
            cDist=forCollapsedPoints(zDist,cDist)
            write(cDist)
    except KeyboardInterrupt:
        execution=False
    




