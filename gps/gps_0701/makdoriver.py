from nmea import input_stream
import requests

dataStream =input_stream.GenericInputStream.open_stream("/dev/ttyACM0") #how to check port number : enter "dmesg | grep tty" command on command line
runOption=True 

lon=0; #longitude
lat=0; #latitude
status='A'

print("Demo Version, date : 2023.02.06")

def PostGPSData(check, lon, lat):
    UNAME = 'GPS'
    URL = 'http://192.168.2.2:9013/GPS'
    with open("./data/gpsData.dat","w") as gpsFile:
        if check:
            gpsFile.write(str(lon)+" "+str(lat)+'\n')
        else:
            gpsFile.write(str(lon)+" "+str(lat)+'\n')
    GPSFile_req=open('./data/gpsData.dat','rb')
    GPSFile={'GPSFile':GPSFile_req}
    reqData={'uname':UNAME,'fileName':GPSFile}
    try:
        res = requests.post(URL, files=GPSFile, data=reqData)
        GPSFile_req.close()
        #if res.status_code==200:
        #    os.remove(GPSFilePath)
    except requests.exceptions.Timeout:
        PostGPSData(GPSFileName,GPSFilePath)


while runOption:
    try:
        check=1
        rawDataSet=dataStream.get_line() #data type : class 'bytes',  
        #print(rawDataSet)
        rawDataSet=str(rawDataSet,'utf-8').strip("\r\n").split(",") #convert data type, 'bytes' to 'string'
        #print(rawDataSet)
        if rawDataSet[3]=='':
            print("!!!!!   Can't find signal from the GPS   !!!!!")
            check=0
            PostGPSData(check, 0, 0)
        else:
            if rawDataSet[0]=="$GNRMC":
                status=rawDataSet[2]
                lon=float(rawDataSet[5])*0.01
                lat=float(rawDataSet[3])*0.01
                print("*****************")
                print("gps status: ",status)
                print("gps lon: ",lon)
                print("gps lat: ",lat)
                PostGPSData(check, lon, lat)
        #        with open("./gpsData.dat","a") as gpsDataFile:
        #            gpsDataFile.write(str(lon)+" "+str(lat)+'\n')
    except KeyboardInterrupt:
        runOption=False
        dataStream.ensure_closed()
