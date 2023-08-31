import requests 
import threading
from PythonUtils import printDebug, WriteJsonToPathFile, WriteStringToPathFile
import json
from PythonUtils import printDebug
import time
import sys

incValue = 0
fStillBusySendLiveImagestoCloud = False

fWriteDebugtoDisk = False
iWriteSeqNumber = 0
strDebugPath = "c:\\Scenera_Json\\"

semRequest = threading.Semaphore()

def RstAPIGetFiles(API_ENDPOINT, PARAMS):
    global semRequest
    semRequest.acquire()
    iRetryCount = 0
    while True:
        try:
            r = requests.get(url = API_ENDPOINT, params = PARAMS, timeout = 60) 
            data = r.json() 
            retFiles = { "Status" : "Success", "Files" : data}
            break
        except Exception as ex:
            iRetryCount += 1
            printDebug("Exception in RstAPIGet :" + str(ex) )
            retFiles = { "Status" : "Timeout"}
        if (iRetryCount > 3):
            break
    semRequest.release()   
    return(retFiles)

  
def RstAPIGet(API_ENDPOINT, PARAMS):
    global semRequest
    semRequest.acquire()
    data = {}
    iRetryCount = 0
    while True:
        try:
            r = requests.get(url = API_ENDPOINT, params = PARAMS, timeout = 60) 
            data = r.json() 
            break
        except Exception as ex:
            iRetryCount += 1
            printDebug("Exception in RstAPIGet :" + str(ex) )
        if (iRetryCount > 3):
            break

    semRequest.release()
    return(data)

def RestAPIGetBin(API_ENDPOINT, PARAMS):
    global semRequest
    semRequest.acquire()
    data = 0
    iRetryCount = 0
    while True:
        try:
            headers = {'Content-type': 'application/octet-stream'}
            r = requests.get(url = API_ENDPOINT, params = PARAMS, headers=headers, timeout = 300) 
            data = r.content
            break
        except Exception as ex:
            iRetryCount += 1
            #printDebug("Exception in RestAPIGetBin :" + str(ex) )
        if (iRetryCount > 3):
            break
    semRequest.release() 
    return(data)    
  
def RestAPIPost(API_ENDPOINT, data):
    global semRequest
    semRequest.acquire()
    retval = {}
    iRetryCount = 0
    while True:
        try:
            headers = {'Content-type': 'application/json'}
            print("#### RestAPIPost ", API_ENDPOINT,data)
            r = requests.post(url = API_ENDPOINT, json = data, headers=headers, timeout = 120, verify=False)  
            retval = r.json() 
            print("##### DATA SIZE #####",sys.getsizeof(retval))
            break
        except Exception as ex:
            iRetryCount += 1
            printDebug("Exception in RestAPIPost :" + str(ex),"#####")


        if (iRetryCount > 3):
            status_f = open("status.dat","w")
            status_f.write("3")
            status_f.close()
            break
    semRequest.release()   
    return(retval)

def RestAPIPost_With_AccessToken_FirmWare(API_ENDPOINT, data, strAccessToken):
    global semRequest
    semRequest.acquire()
    retval = {}
    iRetryCount = 0

    while True:
        try:
            headers = {'Authorization': strAccessToken,'Accept': '*/*'}
            #print("####### RestAPIPost_With_AccessToken", headers)


            r = requests.post(url = API_ENDPOINT, json = data, headers=headers, timeout = 120, verify=False)  
            retval = r.json() 
            #print("### RESTAPI",r)
            #print("##### DATA SIZE #####",sys.getsizeof(retval))
            break
        except Exception as ex:
            iRetryCount += 1
            #printDebug("Exception in RestAPIPost :" + str(ex),"#####")


        if (iRetryCount > 3):
            status_f = open("status.dat","w")
            status_f.write("3")
            status_f.close()
            break
    semRequest.release()   
    return(retval)


def RestAPIPost_With_AccessToken(API_ENDPOINT, data, strAccessToken):
    global semRequest
    semRequest.acquire()
    retval = {}
    iRetryCount = 0

    while True:
        try:
            headers = {'Authorization': 'Bearer ' + strAccessToken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'}
            #print("####### RestAPIPost_With_AccessToken", headers)
            r = requests.post(url = API_ENDPOINT, json = data, headers=headers, timeout = 120, verify=False)  
            print("###====================> RESTAPI Start",r,API_ENDPOINT)
            retval = r.json() 
            print("###====================> RESTAPI End",r,API_ENDPOINT)
            #print("##### DATA SIZE #####",sys.getsizeof(retval))
            break
        except Exception as ex:
            iRetryCount += 1
            #printDebug("Exception in RestAPIPost :" + str(ex),"#####")


        if (iRetryCount > 3):
            status_f = open("status.dat","w")
            status_f.write("3")
            status_f.close()
            break
    semRequest.release()   
    return(retval)

def RestAPIGet_With_AccessToken(API_ENDPOINT, data, strAccessToken):
    global semRequest
    semRequest.acquire()
    retval = {}
    iRetryCount = 0

    while True:
        try:
            headers = {'Authorization':'Bearer ' + strAccessToken}
            #print("####### RestAPIGet_With_AccessToken", headers)

            r = requests.get(url = API_ENDPOINT, headers=headers, timeout = 120, verify=False)  
            #print("#### RESPONSE",API_ENDPOINT,r)
            retval = r.json() 
            #print("### RESTAPI",r)
            #print("##### DATA SIZE #####",sys.getsizeof(retval))
            break
        except Exception as ex:
            iRetryCount += 1
            print("Exception in RestAPIGet_With_AccessToken :" + str(ex),"#####")


        if (iRetryCount > 3):
            status_f = open("status.dat","w")
            status_f.write("3")
            status_f.close()
            break
    semRequest.release()   
    return(retval)

def RestAPIPostVideo(API_ENDPOINT, data):
    global semRequest
    semRequest.acquire()
    retval = {}
    iRetryCount = 0
    while True:
        try:
            headers = {'Content-type': 'application/json'}
            r = requests.post(url = API_ENDPOINT, json = data, headers=headers, timeout = 300, verify=False)  
            retval = r.json() 
            break
        except Exception as ex:
            iRetryCount += 1
            printDebug("Exception in RestAPIPostVideo :" + str(ex) )
        if (iRetryCount > 3):
            break
    semRequest.release() 
    return(retval)

# def RestAPISendLiveImageToCloud(strCloudURL, strPassword, strAccountName, objEvent):
#     try:
#         threading.Thread(target=RestAPISendLiveImageToCloudThread, args=(strCloudURL, strPassword, strAccountName, objEvent), daemon=True).start()  
#     except Exception as ex:
#         printDebug("Exception in RestAPI -> RestAPISendLiveImageToCloud :" + str(ex) )


def RestAPISendLiveImageToCloud(strCloudURL, strPassword, strAccountName, objEvent):
    jsonRet = {}
    try:
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/" +  strPassword + "/event"
        data = {"Id":0,"Info": strPassword,"EventNumber": int(objEvent.iEventNumber) ,"ImageNumber": int(objEvent.iImageNumber), "MaxNumberOfImages": int(objEvent.iMaxNumberImages),"Year":objEvent.year,"Month":objEvent.month,"Day":objEvent.day,"Hour":objEvent.hour,"Minute":objEvent.minute,"Second":objEvent.second, "TotalSeconds" : objEvent.totalSeconds,  "label" : objEvent.label, "xmin": objEvent.xmin, "ymin": objEvent.ymin, "xmax": objEvent.xmax, "ymax": objEvent.ymax, "Base64Image": objEvent.strBase64OfImage}    
        jsonRet = RestAPIPost(API_ENDPOINT, data)
    except Exception as ex:
        printDebug("Exception in RetAPISendLiveImageToCloud :" + str(ex) )
    return(jsonRet)

# def RestAPISendEventImageToCloudx(strCloudURL, strPassword, strAccountName, objEvent):
#     try:
#         threading.Thread(target=RestAPISendEventImageToCloudThread, args=(strCloudURL, strPassword, strAccountName, objEvent), daemon=True).start()  
#     except Exception as ex:
#         printDebug("Exception in RestAPI -> RestAPISendEventImageToCloud :" + str(ex) )

def RestAPISendEventImageToCloud(strCloudURL, strPassword, strAccountName, objEvent):
    jsonRet = {}
    try:
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/" +  strPassword + "/event"
        data = {"Id":0,"Info": strPassword,"EventNumber": int(objEvent.iEventNumber) ,"ImageNumber": int(objEvent.iImageNumber), "MaxNumberOfImages": int(objEvent.iMaxNumberImages),"Year":objEvent.year,"Month":objEvent.month,"Day":objEvent.day,"Hour":objEvent.hour,"Minute":objEvent.minute,"Second":objEvent.second, "TotalSeconds" : objEvent.totalSeconds,  "label" : objEvent.label, "xmin": objEvent.xmin, "ymin": objEvent.ymin, "xmax": objEvent.xmax, "ymax": objEvent.ymax, "Base64Image": objEvent.strBase64OfImage}    
        jsonRet = RestAPIPost(API_ENDPOINT, data)
    except Exception as ex:
        printDebug("Exception in RetAPISendEventImageToCloud :" + str(ex) )
    return(jsonRet)

def RestAPISendVideoToCloud(strCloudURL, strPassword, strAccountName, objVideo):
    jsonResponse = {}
    try:
        base64MP4 = objVideo.strBase64OfVideo
        strPathID = objVideo.strPath
        #filename =  "Video_" + str(objVideo.iEventNumber) + "_" + str(objVideo.iVideoNumber) + ".mp4"
        filename = strAccountName + "_" + strPassword + "_" + str(objVideo.iEventNumber) + "_" + str(objVideo.iVideoNumber) + ".mp4"
        dictDataSectionObject = {"FileType":"Video","FileName":filename,"Section":objVideo.iChunkNumber,"LastSection":objVideo.iNumberOfChunks,"SectionBase64":base64MP4,"DataID":"SDT_00000001-5cdd-280b-8002-0df865fd7fca0001_00000001","Version":"1.0","PathURI": strPathID,"HashMethod":"SHA256","OriginalFileHash":"ABCDEFGHIJKLMNO", "VideoEventNumber" : objVideo.iEventNumber, "VideoNumber" : objVideo.iVideoNumber }
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/video"
        jsonResponse = RestAPIPostVideo(API_ENDPOINT, dictDataSectionObject)
        #print(str(jsonResponse))
    except Exception as ex:
        printDebug("Exception in RetAPISendVideoToCloud :" + str(ex) )
    return(jsonResponse)

def RestAPIGetNumbers(strCloudURL, strAccountName):
    global incValue

    retData = {}
    try:
        incValue = incValue + 1
        if (incValue > 10000):
            incValue = 0
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/number/" + str(incValue)
        retData = RstAPIGet(API_ENDPOINT, "") 
    except Exception as ex:
        printDebug("Exception in RetAPIGetNumbers : " + str(ex))
    return(retData)

def RestAPIGetAlarm(strCloudURL, strAccountName, strPassword ):
    global incValue
    
    retData = {}
    try:
        incValue = incValue + 1
        if (incValue > 10000):
            incValue = 0
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/" + strPassword + "/alarm/" + str(incValue) 
        retData = RstAPIGet(API_ENDPOINT, "") 
    except Exception as ex:
        printDebug("Exception in RestAPIGetAlarm : " + str(ex))
    return(retData)

def RestAPIGetConfig(strPassword, strCloudURL, strAccountName):
    global incValue
    
    retData = {}
    try:
        incValue = incValue + 1
        if (incValue > 10000):
            incValue = 0
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strPassword + "/" + strAccountName + "/config/" + str(incValue)  # ###AJ@@@ Changed back to 3 for gen 2 
        retData = RstAPIGet(API_ENDPOINT, "") 
    except Exception as ex:
        printDebug("Exception in RetAPIGetConfig : " + str(ex))

    return(retData)

def RestAPIGetUserInfo(strCloudURL, strAccountName):
    global incValue
    retData = {}
    try:
        incValue = incValue + 1
        if (incValue > 10000):
            incValue = 0
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/userinfo/" + str(incValue)
        retData = RstAPIGet(API_ENDPOINT, "") 
    except Exception as ex:
        printDebug("Exception in RetAPIGetUserInfo : " + str(ex))
        
    return(retData)

def RestAPIGetFileList(strCloudURL, strAccountName):
    global incValue
    retData = []
    try:
        incValue = incValue + 1
        if (incValue > 10000):
            incValue = 0
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/files/" + str(incValue)
        retData = RstAPIGetFiles(API_ENDPOINT, "") 
    except Exception as ex:
        printDebug("Exception in RetAPIGetFileList : " + str(ex))
        
    return(retData)    

def RestAPIGetFile(strCloudURL, strPassword, strAccountName, strFilename):
    global incValue
    retData = {}
    try:
        incValue = incValue + 1
        if (incValue > 10000):
            incValue = 0
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/" + strPassword + "/" + strFilename + "/" + str(incValue)
        retData = RestAPIGetBin(API_ENDPOINT, "")
    except Exception as ex:
        printDebug("Exception in RetAPIGetConfig : " + str(ex))
        
    return(retData)

def RestAPISendStatusToCloud(strCloudURL, strAccountName, strTime, strVersion, strStatus, strIpAddress, strMacAddress, strTemp, strListenForExternalTrigger, iExternalTriggerPort):
    retData = {}
    try:
        API_ENDPOINT = "http://" + strCloudURL + "/api/4/" + strAccountName + "/status"
        data = {"Id":0, "Time" : strTime, "Version" : strVersion, "Status": strStatus, "IpAddress" : strIpAddress, "MacAddress" : strMacAddress, "Temp" : strTemp, "TriggerOnExternal" : strListenForExternalTrigger, "ExternalTriggerPort" : iExternalTriggerPort }
        #printDebug(str(data))
        retData = RestAPIPost(API_ENDPOINT, data)
    except Exception as ex:
        printDebug("Exception in RetAPISendStatusToCloud : " + str(ex))

    return(retData)






    