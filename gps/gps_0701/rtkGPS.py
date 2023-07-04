from nmea import input_stream
import requests

dataStream =input_stream.GenericInputStream.open_stream("/dev/ttyACM0")
runOption=True 

lon=0; 
lat=0;

print("Demo Version, date : 2023.02.11")

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
    x0 = 128.96665693
    y0 = 35.115026838333335
    x1 = 128.96675848333
    y1 = 35.11486302833333
    x2 = 128.96685016666666
    y2 = 35.11511052

    X1 = 20.5
    Y1 = 0
    X2 = 0
    Y2 = 20
               
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
        #if rawDataSet[0]=="$GNGGA" or rawDataSet[0]=="$GNRMC":
        #    print(rawDataSet)
        if rawDataSet[0]=="$GNGGA":
            if rawDataSet[6]==0:
                print("!!!!!   Can't find signal from the GPS   !!!!!")
                check=0
                PostGPSData(check, 0, 0)
            elif rawDataSet[6]=='1':
                print('\n'+'         GPS Fixed1'+'\n')
                lat=rawDataSet[2]
                lon=rawDataSet[4]
                lat, lon=dataConversion(lat, lon)
                X, Y=transCoordinateSystem(lat, lon)
                print("------------------------------")
                print("Latitude : ",lat)
                print("Longitude : ",lon)
                print('X : ', X, 'Y : ', Y)
                print("*********************************")
                PostGPSData(check, X, Y)
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                    gpsDataFile.write(str(1)+" "+str(lat)+" "+str(lon)+'\n')
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(1)+" "+str(X)+" "+str(Y)+'\n')
            elif rawDataSet[6]=='2':
                print('\n'+'         GPS Fixed2'+'\n')
                lat=rawDataSet[2]
                lon=rawDataSet[4]
                lat, lon=dataConversion(lat, lon)
                X, Y=transCoordinateSystem(lat, lon)
                print("------------------------------")
                print("Latitude : ",lat)
                print("Longitude : ",lon)
                print('X : ', X, 'Y : ', Y)
                print("*********************************")
                PostGPSData(check, X, Y)
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                    gpsDataFile.write(str(2)+" "+str(lat)+" "+str(lon)+'\n')
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(2)+" "+str(X)+" "+str(Y)+'\n')
                '''
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                    gpsDataFile.write(str(lat)+" "+str(lon)+'\n')
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(X)+" "+str(Y)+'\n')
                '''
            elif rawDataSet[6]=='4':
                print('\n'+'         RTK Fixed'+'\n')
                lat=rawDataSet[2]
                lon=rawDataSet[4]
                lat, lon=dataConversion(lat, lon)
                X, Y=transCoordinateSystem(lat, lon)
                print("------------------------------")
                print("Latitude : ",lat)
                print("Longitude : ",lon)
                print('X : ', X, 'Y : ', Y)
                print("*********************************")
                PostGPSData(check, X, Y)
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                    gpsDataFile.write(str(4)+" "+str(lat)+" "+str(lon)+'\n')
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(4)+" "+str(X)+" "+str(Y)+'\n')
                '''
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(X)+" "+str(Y)+'\n')
                with open("./data/velocity.dat","a") as velocityDataFile:
                    velocityDataFile.write(str(velocity)+'\n')
                '''
            elif rawDataSet[6]=='5':
                print('\n'+'         RTK Float'+'\n')
                lat=rawDataSet[2]
                lon=rawDataSet[4]
                lat, lon=dataConversion(lat, lon)
                X, Y=transCoordinateSystem(lat, lon)
                print("------------------------------")
                print("Latitude : ",lat)
                print("Longitude : ",lon)
                print('X : ', X, 'Y : ', Y)
                print("*********************************")
                PostGPSData(check, X, Y)
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                    gpsDataFile.write(str(5)+" "+str(lat)+" "+str(lon)+'\n')
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(5)+" "+str(X)+" "+str(Y)+'\n')
                '''
                with open("./data/gps_lonlat.dat","a") as gpsDataFile:
                with open("./data/transData.dat","a") as coordinateDataFile:
                    coordinateDataFile.write(str(X)+" "+str(Y)+'\n')
                with open("./data/velocity.dat","a") as velocityDataFile:
                    velocityDataFile.write(str(velocity)+'\n')
                '''
            else:
                print("!!!!!   Wrong signal from the GPS   !!!!!")
        #       PostGPSData(check, lon, lat)
    except KeyboardInterrupt:
        runOption=False
        dataStream.ensure_closed()
