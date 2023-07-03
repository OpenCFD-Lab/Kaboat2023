from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Listener
import os
import time
import sys
import select
import tty
import termios



def is_key_pushed():
    return select.select([sys.stdin],[],[],0) == ([sys.stdin],[],[])


def on_press(key):
    #os.system('clear')
    if key == Key.enter:
        autoMode =  False


def on_releases(key):
    global autoSpeed, datasList, autoMode, memoMode, memoKey, memoKeys, memoKeyList, n, flipSpeed, intKey, intKeys, saveTimes, saveTimesN, memoFileNum, timeSleep, totalTime
    if key == Key.esc:
        saveFile(memoFileNum, memoKeyList)
        return False
    flipSpeed = speedSetting(key, flipSpeed)
    if memoMode:
        memoMode, memoKey, memoKeys, memoKeyList = memoModeFun(key, memoMode, memoKey, memoKeys, memoKeyList)
    else:
        datasList = readData(filePath, fileName, datasList, n)
        autoMode, memoMode, memoKeyList, n, intKey, saveTimes, saveTimesN, autoSpeed, timeSleep, totalTime = action(key, intKey, intKeys, autoMode, memoMode, memoKeyList, datasList, n, flipSpeed, saveTimes, saveTimesN, memoFileNum, autoSpeed, totalTime)
    prints(autoMode, key, intKey, memoMode, memoKey, memoKeyList, n, flipSpeed, saveTimes, saveTimesN, autoSpeed, timeSleep, datasList, totalTime)


def saveFile(memoFileNum, memoKeyList):
    with open('./memoData'+str(memoFileNum)+'.dat','wt') as FileOpen:
        FileOpen.write(memoKeyList)


def memoModeFun(key, memoMode, memoKey, memoKeys, memoKeyList):
    memo = True
    nonMemoKeys = [Key.enter, Key.backspace, Key.shift, Key.shift_r, Key.left, Key.right, Key.up, Key.down, Key.tab, Key.caps_lock, Key.ctrl, Key.alt, Key.cmd, Key.alt_r, Key.ctrl_r, Key.space]
    for i in nonMemoKeys:
        if key == i:
            memo = False
    if key == Key.enter:
        memoKeyList += memoKey
        memoKeyList += "\n"
        memoKey = ""
        memoMode = False
    if key == Key.backspace:
        if len(memoKey) >= 1:
            memoKey = memoKey[:-1]
    if key == Key.space:
        memoKey += " "
    key = str(key)
    key = key[1]
    for i in memoKeys:
        if memo:
            if key == i:
                if len(key) == 1:
                    memoKey += i
    return memoMode, memoKey, memoKeys, memoKeyList


def speedSetting(key, flipSpeed):
    if key == KeyCode(char="!"):
        flipSpeed = 1
    if key == KeyCode(char="@"):
        flipSpeed = 2
    if key == KeyCode(char="#"):
        flipSpeed = 3
    if key == KeyCode(char="$"):
        flipSpeed = 4
    return flipSpeed


def autoPlay(key, autoMode, n, autoSpeed, timeSleep, totalTime):
    old_settings = termios.tcgetattr(sys.stdin)
    eTime = time.time()
    whileTime = 0
    datasList = []
    datasList = readData(filePath, fileName, datasList, n)
    while autoMode:
        try:
            cTime = time.time()
            gTime = cTime - eTime
            eTime = cTime
            whileTime += gTime
            datasList = readData(filePath, fileName, datasList, n)
            if whileTime >= timeSleep:
                timeSleep = float(datasList[1][0][0]) * autoSpeed
                totalTime += timeSleep
                prints(autoMode, key, intKey, memoMode, memoKey, memoKeyList, n, flipSpeed, saveTimes, saveTimesN, autoSpeed, timeSleep, datasList, totalTime)
                n += 1
                whileTime = 0
            tty.setcbreak(sys.stdin.fileno())
            if is_key_pushed():
                c = sys.stdin.read(1)
                print('key: ', c)
                time.sleep(0.8)
                if c == ' ':
                    break
        except KeyboardInterrupt:
            break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    autoMode = False
    return autoMode, n, autoSpeed, timeSleep, totalTime


def action(key, intKey, intKeys, autoMode, memoMode, memoKeyList, datasList, n, flipSpeed, saveTimes, saveTimesN, memoFileNumi, autoSpeed, totalTime):
    sumTotalTime = False
    if key == Key.left:
        n -= 1
        sumTotalTime = True
    if key == Key.right:
        n += 1
        sumTotalTime = True
    if key == Key.down:
        n -= 10**flipSpeed
        sumTotalTime = True
    if key == Key.up:
        n += 10**flipSpeed
        sumTotalTime = True
    if key == KeyCode(char="m"):
        memoMode = True
    if key == KeyCode(char="e"):
        if len(saveTimes) >= 1 and len(saveTimesN) >= 1:
            saveTimes.pop(-1)
            saveTimesN.pop(-1)
    if key == KeyCode(char="E"):
        saveTimes = []
        saveTimesN = []
    if key == KeyCode(char="s"):
        saveTimes.append(datasList[-1][0])
        saveTimesN.append(n)
    if key == KeyCode(char="S"):
        autoSpeed *= 2
    if key == KeyCode(char="F"):
        autoSpeed /= 2
    if key == Key.backspace:
        if len(intKey) >= 1:
            intKey = intKey[:-1]
    if key == KeyCode(char="g"):
        if intKey == "":
            pass
        else:
            n = int(intKey)
            sumTotalTime = True
            intKey = ""
    if key == KeyCode(char="M"):
        memoKeyList = ""
    if key == Key.enter:
        autoMode = True
        key = Key.space

    timeSleep = -0.5
    if autoMode:
        autoMode, n, autoSpeed, timeSleep, totalTime = autoPlay(key, autoMode, n, autoSpeed, timeSleep, totalTime)

    key = str(key)
    key = key[1]
    for i in intKeys:
        if key == i:
            intKey += key
    if sumTotalTime:
        sumTotalTime = 0
        for j in range(n):
            datasList = readData(filePath, fileName, datasList, n)
            sumTotalTime += float(datasList[-1][-2][0])
        totalTime = sumTotalTime

    return autoMode, memoMode, memoKeyList, n, intKey, saveTimes, saveTimesN, autoSpeed, timeSleep, totalTime


def prints(autoMode, key, intKey, memoMode, memoKey, memoKeyList, n, flipSpeed, saveTimes, saveTimesN, autoSpeed, timeSleep, datasList, totalTime):
    os.system('clear')
    print("###################      autoMode :     " + str(autoMode) + "     ########################")
    print('Key %s released' %key)
    for dataN, data in enumerate(datasList[-1][-2]):
        if dataN == 1 or dataN == 2 or dataN == 5 or dataN  == 6 or dataN == 12:
            data = float(data)
            datasList[-1][-2][dataN] = round(data,3)
        if dataN == 0:
            datasList[-1][-2][dataN] = totalTime

    print("fileNumber : " + str(n) + ",  flipSpeed(10^n) : " + str(flipSpeed) +",  autoSpeed : " + str(1/autoSpeed) + "\n" + "fileData : " + str(datasList[-1][-2]) + "\n" + "lidarData : " + str(datasList[-1][-1]) + "\n")
    print("intKey : " + str(intKey))
    print("saveFileNumber : " + str(saveTimesN))
    print("###################      memoMode :     " + str(memoMode) + "     ########################")
    print("memo : " + str(memoKey))
    print("memoList\n-\n" + str(memoKeyList))


def readData(filePath, fileName, datasList, n):
    dataList = []
    with open(filePath + fileName + str(n) + '.dat', 'r') as FileOpen:
        datas = FileOpen.readlines()
    for i in range(len(datas)):
        if i == 1:
            datas[i] = datas[i].strip("\n")
        else:
            datas[i] = datas[i].strip("\n").split(" ")
        dataList.append(datas[i])
    dataList.pop(-1)
    datasList.append(dataList)
    if len(datasList) >= 3:
        datasList.pop(0)

    return datasList


memoFileNum = 0
autoSpeed = 1
filePath = './backup/'
#filePath = './realTimeShipDatas/'
fileName = 'realTimeShipData'
datasList = []
n = 0
totalTime = 0
flipSpeed = 1
intKeys = "1234567890"
autoMode = False
memoMode = False
intKey = str()
memoKey = str()
memoKeyList = str()
memoKeys = "`{}~1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM,./;'[]-=_+<>?:!@#$%^&*()"
saveTimes = []
saveTimesN = []

print('press any key, start simulate.')
time.sleep(1)
#with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#    listener.join()
datasList = readData(filePath, fileName, datasList, n)
with keyboard.Listener(on_release=on_releases) as listener:
    listener.join()
