# Scenera SceneMode Processing Version 1.0 2020-08-22
import json
from RestAPI import RestAPIPost
from PythonUtils import printDebug, GetDateTime
import threading
import time


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

class SceneModeConfigClass:
    CustomAnalysisStage = ""
    AnalysisRegion = []

class AnalysisRegionClass:
    XCoord = 0
    YCoord = 0

class SceneMarkOutputListClass:
    AppEndPoint = None
    NetEndPoint = None

def GetSceneMode(API_ENDPOINT, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, strAccessToken):  
    objSceneMode = None

    try:
        dictPayload = { "DeviceID": strBrigdeUUID }

        SourceEndPointID = strBrigdeUUID
        DestinationEndPointID = strCloudServerUUID

        strCommandType =  "GetSceneMode"
        jsonCMP = CreateCMFHeadersSceneMode(dictPayload, SourceEndPointID, DestinationEndPointID, NodeID, PortID, strAccessToken, strCommandType)
        #print(str(jsonCMP))
        
        dictReturn = RestAPIPost(API_ENDPOINT, jsonCMP) ###AJ@@@[For Scenera Pipeline]
        dictSceneMode = dictReturn.get("Payload")
        jsonSceneMode = json.dumps(dictSceneMode)
        #printDebug("####== " + str(jsonSceneMode))

        if dictSceneMode:
            objSceneMode = ProcessSceneMode(dictSceneMode)
        
    except Exception as ex:
        pass
        #print("Exception in SceneMode -> GetSceneMode : " + str(ex)) 

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


        listOfInputs = dictSMode.get("Inputs")
        for item in listOfInputs:
            objInputs = InputClass()
            objInputs.Type = item.get("Type")
            dictVideoEndPoint = item.get("VideoEndPoint")
            objVideoEndPointClass = VideoEndPointClass()
            objVideoEndPointClass.VideoURL = dictVideoEndPoint.get("VideoURI")
            objInputs.VideoEndPointClass = objVideoEndPointClass
            objSceneMode.Inputs.append(objInputs)


        listOfOutputs = dictSMode.get("Outputs")
        for item in listOfOutputs:
            objOutputs = OutputsClass()
            objOutputs.Type = item.get("Type")
            objOutputs.PortID = item.get("PortID")

            listDestinationEndPointList = item.get("DestinationEndPointList")
            for itemDestinationEndPointList in listDestinationEndPointList:
                objDestinationEndPointList = DestinationEndPointListClass()
                
                dictAppEndPoint = itemDestinationEndPointList.get("AppEndPoint")
                objAppEndPointClass = AppEndPointClass()
                objAppEndPointClass.APIVersion = dictAppEndPoint.get("APIVersion")
                objAppEndPointClass.EndPointID = dictAppEndPoint.get("EndPointID")
                objAppEndPointClass.AccessToken = dictAppEndPoint.get("AccessToken")
                objDestinationEndPointList.AppEndPoint = objAppEndPointClass

                
                dictNetEndPoint = itemDestinationEndPointList.get("NetEndPoint")
                objNetEndPointClass = NetEndPointClass()
                objNetEndPointClass.APIVersion = dictNetEndPoint.get("APIVersion")
                objNetEndPointClass.EndPointID = dictNetEndPoint.get("EndPointID")
                
                listScheme = dictNetEndPoint.get("Scheme")
                for itemScheme in listScheme:
                    objScheme = SchemeClass()
                    objScheme.Protocol = itemScheme.get("Protocol")
                    objScheme.Authority = itemScheme.get("Authority")
                    objScheme.Role = itemScheme.get("Role")
                    objScheme.AccessToken = itemScheme.get("AccessToken")
                    objNetEndPointClass.Scheme.append(objScheme)

                objDestinationEndPointList.NetEndPoint = objNetEndPointClass
                
                objOutputs.DestinationEndPointList.append(objDestinationEndPointList)

            objSceneMode.Outputs.append(objOutputs)
        
        distMode = dictSMode.get("Mode")
        objMode = ModeClass()

        objMode.SceneMode = distMode["SceneMode"]
        listSceneModeConfig = distMode["SceneModeConfig"]
        for item in listSceneModeConfig:
            objSceneModeConfig = SceneModeConfigClass()
            objSceneModeConfig.CustomAnalysisStage = item["CustomAnalysisStage"]
            # Add Region processing 
            listAnalysisRegion = item["AnalysisRegion"]
            for itemRegion in listAnalysisRegion:
                dictRegion = itemRegion
                XCoord = dictRegion["XCoord"]
                YCoord = dictRegion["XCoord"]
                objAnalysisRegionClass = AnalysisRegionClass()
                objAnalysisRegionClass.XCoord = XCoord
                objAnalysisRegionClass.XCoord = YCoord
                objSceneModeConfig.AnalysisRegion.append(objAnalysisRegionClass)

            objMode.SceneModeConfig.append(objSceneModeConfig)

        listMarkOutputList =  distMode["SceneMarkOutputList"]
        for item in listMarkOutputList:
            objSceneMarkOutputListClass = SceneMarkOutputListClass()
            dictAppEndPoint = item.get("AppEndPoint")
            objAppEndPointClass = AppEndPointClass()
            objAppEndPointClass.APIVersion = dictAppEndPoint.get("APIVersion")
            objAppEndPointClass.EndPointID = dictAppEndPoint.get("EndPointID")
            objAppEndPointClass.AccessToken = dictAppEndPoint.get("AccessToken")
            objSceneMarkOutputListClass.AppEndPoint = objAppEndPointClass

            dictNetEndPoint = item.get("NetEndPoint")
            objNetEndPointClass = NetEndPointClass()
            objNetEndPointClass.APIVersion = dictNetEndPoint.get("APIVersion")
            objNetEndPointClass.EndPointID = dictNetEndPoint.get("EndPointID")
            
            listScheme = dictNetEndPoint.get("Scheme")
            for itemScheme in listScheme:
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




