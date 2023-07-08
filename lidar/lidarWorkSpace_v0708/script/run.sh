# :: Notice
# :: there are 2 models of lidar, named S1 and S2
# :: if model name is S1 --> baudrate is 256000
# :: if model name is S2 --> baudrate is 1M (1000000) 
# :: please check your lidar model and modify baudrate after /dev/ttyUSB0
# :: 23.06.01 SYLEE

./../source/output/Linux/Release/ultra_simple --channel --serial /dev/ttyUSB0 256000
