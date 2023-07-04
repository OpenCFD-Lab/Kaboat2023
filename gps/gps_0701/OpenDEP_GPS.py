from nmea import input_stream
import requests
import random

dataStream = input_stream.GenericInputStream.open_stream("/dev/ttyACM0")
runOption = True

lon = 0
lat = 0

print("Demo Version, date : 2023.04.07")

def PostGPSData(check, status, lon, lat):
    UNAME = 'GPS'
    URL = 'http://192.168.2.4:9013/GPS'
    with open("./data/gpsData.dat","w") as gpsFile:
        if check:
            gpsFile.write(str(status)+" "+str(lon)+" "+str(lat)+'\n')
        else:
            gpsFile.write(str(status)+" "+str(lon)+" "+str(lat)+'\n')
    GPSFile_req = open('./data/gpsData.dat','rb')
    GPSFile = {'GPSFile':GPSFile_req}
    reqData = {'uname':UNAME,'fileName':GPSFile}
    try:
        res = requests.post(URL, files=GPSFile, data=reqData, timeout=0.1)
        GPSFile_req.close()
        #if res.status_code==200:
        #    os.remove(GPSFilePath)
    except requests.exceptions.Timeout:
        PostGPSData(check, status, lon, lat)


def dataConversion(lat, lon):
    lat_dd = lat[0:2]
    lat_mm = lat[2:]
    lat_mm = float(lat_mm)/60
    lat_ = int(lat_dd)+float(lat_mm)

    lon_dd = lon[0:3]
    lon_mm = lon[3:]
    lon_mm = float(lon_mm)/60
    lon_ = int(lon_dd)+float(lon_mm)

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
    '''           
    x0 = 128.9666242783334
    y0 = 35.115988426667
    x1 = 128.96657041
    y1 = 35.11604530833334
    x2 = 128.9665515983333
    y2 = 35.1159368166667

    X1 = 8
    Y1 = 0
    X2 = 0
    Y2 = 8
    '''
    a = ((y2-y0)*X1 - (y1-y0)*X2) / ((y2-y0)*(x1-x0) - (y1-y0)*(x2-x0))
    b = ((x2-x0)*X1 - (x1-x0)*X2) / ((x2-x0)*(y1-y0) - (x1-x0)*(y2-y0))
    c = ((y2-y0)*Y1 - (y1-y0)*Y2) / ((y2-y0)*(x1-x0) - (y1-y0)*(x2-x0))
    d = ((x2-x0)*Y1 - (x1-x0)*Y2) / ((x2-x0)*(y1-y0) - (x1-x0)*(y2-y0))

    X = a*(lon - x0) + b*(lat - y0)
    Y = c*(lon - x0) + d*(lat - y0)
              
    return X, Y


def log(status, lat, lon, X, Y):
    if status == 1:
        print('\n' + '         GPS Fixed1' + '\n')
    elif status == 2:
        print('\n' + '         GPS Fixed2' + '\n')
    elif status == 4:
        print('\n'+'         RTK Fixed'+'\n')
    elif status == 5:
        print('\n'+'         RTK Float'+'\n')
    print("------------------------------")
    print("Latitude : ", round(lat,3))
    print("Longitude : ", round(lon,3))
    print('X : ', round(X,3), 'Y : ', round(Y,3))
    print("*********************************")


def writeData(status, lat, lon, X, Y):
    with open("./data/gps_lonlat.dat", "a") as gpsDataFile:
        gpsDataFile.write(str(status) + " " + str(lat) + " " + str(lon) + '\n')
    with open("./data/transData.dat", "a") as coordinateDataFile:
        coordinateDataFile.write(str(status) + " " + str(X) + " " + str(Y) + '\n')

while runOption:
    try:
        check = 1
        rawDataSet = dataStream.get_line()
        rawDataSet = str(rawDataSet, 'utf-8').strip("\r\n").split(",")
        '''
        if rawDataSet[0]=="$GNRMC":
            if rawDataSet[8] == '':
                print('HEADING NO DATA'+'\n')
                with open("./data/heading.dat", "a") as headingfile:
                    headingfile.write('nan' + '\n')
            else:
                heading=rawDataSet[8]
                print('HEADING IS  :  '+heading+'\n')
                with open("./data/heading.dat", "a") as headingfile:
                    headingfile.write(str(heading) + '\n')
        '''
        if rawDataSet[0]=="$GNGGA":
            if rawDataSet[6] == '1':
                status=1
                lat = rawDataSet[2]
                lon = rawDataSet[4]
                lat, lon = dataConversion(lat, lon)
                X, Y = transCoordinateSystem(lat, lon)
                PostGPSData(check, status, X, Y)
                log(status, lat, lon, X, Y)
                #writeData(status, lat, lon, X, Y)
            elif rawDataSet[6] == '2':
                status = 2
                lat=rawDataSet[2]
                lon=rawDataSet[4]
                lat, lon=dataConversion(lat, lon)
                X, Y=transCoordinateSystem(lat, lon)
                PostGPSData(check, status, X, Y)
                log(status, lat, lon, X, Y)
                #writeData(status, lat, lon, X, Y)
            elif rawDataSet[6]=='4':
                status = 4
                lat = rawDataSet[2]
                lon = rawDataSet[4]
                lat, lon = dataConversion(lat, lon)
                X, Y = transCoordinateSystem(lat, lon)
                PostGPSData(check, status, X, Y)
                log(status, lat, lon, X, Y)
                #writeData(status, lat, lon, X, Y)
            elif rawDataSet[6]=='5':
                status = 5
                lat = rawDataSet[2]
                lon = rawDataSet[4]
                lat, lon = dataConversion(lat, lon)
                X, Y = transCoordinateSystem(lat, lon)
                PostGPSData(check, status, X, Y)
                log(status, lat, lon, X, Y)
                #writeData(status, lat, lon, X, Y)
            else:
                status = -1
                print("!!!!!   Wrong signal from the GPS   !!!!!")
                check = 0
                #PostGPSData(check, status, -1, -1)
                PostGPSData(check, status, random.random(), random.random())
                log(status, -1, -1, -1, -1)
                #writeData(status, -1, -1, -1, -1)
    except KeyboardInterrupt:
        runOption = False
        dataStream.ensure_closed()
