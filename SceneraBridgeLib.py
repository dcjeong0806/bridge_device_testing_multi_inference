import requests 
import threading
from PythonUtils import printDebug, WriteJsonToPathFile, WriteStringToPathFile, GetDateTime
import json
from GenerateNewSceneData import SceneDataValues, CreateSceneData
from RestAPI import RestAPIPost
import time
import threading
from ImageAndVideoClasses import EventClass, EventVideoClass
from SceneMode import GetSceneMode

from GenerateNewScenemark import CreateSceneMark, SceneMarkValues   

incValue = 0
fStillBusySendLiveImagestoCloud = False

NodeID = 1   
PortID = 1234   
strBrigdeUUID = "00000001-5cdd-280b-8002-00010000f3e0"  # "00000001-5cdd-280b-8002-0df865fd7fca"   #str(uuid.uuid4())  ###AJ@@@[Scenera Only] 
strCloudServerUUID = "00000001-5cdd-280b-8003-00020000ffff" ###AJ@@@[Scenera Only] 
strAccessTokenController = ""
API_ENDPOINT_CONTROLER = "http://controllerapp.azurewebsites.net/api/GetDeviceSceneMode"

strAccessToken = ""  

fTokenProcessIsRunning = False
fGetSceneModeProcessIsRunning = False
fDebugSendToMSPipeLine = False


strGlobalSceneMarkEndPoint = ""
strGlobalSceneMarkToken = ""
strGlobalSceneMarkAuthority = ""

strGlobalSceneDataImageEndPoint = ""
strGlobalSceneDataImageToken = ""
strGlobalSceneDataImageAuthority = ""

strGlobalSceneDataVideoEndPoint = ""
strGlobalSceneDataVideoToken = ""
strGlobalSceneDataVideoAuthority = ""



fWriteDebugtoDisk = False
iWriteSeqNumber = 0
strDebugPath = "c:\\Scenera_Json\\"


def DeviceNodeID(strUUID, NodeID):
    hexNodeID = hex(NodeID)[2:]
    hexNodeIDPadded =  hexNodeID.zfill(4)
    DeviceNodeID = strUUID + "_" + hexNodeIDPadded
    return(DeviceNodeID)

def DevicePortID(strUUID, NodeID, PortID):
    hexNodeID = hex(NodeID)[2:]
    hexNodeIDPadded =  hexNodeID.zfill(4)
    hexPortID =  hex(PortID)[2:]
    hexPortIDPadded =  hexPortID.zfill(4)
    DevicePortID = strUUID + "_" + hexNodeIDPadded + "_" + hexPortIDPadded
    return(DevicePortID)

def CreateSceneMarkID(Instance):
    global NodeID
    global strBrigdeUUID

    strDeviceNodeID = DeviceNodeID(strBrigdeUUID, NodeID)
    hexInstance = hex(Instance)[2:]
    hexInstancePadded = hexInstance.zfill(8)
    SceneMarkID = "SMK_" + strDeviceNodeID + "_" + hexInstancePadded
    return(SceneMarkID)

def CreateSceneDataID(Instance):
    global NodeID
    global strBrigdeUUID

    strDeviceNodeID = DeviceNodeID(strBrigdeUUID, NodeID)
    hexInstance = hex(Instance)[2:]
    hexInstancePadded = hexInstance.zfill(8)
    SceneDataID = "SDT_" + strDeviceNodeID + "_" + hexInstancePadded
    return(SceneDataID)


def StartSceneLibraryProcesses():
    try:
        #StartTokenProcess()
        StartGetSceneModeProcess()
    except Exception as ex:
        printDebug("Exception in SceneraBridgeLib -> StartSceneProcesses :" + str(ex))  


def StartGetSceneModeProcess():
    global fGetSceneModeProcessIsRunning
    try:
        if not fGetSceneModeProcessIsRunning:
            fGetSceneModeProcessIsRunning = True
            threadGetSceneModeThread = threading.Thread(target=GetSceneModeThread, args=(), daemon=True)
            threadGetSceneModeThread.start()
    except Exception as ex:
        printDebug("Exception in SceneraBridgeLib -> StartGetSceneModeProcess :" + str(ex))

def GetVideoURL(iIndex):
    global objGlobalGetSceneMode
    strVideoUrl = ""

    try:
        iIndexCount = 0
        for item in objGlobalGetSceneMode.Inputs:
            if (item.Type == "Video"):
                if (iIndex == iIndexCount):
                    strVideoUrl = item.VideoEndPointClass.VideoURL
                    break
                iIndexCount += 1

    except Exception as ex:
        printDebug("Exception in SceneMode -> GetVideoURL :" + str(ex))
    
    return(strVideoUrl)


def GetSceneMarkInfo(objGlobalGetSceneMode):
    strSceneMarkEndPoint = ""
    strSceneMarkToken = ""
    strSceneMarkAuthority = ""

    try:
        listSceneMarkOutput = objGlobalGetSceneMode.Mode.SceneMarkOutputList
        for item in listSceneMarkOutput:
            strSceneMarkEndPoint = item.NetEndPoint.EndPointID
            listScheme = item.NetEndPoint.Scheme
            for itemScheme in listScheme:
                strSceneMarkAuthority = itemScheme.Authority
                strSceneMarkToken = itemScheme.AccessToken
                break

    except Exception as ex:
        printDebug("Exception in SceneMode -> GetSceneMarkEndPointAndToken :" + str(ex))
    
    return(strSceneMarkEndPoint, strSceneMarkToken, strSceneMarkAuthority)


def GetSceneDataInfo(objGlobalGetSceneMode, strType):
    strSceneMarkEndPoint = ""
    strSceneMarkToken = ""
    strSceneMarkAuthority = ""

    try:
        listOutput = objGlobalGetSceneMode.Outputs
        for item in listOutput:
            if (item.Type == strType):
                listDestination = item.DestinationEndPointList
                for itemDest in listDestination:
                    strSceneMarkEndPoint = itemDest.NetEndPoint.EndPointID
                    listScheme = itemDest.NetEndPoint.Scheme
                    for itemScheme in listScheme:
                        strSceneMarkAuthority = itemScheme.Authority
                        strSceneMarkToken = itemScheme.AccessToken
                        break

    except Exception as ex:
        printDebug("Exception in SceneMode -> GetSceneDataInfo :" + str(ex))
    
    return(strSceneMarkEndPoint, strSceneMarkToken, strSceneMarkAuthority)

def GetSceneDataVideoInfo(objGlobalGetSceneMode):
    strSceneMarkEndPoint = ""
    strSceneMarkToken = ""
    strSceneMarkAuthority = ""

    try:
        listOutput = objGlobalGetSceneMode.Outputs
        for item in listOutput:
            if (item.Type == ""):
                listDestination = item.DestinationEndPointList
                for itemDest in listDestination:
                    strSceneMarkEndPoint = itemDest.NetEndPoint.EndPointID
                    listScheme = itemDest.NetEndPoint.Scheme
                    for itemScheme in listScheme:
                        strSceneMarkAuthority = itemScheme.Authority
                        strSceneMarkToken = itemScheme.AccessToken
                        break

    except Exception as ex:
        printDebug("Exception in SceneraModde -> GetSceneMarkEndPointAndToken :" + str(ex))
    
    return(strSceneMarkEndPoint, strSceneMarkToken, strSceneMarkAuthority)




def GetSceneModeThread():
    global API_ENDPOINT_CONTROLER
    global NodeID
    global strBrigdeUUID
    global strCloudServerUUID
    global strAccessTokenController
    global objGlobalGetSceneMode
    global strGlobalSceneMarkEndPoint
    global strGlobalSceneMarkToken
    global strGlobalSceneMarkAuthority
    global strGlobalSceneDataImageEndPoint
    global strGlobalSceneDataImageToken
    global strGlobalSceneDataImageAuthority
    global strGlobalSceneDataVideoEndPoint
    global strGlobalSceneDataVideoToken
    global strGlobalSceneDataVideoAuthority

    while True:
        try:
            objGlobalGetSceneMode = GetSceneMode(API_ENDPOINT_CONTROLER, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, strAccessTokenController)
            strGlobalSceneMarkEndPoint, strGlobalSceneMarkToken, strGlobalSceneMarkAuthority = GetSceneMarkInfo(objGlobalGetSceneMode)
            strGlobalSceneDataImageEndPoint, strGlobalSceneDataImageToken, strGlobalSceneDataImageAuthority = GetSceneDataInfo(objGlobalGetSceneMode,"Image")
            strGlobalSceneDataVideoEndPoint, strGlobalSceneDataVideoToken, strGlobalSceneDataVideoAuthority = GetSceneDataInfo(objGlobalGetSceneMode,"Video")

            #CheckSceneMode()
            #printDebug("GetSceneModeThread")
        except Exception as ex:
            printDebug("Exception in SceneraBridgeLib -> GetSceneModeThread :" + str(ex))

        time.sleep(60*10)  # Get the Token Every 10 Minutes


# def StartTokenProcess():
#     global fTokenProcessIsRunning
#     try:
#         if not fTokenProcessIsRunning:
#             fTokenProcessIsRunning = True
#             threadGetAccessTokenThread = threading.Thread(target=GetAccessTokenThread, args=(), daemon=True)
#             threadGetAccessTokenThread.start()
#     except Exception as ex:
#         printDebug("Exception in SceneraBridgeLib -> StartTokenProcess :" + str(ex))

    
# def GetAccessTokenThread():
#     global strAccessToken

#     while True:
#         try:
#             strAccessToken = GetAccessToken()
#         except Exception as ex:
#             printDebug("Exception in SceneraBridgeLib -> GetAccessTokenThread :" + str(ex))

#         time.sleep(60*10)  # Get the Token Every 10 Minutes


def CreateAndSendSceneMarkAndSceneData(iGlobalDetectionsEventNumber, listObjectsToCloud, iSecondsToRecord,  iVideoEventNumber, objEvent, strGlobalVideoSceneDataID):
    global NodeID 
    global PortID
    global strBrigdeUUID
    global strCloudServerUUID
    global strAccessToken
    
    try:
        objSM = SceneMarkValues()
        strGlobalSceneMarkID = CreateSceneMarkID(iGlobalDetectionsEventNumber)
        objSM.SceneMarkID = strGlobalSceneMarkID
        
        objSM.NodeID = DeviceNodeID(strBrigdeUUID, NodeID)
        objSM.PortID = DevicePortID(strBrigdeUUID, NodeID, PortID)
        objSM.Version = "1.0"
        objSM.SceneMarkStatus = "Active"
        objSM.SceneMode = "Human"
        objSM.Status = "Upload in Progress"
        objSM.CustomAnalysisID =  ""
        objSM.AnalysisDescription = "Yolo v3 configured to detect Human"
        objSM.ProcessingStatus = "Detect"
        objSM.AlgorithmID = "12345678-1234-1234-1234-123456789abc"
    
        objThumbnail = EventClass()
        objSM.CustomItemType = ""
        for item in listObjectsToCloud:
            if (item.label == 'person'):
                objSM.NICEItemType = "Human"
            elif (item.label == 'car') or (item.label == 'truck'):
                objSM.NICEItemType = "Vehicle"
            else:
                objSM.NICEItemType = "Custom"
                objSM.CustomItemType = item.label
            
            objSM.Resolution_Height = item.ymax - item.ymin
            objSM.Resolution_Width = item.xmax - item.xmin
            objSM.XCoordinate = item.xmin
            objSM.YCoordinate = item.ymin
            objThumbnail = item
            objThumbnail.fSendSceneData = True  
            
            break

        iSceneDataInstance = (iGlobalDetectionsEventNumber * 10) + 1
        strGlobalThumbnailSceneDataID = CreateSceneDataID(iSceneDataInstance)
        objSM.Thumbnail_SceneDataID = strGlobalThumbnailSceneDataID
        objThumbnail.strSceneDataID = strGlobalThumbnailSceneDataID
        objThumbnail.strSceneMarkID = strGlobalSceneMarkID

        iSceneDataInstance = (iGlobalDetectionsEventNumber * 10)
        strFullImageSceneDataID = CreateSceneDataID(iSceneDataInstance)
        
        objSM.DetectedObjects_Image_SceneDataID = strFullImageSceneDataID
        objEvent.strSceneDataID = strFullImageSceneDataID
        objEvent.strSceneMarkID = strGlobalSceneMarkID

        objSM.DetectedObjects_Video_SceneDataID = strGlobalVideoSceneDataID

        objSM.DestinationID = strCloudServerUUID
        objSM.SceneDataList_SourceNodeID = DeviceNodeID(strBrigdeUUID, NodeID)
        
        objSM.SceneDataList_Duration = str(iSecondsToRecord)
        objSM.TimeStamp = GetDateTime()       

        objSM.SourceNodeID = DeviceNodeID(strBrigdeUUID, NodeID)
        objSM.SourceNodeDescription = "Scenera Bridge - NVidia Jetson Nano" 

        objSM.Video_Duration = iSecondsToRecord

        objSM.Thumbnail_DataType = "RGBStill"
        objSM.DetectedObjects_Image_DataType = "RGBStill"
        objSM.DetectedObjects_Video_DataType = "RGBVideo"

        objSM.Thumbnail_MediaFormat  = "JPEG"
        objSM.DetectedObjects_Image_MediaFormat = "JPEG"
        objSM.DetectedObjects_Video_MediaFormat = "H.264"

        strPathVideo =  strCloudServerUUID + "/SceneData/Video"  
        strPathImages =  strCloudServerUUID + "/SceneData/Images" 

        objSM.Thumbnail_SceneDataURI = "" 
        objSM.DetectedObjects_Image_SceneDataURI = "" 
        objSM.DetectedObjects_Video_SceneDataURI = "" 

        dictNiceSceneMark = {} #Scenera

        dictNiceSceneMark = CreateSceneMark(objSM)
        threadNiceSendSceneMark = threading.Thread(target=NICESendScenemarkAndSceneDataThread, args=(dictNiceSceneMark, strBrigdeUUID, NodeID, PortID, strAccessToken, objThumbnail,  objEvent, strPathImages), daemon=True)
        threadNiceSendSceneMark.start()
    except Exception as ex:
        printDebug("Exception in SceneraBridgeLib -> CreateAndSendSceneMark :" + str(ex))

    return(strGlobalSceneMarkID)




def CreateCMFHeaders(jsonBody, SourceEndPointID, DestinationEndPointID, NodeID, PortID, strAccessToken, strCommandType ):
    jsonRequestCMP = {}
    try:
        Version = "1.0"
        MessageType = "request"
        DestinationEndPointID = DestinationEndPointID
        SourceEndPointID = SourceEndPointID
        CommandID = 4
        CommandType =  strCommandType
        AccessToken = strAccessToken
        DateTimeStamp = GetDateTime() 
        EncryptionOn = False
        jsonRequestCMP = {"Version": Version, "MessageType": MessageType, "SourceEndPointID": SourceEndPointID , "DestinationEndPointID": DestinationEndPointID, "CommandID" : CommandID , "CommandType" : CommandType, "AccessToken": AccessToken, "DateTimeStamp": DateTimeStamp, "EncryptionOn": EncryptionOn, "Payload":{"Body": jsonBody} }
    except Exception as ex:
        print("Exception in CreateCMFHeaders:" + str(ex))

    return(jsonRequestCMP)

def NICESendScenemarkAndSceneDataThread(dictNiceSceneMark, strBrigdeUUID, NodeID, PortID, strAccessToken, objThumbnail,  objEvent, strPathImages):
    try:
        #SceneMark
        NICERestAPISendSceneMarkToCloud(dictNiceSceneMark, strBrigdeUUID,  NodeID, PortID, strAccessToken)

        #Thumbnail
        NiceRestAPISendImagesToCloud(objThumbnail, strBrigdeUUID, NodeID, PortID, strAccessToken, strPathImages)
        #Full Detected Image 
        NiceRestAPISendImagesToCloud(objEvent, strBrigdeUUID, NodeID, PortID, strAccessToken, strPathImages)   
    except Exception as ex:
        print("Exception in NICESendScenemarkAndSceneDataThread:" + str(ex))

def NICERestAPISendSceneMarkToCloud(dictNiceSceneMark, strBrigdeUUID,  NodeID, PortID, strAccessToken):  
    global fWriteDebugtoDisk
    global iWriteSeqNumber
    global strDebugPath

    jsonResponse = {}
    try:
        jsonSceneMark = json.dumps(dictNiceSceneMark) 
        strCommandType =  "SetSceneMark"
        jsonCMP = CreateCMFHeaders(jsonSceneMark, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, strAccessToken, strCommandType)
        
        SendSceneMarkToMSPipeLine(strAccessToken, jsonCMP) 
      
        if fWriteDebugtoDisk:
            iWriteSeqNumber += 1
            strSceneMarkID = dictNiceSceneMark['SceneMarkID']
            WriteJsonToPathFile(strDebugPath, "SceneMark " + strSceneMarkID + " seq " + str(iWriteSeqNumber)  +".json", jsonCMP)
            
    except Exception as ex:
        printDebug("Exception in SceneraBridge -> NICERestAPISendSceneMarkToCloud :" + str(ex) )
    return(jsonResponse)

def SendSceneMarkToMSPipeLine(strAccessToken, jsonCMP):
    global strGlobalSceneMarkEndPoint
    global strGlobalSceneMarkToken
    global strGlobalSceneMarkAuthority
    global iWriteSeqNumber
    global fDebugSendToMSPipeLine

    # We just add that token to the header. We only need one token for both SceneData and SceneMark, because they are registered as the same service (no need for them to be different).
    header = {'Authorization': 'Bearer ' + strGlobalSceneMarkToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'}
    #printDebug("header=" + str(header))

    scenemark_endpoint = "https://" +  strGlobalSceneMarkAuthority  + "/1.0/" + strGlobalSceneMarkEndPoint  + "/data/0000/0000/setSceneMark"

    payload = json.dumps(jsonCMP)
    #printDebug("payload=" + str(payload))
    answer = requests.post(scenemark_endpoint,data=payload, headers=header, verify=False, stream=False).json() 
    printDebug("SendSceneMarkToMSPipeLine Server " +  scenemark_endpoint + " Answer=" +  str(answer['ReplyStatusCode']))
    
    if fDebugSendToMSPipeLine:
        iWriteSeqNumber += 1
        WriteStringToPathFile(strDebugPath, str(iWriteSeqNumber) + " - endpoint.txt", scenemark_endpoint)
        WriteJsonToPathFile(strDebugPath, str(iWriteSeqNumber) + " - header.json", header)
        WriteJsonToPathFile(strDebugPath, str(iWriteSeqNumber) + " - payload.json", payload)
        WriteStringToPathFile(strDebugPath, str(iWriteSeqNumber) + " - answer.txt", str(answer['ReplyStatusCode']))



def NiceRestAPISendImagesToCloud(objEvent, strBrigdeUUID, NodeID, PortID, strAccessToken, strPathImages):
    global fWriteDebugtoDisk
    global iWriteSeqNumber
    global strDebugPath
    
    jsonResponse = {}
    try:
        base64Image = objEvent.strBase64OfImage
        strPathID = strPathImages
        filename =  "_Image_" + str(objEvent.iEventNumber) + "_" + str(objEvent.iImageNumber) + ".jpg"
        objSD = SceneDataValues()
        objSD.Version = "1.0"
        objSD.DataID = objEvent.strSceneDataID
        objSD.FileType = "Image"
        objSD.FileName = filename
        objSD.PathURI = strPathID
        objSD.Section = 1
        objSD.LastSection = 1
        objSD.HashMethod = "SHA256"
        objSD.OriginalFileHash = "ABCDEFGHIJKLMNO"
        objSD.SectionBase64 = base64Image
        objSD.RelatedSceneMarks = [ objEvent.strSceneMarkID  ]
        #printDebug("SceneDataID = " + objEvent.strSceneMarkID +  "   RelatedSceneMarks = " + objEvent.strSceneMarkID)

        dictDataSectionObject = CreateSceneData(objSD)
            
        
        jsonDataSectionObject = json.dumps(dictDataSectionObject) 
        strCommandType =  "SetSceneData"
        jsonCMP = CreateCMFHeaders(jsonDataSectionObject, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, strAccessToken, strCommandType)
        SendSceneDataImageToMSPipeLine(strAccessToken, jsonCMP)  ###AJ@@@[Microsoft PipeLine]
        #print(str(jsonResponse))
        if fWriteDebugtoDisk:
            iWriteSeqNumber += 1
            WriteJsonToPathFile(strDebugPath, "Image " + objEvent.strSceneDataID + " seq "+ str(iWriteSeqNumber)  +".json", jsonCMP)
            
    except Exception as ex:
        printDebug("Exception in SceneraBridgeLib -> NiceRestAPISendImagesToCloud :" + str(ex) )
    return(jsonResponse)

def SendSceneDataImageToMSPipeLine(strAccessToken, jsonCMP):
    global strGlobalSceneDataImageEndPoint
    global strGlobalSceneDataImageToken
    global strGlobalSceneDataImageAuthority
    global fDebugSendToMSPipeLine
    global iWriteSeqNumber

    try:
        # We just add that token to the header. We only need one token for both SceneData and SceneMark, because they are registered as the same service (no need for them to be different).
        header = {'Authorization': 'Bearer ' + strGlobalSceneDataImageToken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'}

        scenedata_endpoint = "https://"  + strGlobalSceneDataImageAuthority + "/1.0/" + strGlobalSceneDataImageEndPoint  + "/data/0000/0000/setSceneData"
        payload = json.dumps(jsonCMP)
        #print(str(payload))
        answer = requests.post(scenedata_endpoint,data=payload, headers=header, verify=False, stream=False).json() 
        printDebug("SendSceneDataToMSPipeLine Server " + scenedata_endpoint + " reply: " + str(answer['ReplyStatusCode']))
        
        if fDebugSendToMSPipeLine:
            iWriteSeqNumber += 1
            WriteStringToPathFile(strDebugPath, str(iWriteSeqNumber) + " - endpoint.txt", scenedata_endpoint)
            WriteJsonToPathFile(strDebugPath, str(iWriteSeqNumber) + " - header.json", header)
            WriteJsonToPathFile(strDebugPath, str(iWriteSeqNumber) + " - payload.json", payload)
            WriteStringToPathFile(strDebugPath, str(iWriteSeqNumber) + " - answer.txt", str(answer['ReplyStatusCode']))

    except Exception as ex:
        printDebug("Exception in SendSceneDataToMSPipeLine :" + str(ex) )

def SendSceneDataVideoToMSPipeLine(strAccessToken, jsonCMP):
    global strGlobalSceneDataVideoEndPoint
    global strGlobalSceneDataVideoToken
    global strGlobalSceneDataVideoAuthority

    try:
        # We just add that token to the header. We only need one token for both SceneData and SceneMark, because they are registered as the same service (no need for them to be different).
        header = {'Authorization': 'Bearer ' + strGlobalSceneDataVideoToken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'}
        #print(str(header))
 
        scenedata_endpoint = "https://"  + strGlobalSceneDataVideoAuthority + "/1.0/" + strGlobalSceneDataVideoEndPoint  + "/data/0000/0000/setSceneData"
       
        payload = json.dumps(jsonCMP)
        #print(str(payload))
        answer = requests.post(scenedata_endpoint,data=payload, headers=header, verify=False, stream=False).json() 
        printDebug("SendSceneDataToMSPipeLine Server " + scenedata_endpoint + " reply: " + str(answer['ReplyStatusCode']))
    except Exception as ex:
        printDebug("Exception in SendSceneDataToMSPipeLine :" + str(ex) )


def NiceRestAPISendVideoToCloud(strCloudUrl, objVideo, strCreateSceneDataID, listRelatedSceneMarksToVideo):
    global strAccessToken
    global strBrigdeUUID
    global strCloudServerUUID
    global NodeID
    global PortID

    try:
        #printDebug("NiceRestAPISendVideoToCloud")
        threadNiceSendVideoToCloudThread = threading.Thread(target=NiceRestAPISendVideoToCloudThread, args=(objVideo, strCreateSceneDataID, strBrigdeUUID,  NodeID, PortID, strAccessToken, listRelatedSceneMarksToVideo), daemon=True)
        threadNiceSendVideoToCloudThread.start()

    except Exception as ex:
        printDebug("Exception in NiceRestAPISendVideoToCloud :" + str(ex) )


def NiceRestAPISendVideoToCloudThread(objVideo, strCreateSceneDataID, strBrigdeUUID, strNodeID, strPortID, strAccessToken, listRelatedSceneMarksToVideo):
    global fWriteDebugtoDisk
    global iWriteSeqNumber
    global strDebugPath

    jsonResponse = {}
    try:
        base64MP4 = objVideo.strBase64OfVideo
        strPathID =  "/SceneData/Video"   
        filename =  "Video_" + str(objVideo.iEventNumber) + "_" + str(objVideo.iVideoNumber) + ".mp4"
        
        objSD = SceneDataValues()
        objSD.Version = "1.0"
        objSD.DataID = strCreateSceneDataID
        objSD.FileType = "Video"
        objSD.FileName = filename
        objSD.PathURI = strPathID
        objSD.Section = objVideo.iChunkNumber
        objSD.LastSection = objVideo.iNumberOfChunks
        objSD.HashMethod = "SHA256"
        objSD.OriginalFileHash = "ABCDEFGHIJKLMNO"
        objSD.SectionBase64 = base64MP4
        objSD.RelatedSceneMarks = listRelatedSceneMarksToVideo
        

        dictDataSectionObject = CreateSceneData(objSD)
        
        jsonDataSectionObject = json.dumps(dictDataSectionObject) 
        strCommandType =  "SetSceneData"
        jsonCMP = CreateCMFHeaders(jsonDataSectionObject, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, strAccessToken, strCommandType)

        SendSceneDataVideoToMSPipeLine(strAccessToken, jsonCMP)  

        #print(str(jsonResponse))
        if fWriteDebugtoDisk:
            iWriteSeqNumber += 1
            #WriteStringToPathFile(strDebugPath, "Video " +strCreateSceneDataID + " seq " + str(iWriteSeqNumber)  +".txt", API_ENDPOINT)
            WriteJsonToPathFile(strDebugPath, "Video " + strCreateSceneDataID + " seq "+ str(iWriteSeqNumber)  +".json", jsonCMP)
           
    except Exception as ex:
        printDebug("Exception in RetAPISendVideoToCloud :" + str(ex) )
    return(jsonResponse)









