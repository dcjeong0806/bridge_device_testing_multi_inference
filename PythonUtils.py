import base64
import cv2
import os
import time
import io
import socket
import psutil
import zipfile
import os
import json
from datetime import datetime

def printDebug(strMessage):
    strTime = time.strftime("%H:%M:%S")
    print(strTime + " : " + strMessage)

def GetDateTime():
    now = datetime.utcnow() # current date and time
    timeStamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] ## YYYY-MM-DDThh:mm:ss.sssZ
    DateTimeStamp = timeStamp + "Z"
    return DateTimeStamp

def GetFileSizeBytes(strFilename):
    try:
        fileOpen = open(strFilename, "rb")
        fileSize = len(fileOpen.read())
        fileOpen.close()
    except Exception as ex:
        fileSize = 0
        printDebug("Exception in GetFileSizeBytes : " + str(ex))
    return(fileSize)

def DeleteFile(strPathFilename):
    try:
        os.remove(strPathFilename)
        #print("### Delete File:" + strPathFilename)
    except Exception as ex:
        printDebug("Exception in DeleteFile:" + strPathFilename + " Exception:" + str(ex))
   

def DeleteMp4Files():
    try:
        files = os.listdir(os.curdir)
        for item in files:
            if ".mp4" in item:
                try:
                    #os.remove(item)
                    printDebug("### Delete File:" + item)
                    DeleteFile(item)
                except:
                    pass
    except Exception as ex:
        printDebug("Exception in DeleteMp4Files:" + str(ex))

def ConvertFrameToBase64(frame):
    try:
        ret, binjpg = cv2.imencode('.jpg', frame)
        if ret:
            bimageBase64 = base64.b64encode(binjpg)
            imageBase64 = bimageBase64.decode()
        else:
            imageBase64 = ""
    except Exception as ex:
        printDebug("Exception in ConvertFrameToBase64 : " + str(ex))
        imageBase64 = ""
    return(imageBase64)

def WriteBinaryToFile(strPath, strFilename, stringData): 
    try:
        if not os.path.exists(strPath):
            os.makedirs(strPath)
        # Write JSON file
        with io.open(strPath + strFilename, 'wb') as outfile:
            outfile.write(stringData)
            outfile.close()
    except Exception as ex:
        printDebug("Exception in WriteBinaryToFile:" + str(ex))

def WriteBinaryToFileLocal(strFilename, stringData): 
    try:
        with io.open(strFilename, 'wb') as outfile:
            outfile.write(stringData)
            outfile.close()
    except Exception as ex:
        printDebug("Exception in WriteBinaryToFileLocal:" + str(ex))



def WriteStringToPathFile(strPath, strFilename, stringData): 
    try:
        if not os.path.exists(strPath):
            os.makedirs(strPath)
        # Write JSON file
        with io.open(strPath + strFilename, 'w') as outfile:
            outfile.write(stringData)
            outfile.close()
    except Exception as ex:
        printDebug("Exception in WriteStringToPathFile:" + str(ex))

def ReadBinaryFromFile(strPath, strFilename):
    jpegBin = 0
    try: 
        with io.open(strPath + strFilename, 'rb') as inputfile:
            jpegBin =inputfile.read()
            inputfile.close()
    except Exception as ex:
        printDebug("Exception in ReadBinaryToFile:" + str(ex))
        jpegBin = 0
    
    return(jpegBin)

def getIpAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getMacAddress(ipaddress):
    macAddress = ""
    try:
        nics = psutil.net_if_addrs()
        nics.pop('lo') # remove loopback since it doesnt have a real mac address
        fIpAddressFound = False
        for i in nics:
            for j in nics[i]:
                if j.family == 2:
                    if (j.address == ipaddress):
                        fIpAddressFound = True
                        break
            if (fIpAddressFound):
                for j in nics[i]:
                    if j.family == 17:  # AF_LINK
                        macAddress = j.address
                        fIpAddressFound = False
                        break
    except:
        macAddress = ""

    return(macAddress)


def UnzipFile(pathAndFilename, folderToExtractTo):
    zip_ref = zipfile.ZipFile(pathAndFilename, 'r')
    zip_ref.extractall(folderToExtractTo)
    zip_ref.close()

def CreateDHCPFile(fStaticIP, fEthernet, strStaticIP, strDefaultGateway, strDnsServer):
    try:
        strToWrite = "hostname\nclientid\npersistent\noption rapid_commit\noption domain_name_servers, domain_name, domain_search, host_name\noption classless_static_routes\noption ntp_servers\noption interface_mtu\nrequire dhcp_server_identifier\nslaac private\n"
        if (fStaticIP):
            if (fEthernet):
                strToWrite += "interface eth0\n"
            else:
                strToWrite += "interface wlan0\n"
            strToWrite += "static ip_address=" + strStaticIP + "/24\n"
            strToWrite += "static routers=" + strDefaultGateway + "\n"
            strToWrite += "static domain_name_servers=" + strDnsServer + "\n"
                
        WriteStringToFile("/home/pi/Documents/YoloV3IntelVinuEC/", "dhcpcd.conf", strToWrite)
    except:
        printDebug("Issue in creating file: " + CreateDHCPFile)


def WriteJsonToPathFile(strPath, strFilename, jsonData):
    fSuccess = False
    # Write JSON file
    try:
        if not os.path.exists(strPath):
            os.makedirs(strPath)
        with io.open(strPath + strFilename, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(jsonData,
                            indent=4, sort_keys=True,
                            separators=(',', ': '), ensure_ascii=False)
            outfile.write(str_)
            outfile.close()
            fSuccess = True
    except Exception as ex:
        print("Exception in WriteJsonToPathFile : " + str(ex))
    return(fSuccess)


def WriteJsonToFile(strFilename, jsonData):
    fSuccess = False
    # Write JSON file
    try:
        with io.open(strFilename, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(jsonData,
                            indent=4, sort_keys=True,
                            separators=(',', ': '), ensure_ascii=False)
            outfile.write(str_)
            outfile.close()
            fSuccess = True
    except Exception as ex:
        print("Exception in WriteJsonToFile : " + str(ex))
    return(fSuccess)

def DeleteFile(strPathFilename):
    try:
        os.remove(strPathFilename)
    except:
        print("File does not exist:" + strPathFilename)


def ReadJsonFromFile(strPathFilename):
    jsonData = {}
    try: 
        with io.open(strPathFilename, 'r') as inputfile:
            #jsonData = inputfile.read()
            jsonData = json.load(inputfile)
            inputfile.close()
    except Exception as ex:
        print("Exception in ReadJsonFromFile:" + str(ex))
    return(jsonData)

def WriteLocalNumbersToDisk(strAccountName, iGlobalDetectionsEventNumber, iGlobalLiveImageNumber):
    fSuccess = False
    try:
        strPathFilename = "LocalNumbers_" +  strAccountName  + ".json"
        jsonLocalNumbers = {}
        jsonLocalNumbers["NumberOfEvents"] = iGlobalDetectionsEventNumber
        jsonLocalNumbers["LiveEventLastImageNum"] = iGlobalLiveImageNumber
        fSuccess = WriteJsonToFile(strPathFilename, jsonLocalNumbers)
    except Exception as ex:
        printDebug("Exception in WriteLocalNumbersToDisk : " + str(ex))
    return(fSuccess)

def ReadLocalNumbersFromDisk(strAccountName):
    fSuccess = False
    iGlobalDetectionsEventNumber = 1
    iGlobalLiveImageNumber = 1
    try:
        strPathFilename = "LocalNumbers_" + strAccountName + ".json"
        jsonLocalNumbers = ReadJsonFromFile(strPathFilename)
        if (jsonLocalNumbers != {}):
            iGlobalDetectionsEventNumber = jsonLocalNumbers["NumberOfEvents"]
            iGlobalLiveImageNumber = jsonLocalNumbers["LiveEventLastImageNum"]
            fSuccess = True
    except Exception as ex:
        printDebug("Exception in ReadLocalNumbersToDisk : " + str(ex))
    return(fSuccess, iGlobalDetectionsEventNumber, iGlobalLiveImageNumber)


def ReadLocalConfigFromDisk(strAccountName):
    iCounter = 0
    strJsonConfig = {}
    try:
        strPathFilename = "Config_" + strAccountName + ".json"
        strJsonConfig = ReadJsonFromFile(strPathFilename)
        if (strJsonConfig != {}):
            iCounter = strJsonConfig["Counter"]
    except Exception as ex:
        printDebug("Exception in ReadLocalConfigFromDisk : " + str(ex))

    return(strJsonConfig, iCounter)
                    

def WriteLocalConfigJsonToDisk(strAccountName, strJsonConfig, iCounter):
    fSuccess = False
    try:
        strPathFilename = "Config_" + strAccountName + ".json"
        strJsonConfig["Counter"] = iCounter
        fSuccess = WriteJsonToFile(strPathFilename, strJsonConfig)
    except Exception as ex:
        printDebug("Exception in WriteLocalConfigJsonToDisk : " + str(ex))
    return(fSuccess)

def PrintBinInHex(strName, binVal):
    strHexVal = ""
    for byteVal in binVal:
        strHexVal += hex(byteVal) + ","
    print(strName + " = " + strHexVal)    