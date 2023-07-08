import os
import copy
import time
import math
import requests
import config

def updateNewestFile():
    fileGeneratedTime=[]
    for fileName in os.listdir(config.diskPath):
        filePath=config.diskPath+fileName
        generatedTime=os.path.getctime(filePath)
        fileGeneratedTime.append((filePath,generatedTime))
    newestFilePath=max(fileGeneratedTime, key=lambda x:x[1])[0]
    return newestFilePath

def read(rawDist,rawAngle,initialTime):
   newestFilePath=updateNewestFile()
   fileState=-1
   if(newestFilePath!=config.errorAvoidancePath):
       with open(newestFilePath,"r") as raw:
           fileState=len(raw.readlines())
           if(fileState==360): 
               raw.seek(0)
               rAngle=0
               rDist=raw.readline().strip("\n")
               while rDist!="":
                   if(0<=rAngle<=100):
                       rawDist.append(float(rDist))
                       rawAngle.append(rawAngle)
                   elif(260<=rAngle<=359):
                       rawDist.insert(int(abs(259-rAngle)-1),float(rDist))
                       rawAngle.insert(int(abs(259-rAngle)-1),float(rAngle-360))
                   rDist=raw.readline().strip("\n")
                   rAngle+=1
               os.system('rm -rf '+config.diskPath+'Lidar*')
   return fileState

def refineZeroPoints(rawDist,filteredDist):
    filteredDist=copy.copy(rawDist)
    for rDi in range(2, len(rawDist)-2):
        if rawDist[rDi]==0:
            if rawDist[rDi+1] ==0 and rawDist[rDi-1]==0: filteredDist[rDi]=max(rawDist[rDi-2],rawDist[rDi+2])
            elif rawDist[rDi+1] ==0 or rawDist[rDi-1]==0: filteredDist[rDi]=max(rawDist[rDi-1],rawDist[rDi+1])
            else:
                 diffLeft=abs(rawDist[rDi]-rawDist[rDi-1])
                 diffRight=abs(rawDist[rDi]-rawDist[rDi+1])
                 if diffLeft<diffRight: filteredDist[rDi]=rawDist[rDi-1]
                 else: filteredDist[rDi]=rawDist[rDi+1]
    return filteredDist

def refineCollapsedPoints(filteredDist):
    Threshold= 0.6#
    cFilteredDist=copy.copy(filteredDist)
    for fDi in range(2,len(filteredDist)-2):
        diffLeft=cFilteredDist[fDi]-cFilteredDist[fDi-1]
        diffRight=cFilteredDist[fDi]-cFilteredDist[fDi+1]
        diffBeforeLeft=(cFilteredDist[fDi-1]-cFilteredDist[fDi-2])
        diffAfterRight=(cFilteredDist[fDi+1]-cFilteredDist[fDi+2])
        if Threshold<=abs(diffLeft) or Threshold<=abs(diffRight):
            if Threshold<=abs(diffLeft) and Threshold<=abs(diffRight):
                if Threshold<=abs(diffBeforeLeft) and Threshold>abs(diffAfterRight): filteredDist[fDi]=cFilteredDist[fDi+1]
                elif Threshold>abs(diffBeforeLeft) and Threshold<=abs(diffAfterRight): filteredDist[fDi]=cFilteredDist[fDi-1]
                elif Threshold>abs(diffBeforeLeft) and Threshold>abs(diffAfterRight): filteredDist[fDi]=max(cFilteredDist[fDi+1],cFilteredDist[fDi-1])
            elif Threshold>abs(diffLeft) and Threshold<=abs(diffRight):
                if diffRight>0 and diffBeforeLeft>0 :pass
                else:
                    if Threshold<=abs(diffBeforeLeft) and Threshold>abs(diffAfterRight): filteredDist[fDi]=cFilteredDist[fDi+1]
                    elif Threshold>abs(diffBeforeLeft) and Threshold<=abs(diffAfterRight): filteredDist[fDi]=cFilteredDist[fDi-1]
            elif Threshold<=abs(diffLeft) and Threshold>abs(diffRight):
                if diffLeft>0 and diffAfterRight> 0:pass
                else:
                    if Threshold>abs(diffBeforeLeft) and Threshold<=abs(diffAfterRight): filteredDist[fDi]=cFilteredDist[fDi-1]
                    elif Threshold <= abs(diffBeforeLeft) and Threshold > abs(diffAfterRight): filteredDist[fDi]=cFilteredDist[fDi+1]
    return filteredDist

def refineFiercedPoints(filteredDist):
    Threshold=0.6
    cFilteredDist = copy.copy(filteredDist)
    for fDi in range(2,len(filteredDist)-2):
        diffLeft=(cFilteredDist[fDi]-cFilteredDist[fDi-1])
        diffRight=(cFilteredDist[fDi]-cFilteredDist[fDi+1])
        if abs(diffLeft)>=Threshold and abs(diffRight)>=Threshold:
            if diffLeft<0 and diffLeft*diffRight>0: filteredDist[fDi]=min(cFilteredDist[fDi+1],cFilteredDist[fDi-1])
    return filteredDist

def patchDetectionRange(filteredDist):
    for fDi in range(len(filteredDist)):
        if filteredDist[fDi]>8.0: filteredDist[fDi]=8.0
        elif filteredDist[fDi]<0.1: filteredDist[fDi]=8.0
        
    return filteredDist

def post(url):
    userName="Lidar"
    lidar_req=open(config.writePath,"rb")
    lidarFile={'lidarFile':lidar_req}
    reqData={'uname':userName, 'fileName':'Lidar.dat'}
    try:
        res=requests.post(url,files=lidarFile,data=reqData,timeout=0.1)
    except requests.exceptions.Timeout:
        post(url)

def write(rawDist,filteredDist,initialTime):
    elapsedTime=round(time.time()-initialTime,3)
    rawfilePath=config.blackBoxPath+"/LidarRAW_"+str(elapsedTime)+".dat"
    filteredfilePath=config.blackBoxPath+"/LidarFiltered_"+str(elapsedTime)+".dat"
    with open(config.writePath,"w") as lidarData:
        for fDi in range(0,len(filteredDist)):
            lidarData.write(str(filteredDist[fDi])+" ")
    #post(config.urlforServer)
    post(config.urlforSYLEETool)
    print("LidarFilterd_"+str(elapsedTime)+".dat"+" was created")
    os.system('cp -r '+config.writePath+' '+filteredfilePath)
    with open(rawfilePath,"w") as rawData:
        for rDi in range(0,len(rawDist)):
            rawData.write(str(rawDist[rDi])+" ")

def clearAllVariance(rawDistance,rawAngle,filteredDist):
    rawDist.clear()
    rawAngle.clear()
    filteredDist.clear()
    return rawDist,rawAngle,filteredDist

rawDist=[]
rawAngle=[]
filteredDist=[]

fileState=0
initialTime=time.time()

execution=True
while execution:
    try:
        start=time.time()
        fileState=read(rawDist,rawAngle,initialTime)
        if(fileState==360):
            filteredDist=refineZeroPoints(rawDist,filteredDist)
            filteredDist=refineCollapsedPoints(filteredDist)
            filteredDist=refineFiercedPoints(filteredDist)
            filteredDist=patchDetectionRange(filteredDist)
            write(rawDist,filteredDist,initialTime)
            rawDistance,rawAngle,filteredDistance=clearAllVariance(rawDist,rawAngle,filteredDist)
        #print("dt :",time.time()-start)
    except KeyboardInterrupt:
        execution=False

