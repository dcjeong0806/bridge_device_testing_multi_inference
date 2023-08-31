
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
from BoundingBoxAnalysis import BoundingBoxClass, MovementAnalysis

import traceback 
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
import queue

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

from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint,decimal_fill, current_milli_time
BridgeDeviceConfigVariable = VariableConfigClass()

import matplotlib.path as mpltPath
from shapely.geometry import  Polygon
import pickle 
#kIsSelfCheckDone = [False,False,False,False,False,False,False,False,False,False]
IsSelfCheckDone = False


FireDataDict = None 
HatOffDataDict = None 
VestOffDataDict = None 
FallDownEllexiDataDict = None 

### ABM 
TripNFallDataDict = None
GateStuckDataDict = None 
RoadBlockCarDataDict = None 
TailgatingCarDataDict = None 
AbandonedDataDict = None  
LoiteringPPEDataDict = None 

FireDataDict = {}
HatOffDataDict = {}
VestOffDataDict = {}
FallDownEllexiDataDict = {}

### ABM 
TripNFallDataDict = {}
GateStuckDataDict = {}
RoadBlockCarDataDict = {} 
TailgatingCarDataDict = {} 
AbandonedDataDict = {}  
LoiteringPPEDataDict = {} 

FireData = []
HatOffData = []
VestOffData = []
FallDownEllexiData = []

### ABM
TripNFallData = []
GateStuckData = []
RoadBlockCarData = []
TailgatingCarData = []
AbandonedData = [] 
LoiteringPPEData = []

TimeSleepProcess = .001

for i in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
    nodeid = str(i + 1)
    CameraID = nodeid.zfill(4)

    FireDataDict[CameraID] = []
    HatOffDataDict[CameraID] = []
    VestOffDataDict[CameraID] = []
    FallDownEllexiDataDict[CameraID] = []

    ### ABM 
    TripNFallDataDict[CameraID] = []
    GateStuckDataDict[CameraID] = []
    RoadBlockCarDataDict[CameraID] = [] 
    TailgatingCarDataDict[CameraID] = []
    AbandonedDataDict[CameraID] = [] 
    LoiteringPPEDataDict[CameraID] = []






class person_object:
    xmax = 0 
    xmin = 0 
    ymax = 0 
    ymin = 0 
    strObjectType = ""

class overlaps_contains:
    overlaps = False
    contains = False



def check_confidence(CustomAnalysisStage,sm_meta_info,item):
    if(CustomAnalysisStage.lower().startswith("abandonment")):
        for detected_item in sm_meta_info.detected_object_info_list:
            if detected_item.detected_object.lower() == "person" and detected_item.detected_object.lower() == "bag":
                set_confidence = int(item["Threshold"] * 100)
                get_confidence = int(detected_item.confidence * 100) 
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
            if detected_item.detected_object.lower() == "person":
                set_confidence = int(item["Threshold"] * 100)
                get_confidence = int(detected_item.confidence * 100) 
                #if(detected_item.detected_object.lower() == "person"):
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
    if(str(item.get("CustomAnalysisStage")) != "NewSceneMode"):
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

                if StartTime <= detectedtime and EndTime >= detectedtime:
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

                if StartTime <= detectedtime and EndTime >= detectedtime:
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
    print(person)
    # configuring person points
    person_points = [tuple(person[0])]
    print("####",person_points)
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
    print(person_points,result,str(EndTime-StartTime))
    #
    # print("\n")
    return result


def send_scenemark_metadata_to_algorithm(sm_meta_info_list):
    global FireDataDict 
    global HatOffDataDict  
    global VestOffDataDict 
    global FallDownEllexiDataDict 

    ### ABM 
    global TripNFallDataDict
    global GateStuckDataDict
    global RoadBlockCarDataDict
    global TailgatingCarDataDict
    global AbandonedDataDict
    global LoiteringPPEDataDict 

    global FireData
    global VestOffData 
    global HatOffData
    global FallDownEllexiData

    ### ABM 
    global TripNFallData
    global GateStuckData 
    global RoadBlockCarData 
    global TailgatingCarData 
    global AbandonedData 
    global LoiteringPPEData 


    
    global BridgeDeviceConfigVariable
    global IsSelfCheckDone


    Fire4TnmScreenSize = None 
    HatOffScreenSize = None
    FallDownScreenSize = None 

    ### ABM 
    Abandoned4TnmScreenSize = None 
    LoiteringPPE4TnmScreenSize = None 
    TripNFall4TnmScreenSize = None 
    GateStuck4TnmScreenSize = None 
    RoadBlockCar4TnmScreenSize = None 
    TailgatingCar4TnmScreenSize = None 


    IsFire4Tnm = False
    IsFalldown4Ellexi = False
    IsHatOff4Tnm = False

    ### ABM 
    IsTripNFall4Tnm = False
    IsGateStuck4Tnm = False
    IsRoadBlockCar4Tnm = False
    IsTailgatingCar4Tnm = False
    IsAbandoned4Tnm = False 
    IsLoiteringPPE4Tnm = False 

    sm_meta_info = None
    sm_meta_info = sm_meta_info_list[0]

    '''
    camera_index = 0 
    for item in BridgeDeviceConfigVariable.RecentResultList:
        print("########========Origin", item)
        IsExisted = False 
        if(int(sm_meta_info.camera_id) == camera_index):
            for result_key in item:
                
                for config_item in sm_meta_info.camera_info.get("SceneModeConfig"):
                    if(str(config_item.get("Analysis")).lower() == str(result_key).lower()):
                        IsExisted = True 
                        break
            if(IsExisted == False):
                item[result_key] = [0,"0000"]
        camera_index = camera_index + 1

        print("########========Added", item)
        print("\n\n\n\n")
    '''

           
    

    #for config_item in sm_meta_info.camera_info.get("SceneModeConfig"):
    #    print("######### EVENTMANAGER CustomAnalysisStage",str(item.get("CustomAnalysisStage")),len(sm_meta_info.camera_info.get("SceneModeConfig")))


    #print("####:::#### Performance Test EventManager Start ####:::####", time.time(), sm_meta_info_list[0].camera_info.CameraID,sm_meta_info_list[0].frame_num)
    #print("+++++++++++++++++++++++++++++++")
    #print("#### CREATE SCENEMARK ######### = ",sm_meta_info_list[0].camera_info.CameraID,sm_meta_info_list[0].frame_num, len(sm_meta_info_list))
    #print("+++++++++++++++++++++++++++++++")


    #if(len(sm_meta_info.camera_info.get("SceneModeConfig")) > 0): ### Check Schedule
    #    for item in sm_meta_info.camera_info.get("SceneModeConfig"):
    #        check_schedule(item,sm_meta_info)


    '''
    for sm_meta_info_item in sm_meta_info_list: ### Check Meta Info
        if(len(sm_meta_info.camera_info.get("SceneModeConfig")) > 0):
            for item in sm_meta_info.camera_info.get("SceneModeConfig"):                
                CustomAnalysisStage = str(item.get("CustomAnalysisStage"))
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
    currenttime = current_milli_time()

    BridgeDeviceID = sm_meta_info.camera_info.get("DeviceID")
    CameraID = sm_meta_info.camera_info.get("CameraID")

    print("##### BridgeDeviceID CameraID ", BridgeDeviceID, CameraID)
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #print(sm_meta_info.detected_time)
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    event_start_timedone = None

    for item in sm_meta_info.camera_info.get("SceneModeConfig"):

        if(str(item.get("Analysis")).lower().startswith("fire") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            Fire4TnmScreenSize = item.get("Resolution")
            IsFire4Tnm = True
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }
        
        if(str(item.get("Analysis")).lower().startswith("hatoff") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            HatOffScreenSize = item.get("Resolution")
            IsHatOff4Tnm = True
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }
        
        if(str(item.get("Analysis")).lower().startswith("falldown") and str(item.get("AnalysisVendor").lower().startswith("ellexi"))):
            FallDownScreenSize = item.get("Resolution")
            IsFalldown4Ellexi = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }
        
        ### ABM 
        '''
        if(str(item.get("Analysis")).lower().startswith("abandoned") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            Abandoned4TnmScreenSize = item.get("Resolution")
            IsAbandoned4Tnm = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }

        if(str(item.get("Analysis")).lower().startswith("loiteringppe") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            LoiteringPPE4TnmScreenSize = item.get("Resolution")
            IsLoiteringPPE4Tnm = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }

        if(str(item.get("Analysis")).lower().startswith("tripnfall") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            TripNFall4TnmScreenSize = item.get("Resolution")
            IsTripNFall4Tnm = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }

        if(str(item.get("Analysis")).lower().startswith("gatestuck") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            GateStuck4TnmScreenSize = item.get("Resolution")
            IsGateStuck4Tnm = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }
            
        if(str(item.get("Analysis")).lower().startswith("roadblockcar") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            RoadBlockCar4TnmScreenSize = item.get("Resolution")
            IsRoadBlockCar4Tnm = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }

        if(str(item.get("Analysis")).lower().startswith("tailgatingcar") and str(item.get("AnalysisVendor").lower().startswith("tnm"))):
            TailgatingCar4TnmScreenSize = item.get("Resolution")
            IsTailgatingCar4Tnm = True 
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }
        '''



    if(IsFire4Tnm):
        for meta_info in sm_meta_info_list:
            if int(meta_info.detected_time) % 2 == 0 or True==True:
                for item_scenemodeconfig in meta_info.camera_info.get("SceneModeConfig"):
                #if (str(item_scenemodeconfig.get("Analysis")).lower().startswith("fire") and str(item_scenemodeconfig.get("AnalysisVendor").lower().startswith("tnm"))):
                    result = overlaps_contains()
                    ScreenSize = item_scenemodeconfig["Resolution"].split("x")
                    MaxX = 0
                    MinX = int(int(ScreenSize[0]) / (int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width)))
                    MaxY = 0 
                    MinY = int(int(ScreenSize[1]) / (int(ScreenSize[1])/int(BridgeDeviceConfigVariable.Resolution_Convert_Height)))
                    AnalysisRegion = []
                    analysis_item = item["AnalysisRegion"]["ROICoords"]

                    for roi in analysis_item:
                        # GET ROI 
                        for item2 in roi["Coords"]:
                            #print("####### FIRE SIZE ",FireScreenSize[0],FireScreenSize[1],Fire4Tnm,len(sm_meta_info_list))

                            Coordinate = []
                            x = int(item2["XCoord"] / (int(ScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width)))
                            y = int(item2["YCoord"] / (int(ScreenSize[1])/int(BridgeDeviceConfigVariable.Resolution_Convert_Height)))  
                            item2["XCoord"] = x
                            item2["YCoord"] = y   
                            if(x <= MinX):
                                MinX = x

                            if(x >= MaxX):
                                MaxX = x
                            #print("####",x,y,FireScreenSize[0],FireScreenSize[1],int(FireScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width))    
                            Coordinate.append(x)
                            Coordinate.append(y)
                            AnalysisRegion.append(Coordinate)

                    for item in meta_info.detected_object_info_list:
                        for item2 in item_scenemodeconfig.get("Filters").get("TriggerOnTheseDetectedItems"):
                            if item.detected_object.lower() == item2.lower():
                                #print("######### ", item.detected_object)
                                top = item.top
                                left = item.left
                                width = item.width 
                                height = item.height
                                StartTime = time.time()
                                result = person_intersect(AnalysisRegion,[[left,top],[width,height]])
                                if(result.overlaps):      
                                    print("####### FIRE IN ROI",AnalysisRegion)
                                    FireData.append(item)



                    InferenceFPS = int(sm_meta_info.camera_info.InferenceFPS)
                    AlarmDelay = 0
                    DetectDelay = 0
                    DetectFrame = 10 
                    InferenceFPS = int(sm_meta_info.camera_info.get("InferenceFPS"))
                    CameraFPS = int(sm_meta_info.camera_info.get("CameraFPS"))

                    for params_item in config_item.get("AnalysisParams"):
                        if(params_item.get("ParamName").lower() == "alarmdelay"):
                            AlarmDelay = int(params_item.get("ParamValue"))
                        
                        if params_item.get("ParamName").lower() == "detectdelay":
                            DetectDelay = int(params_item.get("ParamValue")) * 1000

                    DetectFrame = int(int(CameraFPS / InferenceFPS) * (DetectDelay / 1000) * .5)

                    print("DetectDelay ", DetectDelay , "AlarmDelay" ,AlarmDelay, "InferenceFPS", InferenceFPS, "CameraFPS", CameraFPS , "DetectFrame",DetectFrame )

                    FrameStartTime = int(config_item.get("StartTimeRelTrigger"))
                    FrameEndTime = int(config_item.get("EndTimeRelTrigger"))   
                

                    for fire in FireData:
                        if((current_milli_time() - int(fire.detected_time_ms)) >= DetectDelay):
                            FireData.remove(fire)
                    #print("########## FIRE DATA COUNT ", len(FireData))
                    if(len(FireData) > 20):
                        for fire in FireData:
                            FireData.pop(0)

                        sm_meta_info = None
                        sm_meta_info = sm_meta_info_list[0]
                        timedone = {
                            "Process":"BD_EVENT_AT",
                            "TimeStamp":str(datetime.datetime.utcnow())
                        }
                        sm_meta_info.ProcessTimeList = None
                        sm_meta_info.ProcessTimeList = []
                        sm_meta_info.ProcessTimeList.append(event_start_timedone)
                        sm_meta_info.ProcessTimeList.append(timedone)

        

                        start_frame = sm_meta_info.frame_num
                        
              

                        StartFrame = start_frame - (FrameStartTime * InferenceFPS)
                        EndFrame = start_frame + (FrameEndTime * InferenceFPS)
                        if(StartFrame < 0):
                            StartFrame = 1
                        sm_meta_info.FrameDetected = start_frame

                        debug_message = ("############ StartFrame:{} EndFrame:{}".format(StartFrame,EndFrame))
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                        for i in range(StartFrame,EndFrame):
                            image_file  = "{}/{}_{}/{}.jpeg".format(BridgeDeviceConfigVariable.ImageSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(i)).zfill(10))
                            if(os.path.isfile(image_file)):
                                sm_meta_info.full_image_file_name = decimal_fill(i,10) + ".jpeg"
                                sm_meta_info.thumbnail_image_file_name = decimal_fill(i,10) + ".jpeg"
                                break
                                
                        IsUploadTwoImage = False

                        sm_meta_info.IsUploadTwoImage = IsUploadTwoImage   

                        debug_message = ("############ IsUploadTwoImage ".format(str(IsUploadTwoImage)))
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                        sm_meta_info.FrameStarted = StartFrame
                        sm_meta_info.FrameEnded = EndFrame
                        sm_meta_info.DetectedEvent = None
                        sm_meta_info.DetectedEvent = []
                        sm_meta_info.DetectedEvent.append("Fire4Tnm")

                        #for detected_event_item in sm_meta_info.DetectedEvent:
                        #    debug_message = ("DETECTED EVENT ITEM " + detected_event_item)
                        #    print(debug_message)


                        sm_meta_info.SaveImageDirectory = BridgeDeviceConfigVariable.ImageSaveDirectory
                        sm_meta_info.SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(CameraID), int(currenttime))
                        sm_meta_info.SceneDataThumbnailID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 1)
                        sm_meta_info.SceneDataImageID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 2)
                        sm_meta_info.SceneDataVideoID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 3)
                        sm_meta_info.SceneMarkIsDone = False
                        for check_config_item in sm_meta_info.camera_info.get("SceneModeConfig"):
                            if(str(item.get("CustomAnalysisStage")).lower().startswith("fire4tnm")):
                                check_config_item["AnalysisResult"]["Result"] = "Detected"
                                break

                        #BridgeDeviceConfigVariable.SceneMarkList.put(sm_meta_info)

                        AlarmDelay = 0
                        for analysis_item in item.get("AnalysisParams"):
                            if(analysis_item.get("ParamName").lower() == "alarmdelay"):
                                AlarmDelay = int(analysis_item.get("ParamValue"))

                        if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["fire4tnm"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["fire4tnm"][1] == sm_meta_info.camera_info.CameraID)  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["fire4tnm"][0]) >= AlarmDelay):

                            create_scenemark_as_file_sync(sm_meta_info)
                            BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["fire4tnm"][0] = int(sm_meta_info.detected_time)
                            BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.CameraID) - 1]["fire4tnm"][1] = sm_meta_info.camera_info.CameraID


    if(IsFalldown4Ellexi):
        for meta_info in sm_meta_info_list:
            for config_item in meta_info.camera_info.get("SceneModeConfig"):
                if str(config_item.get("Analysis")).lower().startswith("falldown") and str(config_item.get("AnalysisVendor").lower().startswith("ellexi")) :
                    AIServer = str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))

                    result = overlaps_contains()
                    Resolution_Height = config_item.get("Resolution").get("Height")
                    Resolution_Width = config_item.get("Resolution").get("Width")
                    ScreenSize = [Resolution_Height, Resolution_Width]

                    MaxX = 0
                    MinX = int(int(ScreenSize[1]) / (int(ScreenSize[1])/int(Resolution_Width)))
                    MaxY = 0 
                    MinY = int(int(ScreenSize[0]) / (int(ScreenSize[0])/int(Resolution_Height)))
                    AnalysisRegion = []
                    analysis_item = config_item.get("AnalysisRegion").get("ROICoords")

                    for roi in analysis_item:
                        # GET ROI 
                        for item2 in roi["Coords"]:
                            #print("####### FIRE SIZE ",FireScreenSize[0],FireScreenSize[1],Fire4Tnm,len(sm_meta_info_list))

                            Coordinate = []
                            x = int(item2.get("XCoord") / (int(ScreenSize[1])/int(Resolution_Width)))
                            y = int(item2.get("YCoord") / (int(ScreenSize[0])/int(Resolution_Height)))  
                            item2["XCoord"] = x
                            item2["YCoord"] = y   
                            if(x <= MinX):
                                MinX = x

                            if(x >= MaxX):
                                MaxX = x
                            #print("####",x,y,FireScreenSize[0],FireScreenSize[1],int(FireScreenSize[0])/int(BridgeDeviceConfigVariable.Resolution_Convert_Width))    
                            Coordinate.append(x)
                            Coordinate.append(y)
                            AnalysisRegion.append(Coordinate)
             

                    for detected_item in meta_info.detected_object_info_list:
                        if(float(detected_item.confidence) >= float(config_item["AnalysisThreshold"])): ## Checking Confidence ...    
                            debug_message = "{} : {} : {} : {} : {} : {} : {} : {} ".format(AIServer , meta_info.origin_frame_num , detected_item.confidence, config_item["AnalysisThreshold"], detected_item.width,detected_item.height, detected_item.detected_object,config_item.get("Filters").get("TriggerOnTheseDetectedItems"))
                            #print( AIServer,detected_item.confidence, ">>", algorithm_item["AnalysisThreshold"],detected_item.width,detected_item.height,detected_item.detected_object)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                            for filter_item in config_item.get("Filters").get("TriggerOnTheseDetectedItems"): 
                                if(str(filter_item).lower() == str(detected_item.detected_object).lower()):
                                #if detected_item.detected_object.lower() == BridgeDeviceConfigVariable.FallDownDetectObject:
                                    #print("######### ", item.detected_object)
                                    top = detected_item.top
                                    left = detected_item.left
                                    width = detected_item.width 
                                    height = detected_item.height
                                    StartTime = time.time()
                                    result = person_intersect(AnalysisRegion,[[left,top],[width,height]])
                                    EndTime = time.time()
                                    #print("#### TIME TO ROI ", meta_info.frame_num, StartTime, EndTime, EndTime - StartTime)
                                    if(result.overlaps):      
                                        FallDownEllexiDataDict[CameraID].append(detected_item)
                                        debug_message = ("####### " + detected_item.detected_object + " IN ROI", "FRAME NUMBER : " + str(meta_info.frame_num) ,AnalysisRegion,meta_info.camera_info.get("CameraID"),"####" + CameraID + "####",len(FallDownEllexiDataDict[CameraID]))
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                                else:
                                    debug_message = "{} : {} : {} : {} : {} : {} : {} : {} ==> Filter DROP".format(AIServer, meta_info.origin_frame_num, detected_item.confidence, config_item["AnalysisThreshold"], detected_item.width,detected_item.height, detected_item.detected_object , filter_item)
                                    #print( AIServer,detected_item.confidence, ">>", algorithm_item["AnalysisThreshold"],detected_item.width,detected_item.height,detected_item.detected_object)
                                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                        else:
                            debug_message = "{} : {} : {} : {} : {} : {} : {} ==> Threahold DROP".format(AIServer, meta_info.origin_frame_num, detected_item.confidence, config_item["AnalysisThreshold"], detected_item.width,detected_item.height, detected_item.detected_object)
                            #print( AIServer,detected_item.confidence, ">>", algorithm_item["AnalysisThreshold"],detected_item.width,detected_item.height,detected_item.detected_object)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
     


                    AlarmDelay = 0
                    DetectDelay = 0
                    DetectFrame = 10 
                    InferenceFPS = int(sm_meta_info.camera_info.get("InferenceFPS"))
                    CameraFPS = int(sm_meta_info.camera_info.get("CameraFPS"))

                    for params_item in config_item.get("AnalysisParams"):
                        if(params_item.get("ParamName").lower() == "alarmdelay"):
                            AlarmDelay = int(params_item.get("ParamValue"))
                        
                        if params_item.get("ParamName").lower() == "detectdelay":
                            DetectDelay = int(params_item.get("ParamValue")) * 1000

                    DetectFrame = int(int(CameraFPS / InferenceFPS) * (DetectDelay / 1000) * .5)

                    print("DetectDelay ", DetectDelay , "AlarmDelay" ,AlarmDelay, "InferenceFPS", InferenceFPS, "CameraFPS", CameraFPS , "DetectFrame",DetectFrame )
                    for falldown in FallDownEllexiDataDict[CameraID]:
                        currenttime = current_milli_time()
                        #print("##### TIME ",currenttime - int(falldown.detected_time_ms) , currenttime,falldown.detected_time_ms)
                        if((current_milli_time() - int(falldown.detected_time_ms)) > DetectDelay):
                            FallDownEllexiDataDict[CameraID].remove(falldown)

                    if(len(FallDownEllexiDataDict[CameraID]) > DetectFrame):
                        debug_message = CameraID  + " #######=======> FallDown is detected......."
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                        for falldown in FallDownEllexiDataDict[CameraID]:
                            FallDownEllexiDataDict[CameraID].pop(0)
                    
                            
                        timedone = {
                            "Process":"BD_EVENT_AT",
                            "TimeStamp":str(datetime.datetime.utcnow())
                        }
                        sm_meta_info.ProcessTimeList = None
                        sm_meta_info.ProcessTimeList = []
                        sm_meta_info.ProcessTimeList.append(event_start_timedone)
                        sm_meta_info.ProcessTimeList.append(timedone)
                        

                        InferenceFPS = int(sm_meta_info.camera_info.get("InferenceFPS"))
                        start_frame = sm_meta_info.frame_num
                        
                        FrameStartTime = int(config_item.get("StartTimeRelTrigger"))
                        FrameEndTime = int(config_item.get("EndTimeRelTrigger"))   
                        

                        StartFrame = start_frame - (FrameStartTime * InferenceFPS)
                        EndFrame = start_frame + (FrameEndTime * InferenceFPS)
                        if(StartFrame < 0):
                            StartFrame = 1
                        sm_meta_info.FrameDetected = start_frame
                        sm_meta_info.DetentionTime = int(FrameEndTime)
                        sm_meta_info.EndTimeStamp = int(time.time())
                        

                        debug_message = ("############ StartFrame:{} EndFrame:{}".format(StartFrame,EndFrame))
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                        for i in range(StartFrame,EndFrame):
                            image_file  = "{}/{}_{}/{}.jpeg".format(BridgeDeviceConfigVariable.ImageSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(i)).zfill(10))
                            if(os.path.isfile(image_file)):
                                sm_meta_info.full_image_file_name = decimal_fill(i,10) + ".jpeg"
                                sm_meta_info.thumbnail_image_file_name = decimal_fill(i,10) + ".jpeg"
                                break
                                
                        IsUploadTwoImage = False

                        sm_meta_info.IsUploadTwoImage = IsUploadTwoImage   

                        debug_message = ("############ IsUploadTwoImage ".format(str(IsUploadTwoImage)))
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)


                        #BridgeDeviceConfigVariable.FallDown4Ellexi = config_item.get("Analysis").lower() + "4" + config_item.get("AnalysisVendor").lower()
                        sm_meta_info.FrameStarted = StartFrame
                        sm_meta_info.FrameEnded = EndFrame
                        sm_meta_info.DetectedEvent = None
                        sm_meta_info.DetectedEvent = []
                        sm_meta_info.DetectedEvent.append(config_item.get("Analysis"))

                        for detected_event_item in sm_meta_info.DetectedEvent:
                            debug_message = ("DETECTED EVENT ITEM " + str(detected_event_item))
                            print(debug_message)


                        sm_meta_info.SaveImageDirectory = BridgeDeviceConfigVariable.ImageSaveDirectory
                        sm_meta_info.SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(CameraID), int(currenttime))
                    
                        sm_meta_info.SceneDataThumbnailID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 1)
                        sm_meta_info.SceneDataImageID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 2)
                        sm_meta_info.SceneDataVideoID = CreateSceneDataID(BridgeDeviceID,int(CameraID),int(currenttime) + 3)
                        sm_meta_info.SceneMarkIsDone = False
                        
                        #for check_config_item in sm_meta_info.camera_info.get("SceneModeConfig"):
                        #    str(item.get("Analysis")).lower().startswith("falldown") and str(item.get("AnalysisVendor").lower().startswith("ellexi"))
                        #    if(check_config_item["CustomAnalysisStage"].lower().startswith("falldown4ellexi")):
                        #        check_config_item["AnalysisResult"]["Result"] = "Detected"
                        #        break
                        

       

                        print("Falldown Dtected========>>>> ##################++++++++++++======>", int(meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][0]), int(meta_info.detected_time), int(BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][0]), AlarmDelay)

                        if((BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][1] == CameraID) and int(meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][0]) >= AlarmDelay):
                            print("Falldown Dtected ##################++++++++++++======>", int(meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][0]), int(meta_info.detected_time), int(BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][0]), AlarmDelay)
                            create_scenemark_as_file_sync(sm_meta_info)
                            BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][0] = int(sm_meta_info.detected_time)
                            BridgeDeviceConfigVariable.RecentResultList[int(CameraID) - 1][BridgeDeviceConfigVariable.FallDown4Ellexi][1] = CameraID   


    if(IsTailgatingCar4Tnm):
        pass

    IsAbandoned4Tnm = False 
    if(IsAbandoned4Tnm):
        pass
 
    if(IsTripNFall4Tnm):
       
        pass

    if(IsGateStuck4Tnm):
        pass

    if(IsRoadBlockCar4Tnm):
        pass 

    if(IsTailgatingCar4Tnm):
        pass 


    ###### NextK GRPC Version Algorithm 
    if(not IsFire4Tnm 
       and not IsFalldown4Ellexi 
       and not IsHatOff4Tnm
       and not IsAbandoned4Tnm
       and not IsLoiteringPPE4Tnm
       and not IsTripNFall4Tnm
       and not IsGateStuck4Tnm
       and not IsRoadBlockCar4Tnm 
       and not IsTailgatingCar4Tnm
       ):
        #print("#### ######## ######## ######### ############",str(Violence4NextK),str(Fire4Tnm))
        if(len(sm_meta_info_list) > 0):
            Port = 0
            ID = 0
            Resolution = []
            DetectionAreaList = []
            AIServerList = None 
            AIServerList = {}
            DetectionArea = []
            
            
            print("+++++++++++++++++++++++++++++++")
            print("#### Send Meta Data to Algorithm Server ######### = ",sm_meta_info_list[0].camera_info.get("CameraID"),sm_meta_info_list[0].frame_num, len(sm_meta_info_list))
            print("+++++++++++++++++++++++++++++++")
            
            try:
                for item in sm_meta_info.camera_info.get("SceneModeConfig"):
                    if(str(item.get("CustomAnalysisStage")).lower() != "newscenemode"):
                        if(item["AIServer"] != None):
                            RegionOfInterested = str(item.get("Analysis")) + str(item.get("AnalysisVendor"))
                            AIServerList[RegionOfInterested] = RegionOfInterested
                            #print("\n\n=====",RegionOfInterested,"\n\n")

            except Exception as aiserver_ex:
                print(traceback.format_exc())
                pass
            
            try:
                for config_item in sm_meta_info.camera_info.get("SceneModeConfig"):
                    #print("####===>>>>> ",str(item.get("Analysis")).lower(),str(item.get("AnalysisVendor")).lower())
                    if(str(config_item.get("CustomAnalysisStage")).lower() != "newscenemode"):
                        EventID = 0
                        DetectDelay = 0   
                        AlarmDelay = 0
                        RegionOfInterested = str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))
                        #print("\n\nRegionOfInterested",RegionOfInterested)
                        AIServerList[RegionOfInterested] = RegionOfInterested

                        #config_item.get("Filters").get("TriggerOnTheseDetectedItems").append("Person") ##### --> hardcoded Scenemodeconfig, 


                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.LoiteringKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.LOITERING
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  

                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")

                            #print("######## Loitering DetectDelay",DetectDelay)


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
                                
                                DetectedAreaDict = None
                                DetectedAreaDict = {
                                    "ID":ID,
                                    "EventType":EventID,
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }

                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.IntrusionKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.INTRUSION
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  

                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")

                            #print("######## Intrusion DetectDelay",DetectDelay)


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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }

                                #print("INTRUSION ::::::", DetectedAreaDict)

                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.AbandonmentKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.ABANDONMENT  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## Abandonment DetectDelay",DetectDelay)          
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1
                    
                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.RevIntrusionKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.REVINTRUSION           
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## RevIntrusion DetectDelay",DetectDelay)          
                            analysis_item = config_item["AnalysisRegion"]["ROICoords"]

                            for item in analysis_item:
                                DetectionArea = []
                                for item2 in item["Coords"]:

                                    Coordinate = []
                                    if(int(item2["XCoord"]) < 0):
                                        item2["XCoord"] = 0
                                    
                                    if(int(item2["YCoord"]) < 0):
                                        item2["YCoord"] = 0

                                    Coordinate.append(item2["XCoord"])
                                    Coordinate.append(item2["YCoord"])
                                    DetectionArea.append(Coordinate)
                                
                                DetectedAreaDict = {}
                                DetectedAreaDict = {
                                    "ID":ID,
                                    "EventType":EventID,
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1
                        
                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.ViolenceKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.FIGHT           
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")

                            #print("######## Violence DetectDelay",DetectDelay)       
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1
                        
                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.SpeedGateKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.TAILGATE  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## SpeedGate DetectDelay",DetectDelay)           
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.TailGateKey.lower() and 
                           (str(config_item.get("AnalysisVendor")).lower() == "nextk" or str(config_item.get("AnalysisVendor")).lower() == "tnm")):
                            EventID = BridgeDeviceConfigVariable.TAILGATE  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## TailGate DetectDelay",DetectDelay)          
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.TailgatingCar4TnmKey.lower() and 
                           str(config_item.get("AnalysisVendor")).lower() == "tnm"):
                            EventID = BridgeDeviceConfigVariable.TailgatingCar4Tnm  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## TailGate DetectDelay",DetectDelay)          
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.Abandoned4TnmKey.lower() and 
                           str(config_item.get("AnalysisVendor")).lower() == "tnm"):
                            EventID = BridgeDeviceConfigVariable.Abandoned4Tnm  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## TailGate DetectDelay",DetectDelay)          
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.RoadBlockCar4TnmKey.lower() and 
                           str(config_item.get("AnalysisVendor")).lower() == "tnm"):
                            EventID = BridgeDeviceConfigVariable.RoadBlockCar4Tnm  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## TailGate DetectDelay",DetectDelay)          
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
                                    "Pts":DetectionArea,
                                    "ROIType": config_item["AnalysisRegion"]["ROIType"],
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

                        if(str(config_item.get("Analysis")).lower() == BridgeDeviceConfigVariable.LoiteringPPE4TnmKey.lower() and 
                           str(config_item.get("AnalysisVendor")).lower() == "tnm"):
                            EventID = BridgeDeviceConfigVariable.LoiteringPPE4Tnm  
                            ScreenSize = [config_item.get("Resolution").get("Width"),config_item.get("Resolution").get("Height")]
                            Resolution = [int(ScreenSize[0]),int(ScreenSize[1])]  
                            for param in config_item.get("AnalysisParams"):
                                if param.get("ParamName").lower() == "detectdelay":
                                    DetectDelay = param.get("ParamValue")  
                                if param.get("ParamName").lower() == "alarmdelay":
                                    AlarmDelay = param.get("ParamValue")
                            #print("######## TailGate DetectDelay",DetectDelay)          
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
                                    "Pts":DetectionArea,
                                    "Analysis":str(config_item.get("Analysis")),
                                    "AnalysisVendor": str(config_item.get("AnalysisVendor")),
                                    "AnalysisThreshold":float(config_item.get("AnalysisThreshold")),
                                    "DetectDelay":DetectDelay,
                                    "AlarmDelay":AlarmDelay,
                                    "AIServer":config_item.get("AIServer").get("Authority"),
                                    "ExecuteOnPipeline": config_item.get("ExecuteOnPipeline"),
                                    "StartTimeRelTrigger": config_item.get("StartTimeRelTrigger"),
                                    "EndTimeRelTrigger": config_item.get("EndTimeRelTrigger"),
                                    "MinimumSceneData": config_item.get("MinimumSceneData"),
                                    "Filters" : config_item.get("Filters"),
                                    "Resolution": config_item.get("Resolution"),
                                    "SceneModeConfig": config_item
                                }


                                AIServerList[str(config_item.get("Analysis")) + str(config_item.get("AnalysisVendor"))] = DetectedAreaDict
                                ID = ID + 1

            except Exception as multi_ex:
                debug_message = (":::::: Error Message ::::::" + str(multi_ex) + str(traceback.format_exc()))
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                pass            
            

      

            ###### -------------------- Sending Event Start... ----------------- ######
            event_start_timedone = {
                "Process":"BD_EVENT_ST",
                "TimeStamp":str(datetime.datetime.utcnow())
            }
            ###### -------------------- Sending Event Start... ----------------- ######
            

            IsAIServerRunning = False
            sm_meta_info.DetectedEvent = []
            #print("####### =======>>>>>>>",len(AIServerList), AIServerList)
            for AIServer in AIServerList: ##### GRPC
                #print("#####????????????????????",AIServer)
                response = None

                if os.environ.get('https_proxy'):
                    del os.environ['https_proxy']
                if os.environ.get('http_proxy'):
                    del os.environ['http_proxy']
                
                with grpc.insecure_channel(AIServerList[AIServer].get("AIServer"),options=(('grpc.enable_http_proxy', 0),)) as channel:
                    debug_message = (":::::: CONNECTED AI SERVER ::::::"  + ":::" ,AIServerList[AIServer].get("AIServer") ,":::", AIServer)
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                    stub = detectedobject_pb2_grpc.DetectedObjectServiceStub(channel)
                    CameraID = sm_meta_info.camera_info.get("CameraID")
                    UniqueID = "{}_{}_{}".format(BridgeDeviceID,CameraID,AIServer)

                    tmp = detectedobject_pb2.DetectedObjectMessage()                
                    tmp.deviceid = BridgeDeviceID
                    tmp.uid = UniqueID 
                    tmp.scenemarkid = ""
                    tmp.eventoptions.tailgate.time = BridgeDeviceConfigVariable.tailgate_threshold_time
                    tmp.eventoptions.loiteringTime = 0 
             
                    tmp.resolution.append(int(AIServerList[AIServer].get("Resolution").get("Width")))
                    tmp.resolution.append(int(AIServerList[AIServer].get("Resolution").get("Height")))

                    algorithm_item = AIServerList[AIServer]
                    area = detectedobject_pb2.Area()
                    area.id = (int(algorithm_item["ID"]))
                    EventID = (int(algorithm_item["EventType"]))
                    
                    DetectDelay = (int(algorithm_item["DetectDelay"]))
                    AlarmDelay = (int(algorithm_item["AlarmDelay"]))

                    area.eventtype = EventID
                    tmp.eventoptions.loiteringTime = DetectDelay
        
                    '''
                    if EventID == BridgeDeviceConfigVariable.LOITERING:
                        area.eventtype = common_pb2.EventType.Loitering
                        tmp.eventoptions.loiteringTime = DetectDelay
                    elif EventID == BridgeDeviceConfigVariable.INTRUSION:
                        area.eventtype = common_pb2.EventType.Intrusion  
                    elif EventID == BridgeDeviceConfigVariable.REVINTRUSION:
                        area.eventtype = common_pb2.EventType.LineEnter                      
                    elif EventID == BridgeDeviceConfigVariable.ABANDONMENT:
                        area.eventtype = common_pb2.EventType.Abandonded
                    elif EventID == BridgeDeviceConfigVariable.FALLDOWN:
                        area.eventtype = common_pb2.EventType.FallDown    
                    elif EventID == BridgeDeviceConfigVariable.FIGHT:
                        area.eventtype = common_pb2.EventType.Fight
                    elif EventID == BridgeDeviceConfigVariable.TAILGATE:
                        area.eventtype = common_pb2.EventType.TailGate
                    '''


                    InputResolution = [int(sm_meta_info.camera_info.get("SceneMode").get("Inputs")[0].get("Resolution").get("Width")),int(sm_meta_info.camera_info.get("SceneMode").get("Inputs")[0].get("Resolution").get("Height"))]  
                    



                    IgnoreData = [] 
                    AnalysisRegion = None 
                    AnalysisRegion = []
                    for item2 in algorithm_item["Pts"]:
                        points = common_pb2.Point()
                        points.x = int(item2[0] / (int(InputResolution[0])/int(AIServerList[AIServer].get("Resolution").get("Width"))))
                        points.y = int(item2[1] / (int(InputResolution[1])/int(AIServerList[AIServer].get("Resolution").get("Height"))))
                        area.points.append(points)

                        Coordinate = []   
                        Coordinate.append(points.x)
                        Coordinate.append(points.y)
                        AnalysisRegion.append(Coordinate)

                    IsIgnoreTheseDetectedItems = False 
                    


                
                    #if(algorithm_item["ROIType"].lower().endswith("polygon")):
                    #    for ignore_item in AIServerList[AIServer].get("Filters").get("IgnoreTheseDetectedItems"):
                    #        for sm_meta_info_list_item in sm_meta_info_list:
                    #            for ignore_detected_item in sm_meta_info_list_item.detected_object_info_list:
                    #                if(ignore_detected_item.detected_object.lower() == ignore_item.lower()):
                    #                    top = ignore_detected_item.top
                    #                    left = ignore_detected_item.left
                    #                    width = ignore_detected_item.width 
                    #                    height = ignore_detected_item.height
                    #                    result = person_intersect(AnalysisRegion,[[left,top],[width,height]])
                    #                    print(AnalysisRegion,top,left,width,height,ignore_detected_item.detected_object)
                    #                    if(result.overlaps):
                    #                        IsIgnoreTheseDetectedItems = True 
                    #                        print(" IN ROI ########")
                    #                        break 
                    #        if(IsIgnoreTheseDetectedItems):
                    #            break 
                    
                    #if(IsIgnoreTheseDetectedItems):
                    #    break 
                    
                    if(IsIgnoreTheseDetectedItems == False):
                        tmp.area.append(area)  

                    #print("#### PTS TMP =====>>>>",tmp)  
                    #print("#### ORIGIN PTS =====>>>>",algorithm_item["Pts"]) 
        
            
                    if(len(tmp.area) > 0):
                        for sm_meta_info_list_item in sm_meta_info_list:
                            if(len(sm_meta_info_list_item.detected_object_info_list) > 0):
                                detected_list = ""
                                for detected_item in sm_meta_info_list_item.detected_object_info_list:
                                    #if((detected_item.width > 0 and detected_item.height > 0)):

                                    #print("####### CONFIDENCE ######## ::::::", AIServer, float(detected_item.confidence),float(algorithm_item["AnalysisThreshold"]))
                                    if(float(detected_item.confidence) >= float(algorithm_item["AnalysisThreshold"])): ## Checking Confidence ...
                                        objects = detectedobject_pb2.Object()
                                        TimeStamp = datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                                        objects.timestamp = str(detected_item.detected_time_ms)
                                        objects.framenumber = (sm_meta_info_list_item.origin_frame_num)

                                        
                                        #FilterList = ["Person"]
                                        #AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems") = []
                                        #AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems").append("person")
                                    

                                        IsTriggerOnTheseDetectedItems = False 
                                        #for filter_item in AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems"): 
                                        #TriggerData = ["suitcase"]
                                        #TriggerData = ["car","truck"]
                                        #for filter_item in TriggerData:
                                        
                                        for filter_item in AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems"): 
                                            if(str(filter_item).lower() == str(detected_item.detected_object).lower()):
                                                IsTriggerOnTheseDetectedItems = True 
                                                break 

                                                break 
                                        print("####### ===> sm_meta_info_list_item.detected_object_info_list len",detected_item.detected_object,AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems"),len(sm_meta_info_list_item.detected_object_info_list),IsTriggerOnTheseDetectedItems)
                                        if(IsTriggerOnTheseDetectedItems):
                                            debug_message = "{} : {} : {} : {} : {} : {} : {} : {}".format(AIServer, sm_meta_info_list_item.origin_frame_num, detected_item.confidence, algorithm_item["AnalysisThreshold"], detected_item.width,detected_item.height, detected_item.detected_object, AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems"))
                                  
                                            objects.eventclass = BridgeDeviceConfigVariable.EventClass.get(detected_item.detected_object.lower())

                                            objects.x = detected_item.x1
                                            objects.y = detected_item.y1
                                            objects.width = detected_item.width
                                            objects.height = detected_item.height
                                            
                                            tmp.object.append(objects)    
                                        else:
                                            debug_message = "{} : {} : {} : {} : {} : {} : {} : {} ==> FILTER DROP".format(AIServer, sm_meta_info_list_item.origin_frame_num, detected_item.confidence, algorithm_item["AnalysisThreshold"], detected_item.width,detected_item.height, detected_item.detected_object, AIServerList[AIServer].get("Filters").get("TriggerOnTheseDetectedItems"))
                                            #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                                    else:
                                        debug_message = "{} : {} : {} : {} : {} : {} : {} ==> Threshold DROP".format(AIServer, sm_meta_info_list_item.origin_frame_num, detected_item.confidence, algorithm_item["AnalysisThreshold"], detected_item.width,detected_item.height, detected_item.detected_object)
                                        #print( AIServer,detected_item.confidence, ">>", algorithm_item["AnalysisThreshold"],detected_item.width,detected_item.height,detected_item.detected_object)
                                        #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                                        #print( AIServer,detected_item.confidence, "<<", algorithm_item["AnalysisThreshold"],detected_item.width,detected_item.height,detected_item.detected_object, "=====> DROP")
                                        pass
                    
                    
                    
                    
                    if(len(tmp.object) > 0 and len(tmp.area) > 0):
                        StartTime = time.time()
                        debug_message = "### GRPC REQUEST ::: {} : {} : {}".format(sm_meta_info.frame_num,StartTime,datetime.datetime.now())
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)


                        #print("\n\n\n################## SIZE ", len(str(tmp)))
                        if(BridgeDeviceConfigVariable.EventPrintLog):
                            print("###################REQUEST DATA START==============================================")
                            print(tmp)
                            print("###################REQUEST DATA END  ==============================================")
                            print("\n")
                        EndTime = time.time()
                        try:
                            response = stub.SendDetectedObject(tmp)
                        except Exception as ex:
                            print(traceback.format_exc(), str(ex))

                        debug_message = "### GRPC RESPONSE ::: {} : {} : {} : {} : {} : {} : {} : {}".format(sm_meta_info.frame_num,response,len(str(response)),len(str(response.eventinfo)),StartTime,EndTime,EndTime-StartTime,datetime.datetime.now())
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                try:
                    if(response != None):
                        IsDetected = False
                        for item in response.eventinfo:
                            debug_message = ("######## ResultType::::" + str(item.eventtype))
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                            result_type = ""
                            #print("########RESULT TYPE = ",item.eventtype,BridgeDeviceConfigVariable.FIGHT)
                            '''
                            if item.eventtype == BridgeDeviceConfigVariable.LOITERING:
                                result_type = BridgeDeviceConfigVariable.LoiteringKey
                            elif item.eventtype == BridgeDeviceConfigVariable.INTRUSION:
                                result_type = BridgeDeviceConfigVariable.IntrusionKey
                            elif item.eventtype == BridgeDeviceConfigVariable.FALLDOWN:
                                result_type = BridgeDeviceConfigVariable.FallDownKey
                            elif item.eventtype == BridgeDeviceConfigVariable.LONGSTAY:
                                result_type = BridgeDeviceConfigVariable.LongStayKey
                            elif item.eventtype == BridgeDeviceConfigVariable.ABANDONMENT:
                                result_type = BridgeDeviceConfigVariable.AbandonmentKey
                            elif item.eventtype == BridgeDeviceConfigVariable.SPEEDGATE:
                                result_type = BridgeDeviceConfigVariable.SpeedGateKey
                            elif item.eventtype == BridgeDeviceConfigVariable.TAILGATE:
                                result_type = BridgeDeviceConfigVariable.TailGateKey
                            elif item.eventtype == BridgeDeviceConfigVariable.FIGHT:
                                result_type = BridgeDeviceConfigVariable.ViolenceKey
                            elif item.eventtype == BridgeDeviceConfigVariable.REVINTRUSION:
                                result_type = BridgeDeviceConfigVariable.RevIntrusionKey
                            '''

                            start_frame = item.framenumber
                            DetectedEvent = ""
                            FrameStartTime = 0
                            FrameEndTime = 0 
            

                            print("\n\n\n### RESULT TYPE",result_type,item.eventtype, "\n\n\n")

                            DetectDelay = int(AIServerList[AIServer].get("DetectDelay"))
                            AlarmDelay = int(AIServerList[AIServer].get("AlarmDelay"))

                            FrameStartTime = int(AIServerList[AIServer].get("StartTimeRelTrigger"))
                            FrameEndTime = int(AIServerList[AIServer].get("EndTimeRelTrigger"))   

                            print("###### AlarmDelay FrameStartTime FrameEndTime ", AlarmDelay, FrameStartTime, FrameEndTime)
                            print("DETECTED RESULT " , ":::" ,str(AIServerList[AIServer].get("Analysis")).lower(),":::",result_type.lower(), ":::",str(AIServerList[AIServer].get("AnalysisVendor")).lower())

                            if(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.LoiteringKey.lower() and 
                               item.eventtype == BridgeDeviceConfigVariable.LOITERING and 
                               (str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "nextk" or str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm")): ##Loitering
                                
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringKey][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringKey][1] == sm_meta_info.camera_info.get("CameraID")) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringKey][0]) >= int(AlarmDelay)):
                            
                                    IsDetected = True
                                    DetectedEvent = "Loitering"
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["loitering"][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["loitering"][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debug_message = ("\n#######::::: NEXT K0000 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.IntrusionKey.lower() and 
                                 item.eventtype == BridgeDeviceConfigVariable.INTRUSION and 
                                 (str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "nextk" or str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm")): ##Intrusion
                                
                            
                                print("\n\n\n### TIME #######",int(sm_meta_info.detected_time),int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][0]),int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][0]),AlarmDelay,"\n\n\n")

                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][1] == sm_meta_info.camera_info.get("CameraID"))  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][0]) >= AlarmDelay):
                                    IsDetected = True
                                    DetectedEvent = BridgeDeviceConfigVariable.IntrusionKey
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.IntrusionKey][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debug_message = ("#######::::: NEXT KKKK11111 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::" )
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                                
                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.AbandonmentKey.lower() and 
                                 item.eventtype == BridgeDeviceConfigVariable.ABANDONMENT and 
                                 (str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "nextk" or str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm")): ##Abandonment
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["abandonment"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["abandonment"][1] == sm_meta_info.camera_info.get("CameraID"))  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["abandonment"][0]) >= AlarmDelay):
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    IsDetected = True
                                    DetectedEvent = "Abandonment"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["abandonment"][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["abandonment"][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debug_message = ("\n#######::::: NEXT K22222 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                            
                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.RevIntrusionKey.lower() and 
                                 item.eventtype == BridgeDeviceConfigVariable.REVINTRUSION and 
                                 (str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "nextk" or str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm")): ##RevIntrusion
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["revintrusion"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["revintrusion"][1] == sm_meta_info.camera_info.get("CameraID"))  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["revintrusion"][0]) >= AlarmDelay):
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    IsDetected = True  
                                    DetectedEvent = "RevIntrusion"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["revintrusion"][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["revintrusion"][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debut_message = ("\n#######::::: NEXT K4444 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.SpeedGateKey.lower() and 
                                 item.eventtype == BridgeDeviceConfigVariable.SPEEDGATE and 
                                 (str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "nextk" or str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm")):
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["speedgate"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["speedgate"][1] == sm_meta_info.camera_info.get("CameraID"))  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["speedgate"][0]) >= AlarmDelay):
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    IsDetected = True  
                                    DetectedEvent = "SpeedGate"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["speedgate"][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["speedgate"][1] = sm_meta_info.camera_info.get("CameraID")
                        
                                debug_message = ("\n#######::::: NEXT K4444 AI Result = " + result_type + ":::::::" + str(item.get("Analysis")) + ":::::" )
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.TailGateKey.lower() and 
                                 item.eventtype == BridgeDeviceConfigVariable.TAILGATE and 
                                 (str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "nextk" or str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm")):
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["tailgate"][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["tailgate"][1] == sm_meta_info.camera_info.get("CameraID")) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["tailgate"][0]) >= AlarmDelay):
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    IsDetected = True  
                                    DetectedEvent = "tailgate"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["tailgate"][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1]["tailgate"][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False

                                debug_message = ("\n#######::::: NEXT K5555 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                           
                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.TailgatingCar4TnmKey.lower() and 
                                 item.eventtype == BridgeDeviceConfigVariable.TailgatingCar4Tnm and
                                 str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm"): ##TailGating Car 

                                detected_time = str(int(time.time()))
                                debug_message = ("\n\n\n\n\n\n#######::::: TNM AI Result = " + detected_time + "::::" + "ID :::" + str(item.id) + ":::::"  + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                                print("##### DataList =====> ", TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")])

                                if(len(TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")]) > 0):
                                #for i in range(1, len(TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")])):
                                    
                                    tailgating_item = TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")][len(TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")]) - 1]
                                    print("######=====>>>>>>>>>", AlarmDelay, tailgating_item[0], tailgating_item[1] , detected_time , int(detected_time) -  int(tailgating_item[1]))
                                    detected_interval = int(detected_time) - int(tailgating_item[1])
                                    if(detected_interval <= DetectDelay):
                                        if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.TailgatingCar4TnmKey][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.TailgatingCar4TnmKey][1] == sm_meta_info.camera_info.get("CameraID"))  and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.TailgatingCar4TnmKey][0]) >= AlarmDelay):
                                            IsDetected = True  
                                            DetectedEvent = BridgeDeviceConfigVariable.TailgatingCar4TnmKey
                                            BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.TailgatingCar4TnmKey][0] = int(sm_meta_info.detected_time)
                                            BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.TailgatingCar4TnmKey][1] = sm_meta_info.camera_info.get("CameraID")
                                            break 
                                        else:
                                            #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                            IsDetected = False
                                    #debut_message = ("\n#######::::: NEXT K4444 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                    #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                                    
                                    for tailgating_item in TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")]:
                                        if((int(time.time()) - int(tailgating_item[1])) >= (DetectDelay * 10)):
                                            TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")].remove(tailgating_item)
                                
                                TailgatingCarDataDict[sm_meta_info.camera_info.get("CameraID")].append([str(item.id), detected_time, str(item.framenumber)])

         
                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.Abandoned4TnmKey.lower() and 
                                item.eventtype == BridgeDeviceConfigVariable.Abandoned4Tnm and
                                 str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm"): ##Abandoned Baggage 
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.Abandoned4TnmKey][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.Abandoned4TnmKey][1] == sm_meta_info.camera_info.get("CameraID")) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.Abandoned4TnmKey][0]) >= int(AlarmDelay)):
                            
                                    IsDetected = True
                                    DetectedEvent = BridgeDeviceConfigVariable.Abandoned4TnmKey
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.Abandoned4TnmKey][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.Abandoned4TnmKey][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debug_message = ("\n#######::::: NEXT K0000 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)

                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.LoiteringPPE4TnmKey.lower() and 
                                item.eventtype == BridgeDeviceConfigVariable.LoiteringPPE4Tnm and
                                 str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm"): ##Loitering without PPE  
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringPPE4TnmKey][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringPPE4TnmKey][1] == sm_meta_info.camera_info.get("CameraID")) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringPPE4TnmKey][0]) >= int(AlarmDelay)):
                            
                                    IsDetected = True
                                    DetectedEvent = BridgeDeviceConfigVariable.LoiteringPPE4TnmKey
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringPPE4TnmKey][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.LoiteringPPE4TnmKey][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debug_message = ("\n#######::::: NEXT K0000 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
               
                            elif(str(AIServerList[AIServer].get("Analysis")).lower() == BridgeDeviceConfigVariable.RoadBlockCar4TnmKey.lower() and 
                                item.eventtype == BridgeDeviceConfigVariable.RoadBlockCar4Tnm and
                                str(AIServerList[AIServer].get("AnalysisVendor")).lower() == "tnm"): ##RoadBlock Car 
                                if((BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.RoadBlockCar4TnmKey][1] == "0000" or BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.RoadBlockCar4TnmKey][1] == sm_meta_info.camera_info.get("CameraID")) and int(sm_meta_info.detected_time) - int(BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.RoadBlockCar4TnmKey][0]) >= int(AlarmDelay)):
                            
                                    IsDetected = True
                                    DetectedEvent = BridgeDeviceConfigVariable.RoadBlockCar4TnmKey
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "Detected"
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.RoadBlockCar4TnmKey][0] = int(sm_meta_info.detected_time)
                                    BridgeDeviceConfigVariable.RecentResultList[int(sm_meta_info.camera_info.get("CameraID")) - 1][BridgeDeviceConfigVariable.RoadBlockCar4TnmKey][1] = sm_meta_info.camera_info.get("CameraID")
                                else:
                                    #check_AIServerList[AIServer]["AnalysisResult"]["Result"] = "UnDetected"
                                    IsDetected = False
                                debug_message = ("\n#######::::: NEXT K0000 AI Result = " + result_type + ":::::::" + str(AIServerList[AIServer].get("Analysis")) + ":::::")
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
     
                        
                        IsAIServerRunning = True

                        print("######## ======= IsDetected ######", IsDetected , AIServer)

                        if(IsDetected): 
                            print("###### DetectDely FrameStartTime FrameEndTime ", AlarmDelay, FrameStartTime, FrameEndTime)

                            InferenceFPS = int(sm_meta_info.camera_info.get("InferenceFPS"))
                            StartFrame = start_frame - (FrameStartTime * InferenceFPS)
                            EndFrame = start_frame + (FrameEndTime * InferenceFPS)
                            sm_meta_info.FrameDetected = start_frame
                            sm_meta_info.DetentionTime = int(FrameEndTime)
                            sm_meta_info.EndTimeStamp = int(time.time())

                            debug_message = ("############ StartFrame:{} EndFrame:{}  FrameStartTime : {}  FrameEndTime : {} ".format(StartFrame,EndFrame,FrameStartTime,FrameEndTime))
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                
                            for i in range(StartFrame,EndFrame):
                                image_file  = "{}/{}_{}/{}.jpeg".format(BridgeDeviceConfigVariable.ImageSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(i)).zfill(10))
                                if(os.path.isfile(image_file)):
                                    sm_meta_info.full_image_file_name = decimal_fill(i,10) + ".jpeg"
                                    sm_meta_info.thumbnail_image_file_name = decimal_fill(i,10) + ".jpeg"
                                    break

                            IsUploadTwoImage = False
                            for item in sm_meta_info.camera_info.get("SceneModeConfig"):
                                if str(item.get("Analysis")).lower().startswith("facility"):
                                    #item["AnalysisResult"]["Result"] = "Failed"
                                    break
                            
                            sm_meta_info.IsUploadTwoImage = IsUploadTwoImage   

                            debug_message = ("############ IsUploadTwoImage ".format(str(IsUploadTwoImage)))
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                
                            sm_meta_info.FrameStarted = StartFrame
                            sm_meta_info.FrameEnded = EndFrame

                            print("###### =====>>>>>>>sm_meta_info.DetectedEvent.append(DetectedEvent)" , DetectedEvent , len(sm_meta_info.DetectedEvent) )
                            sm_meta_info.DetectedEvent.append(DetectedEvent)
                            currenttime = current_milli_time()
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
                            sm_meta_info.ProcessTimeList.append(event_start_timedone)
                            sm_meta_info.ProcessTimeList.append(timedone)
                            #BridgeDeviceConfigVariable.SceneMarkList.put(sm_meta_info)
                            create_scenemark_as_file_sync(sm_meta_info)

                            #print("###################[GENERATE SCENEMARK DATA START$$$$$]  ==============================================")
                            #print(sm_meta_info.SceneMarkID,datetime.datetime.now())
                            #print("###################[[GENERATE SCENEMARK DATA END$$$$$]  ==============================================")
                            #print("\n\n")
                    
                except Exception as resEx:
                    print(traceback.format_exc())

                    SelfCheckYn = sm_meta_info.camera_info.get("SelfCheckYn")
                    if(SelfCheckYn == "Y"):
                        if(IsSelfCheckDone == False):
                            IsSelfCheckDone = True
                            SELF_CHECK_RESULT_API_ENDPOINT = BridgeDeviceConfigVariable.SELF_CHECK_RESULT_API_ENDPOINT.format(BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.BridgeDeviceID,sm_meta_info.camera_info.get("CameraID"),str(sm_meta_info.camera_info.get("SceneModeConfig")[0].get("CustomAnalysisStage")))

                            Data = {
                                "reportTime":sm_meta_info.camera_info.get("SelfCheckReportTime"),
                                "source":"BridgeDevice",
                                "target" : "AIserver",
                                "result":"fail"
                            }
                            headers = {'Authorization': sm_meta_info.camera_info.get("AccessToken"),'Accept': '*/*'}

                            #print("####### DATA ", json.dumps(Data))
                            answer = requests.post(SELF_CHECK_RESULT_API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
                            print("############# FAIL EVENTMANAGER ANSWER",SELF_CHECK_RESULT_API_ENDPOINT,answer)
                    
                    debug_message = "::: ERROR MESSAGE ::: " + str(resEx)
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                    pass
                


                
            if(IsAIServerRunning):
                SelfCheckYn = sm_meta_info.camera_info.get("SelfCheckYn")
                if(SelfCheckYn == "Y"):
                    #print("############# sm_meta_info.camera_info.SelfCheckYn",sm_meta_info.camera_info.SelfCheckYn,id(IsSelfCheckDone),IsSelfCheckDone,sm_meta_info)
                    #print("######## EVENT CUSTOMANALYSISSTAGE",len(sm_meta_info.camera_info.get("SceneModeConfig")),sm_meta_info.camera_info.get("SceneModeConfig")[0]["CustomAnalysisStage"])
                    if(IsSelfCheckDone == False):
                        IsSelfCheckDone = True 
                        SELF_CHECK_RESULT_API_ENDPOINT = BridgeDeviceConfigVariable.SELF_CHECK_RESULT_API_ENDPOINT.format(BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.BridgeDeviceID,sm_meta_info.camera_info.get("CameraID"),str(sm_meta_info.camera_info.get("SceneModeConfig")[0].get("CustomAnalysisStage")))

                        Data = None
                        Data = {
                            "reportTime":sm_meta_info.camera_info.get("SelfCheckReportTime"),
                            "source":"BridgeDevice",
                            "target" : "AIserver",
                            "result":"success"
                        }
                        headers = {'Authorization': sm_meta_info.camera_info.AccessToken,'Accept': '*/*'}
                        #print("####### DATA ", IsSelfCheckDone , json.dumps(Data))
                        answer = requests.post(SELF_CHECK_RESULT_API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
                        print("############# EVENTMANAGER ANSWER",SELF_CHECK_RESULT_API_ENDPOINT,answer)
                
def scenemark_metadata_event_manager(CameraID):
    global IsSelfCheckDone
    while(True):
        try:
            for k in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
                CameraID = str(int(k+1)).zfill(4)
                MetaFileDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.MetaDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                if(os.path.isdir(MetaFileDirectory)):
                    file_list = os.listdir(MetaFileDirectory)
                    file_list.sort()
                    #print(MetaFileDirectory,len(file_list))
                    for item in file_list:
                        metadata_file = MetaFileDirectory + "/" + item
                        if os.path.isfile(metadata_file) and os.path.getsize(metadata_file) > 0:
                            StartTime = time.time()
                            with open(metadata_file,"rb") as f:
                                unpickler = pickle.Unpickler(f)
                                sm_meta_info = unpickler.load()
                                if(os.path.isfile(metadata_file)):
                                    os.remove(metadata_file)
                                #print("####:::#### Performance Test EventManager Start ####:::####", time.time(), sm_meta_info[0].camera_info.CameraID,sm_meta_info[0].frame_num)
                                send_scenemark_metadata_to_algorithm(sm_meta_info)
                                #print("####:::#### Performance Test EventManager End ####:::####", time.time(), sm_meta_info[0].camera_info.CameraID,sm_meta_info[0].frame_num)
                                #print("####### metadata_file",metadata_file)
                
                            EndTime = time.time()   

                            debug_message = ("META DATA PROCESSING.... {}_{} {} : {} : {} ".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,StartTime,EndTime,EndTime-StartTime))      
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
        
        
        except Exception as ex:
            print(traceback.format_exc())

            if "RPC" in str(ex):
                if(len(sm_meta_info) > 0):
                    
                    SelfCheckYn = sm_meta_info[0].camera_info.get("SelfCheckYn")
                    if(SelfCheckYn == "Y"):
                        #print("############# sm_meta_info.camera_info.SelfCheckYn",sm_meta_info.camera_info.SelfCheckYn,id(IsSelfCheckDone),IsSelfCheckDone,sm_meta_info)
                        #print("######## EVENT CUSTOMANALYSISSTAGE",len(sm_meta_info.camera_info.get("SceneModeConfig")),sm_meta_info.camera_info.get("SceneModeConfig")[0]["CustomAnalysisStage"])
                        if(IsSelfCheckDone == False):
                            IsSelfCheckDone = True 
                            SELF_CHECK_RESULT_API_ENDPOINT = BridgeDeviceConfigVariable.SELF_CHECK_RESULT_API_ENDPOINT.format(BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.BridgeDeviceID,sm_meta_info[0].camera_info.CameraID,sm_meta_info[0].camera_info.get("SceneModeConfig")[0]["CustomAnalysisStage"])
                            Data = None
                            Data = {
                                "reportTime":sm_meta_info[0].camera_info.SelfCheckReportTime,
                                "source":"BridgeDevice",
                                "target" : "AIserver",
                                "result":"fail"
                            }
                            headers = {'Authorization': sm_meta_info[0].camera_info.AccessToken,'Accept': '*/*'}
                            #print("####### DATA ", IsSelfCheckDone , json.dumps(Data))
                            answer = requests.post(SELF_CHECK_RESULT_API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
                            print("############# EVENTMANAGER ANSWER",SELF_CHECK_RESULT_API_ENDPOINT,answer)
            
                    
            debug_message = ("#### ERROR Message  scenemark_metadata_event_manager::: " + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
            pass  
        
        time.sleep(TimeSleepProcess)


def scenemark_metadata_event_manager2(CameraID):
    global IsSelfCheckDone
    while(True):
        try:
            #CameraID = str(int(k+1)).zfill(4)
            MetaFileDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.MetaDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            if(os.path.isdir(MetaFileDirectory)):
                file_list = os.listdir(MetaFileDirectory)
                file_list.sort()
                #print(MetaFileDirectory,len(file_list))
                for item in file_list:
                    metadata_file = MetaFileDirectory + "/" + item
                    if os.path.isfile(metadata_file) and os.path.getsize(metadata_file) > 0:
                        StartTime = time.time()
                        with open(metadata_file,"rb") as f:
                            unpickler = pickle.Unpickler(f)
                            sm_meta_info = unpickler.load()
                            if(os.path.isfile(metadata_file)):
                                os.remove(metadata_file)
                            #print("####:::#### Performance Test EventManager Start ####:::####", time.time(), sm_meta_info[0].camera_info.CameraID,sm_meta_info[0].frame_num)
                            send_scenemark_metadata_to_algorithm(sm_meta_info)
                            #print("####:::#### Performance Test EventManager End ####:::####", time.time(), sm_meta_info[0].camera_info.CameraID,sm_meta_info[0].frame_num)
                            #print("####### metadata_file",metadata_file)
            
                        EndTime = time.time()   

                        debug_message = ("META DATA PROCESSING.... {}_{} {} : {} : {} ".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,StartTime,EndTime,EndTime-StartTime))      
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
    
    
        except Exception as ex:
            print(traceback.format_exc())

            if "RPC" in str(ex):
                if(len(sm_meta_info) > 0):
                    
                    SelfCheckYn = sm_meta_info[0].camera_info.get("SelfCheckYn")
                    if(SelfCheckYn == "Y"):
                        #print("############# sm_meta_info.camera_info.SelfCheckYn",sm_meta_info.camera_info.SelfCheckYn,id(IsSelfCheckDone),IsSelfCheckDone,sm_meta_info)
                        #print("######## EVENT CUSTOMANALYSISSTAGE",len(sm_meta_info.camera_info.get("SceneModeConfig")),sm_meta_info.camera_info.get("SceneModeConfig")[0]["CustomAnalysisStage"])
                        if(IsSelfCheckDone == False):
                            IsSelfCheckDone = True 
                            SELF_CHECK_RESULT_API_ENDPOINT = BridgeDeviceConfigVariable.SELF_CHECK_RESULT_API_ENDPOINT.format(BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.BridgeDeviceID,sm_meta_info[0].camera_info.CameraID,sm_meta_info[0].camera_info.get("SceneModeConfig")[0]["CustomAnalysisStage"])
                            Data = None
                            Data = {
                                "reportTime":sm_meta_info[0].camera_info.SelfCheckReportTime,
                                "source":"BridgeDevice",
                                "target" : "AIserver",
                                "result":"fail"
                            }
                            headers = {'Authorization': sm_meta_info[0].camera_info.AccessToken,'Accept': '*/*'}
                            #print("####### DATA ", IsSelfCheckDone , json.dumps(Data))
                            answer = requests.post(SELF_CHECK_RESULT_API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
                            print("############# EVENTMANAGER ANSWER",SELF_CHECK_RESULT_API_ENDPOINT,answer)
            
                    
            debug_message = ("#### ERROR Message  scenemark_metadata_event_manager::: " + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)
            pass  
        
        time.sleep(TimeSleepProcess)





def create_scenemark_as_file_sync(sm_meta_info):
    ## SceneMark Save
    BridgeDeviceID = sm_meta_info.device_id
    CameraID = sm_meta_info.camera_id 
    NodeID = int(sm_meta_info.camera_id)
    SceneMarkResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneMarkDirectory,BridgeDeviceID,CameraID)
    if not(os.path.isdir(SceneMarkResultDirectory)):
        os.mkdir(SceneMarkResultDirectory)

    SceneMarkID = sm_meta_info.SceneMarkID
    print("############SceneMark Result Data ",SceneMarkResultDirectory + "/" + SceneMarkID + ".dat")
    with open(SceneMarkResultDirectory + "/" + SceneMarkID + ".dat","wb") as f:
        pickle.dump(sm_meta_info,f)


def main():
    print("==========================================")
    print("::::: Algorithm Analysis is started...::::")
    print("==========================================")
    #threading.Thread(target=scenemark_metadata_event_manager,args=("",)).start()

    for CameraID in BridgeDeviceConfigVariable.range_list:
        threading.Thread(target=scenemark_metadata_event_manager2,args=(CameraID,)).start()


def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable

    '''
    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventManager) > 1):
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


