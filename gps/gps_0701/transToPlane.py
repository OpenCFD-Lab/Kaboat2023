from nmea import input_stream

dataStream =input_stream.GenericInputStream.open_stream("/dev/ttyACM0") #how to check port number : enter "dmesg | grep tty" command on command line
runOption=True 

lon=0; #longitude
lat=0; #latitude
status='A'

print("Demo Version, date : 2023.02.06")
while runOption:
    try:
        rawDataSet=dataStream.get_line() #data type : class 'bytes',  
        rawDataSet=str(rawDataSet,'utf-8').strip("\r\n").split(",") #convert data type, 'bytes' to 'string'
        if rawDataSet[3]=='':
            print("!!!!!   Can't find signal from the GPS   !!!!!")
        else:
            if rawDataSet[0]=="$GNRMC":
                status=rawDataSet[2]
                lon=float(rawDataSet[5])*0.01
                lat=float(rawDataSet[3])*0.01

                x0 = 128.3789789798
                y0 = 35.1112535
                x1 = 128.3138910
                y1 = 35.11133131
                x2 = 128.319730197
                y2 = 35.1114132678

                X1 = 14
                Y1 = 0
                X2 = 0
                Y2 = 14
                
                a = ((y2-y0)*X1 - (y1-y0)*X2) / ((y2-y0)*(x1-x0) - (y1-y0)*(x2-x0))
                b = ((x2-x0)*X1 - (x1-x0)*X2) / ((x2-x0)*(y1-y0) - (x1-x0)*(y2-y0))
                c = ((y2-y0)*Y1 - (y1-y0)*Y2) / ((y2-y0)*(x1-x0) - (y1-y0)*(x2-x0))
                d = ((x2-x0)*Y1 - (x1-x0)*Y2) / ((x2-x0)*(y1-y0) - (x1-x0)*(y2-y0))

                X = a*(lon - x0) + b*(lat - y0)
                Y = c*(lon - x0) + d*(lat - y0)
                print("*****************")
                print("X : ", X, "Y : ", Y)
                #with open("./gpsData.dat","a") as gpsDataFile:
                    #gpsDataFile.write(str(lon)+" "+str(lat)+'\n')
    except KeyboardInterrupt:
        runOption=False
        dataStream.ensure_closed()
