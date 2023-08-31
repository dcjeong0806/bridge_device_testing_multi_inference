# Scenera SceneMode Processing Version 1.0 2020-08-22
import json
from RestAPI import RestAPIPost,RestAPIPost_With_AccessToken
from PythonUtils import printDebug, GetDateTime
import threading
import time
import sys

from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint
BridgeDeviceConfigVariable = VariableConfigClass()


class SceneModeClass:
    SceneModeID = ""
    NodeID = ""
    Version = "1.0"
    Inputs = []
    Outputs = []
    Mode = None

class InputClass:
    Type = ""
    VideoEndPointClass = None

class VideoEndPointClass:
    VideoURL = ""
    Distance = ""
    CameraFPS = 25
    InferenceFPS = 8
    UseYn = ""

class OutputsClass:
    Type = ""
    PortID = ""
    DestinationEndPointList = []

class DestinationEndPointListClass: 
    AppEndPoint = None
    NetEndPoint = None

class AppEndPointClass:
    APIVersion = ""
    EndPointID = ""
    AccessToken = ""

class NetEndPointClass:
    APIVersion = "" 
    EndPointID = ""
    Scheme = []

class SchemeClass:
    Protocol = ""
    Authority = ""
    AccessToken = ""
    Role = ""

class ModeClass:
    SceneMode = ""
    SceneModeConfig = []
    SceneMarkOutputList = []

class AdditionalInfoClass:
    DetectedRegion = []

class AnalysisResultClass:
    Result = "UnDetected"
    AdditionalInfo = []

class SchedulingClass:
    SchedulingType = ""
    StartTime:"00:00"
    EndTime :"00:00"

class SceneModeConfigClass:
    CustomAnalysisStage = ""
    AnalysisRegion = []
    AnalysisResult = None
    Resolution = "1920x1080"
    Threshold = 0.7
    Scheduling = []

class AnalysisRegionClass:
    XCoord = 0
    YCoord = 0

class SceneMarkOutputListClass:
    AppEndPoint = None
    NetEndPoint = None

class Encryption:
    EncryptionOn = False
    SceneEncryptionKeyID = ""
    PrivacyServerEndPoint = None
    dictEncryption = {}


def GetSceneMode(API_ENDPOINT, strDeviceNodeID, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, strAccessToken):  
    objSceneMode = None
    try:
        dictPayload = { "NodeID": strDeviceNodeID }

        SourceEndPointID = strBrigdeUUID
        DestinationEndPointID = strCloudServerUUID

        strCommandType =  "GetSceneMode"
        jsonCMP = CreateCMFHeadersSceneMode(dictPayload, SourceEndPointID, DestinationEndPointID, NodeID, PortID, strAccessToken, strCommandType)
        #printDebug(str(jsonCMP))
        
        debug_message = ("############## :::sceneDataRequest" + str(jsonCMP))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

        dictReturn = RestAPIPost_With_AccessToken(API_ENDPOINT, jsonCMP, strAccessToken) ###AJ@@@[For Scenera Pipeline]

        result = json.dumps(dictReturn)
        result = json.loads(result)
        
        debug_message = ("############## sceneDataResponse" + str(result))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

        debug_message = (NodeID + ":" + str(result["ReplyStatusCode"]))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

        if(int(result["ReplyStatusCode"]) == 200):
            dictSceneMode = dictReturn.get("Payload")
            #jsonSceneMode = json.dumps(dictSceneMode)
            #printDebug(str(jsonSceneMode))

            objSceneMode = ProcessSceneMode(dictSceneMode)
        
    except Exception as ex:
        pass
        #print("Exception in SceneMode.py -> GetSceneMode : " + str(ex)) 

    return(objSceneMode)




def CreateCMFHeadersSceneMode(jsonBody, SourceEndPointID, DestinationEndPointID, NodeID, PortID, strAccessToken, strCommandType ):
    jsonRequestCMP = {}
    try:
        Version = "1.0"
        MessageType = "request"  
        CommandID = 0
        DateTimeStamp = GetDateTime() 
        jsonRequestCMP = { "Version": Version,"MessageType": MessageType, "SourceEndPointID": SourceEndPointID,"DestinationEndPointID": DestinationEndPointID,"DateTimeStamp": DateTimeStamp,"CommandID": CommandID,"CommandType": strCommandType,"Payload": jsonBody}
    except Exception as ex:
        pass
        #print("Exception in SceneMode -> CreateCMFHeadersSceneMode:" + str(ex))

    return(jsonRequestCMP)


def ProcessSceneMode(dictSMode):
    objSceneMode = None
    try:
        objSceneMode = SceneModeClass()
        objSceneMode.SceneModeID = dictSMode.get("SceneModeID")
        objSceneMode.NodeID = dictSMode.get("NodeID")
        objSceneMode.Version = dictSMode.get("Version")
        objSceneMode.Inputs = None
        objSceneMode.Inputs = []

        listOfInputs = None
        listOfInputs = dictSMode.get("Inputs")
        for item in listOfInputs:
            objInputs = None
            objInputs = InputClass()
            objInputs.Type = item.get("Type")
            dictVideoEndPoint = item.get("VideoEndPoint")
            objVideoEndPointClass = None
            objVideoEndPointClass = VideoEndPointClass()
            objVideoEndPointClass.VideoURL = dictVideoEndPoint.get("VideoURI")
            objVideoEndPointClass.Distance = dictVideoEndPoint.get("Distance")
            objVideoEndPointClass.CameraFPS = dictVideoEndPoint.get("CameraFPS")
            objVideoEndPointClass.InferenceFPS = dictVideoEndPoint.get("InferenceFPS")
            objVideoEndPointClass.UseYn = dictVideoEndPoint.get("UseYn")
            objInputs.VideoEndPointClass = objVideoEndPointClass       
            objSceneMode.Inputs.append(objInputs)
        listOfOutputs = None
        listOfOutputs = dictSMode.get("Outputs")
        for item in listOfOutputs:
            objOutputs = None
            objOutputs = OutputsClass()
            objOutputs.Type = item.get("Type")
            objOutputs.PortID = item.get("PortID")
            listDestinationEndPointList = None
            listDestinationEndPointList = item.get("DestinationEndPointList")
            for itemDestinationEndPointList in listDestinationEndPointList:
                objDestinationEndPointList = None
                objDestinationEndPointList = DestinationEndPointListClass()
                
                dictAppEndPoint = itemDestinationEndPointList.get("AppEndPoint")
                objAppEndPointClass = None
                objAppEndPointClass = AppEndPointClass()
                objAppEndPointClass.APIVersion = dictAppEndPoint.get("APIVersion")
                objAppEndPointClass.EndPointID = dictAppEndPoint.get("EndPointID")
                objAppEndPointClass.AccessToken = dictAppEndPoint.get("AccessToken")
                #print("objAppEndPointClass:::::::",objAppEndPointClass.AccessToken)
                objDestinationEndPointList.AppEndPoint = None
                objDestinationEndPointList.AppEndPoint = objAppEndPointClass

                
                dictNetEndPoint = itemDestinationEndPointList.get("NetEndPoint")
                objNetEndPointClass = None
                objNetEndPointClass = NetEndPointClass()
                objNetEndPointClass.APIVersion = dictNetEndPoint.get("APIVersion")
                objNetEndPointClass.EndPointID = dictNetEndPoint.get("EndPointID")
                listScheme = None
                listScheme = dictNetEndPoint.get("Scheme")
                objNetEndPointClass.Scheme = None 
                objNetEndPointClass.Scheme = []
                for itemScheme in listScheme:
                    objScheme = SchemeClass()
                    objScheme.Protocol = itemScheme.get("Protocol")
                    objScheme.Authority = itemScheme.get("Authority")
                    objScheme.Role = itemScheme.get("Role")
                    objScheme.AccessToken = itemScheme.get("AccessToken")
                    objNetEndPointClass.Scheme.append(objScheme)
                objDestinationEndPointList.NetEndPoint = None
                objDestinationEndPointList.NetEndPoint = objNetEndPointClass
                
                objOutputs.DestinationEndPointList.append(objDestinationEndPointList)

            objSceneMode.Outputs.append(objOutputs)
        
        distMode = dictSMode.get("Mode")
        objMode = ModeClass()

        objMode.SceneMode = distMode["SceneMode"]
        listSceneModeConfig = distMode["SceneModeConfig"]



        #for item in listSceneModeConfig:
        #    if(item["CustomAnalysisStage"] == "Loitering"):
        #        item["CustomAnalysisStage"] = "Animal"
        '''
        objMode.SceneModeConfig = []
        for item in listSceneModeConfig:
            objSceneModeConfig = SceneModeConfigClass()
            objSceneModeConfig.CustomAnalysisStage = item["CustomAnalysisStage"]
            # Add Region processing 
            listAnalysisRegion = item["AnalysisRegion"]
            objSceneModeConfig.AnalysisRegion = []
            for itemRegion in listAnalysisRegion:
                dictRegion = itemRegion
                XCoord = dictRegion["XCoord"]
                YCoord = dictRegion["YCoord"]
                objAnalysisRegionClass = AnalysisRegionClass()
                objAnalysisRegionClass.XCoord = XCoord
                objAnalysisRegionClass.YCoord = YCoord
                objSceneModeConfig.AnalysisRegion.append(objAnalysisRegionClass)
            
            objSceneModeConfig.Threshold = item["Threshold"]
            objSceneModeConfig.Resolution = item["Resoultion"]
            for scheduleInfo in item["Scheduling"]:
                schedule = {
                    "SchedulingType":scheduleInfo["SchedulingType"],
                    "StartTime":scheduleInfo["StartTime"],
                    "EndTime":scheduleInof["EndTime"]
                }

                objSceneModeConfig.Scheduling.append(schedule)

            objSceneModeConfig.AnalysisResult = {
                "Result":"UnDetected",
                "AdditionalInfo":[]
            }

            objMode.SceneModeConfig.append(objSceneModeConfig)
        '''
        objMode.SceneModeConfig = listSceneModeConfig
        listMarkOutputList = None
        listMarkOutputList = distMode["SceneMarkOutputList"]
        objMode.SceneMarkOutputList = None
        objMode.SceneMarkOutputList = []
        for item in listMarkOutputList:
            objSceneMarkOutputListClass = None
            objSceneMarkOutputListClass = SceneMarkOutputListClass()
            dictAppEndPoint = item.get("AppEndPoint")
            objAppEndPointClass = None
            objAppEndPointClass = AppEndPointClass()
            objAppEndPointClass.APIVersion = dictAppEndPoint.get("APIVersion")
            objAppEndPointClass.EndPointID = dictAppEndPoint.get("EndPointID")
            objAppEndPointClass.AccessToken = dictAppEndPoint.get("AccessToken")
            objSceneMarkOutputListClass.AppEndPoint = None
            objSceneMarkOutputListClass.AppEndPoint = objAppEndPointClass

            dictNetEndPoint = item.get("NetEndPoint")
            objNetEndPointClass = None
            objNetEndPointClass = NetEndPointClass()
            objNetEndPointClass.APIVersion = dictNetEndPoint.get("APIVersion")
            objNetEndPointClass.EndPointID = dictNetEndPoint.get("EndPointID")
            objNetEndPointClass.Scheme = None
            objNetEndPointClass.Scheme = []
            listScheme = None
            listScheme = dictNetEndPoint.get("Scheme")
            for itemScheme in listScheme:
                objScheme = None
                objScheme = SchemeClass()
                objScheme.Protocol = itemScheme.get("Protocol")
                objScheme.Authority = itemScheme.get("Authority")
                objScheme.Role = itemScheme.get("Role")
                objScheme.AccessToken = itemScheme.get("AccessToken")
                objNetEndPointClass.Scheme.append(objScheme)
            objSceneMarkOutputListClass.NetEndPoint = objNetEndPointClass
            objMode.SceneMarkOutputList.append(objSceneMarkOutputListClass)
        objSceneMode.Mode = objMode

    except Exception as ex:
        objSceneMode = None
        #print("Exception in ProcessSceneMode : " + str(ex)) 

    return(objSceneMode)




