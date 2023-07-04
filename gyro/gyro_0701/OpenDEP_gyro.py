import socket
import requests
import random

UDP_IP='192.168.2.13'
UDP_PORT=3333

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((UDP_IP, UDP_PORT))

error = 173


def PostGyroData(headingAngle):
    UNAME = 'Gyro'
    URL = 'http://192.168.2.4:9014/Gyro'
    with open("./data/gyroData.dat","w") as gyroFile:
        gyroFile.write(str(headingAngle)+'\n')
    GyroFile_req=open('./data/gyroData.dat','rb')
    GyroFile={'GyroFile':GyroFile_req}
    reqData={'uname':UNAME,'fileName':GyroFile}
    try:
        res = requests.post(URL, files=GyroFile, data=reqData, timeout=0.1)
        GyroFile_req.close()
        #if res.status_code==200:
    except requests.exceptions.Timeout:
        PostGyroData(headingAngle)

while True:
    data, addr = sock.recvfrom(8192)
    dataString = data.decode('utf-8')
    data1 = dataString.split(',')
    '''
    a=random.random()
    PostGyroData(a)
    print(a)
    '''
    if len(data1) > 16:
        if float(data1[14]) > 0:
            print('Gyro Data Error : ', float(data1[14]))
        elif float(data1[14]) < 0:
            print('Gyro Data Error : ', -float(data1[14]))
        #print(data1[14]+', '+data1[15]+', '+data1[16])
        headingAngle = -1*float(data1[14]) + error
        if headingAngle > 180:
            headingAngle -= 360
        elif headingAngle < -180:
            headingAngle += 360
        print('HEADING ANGLE : ', headingAngle)
        print('################################################')
        PostGyroData(headingAngle)
