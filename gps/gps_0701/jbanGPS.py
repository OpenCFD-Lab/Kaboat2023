from nmea import input_stream
import requests
import random

dataStream =input_stream.GenericInputStream.open_stream("/dev/ttyACM0")
runOption=True 

lon=0; 
lat=0;

print("Demo Version, date : 2023.02.10")

def PostGPSData(check, lon, lat):
    UNAME = 'GPS'
    URL = 'http://192.168.2.2:9013/GPS'
    lon=random.random()
    lat=random.random()
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


def dataConversion(lat, lon):
    lat_dd=lat[0:2]
    lat_mm=lat[2:]
    lat_mm=float(lat_mm)/60
    lat_=int(lat_dd)+float(lat_mm)

    lon_dd=lon[0:3]
    lon_mm=lon[3:]
    lon_mm=float(lon_mm)/60
    lon_=int(lon_dd)+float(lon_mm)

    return lat_, lon_


def transCoordinateSystem(lat, lon):
    x0 = 128.9670803334
    y0 = 35.11482316667
    x1 = 128.96694083333
    y1 = 35.11475766667
    x2 = 128.96715
    y2 = 35.11471416666

    X1 = 15
    Y1 = 0
    X2 = 0
    Y2 = 14
               
    a = ((y2-y0)*X1 - (y1-y0)*X2) / ((y2-y0)*(x1-x0) - (y1-y0)*(x2-x0))
    b = ((x2-x0)*X1 - (x1-x0)*X2) / ((x2-x0)*(y1-y0) - (x1-x0)*(y2-y0))
    c = ((y2-y0)*Y1 - (y1-y0)*Y2) / ((y2-y0)*(x1-x0) - (y1-y0)*(x2-x0))
    d = ((x2-x0)*Y1 - (x1-x0)*Y2) / ((x2-x0)*(y1-y0) - (x1-x0)*(y2-y0))

    X = a*(lon - x0) + b*(lat - y0)
    Y = c*(lon - x0) + d*(lat - y0)
              
    return X, Y


while runOption:
    try:
        check=1
        rawDataSet=dataStream.get_line()   
        rawDataSet=str(rawDataSet,'utf-8').strip("\r\n").split(",")
        if rawDataSet[0]=="$GNRMC":
            if rawDataSet[2]=='V':
                print("!!!!!   Can't find signal from the GPS   !!!!!")
                check=0
                PostGPSData(check, 0, 0)
            elif rawDataSet[2]=='A':
        #        print(rawDataSet)
                lat=rawDataSet[3]
                lon=rawDataSet[5]
                velocity=float(rawDataSet[7])*0.5144444
                #headingAngle=float(rawDataSet[8])
                lat, lon=dataConversion(lat, lon)
                X, Y=transCoordinateSystem(lat, lon)
                print("*****************")
                print("Latitude : ",lat)
                print("Longitude : ",lon)
                print("Velocity : ",velocity)
                print('X : ', X, 'Y : ', Y)
                #print("Heading Angle : ",headingAngle)
                '''
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                    gpsDataFile.write(str(lat)+" "+str(lon)+'\n')
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(X)+" "+str(Y)+'\n')
                with open("./data/velocity.dat","a") as velocityDataFile:
                    velocityDataFile.write(str(velocity)+'\n')
                '''    
                PostGPSData(check, lon, lat)
    except KeyboardInterrupt:
        runOption=False
        dataStream.ensure_closed()
