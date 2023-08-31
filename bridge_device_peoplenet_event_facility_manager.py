
#!/usr/bin/env python3

################################################################################
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

# refer site https://blog.naver.com/PostView.nhn?blogId=ambidext&logNo=221673421548&from=search&redirect=Log&widgetTypeCall=true&directAccess=false
from Scenera_GenerateNewScenemark import CreateSceneMark, SceneMarkValues
from Scenera_GenerateNewSceneData import CreateSceneData, SceneDataValues
from BridgeDeviceInfo import CameraMetaInfoClass, parsing_camerainfo, GetCameraID, SceneModeConfigClass, PipeLineInfoClass,check_bridge_device_process,SMDetectedObjectInfo, DetectedMetaInfo, DetectedObjectInfo
from PythonUtils import printDebug, GetFileSizeBytes
from CMFHeaders import CreateCMFHeaders
from Scenera_SceneMode import GetSceneMode
from Scenera_BridgeLib import GetSceneDataInfo, GetSceneMarkInfo, GetSceneDataVideoInfo, GetVideoURL,GetDateTime, DeviceNodeID, DevicePortID, CreateSceneMarkID, CreateSceneDataID
from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID, GetNICELAEndPointAuthority, GetNICELAEndPointEndPoint
from Scenera_ManagementObject import GetManagementObject, GetManagementObjectInfo
from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint

from ctypes import *
import time
import sys
import math
import platform
import json
import threading
from multiprocessing import Process, Queue
import concurrent.futures
import os
import datetime
import cv2
import base64
import calendar

from sys  import getsizeof
import asyncio

import copy
import numpy as np
from tempfile import mkdtemp
import os.path as path

import json
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import matplotlib.path as mpltPath
from shapely.geometry import  Polygon

import pickle 

import shutil
import subprocess
import grpc 
import detectedobject_pb2
import detectedobject_pb2_grpc
import common_pb2
import common_pb2_grpc
import trackedobject_pb2
import trackedobject_pb2_grpc

from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint,decimal_fill
BridgeDeviceConfigVariable = VariableConfigClass()
current_milli_time = lambda: int(round(time.time() * 1000))

import matplotlib.path as mpltPath
from shapely.geometry import  Polygon
import pickle 
import signal



FacilityCheckFrameRatio = [0.7,0.7,0.7,0.7,0.7,0.7,0.7,0.7,0.7,0.7]

class overlaps_contains:
    overlaps = False
    contains = False



def check_confidence(CustomAnalysisStage,sm_meta_info,item):

    #print("##### CustomAnalysisStage.lower()",CustomAnalysisStage.lower(),len(sm_meta_info.detected_object_info_list))


    if(CustomAnalysisStage.lower().startswith("abandonment")):
        for detected_item in sm_meta_info.detected_object_info_list:
            if detected_item.detected_object.lower() == "person" and detected_item.detected_object.lower() == "bag":
                set_confidence = int(item["Threshold"] * 100)
                get_confidence = int(detected_item.confidence * 100) 
                set_confidence = 10
                #if(detected_item.detected_object.lower() == "person"):
                #    set_confidence = 50
                if(set_confidence < get_confidence):  
                    pass
                else:
                    sm_meta_info.detected_object_info_list.remove(detected_item) 
    
    elif CustomAnalysisStage.lower().startswith("animal"):
        for detected_item in sm_meta_info.detected_object_info_list:
            if (detected_item.detected_object.lower() == "dog" or detected_item.detected_object.lower() == "cat"):
                #set_confidence = int(item["Threshold"] * 100)
                #get_confidence = int(detected_item.confidence * 100) 

                ##xxprint("###### CONFIDENCE = " + str(set_confidence) + ":" + str(get_confidence))
                #if(set_confidence < get_confidence):  
                #    pass
                #else:
                sm_meta_info.detected_object_info_list.remove(detected_item) 

    elif CustomAnalysisStage.lower().startswith("loitering"):
        for detected_item in sm_meta_info.detected_object_info_list:
            if detected_item.detected_object.lower() == "person":
                set_confidence = int(item["Threshold"] * 100)
                get_confidence = int(detected_item.confidence * 100) 
                #if(detected_item.detected_object.lower() == "person"):
                #    set_confidence = 40
                ##xxprint("###### CONFIDENCE = " + str(set_confidence) + ":" + str(get_confidence))
                if(set_confidence < get_confidence):  
                    pass
                else:
                    sm_meta_info.detected_object_info_list.remove(detected_item) 
            else:
                sm_meta_info.detected_object_info_list.remove(detected_item) 

    elif CustomAnalysisStage.lower().startswith("falldown"):
        for detected_item in sm_meta_info.detected_object_info_list:
            #print("### ",len(sm_meta_info.detected_object_info_list),sm_meta_info.frame_num,detected_item.detected_object,detected_item.top,detected_item.left,detected_item.width,detected_item.height)
            if detected_item.detected_object.lower() == "person":
                set_confidence = int(item["Threshold"] * 100)
                get_confidence = int(detected_item.confidence * 100) 
                #if(detected_item.detected_object.lower() == "person"):
                set_confidence = 10
                #print("###### FALLDOWN CONFIDENCE = " + str(set_confidence) + ":" + str(get_confidence))
                if(set_confidence < get_confidence):  
                    pass
                else:
                    sm_meta_info.detected_object_info_list.remove(detected_item) 
            else:
                sm_meta_info.detected_object_info_list.remove(detected_item) 
        
    else:
        for detected_item in sm_meta_info.detected_object_info_list:
            if detected_item.detected_object.lower() == "person":
                set_confidence = int(item["Threshold"] * 100)
                get_confidence = int(detected_item.confidence * 100) 
                #if(detected_item.detected_object.lower() == "person"):
                #    set_confidence = 10
                ##xxprint("###### CONFIDENCE = " + str(set_confidence) + ":" + str(get_confidence))
                if(set_confidence < get_confidence):  
                    pass
                else:
                    sm_meta_info.detected_object_info_list.remove(detected_item) 
            else:
                sm_meta_info.detected_object_info_list.remove(detected_item) 

def check_schedule(item,sm_meta_info):
    whatdayistoday = datetime.datetime.now().weekday()
    IsSkipSceneMarkProcessing = False
    if(item["CustomAnalysisStage"] != "NewSceneMode"):
        item["AnalysisResult"]["AdditionalInfo"] = []
        for item2 in item["Scheduling"]:
            Scheduling = item2
            SchedulingType = Scheduling["SchedulingType"]
            ##xxprint("SchedulingType = " + str(whatdayistoday) + SchedulingType)
            if(whatdayistoday >= 0 and whatdayistoday < 5 and SchedulingType == "ScheduledWeekDay"):
                StartTime = int(Scheduling["StartTime"].replace(":",""))
                EndTime = int(Scheduling["EndTime"].replace(":",""))
                detectedtime = int(datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time)).strftime("%H%M"))
                ##xxprint("detected time = " + str(sm_meta_info.detected_time) + ":" + ":::" + str(detectedtime) + ":::" + datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time)).strftime("%Y-%m-%d %H:%M"))
                detectedtime = int(detectedtime)
                if EndTime < StartTime:
                    if detectedtime >=0 and detectedtime <= EndTime:
                        detectedtime = detectedtime + 2400
                    EndTime = EndTime + 2400
                
                ##xxprint("######3333333 {} : DetectedTime :{} StartTime : {}, EndTime : {} , SchedulingType : {} ".format(str(whatdayistoday),str(detectedtime),str(StartTime),str(EndTime),SchedulingType))

                if StartTime < detectedtime and EndTime > detectedtime:
                    IsSkipSceneMarkProcessing = True
                    ##xxprint("######111111 {} : DetectedTime :{} StartTime : {}, EndTime : {} , SchedulingType : {} ".format(str(whatdayistoday),str(detectedtime),str(StartTime),str(EndTime),SchedulingType))
                    break
            elif(whatdayistoday > 4 and whatdayistoday < 7 and SchedulingType == "ScheduledWeekEnd"):
                StartTime = int(Scheduling["StartTime"].replace(":",""))
                EndTime = int(Scheduling["EndTime"].replace(":",""))
                detectedtime = int(datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time)).strftime("%H%M"))
                ##xxprint("#####StartTime : {}, EndTime : {} , DetectedTime : {}, SchedulingType : {} ".format(str(StartTime),str(EndTime),str(detectedtime),SchedulingType))

                if EndTime < StartTime:
                    if detectedtime >=0 and detectedtime <= EndTime:
                        detectedtime = detectedtime + 2400
                    EndTime = EndTime + 2400
                
                ##xxprint("#####22222  {} : StartTime : {}, EndTime : {} , DetectedTime : {}, SchedulingType : {} ".format(str(whatdayistoday),str(StartTime),str(EndTime),detectedtime,SchedulingType))

                if StartTime < detectedtime and EndTime > detectedtime:
                    IsSkipSceneMarkProcessing = True
                    break

        if(IsSkipSceneMarkProcessing == False):
            item["AnalysisResult"]["Result"] = "None"

def speedgate_reduce_box(detected_item):
    #print(detected_item.__dict__)
    detected_item_copy = {}
    x1 = detected_item.x1
    y1 = detected_item.y1
    w = detected_item.width
    h = detected_item.height
    #detected_item_copy['x1'] = x1
    #detected_item_copy['y1'] = y1
    #detected_item_copy['width'] = w
    #detected_item_copy['height'] = h

    detected_item_copy['x1'] = x1 #int(x1 + w * (tailgate_box_ratio/2)) #x1
    detected_item_copy['y1'] = y1 #int(y1 + h * (tailgate_box_ratio/2)) #y1
    detected_item_copy['width'] = int(w * (BridgeDeviceConfigVariable.tailgate_box_ratio))
    detected_item_copy['height'] = int(h * (BridgeDeviceConfigVariable.tailgate_box_ratio))
    #print(f"after modification : {detected_item.__dict__}")

    return detected_item_copy


def send_scenemark_metadata_to_algorithm(sm_meta_info_list):


    sm_meta_info = sm_meta_info_list[0]

    #print("+++++++++++++++++++++++++++++++")
    #print("#### CREATE SCENEMARK ######### = ",sm_meta_info_list[0].camera_info.CameraID,sm_meta_info_list[0].frame_num, len(sm_meta_info_list))
    #print("+++++++++++++++++++++++++++++++")
    #if(len(sm_meta_info.camera_info.SceneModeConfig) > 0): ### Check Schedule
    #    for item in sm_meta_info.camera_info.SceneModeConfig:
    #        check_schedule(item,sm_meta_info)


    '''
    for sm_meta_info_item in sm_meta_info_list: ### Check Meta Info
        if(len(sm_meta_info.camera_info.SceneModeConfig) > 0):
            for item in sm_meta_info.camera_info.SceneModeConfig:                
                CustomAnalysisStage = item["CustomAnalysisStage"]
                if CustomAnalysisStage.lower().startswith("loitering"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("intrusion"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("falldown"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("violence"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("revintrusion"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("facility"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("abandonment"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("speedgate"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)
                elif CustomAnalysisStage.lower().startswith("animal"):
                    check_confidence(CustomAnalysisStage,sm_meta_info_item,item)

                    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    '''
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ########### Analysis in Local with Algorithm Server NextK 
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 1 : loitering , 2:Intrusion , 3:falling , 12: longstay , 40 : Anbandoned , 16 : RevIntrusion

    BridgeDeviceID = sm_meta_info.camera_info.BridgeDeviceID
    ##xxprint("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    ##xxprint("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    ##xxprint(sm_meta_info.detected_time)
    ##xxprint("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    ##xxprint("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    if(len(sm_meta_info_list) > 0):
        Port = 0
        ID = 0
        Resolution = []
        DetectionAreaList = []
        AIServerList = {}
        DetectionArea = []
        
        
        #print("+++++++++++++++++++++++++++++++")
        #print("#### CREATE SCENEMARK ######### = ",sm_meta_info_list[0].camera_info.CameraID,sm_meta_info_list[0].frame_num, len(sm_meta_info_list))
        #print("+++++++++++++++++++++++++++++++")


        try:
            for item in sm_meta_info.camera_info.SceneModeConfig:
                if(item["CustomAnalysisStage"] != "NewSceneMode"):
                    if(item["AIServer"] is not None):
                        ResionOfInterested = [item["CustomAnalysisStage"]]
                        AIServerList[item["AIServer"]["Authority"]] = ResionOfInterested
        except Exception as aiserver_ex:
            pass

        try:
            for config_item in sm_meta_info.camera_info.SceneModeConfig:
                if(config_item["CustomAnalysisStage"] != "NewSceneMode"):
                    EventID = 0
                    if(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.LoiteringKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.LONGSTAY
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]
                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:
                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }

                            #print("############################DetectedAreaDict",DetectedAreaDict)
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1

                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.IntrusionKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":                
                        EventID = BridgeDeviceConfigVariable.INTRUSION
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]
                        ##xxprint("analysis_item" , analysis_item)
                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:
                            ##xxprint("########## === ROI " + json.dumps(item) )
                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1

                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.AbandonmentKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.ABANDONMENT  
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]
                        ##xxprint("analysis_item" , analysis_item)
                        for item in analysis_item:
                            DetectionArea = []
                            
                            for item2 in item["Coords"]:
                            ##xxprint("########## === ROI " + json.dumps(item) )
                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            

                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1
                   
                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.FallDownKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.FALLDOWN   
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]

                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:

                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1
                    
                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.RevIntrusionKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.REVINTRUSION           
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]

                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:

                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1
                    
                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.ViolenceKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.FIGHT           
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]
                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:
                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1
                    
                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.SpeedGateKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.TAILGATE  
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]
                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:
                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1
                    
                    elif(config_item["CustomAnalysisStage"].lower().startswith(BridgeDeviceConfigVariable.TailGateKey)) and config_item["AnalysisResult"]["Result"].lower() == "undetected":
                        EventID = BridgeDeviceConfigVariable.TAILGATE  
                        ScreenSize = config_item["Resolution"].split("x")
                        Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]            
                        analysis_item = config_item["AnalysisRegion"]["ROICoords"]
                        for item in analysis_item:
                            DetectionArea = []
                            for item2 in item["Coords"]:
                                Coordinate = []
                                Coordinate.append(item2["XCoord"])
                                Coordinate.append(item2["YCoord"])
                                DetectionArea.append(Coordinate)
                            
                            DetectedAreaDict = {}
                            DetectedAreaDict = {
                                "ID":ID,
                                "EventType":EventID,
                                "Pts":DetectionArea
                            }
                            AIServerList[config_item["AIServer"]["Authority"]].append(DetectedAreaDict)
                            ID = ID + 1
        
        except Exception as multi_ex:
            debug_message = (":::::: Error Message ::::::" + str(multi_ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
            pass            
        

        is_speedgate = False
        for item in sm_meta_info.camera_info.SceneModeConfig:
            if(item["CustomAnalysisStage"].lower().startswith("speedgate")):
                is_speedgate = True
                break
    

        #print("##########AIServerList",AIServerList)
        for AIServer in AIServerList: ##### GRPC
            StartTime = time.time()
            ##xxprint("####  Start GRPC....")
            #with grpc.insecure_channel("52.231.183.89:40400") as channel:
            with grpc.insecure_channel(AIServer) as channel:
                #print(":::::: ### CONNECTED AI SERVER ::::",AIServer)
                stub = detectedobject_pb2_grpc.DetectedObjectServiceStub(channel)
                CameraID = sm_meta_info.camera_info.camera_id
                #UniqueID = "{}_{}_{}".format(DeviceID,CameraID,tracker_id)
                UniqueID = "{}_{}".format(BridgeDeviceID,CameraID)

                tmp = detectedobject_pb2.DetectedObjectMessage()                
                tmp.deviceid = BridgeDeviceID
                tmp.uid = UniqueID 
                tmp.scenemarkid = ""
                tmp.eventoptions.tailgate.time = BridgeDeviceConfigVariable.tailgate_threshold_time
                
                tmp.resolution.append(int(BridgeDeviceConfigVariable.Resolution_Convert_Width))
                tmp.resolution.append(int(BridgeDeviceConfigVariable.Resolution_Convert_Height))
    
                #for item in DetectionAreaList:
                for i in range(1,len(AIServerList[AIServer])):
                    item = AIServerList[AIServer][i]
                    #print("#### ITEM",item)
                    area = detectedobject_pb2.Area()
                    area.id = (int(item["ID"]))
                    EventID = (int(item["EventType"]))
                    if EventID == BridgeDeviceConfigVariable.LONGSTAY:
                        area.eventtype = common_pb2.EventType.LongStay
                    elif EventID == BridgeDeviceConfigVariable.INTRUSION:
                        area.eventtype = common_pb2.EventType.Intrusion                        
                    elif EventID == BridgeDeviceConfigVariable.ABANDONMENT:
                        area.eventtype = common_pb2.EventType.Abandonded
                    elif EventID == BridgeDeviceConfigVariable.FALLDOWN:
                        area.eventtype = common_pb2.EventType.FallDown    
                    elif EventID == BridgeDeviceConfigVariable.REVINTRUSION:
                        area.eventtype = common_pb2.EventType.LineEnter
                    elif EventID == BridgeDeviceConfigVariable.FIGHT:
                        area.eventtype = common_pb2.EventType.Fight
                    elif EventID == BridgeDeviceConfigVariable.TAILGATE:
                        area.eventtype = common_pb2.EventType.TailGate
                
                    
                    for item2 in item["Pts"]:
                        points = common_pb2.Point()
                        points.x = int(item2[0] / (int(Resolution[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width)))
                        points.y = int(item2[1] / (int(Resolution[1])/int(BridgeDeviceConfigVariable.Resolution_Convert_Height)))
                        area.points.append(points)
                    
                    tmp.area.append(area)    
                ##xxprint("\n================================\n")
                
                TimeToUTC = 9 * 3600
                response = None
                for item in sm_meta_info_list:
                    if(len(item.detected_object_info_list) > 0):
                        detected_list = ""
                        if(len(item.detected_object_info_list) > 0):
                            for detected_item in item.detected_object_info_list:
                                objects = detectedobject_pb2.Object()
                                TimeStamp = datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time) - TimeToUTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                                objects.timestamp = str(detected_item.detected_time_ms)
                                objects.framenumber = (item.frame_num)
                                objects.eventclass = common_pb2.EventClass.person
                                ## SpeedGate -> reduce size of width and height
                                if(is_speedgate):
                                    detected_item_copy = speedgate_reduce_box(detected_item)
                                    objects.x = (detected_item_copy.get('x1'))
                                    objects.y = (detected_item_copy.get('y1'))
                                    objects.width = (detected_item_copy.get('width'))
                                    objects.height = (detected_item_copy.get('height'))
                                    detected_list = detected_list + detected_item.detected_object + " "
                                else:
                                    objects.x = (detected_item.x1)
                                    objects.y = (detected_item.y1)
                                    objects.width = (detected_item.width)
                                    objects.height = (detected_item.height)
                                    detected_list = detected_list + detected_item.detected_object + " "

                                tmp.object.append(objects)     
                if(len(tmp.object) > 0):
                    response = stub.SendDetectedObject(tmp)
                    if(BridgeDeviceConfigVariable.EventPrintLog):
                        print("###################REQUEST DATA START==============================================")
                        print(len(str(tmp.area)), len(str(tmp.object)),len(str(tmp)),tmp)
                        print("###################REQUEST DATA END  ==============================================")
                        print("\n\n")
                    ##xxprint("###### SEND GRPC SERVER\n")
                    EndTime = time.time()
                    #dictNiceSceneMark_NextK = {} #Scenera
                    #dictNiceSceneMark_NextK = GenerateNextKMeta(sm_meta_info_list,BridgeDeviceID,CameraID,EventID,DetectionAreaList,Resolution)

                    #scenemark_nextk = json.dumps(dictNiceSceneMark_NextK)
                    ##xxprint(scenemark_nextk)
                    ##xxprint(scenemark_nextk + "\n")

                    debug_message = "{} : {} : {} : {} : {} : {} : {} : {}".format(sm_meta_info.frame_num,response,len(str(response)),len(str(response.eventinfo)),StartTime,EndTime,EndTime-StartTime,datetime.datetime.now())
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

            #if(response is not None):    
            try:
            #if(response.eventinfo is not None):
                sm_meta_info.DetectedEvent = []
                IsDetected = False
                for item in response.eventinfo:
                    debug_message = ("######## ResultType::::" + str(item.eventtype))
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                    result_type = ""
                    if item.eventtype == BridgeDeviceConfigVariable.LOITERING:
                        result_type = "loitering"
                    elif item.eventtype == BridgeDeviceConfigVariable.INTRUSION:
                        result_type = "intrusion"
                    elif item.eventtype == BridgeDeviceConfigVariable.FALLDOWN:
                        result_type = "falldown"
                    elif item.eventtype == BridgeDeviceConfigVariable.CONGESTION:
                        result_type = "congestion"
                    elif item.eventtype == BridgeDeviceConfigVariable.LONGSTAY:
                        result_type = "longStay"
                    elif item.eventtype == BridgeDeviceConfigVariable.ABANDONMENT:
                        result_type = "abandonded"
                    elif item.eventtype == BridgeDeviceConfigVariable.SPEEDGATE:
                        result_type = "speedgate"
                    elif item.eventtype == BridgeDeviceConfigVariable.TAILGATE:
                        result_type = "tailgate"
                    elif item.eventtype == BridgeDeviceConfigVariable.FIGHT:
                        result_type = "violence"
                    elif item.eventtype == BridgeDeviceConfigVariable.REVINTRUSION:
                        result_type = "revintrusion"

                    start_frame = item.framenumber
                    DetectedEvent = ""
                    FrameStartTime = 0
                    FrameEndTime = 0 

                    if(result_type.lower() == "longstay"):
                        result_type = "loitering"
                    elif result_type.lower() == "abandonded":
                        result_type = "abandonment"
                    elif result_type.lower() == "lineenter":
                        result_type = "revintrusion"
                    elif result_type.lower() == "tailgate":
                        result_type = "speedgate"

                    #print("### RESULT TYPE",result_type,item.eventtype)

                    for check_config_item in sm_meta_info.camera_info.SceneModeConfig:
                        if(check_config_item["CustomAnalysisStage"].lower().startswith("loitering") and result_type.lower() == "loitering"): ##Loitering
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["loitering"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["loitering"][1] == sm_meta_info.camera_info.CameraID) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["loitering"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                FrameStartTime = BridgeDeviceConfigVariable.RecLoitering[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecLoitering[1]                    
                                IsDetected = True
                                DetectedEvent = "Loitering"
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["loitering"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["loitering"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False
                            debug_message = ("\n#######::::: NEXT K0000 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        elif(check_config_item["CustomAnalysisStage"].lower().startswith("intrusion") and result_type.lower() == "intrusion"): ##Intrusion
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["intrusion"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["intrusion"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["intrusion"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                IsDetected = True
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                FrameStartTime = BridgeDeviceConfigVariable.RecIntrusion[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecIntrusion[1]
                                DetectedEvent = "Intrusion"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["intrusion"][0] = int(sm_meta_info.detected_time)
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["intrusion"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False
                            debug_message = ("#######::::: NEXT KKKK11111 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        elif(check_config_item["CustomAnalysisStage"].lower().startswith("abandonment") and result_type.lower() == "abandonment"): ##Abandonment
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["abandonment"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["abandonment"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["abandonment"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                IsDetected = True
                                FrameStartTime = BridgeDeviceConfigVariable.RecAbandonment[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecAbandonment[1]
                                DetectedEvent = "Abandonment"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["abandonment"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["abandonment"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False
                            debug_message = ("\n#######::::: NEXT K22222 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        elif((check_config_item["CustomAnalysisStage"].lower().startswith("falldown") and result_type.lower() == "falldown")): ## FallDown
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["falldown"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["falldown"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["falldown"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                IsDetected = True    
                                FrameStartTime = BridgeDeviceConfigVariable.RecFalldown[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecFalldown[1]
                                DetectedEvent = "Falldown"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["falldown"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["falldown"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False
                            debug_message = ("\n#######::::: NEXT K3333 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        elif((check_config_item["CustomAnalysisStage"].lower().startswith("revintrusion") and result_type.lower() == "revintrusion")): ##RevIntrusion
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["revintrusion"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["revintrusion"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["revintrusion"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                IsDetected = True  
                                FrameStartTime = BridgeDeviceConfigVariable.RecRevIntrusion[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecRevIntrusion[1]
                                DetectedEvent = "RevIntrusion"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["revintrusion"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["revintrusion"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False
                            debut_message = ("\n#######::::: NEXT K4444 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        elif((check_config_item["CustomAnalysisStage"].lower().startswith("speedgate") and result_type.lower() == "speedgate")): 
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["speedgate"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["speedgate"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["speedgate"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                IsDetected = True  
                                FrameStartTime = BridgeDeviceConfigVariable.RecSpeedGate[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecSpeedGate[1]
                                DetectedEvent = "SpeedGate"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["speedgate"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["speedgate"][1] = sm_meta_info.camera_info.CameraID
                     
                            debug_message = ("\n#######::::: NEXT K4444 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        elif((check_config_item["CustomAnalysisStage"].lower().startswith("tailgate") and result_type.lower() == "tailgate")): 
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["tailgate"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["tailgate"][1] == sm_meta_info.camera_info.CameraID) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["tailgate"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                IsDetected = True  
                                FrameStartTime = BridgeDeviceConfigVariable.RecSpeedGate[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecSpeedGate[1]
                                DetectedEvent = "tailgate"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["tailgate"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["tailgate"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False

                            debug_message = ("\n#######::::: NEXT K5555 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
                        elif((check_config_item["CustomAnalysisStage"].lower().startswith("violence") and result_type.lower() == "violence")): ##RevIntrusion
                            if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["violence"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["violence"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["violence"][0]) >= BridgeDeviceConfigVariable.NotificationDelay):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                IsDetected = True  
                                FrameStartTime = BridgeDeviceConfigVariable.RecViolence[0]
                                FrameEndTime = BridgeDeviceConfigVariable.RecViolence[1]
                                DetectedEvent = "violence"
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["violence"][0] = sm_meta_info.detected_time
                                BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["violence"][1] = sm_meta_info.camera_info.CameraID
                            else:
                                check_config_item["AnalysisResult"]["Result"] = "UnDetected"
                                IsDetected = False
                            debut_message = ("\n#######::::: NEXT K4444 AI Result = " + result_type + ":::::::" + check_config_item["CustomAnalysisStage"] + ":::::" + check_config_item["AnalysisResult"]["Result"])
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                for check_config_item_result in sm_meta_info.camera_info.SceneModeConfig:
                    if(check_config_item_result["CustomAnalysisStage"] == "NewSceneMode"):
                        pass
                    else:
                        if check_config_item_result["AnalysisResult"]["Result"] == "None":
                            check_config_item_result["AnalysisResult"]["Result"] = "UnDetected"


                if(IsDetected): 
                    InferenceFPS = int(sm_meta_info.camera_info.InferenceFPS)
                    StartFrame = start_frame - (FrameStartTime * InferenceFPS)
                    EndFrame = start_frame + (FrameEndTime * InferenceFPS)
                    sm_meta_info.FrameDetected = start_frame

                    debug_message = ("############ StartFrame:{} EndFrame:{}".format(StartFrame,EndFrame))
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
        
                    for i in range(StartFrame,EndFrame):
                        image_file  = "{}/{}_{}/{}.jpeg".format(BridgeDeviceConfigVariable.ImageSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(i)).zfill(10))
                        if(os.path.isfile(image_file)):
                            sm_meta_info.full_image_file_name = decimal_fill(i,10) + ".jpeg"
                            sm_meta_info.thumbnail_image_file_name = decimal_fill(i,10) + ".jpeg"
                            break

                    
                    IsUploadTwoImage = False
                    for item in sm_meta_info.camera_info.SceneModeConfig:
                        if item["CustomAnalysisStage"].lower().startswith("facility") and item["AnalysisResult"]["Result"].lower() == "detected":
                            IsUploadTwoImage = True
                            break
                    
                    sm_meta_info.IsUploadTwoImage = IsUploadTwoImage             
                    sm_meta_info.FrameStarted = StartFrame
                    sm_meta_info.FrameEnded = EndFrame
                    sm_meta_info.DetectedEvent.append(DetectedEvent)
                    currenttime = current_milli_time()
                    sm_meta_info.SaveImageDirectory = BridgeDeviceConfigVariable.ImageSaveDirectory
                    sm_meta_info.SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(CameraID), int(currenttime))
                    sm_meta_info.SceneDataThumbnailID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 1)
                    sm_meta_info.SceneDataImageID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 2)
                    sm_meta_info.SceneDataVideoID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 3)
                    sm_meta_info.SceneMarkIsDone = False
                    BridgeDeviceConfigVariable.SceneMarkList.append(sm_meta_info)
                    #print("###################[GENERATE SCENEMARK DATA START$$$$$]  ==============================================")
                    #print(sm_meta_info.SceneMarkID,datetime.datetime.now())
                    #print("###################[[GENERATE SCENEMARK DATA END$$$$$]  ==============================================")
                    #print("\n\n")

            except Exception as resEx:
                debug_message = "::: ERROR MESSAGE ::: " + str(resEx)
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
                pass


def scenemark_metadata_event_manager(CameraID):
    #print("EventManager",CameraID)
    running = True
    while(running):
        try:
            for k in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
                CameraID = str(int(k+1)).zfill(4)
                MetaFileDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.MetaDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                if(os.path.isdir(MetaFileDirectory)):
                    file_list = os.listdir(MetaFileDirectory)
                    file_list.sort()
                    for item in file_list:
                        metadata_file = MetaFileDirectory + "/" + item
                        if os.path.isfile(metadata_file) and os.path.getsize(metadata_file) > 0:
                            StartTime = time.time()
                            with open(metadata_file,"rb") as f:
                                unpickler = pickle.Unpickler(f)
                                sm_meta_info = unpickler.load()
                                send_scenemark_metadata_to_algorithm(sm_meta_info)
                                if(os.path.isfile(metadata_file)):
                                    os.remove(metadata_file)
                            EndTime = time.time()   

                            debug_message = ("META DATA PROCESSING.... {} : {} : {}".format(StartTime,EndTime,EndTime-StartTime))      
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

        except Exception as ex:
            tb = sys.exec_info()
            debug_message = ("#### ERROR Message  scenemark_metadata_event_manager::: " + str(ex) + "::::: line no = " + tb.tb_lineno )
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
            pass    

def create_scenemark_as_file_sync(sm_meta_info):
    ## SceneMark Save
    BridgeDeviceID = sm_meta_info.device_id
    CameraID = sm_meta_info.camera_id 
    NodeID = int(sm_meta_info.camera_id)
    SceneMarkResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneMarkDirectory,BridgeDeviceID,CameraID)
    if not(os.path.isdir(SceneMarkResultDirectory)):
        os.mkdir(SceneMarkResultDirectory)

    SceneMarkID = sm_meta_info.SceneMarkID
    #xxprint("############SceneMark Result Data ",SceneMarkResultDirectory + "/" + SceneMarkID + ".dat")
    with open(SceneMarkResultDirectory + "/" + SceneMarkID + ".dat","wb") as f:
        pickle.dump(sm_meta_info,f)
 
 

def generate_result_scenemark_metadata(detected_object_meta_info):
    while(True):
        while detected_object_meta_info:
            create_scenemark_as_file_sync(detected_object_meta_info.pop(0))
      

### FACILITY 
def person_in_roi(roi=None, person=None):
    #pol = [[100, 100], [300, 100], [300, 300], [100, 300]]
    #points = [(101, 101), (80, 80), (150, 150)]
    # example case (should comment it out!)
    #roi = [[100, 100], [300, 100], [300, 300], [100, 300]]
    #person = [[120, 120], [120, 130], [130, 130], [130, 120]]
    path = mpltPath.Path(roi)
    for point in person:
        inside = path.contains_point(point)
        if not inside:
            return False
    return True

def person_intersect(roi=None, person=None):
    StartTime = time.time()
    #roi = [[700, 500], [1200, 500], [1200, 830], [700, 830]]
    #person = [[852,300],[91,99]]
    # make list of list to list of tuples.. dont comment!

    #print("### ROI",roi)
    #print("### PERSON",person)
    roi = [tuple(l) for l in roi]
    person = [tuple(l) for l in person]
    #print(person)
    # configuring person points
    person_points = [tuple(person[0])]
    #print("####",person_points)
    w = person[1][0] # width
    h = person[1][1] # height
    person_points.append((person[0][0] + w, person[0][1]))
    person_points.append((person[0][0] + w, person[0][1] + h))
    person_points.append((person[0][0], person[0][1] + h))
    result = False
    polygon_roi = Polygon(roi)
    polygon_person = Polygon(person_points)
    result = overlaps_contains()
    if polygon_roi.overlaps(polygon_person) or polygon_roi.contains(polygon_person):
        result.overlaps = True 

    if polygon_roi.contains(polygon_person):
        result.contains = True

    EndTime = time.time()
    #print(person_points,result,str(EndTime-StartTime))
    #
    # print("\n")
    return result

def send_scenemark_fmetadata_to_algorithm(sm_meta_info_list):
    global FacilityCheckFrameRatio

    StartTime = time.time()
    cameraIdx = 0
    roi_index = 0
    sm_info = sm_meta_info_list[0]
    sm_meta_info = sm_info

    if(sm_info.SelfCheckYn == "Y" and True == False):
        BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame = sm_meta_info.frame_num + 2

        if(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame % 2 == 1):
            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame - 1
        sm_meta_info.EndFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame
        
        if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame < 0):
            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = 1
        if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame % 2 == 1):
            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame - 1
        sm_meta_info.StartFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame
        
        sm_meta_info.thumbnail_image_file_name = decimal_fill(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame,10) + ".jpeg"
        sm_meta_info.full_image_file_name = decimal_fill(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame,10) + ".jpeg"
        debug_message = ("\n============================================================\n::::: StartImage Frame : " + str(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame) + " EndImage Frame : " + str(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame) + " FRAME_NUMBER : " + str(sm_meta_info.frame_num) + "\n============================================================\n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

        sm_meta_info.IsFacility = True
        BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] = "Start"
        BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] = 0
        BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] = 0 
        BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] = 0 
        BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] = 0 
        BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrameNumber[roi_index] = 0
        BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrameNumber[roi_index] = 0 
        sm_meta_info.IsUploadTwoImage = True        
        sm_meta_info.DetectedEvent.append("Facility")
        currenttime = current_milli_time()
        BridgeDeviceID = sm_meta_info.device_id 
        CameraID = sm_meta_info.camera_id

        for item in sm_info.camera_info.SceneModeConfig:
            if item["CustomAnalysisStage"].lower().startswith("facility"):
                item["Resolution"] = "{}x{}".format(str(BridgeDeviceConfigVariable.Resolution_Convert_Width),str(BridgeDeviceConfigVariable.Resolution_Convert_Height))   
                break

        sm_meta_info.SaveImageDirectory = BridgeDeviceConfigVariable.ImageSaveDirectory
        sm_meta_info.SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(CameraID), int(currenttime))
        sm_meta_info.SceneDataThumbnailID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 1)
        sm_meta_info.SceneDataImageID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 2)
        sm_meta_info.SceneDataVideoID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 3)
        sm_meta_info.SceneMarkIsDone = False
        create_scenemark_as_file_sync(sm_meta_info)
    else:
        CameraID = sm_info.camera_info.camera_id 
        
        for i in range(0,len(BridgeDeviceConfigVariable.CameraList)):
            #print("####### CAMERA ID ################",CameraID,len(BridgeDeviceConfigVariable.CameraList))
            try:
                if(CameraID == BridgeDeviceConfigVariable.CameraList[i].CameraID):
                    cameraIdx = i
                    break
            except Exception as ex:
                debug_message = "::: #ERROR MESSAGE :::" + str(ex)
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
                pass 
        
        StartTime = time.time()
        for item in sm_info.camera_info.SceneModeConfig:
            if item["CustomAnalysisStage"].lower().startswith("facility"):
                analysis_item = item["AnalysisRegion"]["ROICoords"]
                #print(analysis_item)
                ScreenSize = item["Resolution"].split("x")
                Width = int(ScreenSize[0])
                Height = int(ScreenSize[0])

                AnalysisRegion = []
                AnalysisRegion2 = []
                MaxX = 0
                MinX = int(int(ScreenSize[0]) / (int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width)))
                MaxY = 0 
                MinY = int(int(ScreenSize[1]) / (int(ScreenSize[1])/int(BridgeDeviceConfigVariable.Resolution_Convert_Height)))
                
                #int(int(ScreenSize[0])/ int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width))
                #print("#### MMMMMMMM",MinX,MaxX,int(BridgeDeviceConfigVariable.Resolution_Convert_Width))
                for roi in analysis_item:
                    analysis = []
                    # GET ROI 
                    for item2 in roi["Coords"]:
                        Coordinate = []
                        x = int(item2["XCoord"] / (int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width)))
                        y = int(item2["YCoord"] / (int(ScreenSize[1])/int(BridgeDeviceConfigVariable.Resolution_Convert_Height)))  
                        item2["XCoord"] = x
                        item2["YCoord"] = y   
                        if(x <= MinX):
                            MinX = x
                        
                        if(x >= MaxX):
                            MaxX = x
                        #print("####",x,y,ScreenSize[0],ScreenSize[1],int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width))    
                        Coordinate.append(x)
                        Coordinate.append(y)
                        analysis.append(Coordinate)
                    
                    AnalysisRegion.append(analysis)
                    
                    CenterX = MinX + int(int(MaxX - MinX) / 2)
                    CenterY = MinY + int(int(MaxY - MinY) / 2)

                    ratio_width = (int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width))
                    ratio_height = (int(ScreenSize[1])/int(BridgeDeviceConfigVariable.Resolution_Convert_Height))
    
                    for analysis in AnalysisRegion:
                        analysis2 = []
                        for i in range(0,len(analysis)):
                            Coordinate2 = []
                            item2 = analysis[i]
                            item2[0] = int(item2[0])
                            item2[1] = int(item2[1])
                            x = int(item2[0])
                            y = int(item2[1])
    
                            if(CenterX > x):
                                x = x - int(x * BridgeDeviceConfigVariable.REDUCE_ROI_RATIO)
                            else:
                                x = x + int(x * BridgeDeviceConfigVariable.REDUCE_ROI_RATIO)

                            if(CenterY > y):
                                y = y - int(y * BridgeDeviceConfigVariable.REDUCE_ROI_RATIO)
                            else:
                                y = y + int(y  * BridgeDeviceConfigVariable.REDUCE_ROI_RATIO)

                            if(x < 0):
                                x = 0 
                            elif(x > Width):
                                x = Width

                            if(y < 0):
                                y = 0 
                            elif(y > Height):
                                y = Height

                
                            Coordinate2.append(x)
                            Coordinate2.append(y)
                            analysis2.append(Coordinate2)

                        AnalysisRegion2.append(analysis2)
                    
                #print(AnalysisRegion)
                #print(AnalysisRegion2)
                for sm_meta_info in sm_meta_info_list:
                    IsOverlap = False
                    roi_index = 0 
                    result_index = []
                    for i in range(0,len(AnalysisRegion)):
                        result_index.append(False)
                    
                    for analysis in AnalysisRegion:
                        result = overlaps_contains()
                        for item in sm_meta_info.detected_object_info_list:
                            if item.detected_object.lower() == "person":
                                top = item.top
                                left = item.left
                                width = item.width 
                                height = item.height
                                StartTime = time.time()
                                result = person_intersect(analysis,[[left,top],[width,height]])
                                #print("###### RESULT OF CONTAINS[" + str(roi_index) + "]", sm_meta_info.frame_num,result.contains)
                
                                if result.overlaps and BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "Start":
                                    IsOverlap = True 
                                    break
                                elif result.overlaps and BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "End":
                                    IsOverlap = IsOverlap or True
    
                        if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] == 0 and result.contains == True):
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] = 0

                        if((IsOverlap and BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "Start")):
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] + 1
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] = 0

                            if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] == 1):
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrameNumber[roi_index] = sm_meta_info.frame_num
                            #print("#### CAMERAID",BridgeDeviceConfigVariable.CameraList[cameraIdx].CameraID,BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus,BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount,IsOverlap)

                            debug_message = ("BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[" + str(roi_index) + "]" + ":::" + str(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index]) + ":::" + str(sm_meta_info.frame_num),IsOverlap)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                            if BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "Start" and BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] == int(BridgeDeviceConfigVariable.CameraList[cameraIdx].InferenceFPS * FacilityCheckFrameRatio[int(BridgeDeviceConfigVariable.CameraList[cameraIdx].CameraID) - 1]):
                                #BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = sm_meta_info.frame_num - int(BridgeDeviceConfigVariable.CameraList[cameraIdx].InferenceFPS * FacilityCheckFrameRatio[int(BridgeDeviceConfigVariable.CameraList[cameraIdx].CameraID) - 1]) - 5
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrameNumber[roi_index] - int(BridgeDeviceConfigVariable.CameraList[cameraIdx].InferenceFPS * FacilityCheckFrameRatio[int(BridgeDeviceConfigVariable.CameraList[cameraIdx].CameraID) - 1])

                                if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame % 2 == 1):
                                    BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame - 1

                                BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] = "End"
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] = 0
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] = 0 
                        else:
                            if BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] == 4:
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] = 0
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] == 0
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] + 1

                        if(IsOverlap and BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "End"):
                            if BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] == 4:
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] = 0 
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] = 0
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] = BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] + 1
                            
                        if((IsOverlap == False and BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "End") or (BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "End" and len(sm_meta_info.detected_object_info_list) == 0)):
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] = BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] + 1
                            debug_message = ("BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[" + str(roi_index) + "]" + ":::" + str(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index]) + ":::" + str(sm_meta_info.frame_num),IsOverlap)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                        if BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] == "End" and BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] == int(BridgeDeviceConfigVariable.CameraList[cameraIdx].InferenceFPS * FacilityCheckFrameRatio[int(BridgeDeviceConfigVariable.CameraList[cameraIdx].CameraID) - 1]):
                
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame = sm_meta_info.frame_num + 2
                            if(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame % 2 == 1):
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame - 1
                            sm_meta_info.EndFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame
                        
                            if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame < 0):
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = 1
                            if(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame % 2 == 1):
                                BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame - 1
                            sm_meta_info.StartFrame = BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame
                            
                            sm_meta_info.thumbnail_image_file_name = decimal_fill(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame,10) + ".jpeg"
                            sm_meta_info.full_image_file_name = decimal_fill(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame,10) + ".jpeg"
                            debug_message = ("\n============================================================\n::::: StartImage Frame : " + str(BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrame) + " EndImage Frame : " + str(BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrame) + " FRAME_NUMBER : " + str(sm_meta_info.frame_num) + "\n============================================================\n")
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)

                            sm_meta_info.IsFacility = True
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].ImageStatus[roi_index] = "Start"
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectCount[roi_index] = 0
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectCount[roi_index] = 0 
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartObjectResetCount[roi_index] = 0 
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndObjectResetCount[roi_index] = 0 
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].StartFrameNumber[roi_index] = 0
                            BridgeDeviceConfigVariable.CameraList[cameraIdx].EndFrameNumber[roi_index] = 0 
                            result_index[roi_index] = True
                            sm_meta_info.IsUploadTwoImage = True        
                            sm_meta_info.DetectedEvent.append("Facility")
                            currenttime = current_milli_time()
                            BridgeDeviceID = sm_meta_info.device_id 
                            CameraID = sm_meta_info.camera_id

                            for item in sm_info.camera_info.SceneModeConfig:
                                if item["CustomAnalysisStage"].lower().startswith("facility"):
                                    item["Resolution"] = "{}x{}".format(str(BridgeDeviceConfigVariable.Resolution_Convert_Width),str(BridgeDeviceConfigVariable.Resolution_Convert_Height))   
                                    break

                            sm_meta_info.SaveImageDirectory = BridgeDeviceConfigVariable.ImageSaveDirectory
                            sm_meta_info.SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(CameraID), int(currenttime))
                            sm_meta_info.SceneDataThumbnailID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 1)
                            sm_meta_info.SceneDataImageID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 2)
                            sm_meta_info.SceneDataVideoID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 3)
                            sm_meta_info.SceneMarkIsDone = False
                            timedone = {
                                "Process":"BD_EVENT_AT",
                                "TimeStamp":str(datetime.datetime.utcnow())
                            }
                            sm_meta_info.ProcessTimeList = None
                            sm_meta_info.ProcessTimeList = []
                            sm_meta_info.ProcessTimeList.append(timedone)
                            
                            create_scenemark_as_file_sync(sm_meta_info)
                            #BridgeDeviceConfigVariable.FacilitySceneMarkList.append(sm_meta_info)
                            #print("###################[GENERATE FACILITY SCENEMARK DATA START]  ==============================================")
                            #print(sm_meta_info.SceneMarkID,datetime.datetime.now())
                            #print("###################[[GENERATE FACILITY SCENEMARK DATA END]  ==============================================")
                            #print("\n\n")

                        roi_index = roi_index + 1

    EndTime = time.time()

    #print("####### ",StartTime,EndTime,EndTime-StartTime)

def scenemark_facility_metadata_event_manager(cameraid):
    while(True):
    #try : 
        for k in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
            CameraID = str(int(k+1)).zfill(4)
            FMarkDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.FMetaDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            if(os.path.isdir(FMarkDirectory)):
                #print(FMarkDirectory)
                file_list = os.listdir(FMarkDirectory)
                file_list.sort()
                for item in file_list:
                    fmetadata_file = FMarkDirectory + "/" + item
                    if os.path.isfile(fmetadata_file) and os.path.getsize(fmetadata_file) > 0:
                        StartTime = time.time()
                        with open(fmetadata_file,"rb") as f:
                            unpickler = pickle.Unpickler(f)
                            sm_meta_info = unpickler.load()
                            send_scenemark_fmetadata_to_algorithm(sm_meta_info)
                            if(os.path.isfile(fmetadata_file)):
                                os.remove(fmetadata_file)
                        EndTime = time.time()   
                        debug_message = ("FMETA DATA PROCESSING...." + str(StartTime) + ":::" + str(EndTime) + ":::" + str(EndTime-StartTime))
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)   
    #except Exception as ex:
    #    debug_message = "::: ^^^ERROR MESSAGE :::" + str(ex)
    #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
    #    get_camera_list()
    #    pass      
    
def get_camera_list():
    global FacilityCheckFrameRatio
    bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
    #print("#####",bridge_device_config_file_name)
    if(os.path.isfile(bridge_device_config_file_name)):
        with open(bridge_device_config_file_name,"rb") as f:
            Config = json.loads(pickle.load(f))
            if(Config):
                BridgeDeviceInfo = Config["BridgeDeviceInfo"]
                BridgeDeviceConfigVariable.CameraList.clear()
                for item in BridgeDeviceInfo["CameraList"]:
                    camera_info = parsing_camerainfo(item,BridgeDeviceConfigVariable.BridgeDeviceID) 
                    if(camera_info.Use == "Y" and camera_info.CameraType == BridgeDeviceConfigVariable.CameraType and camera_info.AIModelType == BridgeDeviceConfigVariable.AIModelType): 
                        camera_info.camera_id = camera_info.CameraID
                        camera_info.device_id = BridgeDeviceConfigVariable.BridgeDeviceID
                        camera_info.ImageStatus = ["Start","Start","Start","Start","Start","Start","Start","Start","Start","Start"]
                        camera_info.EndObjectCount = [0,0,0,0,0,0,0,0,0,0]
                        camera_info.EndObjectResetCount = [0,0,0,0,0,0,0,0,0,0]
                        camera_info.StartObjectCount = [0,0,0,0,0,0,0,0,0,0]
                        camera_info.StartObjectResetCount = [0,0,0,0,0,0,0,0,0,0]
                        BridgeDeviceConfigVariable.CameraList.append(camera_info)

                        for item in camera_info.SceneModeConfig:
                            if item["CustomAnalysisStage"].lower().startswith("facility"):
                                FacilityCheckFrameRatio[int(camera_info.CameraID) - 1] = int(item["RecognizeTime"]) / 1000
                            if(camera_info.SelfCheckYn == "Y"):
                                FacilityCheckFrameRatio[int(camera_info.CameraID) - 1] = 0.1

    #print("######################### FacilityCheckFrameRatio",FacilityCheckFrameRatio)
    with open("CameraList.dat","wb") as f:
        pickle.dump(BridgeDeviceConfigVariable.CameraList,f)
        #print("###### CAMERA LIST IS UPDATED")

    if(os.path.isfile("CameraList.dat")):
        with open("CameraList.dat","rb") as f:
            unpickler = pickle.Unpickler(f)
            BridgeDeviceConfigVariable.CameraList.clear()
            BridgeDeviceConfigVariable.CameraList = unpickler.load()

            

def generate_result_scenemark_facility_metadata(detected_object_meta_info):
    while(True):
        try:
            while detected_object_meta_info:
                create_scenemark_as_file_sync(detected_object_meta_info.pop(0))
        except Exception as ex:
            debug_message = "::: ERROR MESSAGE :::" + str(ex)
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
            pass      
### FACILITY 
def main():
    print("==========================================")
    print(":::::Facility Algorithm Analysis is started...::::")
    print("==========================================")
    get_camera_list()
    threading.Thread(target=scenemark_facility_metadata_event_manager,args=("",)).start()


    #threading.Thread(target=generate_result_scenemark_facility_metadata,args=(BridgeDeviceConfigVariable.FacilitySceneMarkList,)).start()

## LoadBridgeDeviceSecurityObject Disabled until it works 2020-09-24 DCJeong
def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable

    '''
    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager) > 1):
        print("==========================================")
        print("there is same process running already. process is about to be terminated.")
        print("==========================================")
        sys.exit()
    '''

    if(os.path.isfile(BridgeDeviceConfigVariable.DeviceSeurityObjectFile)):
        with open(BridgeDeviceConfigVariable.DeviceSeurityObjectFile) as DeviceSecurityObject:
            SecurityObject = json.load(DeviceSecurityObject)
            DeviceInfo = GetDeviceSecurityObject(SecurityObject)
            BridgeDeviceConfigVariable.BridgeDeviceID = GetDeviceID(DeviceInfo)
            print(BridgeDeviceConfigVariable.BridgeDeviceID)
            if(BridgeDeviceConfigVariable.BridgeDeviceID):
                main()

LoadBridgeDeviceSecurityObject()

#xxprint("DeviceID = " + BridgeDeviceConfigVariable.BridgeDeviceID)
###################### STARTS ###############################
if(BridgeDeviceConfigVariable.BridgeDeviceID):
    pass
else:
    time.sleep(5)
    LoadBridgeDeviceSecurityObject()


