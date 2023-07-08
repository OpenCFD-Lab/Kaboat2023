import os

case=input("caseNumber :, ex)001 ")
dirName="disk_"+case
os.system("cp -r ../disk/ ../"+dirName)
os.system("./clean.sh")
