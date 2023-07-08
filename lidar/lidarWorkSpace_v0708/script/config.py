import os


#about save Dir

#date=input("date, ex) 230607 :")
#case=input("case, ex) 1,2,3 or case name :")
#blackBoxPath="/home/pi/lidarWorkSpace/blackBox/Lidar_"+date+"_"+case
#os.system("mkdir "+blackBoxPath)

diskPath="/home/pi/lidarWorkSpace/disk/"
#writePath=blackBoxPath+"/Lidar.dat"
writePath="Lidar.dat"
errorAvoidancePath=diskPath+"avoidance.dat"


#set lidar initial datas
rAngle=[0 for rAi in range(201)]
rDist=[0 for rDi in range(201)]
for rA in range(-100,101): rAngle[100+rA]=rA

#url="http://192.168.2.4:9012/Lidar"
url="http://10.3.129.130:9070/Lidar"

