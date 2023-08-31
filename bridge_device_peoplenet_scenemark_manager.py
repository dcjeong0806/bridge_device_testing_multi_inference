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
from Scenera_GenerateNewScenemark import CreateSceneMark,CreateSceneMark2, SceneMarkValues
from Scenera_GenerateNewSceneData import CreateSceneData, SceneDataValues
from BridgeDeviceInfo import CameraMetaInfoClass, parsing_camerainfo, GetCameraID, SceneModeConfigClass, PipeLineInfoClass,check_bridge_device_process,SMDetectedObjectInfo, DetectedMetaInfo, DetectedObjectInfo
from PythonUtils import printDebug, GetFileSizeBytes
from CMFHeaders import CreateCMFHeaders, CreateCMFHeaders2
from Scenera_SceneMode import GetSceneMode
from Scenera_BridgeLib import GetSceneDataInfo, GetSceneMarkInfo, GetSceneDataVideoInfo, GetVideoURL,GetDateTime, DeviceNodeID, DevicePortID, CreateSceneMarkID, CreateSceneDataID
from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID, GetNICELAEndPointAuthority, GetNICELAEndPointEndPoint
from Scenera_ManagementObject import GetManagementObject, GetManagementObjectInfo
from bridge_device_peoplenet_config import VariableConfigClass, DebugPrint, decimal_fill
#from bridge_device_peoplenet_event_manager import create_scenemark_as_file_sync

import time
import sys
import math
import platform

import traceback
import json
import threading
from multiprocessing import Process, Queue
import concurrent.futures
import os
import datetime
import base64
import calendar

from sys  import getsizeof

import copy
import numpy as np
from tempfile import mkdtemp
import os.path as path

import json
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import pickle 

import shutil
current_milli_time = lambda: int(round(time.time() * 1000))
from bridge_device_peoplenet_config import VariableConfigClass
BridgeDeviceConfigVariable = VariableConfigClass()

IsSelfCheckDone = [False,False,False,False,False,False,False,False,False,False]

TimeSleepProcess = 1 

def check_schedule(SceneModeConfig, currentdetecttime):
    whatdayistoday = datetime.datetime.now().weekday()
    IsSkipSceneMarkProcessing = False
    try:
        for item in SceneModeConfig:
            #if(item["CustomAnalysisStage"] != "NewSceneMode" and not item["CustomAnalysisStage"].lower().startswith("falldown") and not item["CustomAnalysisStage"].lower().startswith("violence") and not item["CustomAnalysisStage"].lower().startswith("fire4nextk")):
            if(item["CustomAnalysisStage"] != "NewSceneMode" and not item["CustomAnalysisStage"].lower().startswith("falldown4nextk") and not item["CustomAnalysisStage"].lower().startswith("violence4nextk_exit") and not item["CustomAnalysisStage"].lower().startswith("fire4nextk")):
                ScheduledWeekDay = item["Scheduling"][0]
                ScheduledWeekend = item["Scheduling"][1]
                #currentdetecttime = int(time.strftime("%H%M"))


                debug_message = ("#### WEEKDAY",ScheduledWeekDay["StartTime"],ScheduledWeekDay["EndTime"])
                debug_message = debug_message + ("#### WEEKEND",ScheduledWeekend["StartTime"],ScheduledWeekend["EndTime"])
                debug_message = debug_message + ("#### CURRENTTIME",currentdetecttime, whatdayistoday)
                #currentdetecttime = int(currentdetecttime.replace(":",""))

                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
 
                if(whatdayistoday == 1 or whatdayistoday == 2 or whatdayistoday == 3):
                    StartTime = int(ScheduledWeekDay["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekDay["EndTime"].replace(":",""))
                    detectedtime = currentdetecttime
                    if EndTime < StartTime:
                        if detectedtime >=0 and detectedtime <= EndTime:
                            detectedtime = detectedtime + 2400
                        EndTime = EndTime + 2400
                    
                    if StartTime <= detectedtime and EndTime >= detectedtime:
                        IsSkipSceneMarkProcessing = True
                if(whatdayistoday == 4):
                    StartTime = int(ScheduledWeekDay["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekDay["EndTime"].replace(":",""))
                    detectedtime = currentdetecttime
                    if EndTime < StartTime:
                        if detectedtime >=0 and detectedtime <= EndTime:
                            detectedtime = detectedtime + 2400
                        EndTime = EndTime + 2400
                        if StartTime <= detectedtime and EndTime >= detectedtime:
                            IsSkipSceneMarkProcessing = True
                    else:
                        if StartTime <= detectedtime and EndTime >= detectedtime:
                            IsSkipSceneMarkProcessing = True

                if(whatdayistoday == 5):
                    StartTime = int(ScheduledWeekDay["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekDay["EndTime"].replace(":",""))
                    detectedtime = currentdetecttime
                    if EndTime < StartTime: ### check Fri to Sat 
                        StartTime = 0
                        if StartTime <= detectedtime and EndTime >= detectedtime:
                            IsSkipSceneMarkProcessing = True

                    
                    StartTime = int(ScheduledWeekend["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekend["EndTime"].replace(":",""))
                    detectedtime = currentdetecttime
                    if EndTime < StartTime:
                        if detectedtime >=0 and detectedtime <= EndTime:
                            detectedtime = detectedtime + 2400
                        EndTime = EndTime + 2400
                    
                    if StartTime <= detectedtime and EndTime >= detectedtime:
                        IsSkipSceneMarkProcessing = True

                if(whatdayistoday ==  6):
                    StartTime = int(ScheduledWeekend["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekend["EndTime"].replace(":",""))
                    detectedtime = currentdetecttime
                    if EndTime < StartTime:
                        if detectedtime >=0 and detectedtime <= EndTime:
                            detectedtime = detectedtime + 2400
                        EndTime = EndTime + 2400
                    
                    if StartTime <= detectedtime and EndTime >= detectedtime:
                        IsSkipSceneMarkProcessing = True

                if(whatdayistoday == 0):
                    #### Check Sunday 
                    StartTime = int(ScheduledWeekend["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekend["EndTime"].replace(":",""))
                    if(EndTime < StartTime):
                        detectedtime = currentdetecttime
                        StartTime = 0 
                        if StartTime <= detectedtime and EndTime >= detectedtime:
                            IsSkipSceneMarkProcessing = True

                    StartTime = int(ScheduledWeekDay["StartTime"].replace(":",""))
                    EndTime = int(ScheduledWeekDay["EndTime"].replace(":",""))
                    detectedtime = currentdetecttime
                    if EndTime < StartTime:
                        if detectedtime >=0 and detectedtime <= EndTime:
                            detectedtime = detectedtime + 2400
                        EndTime = EndTime + 2400
                    
                    if StartTime <= detectedtime and EndTime >= detectedtime:
                        IsSkipSceneMarkProcessing = True

    except Exception as ex:
        debug_message = "::: ERROR MESSAGE ::: = {}".format(str(ex))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        pass    

    return IsSkipSceneMarkProcessing


def create_scenemark_as_file_sync(sm_meta_info):
    ## SceneMark Save
    BridgeDeviceID = sm_meta_info.device_id
    CameraID = sm_meta_info.camera_id 
    NodeID = int(sm_meta_info.camera_id)
    SceneMarkResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneMarkDirectory,BridgeDeviceID,CameraID)
    if not(os.path.isdir(SceneMarkResultDirectory)):
        os.mkdir(SceneMarkResultDirectory)

    SceneMarkID = sm_meta_info.SceneMarkID
    #print("############SceneMark Result Data ",SceneMarkResultDirectory + "/" + SceneMarkID + ".dat")
    with open(SceneMarkResultDirectory + "/" + SceneMarkID + ".dat","wb") as f:
        pickle.dump(sm_meta_info,f)


def create_scenemark_sync(sm_meta_info):
    global IsSelfCheckDone

    image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.full_image_file_name).replace("//","/")
    if os.path.isfile(image_file_name):
        BridgeDeviceUUID = sm_meta_info.device_id
        NodeID = int(sm_meta_info.camera_id)
        PortID = 1234
        strCloudServerUUID = DeviceNodeID(BridgeDeviceUUID, NodeID)
        strCloudServerUUID = strCloudServerUUID.replace("_","-")
        #iSecondsToRecord = sm_meta_info.camera_info.RecordTime

        strCloudURL = "https://" + BridgeDeviceUUID
        Instance = current_milli_time()

        timedone = {
            "Process":"BD_SCENEMARK_ST",
            "TimeStamp":str(datetime.datetime.utcnow())
        }
        if(sm_meta_info.ProcessTimeList == None):
            sm_meta_info.ProcessTimeList = []
        sm_meta_info.ProcessTimeList.append(timedone)


        for item in sm_meta_info.ProcessTimeList:
            print(item.get("Process"),item.get("TimeStamp"))


        currentdetecttime = int(datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time)).strftime("%H%M"))
        CameraID = str(int(sm_meta_info.camera_id))

        if(True == True):
            headers = {'Accept': '*/*'}

            print("CameraID ====>>>>>>>>" , CameraID)
            r = requests.get(url = BridgeDeviceConfigVariable.ClearDetectedObjects + "/" + str(int(CameraID)), headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.ClearDetectedObjects,retval)

            for detected_info in sm_meta_info.detected_object_info_list:
                #if(detected_info.detected_object.lower() == "person"):
                detected_info.detected_object = "Human"
                
                detected_object_info = "/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(str(detected_info.confidence),str(detected_info.x1),str(detected_info.x1 + detected_info.width), str(detected_info.y1),str(detected_info.y1 + detected_info.height),str(detected_info.width),str(detected_info.height),str(CameraID), detected_info.detected_object,"None","None")


                thumbnail_image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.thumbnail_image_file_name).replace("//","/")

                print("++++++>>>>", detected_object_info, thumbnail_image_file_name)
                with open(thumbnail_image_file_name, "rb") as f:
                    data = f.read()
                    r = requests.post(url = BridgeDeviceConfigVariable.UpdateDetectedObjects + detected_object_info, data = data, headers=headers, timeout = 120, verify=False)  
                    retval = r.json()
                    print(BridgeDeviceConfigVariable.UpdateDetectedObjects,retval)
                break


            r = requests.get(url = BridgeDeviceConfigVariable.CreateVideoSceneDataID + "/12/1280/720/" + str(int(CameraID)), headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.CreateVideoSceneDataID,retval)

            for detected_event_item in sm_meta_info.DetectedEvent:
                debug_message = ("#####DETECTED EVENT ITEM " + detected_event_item)
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)  
                r = requests.get(url = BridgeDeviceConfigVariable.SendSceneMark + "/" + str(int(CameraID)) + "/1/" + detected_event_item + "/None", headers=headers, timeout = 120, verify=False)  
                retval = r.json()
                print(BridgeDeviceConfigVariable.SendSceneMark,BridgeDeviceConfigVariable.SendSceneMark + "/" + str(int(CameraID)) + "/1/" + detected_event_item + "/None",retval)


            r = requests.get(url = BridgeDeviceConfigVariable.SendDetectedObjectsSceneData + "/1280/720/" + str(int(CameraID)), headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.SendDetectedObjectsSceneData,retval)

            thumbnail_image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.thumbnail_image_file_name).replace("//","/")
            with open(thumbnail_image_file_name, "rb") as f:
                data = f.read()
                r = requests.post(url = BridgeDeviceConfigVariable.SendFullImageSceneData + "/1280/720/" + str(int(CameraID)),data = data, headers=headers, timeout = 120, verify=False)  
                retval = r.json()
                print(BridgeDeviceConfigVariable.SendFullImageSceneData,retval)

            if sm_meta_info.IsUploadTwoImage == False:   
                sm_meta_info.SceneMarkIsDone = True
                #if(sm_meta_info.SceneMarkIsDone):
                if os.path.isdir(BridgeDeviceConfigVariable.SceneDataDirectory) == False:
                    os.mkdir(BridgeDeviceConfigVariable.SceneDataDirectory)
                
                if os.path.isdir(BridgeDeviceConfigVariable.SceneDataDirectory + "/" + BridgeDeviceConfigVariable.BridgeDeviceID + "_" + sm_meta_info.camera_id) == False:
                    os.mkdir(BridgeDeviceConfigVariable.SceneDataDirectory + "/" + BridgeDeviceConfigVariable.BridgeDeviceID + "_" + sm_meta_info.camera_id)
                SceneDataResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,sm_meta_info.camera_id)
                if(os.path.isdir(SceneDataResultDirectory) == False):
                    os.mkdir(SceneDataResultDirectory)
                with open(SceneDataResultDirectory + "/" + sm_meta_info.SceneMarkID + ".done","wb") as f:
                    pickle.dump(sm_meta_info,f)


            pass
    else:
        debug_message = ("NoImageFile:" + image_file_name,datetime.datetime.now())
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                   

def upload_result_scenemark():
    #xxprint("Upload Result SceneMark Thread is started...")
    while(True):
        try:
            for k in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
                CameraID = str(int(k+1)).zfill(4)
                UploadSceneMarkDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneMarkDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                if(os.path.isdir(UploadSceneMarkDirectory)):
                    file_list = os.listdir(UploadSceneMarkDirectory)
                    file_list.sort()
                    #print(UploadSceneMarkDirectory,len(file_list))

                    for item in file_list:
                        scenemark_file = UploadSceneMarkDirectory + "/" + item
                        if os.path.isfile(scenemark_file) and os.path.getsize(scenemark_file) > 0:
                            with open(UploadSceneMarkDirectory + "/" + item,"rb") as f:
                                #print("##########################",scenemark_file)
                                unpickler = pickle.Unpickler(f)
                                sm_meta_info = unpickler.load()
                                #print("###################[UPLOADING SCENEMARK START]  ==============================================")
                                #print(sm_meta_info.SceneMarkID,datetime.datetime.now(),scenemark_file)
                                #print("###################[[UPLOADING SCENEMARK FILE END]  ==============================================")
                                #print("\n\n")
                                full_image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.full_image_file_name).replace("//","/")
                                thumbnail_image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.thumbnail_image_file_name).replace("//","/")
                                
                                currenttime = int(time.time())
                                TimeToUTC = 9 * 3600

                                #print(datetime.datetime.fromtimestamp(int(currenttime) - TimeToUTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")
                                #print(datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time) - TimeToUTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")

                            
                                #print("#######++++++++++========>",sm_meta_info.detected_time)
                                scenemark_time = (currenttime - int(sm_meta_info.detected_time)) * int(sm_meta_info.camera_info.get("InferenceFPS"))

                                #debug_message = str(currenttime) + ":::::" + str(sm_meta_info.detected_time) + ":::::" + str(sm_meta_info.camera_info.InferenceFPS)
                                #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                                #debug_message = (str(BridgeDeviceConfigVariable.DETENTION_FRAME) +  "######## SCENEMARKTIME : DETENTIONTIME " + str(scenemark_time) + ":::" + str(BridgeDeviceConfigVariable.DETENTION_FRAME))
                                #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                                if(scenemark_time < int(BridgeDeviceConfigVariable.DETENTION_FRAME) or True == True):
                                    if os.path.isfile(full_image_file_name) and os.path.isfile(thumbnail_image_file_name): # or True==True):
                                    #try:
                                        StartTime = time.time()
                                        
                                        #print("####:::#### Performance Test SceneMarkManager Start ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)
                                        #print("#######################scenemark_file remove.....",scenemark_file)
                                        
                                        
                                        if(os.path.isfile(scenemark_file)):
                                            os.remove(scenemark_file)
                                        create_scenemark_sync(sm_meta_info)
                                        #print("#########create_scenemark_sync is done... ")
                            
                                        EndTime = time.time()
                                        #print("####:::#### Performance Test SceneMarkManager End ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)



                                        #debug_message = ("####### RESULT #########$$$$$$$$$$$ CameraID" + CameraID + ":::" + str(StartTime) + ":::" + str(EndTime) + ":::" + "[#" + str(EndTime-StartTime) + "#]" + ":::" + str(datetime.datetime.now()))
                                        #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                                        #for detected_event_item in sm_meta_info.DetectedEvent:
                                        #    debug_message = ("#####DETECTED EVENT ITEM " + detected_event_item)
                                        #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                                    #except Exception as file_ex:
                                    #    debug_message = (":::::: Error Message ::::::" + str(file_ex))
                                    #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                                    #    pass
                                    else:
                                        #debug_message = ("####### IMAGE IS NOT GENERATED..." + thumbnail_image_file_name + ":::: " + full_image_file_name)
                                        #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)
                                        #if(scenemark_time > BridgeDeviceConfigVariable.DETENTION_FRAME): 
                                        #    if(os.path.isfile(scenemark_file)):
                                        #        os.remove(scenemark_file)
                                        pass
                                else:
                                    debug_message = ("####### OLD SceneMark is removed..." + scenemark_file)
                                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)    
                                        
                                    os.remove(scenemark_file)
        

        except Exception as ex:
            print(traceback.format_exc())
            debug_message = ("2222:::::: Error Message ::::::" + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
            pass
        
        time.sleep(TimeSleepProcess)

def upload_result_scenemark2(CameraID):
    #xxprint("Upload Result SceneMark Thread is started...")
    while(True):
        try:
            UploadSceneMarkDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneMarkDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            if(os.path.isdir(UploadSceneMarkDirectory)):
                file_list = os.listdir(UploadSceneMarkDirectory)
                file_list.sort()
                #print(UploadSceneMarkDirectory,len(file_list))

                for item in file_list:
                    scenemark_file = UploadSceneMarkDirectory + "/" + item
                    if os.path.isfile(scenemark_file) and os.path.getsize(scenemark_file) > 0:
                        with open(UploadSceneMarkDirectory + "/" + item,"rb") as f:
                            #print("##########################",scenemark_file)
                            unpickler = pickle.Unpickler(f)
                            sm_meta_info = unpickler.load()
                            #print("###################[UPLOADING SCENEMARK START]  ==============================================")
                            #print(sm_meta_info.SceneMarkID,datetime.datetime.now(),scenemark_file)
                            #print("###################[[UPLOADING SCENEMARK FILE END]  ==============================================")
                            #print("\n\n")
                            full_image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.full_image_file_name).replace("//","/")
                            thumbnail_image_file_name = (sm_meta_info.clip_image_directory + "/" + sm_meta_info.thumbnail_image_file_name).replace("//","/")
                            
                            currenttime = int(time.time())
                            TimeToUTC = 9 * 3600

                            #print(datetime.datetime.fromtimestamp(int(currenttime) - TimeToUTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")
                            #print(datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time) - TimeToUTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")

                        
                            #print("#######++++++++++========>",sm_meta_info.detected_time)
                            scenemark_time = (currenttime - int(sm_meta_info.detected_time)) * int(sm_meta_info.camera_info.get("InferenceFPS"))

                            #debug_message = str(currenttime) + ":::::" + str(sm_meta_info.detected_time) + ":::::" + str(sm_meta_info.camera_info.InferenceFPS)
                            #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                            #debug_message = (str(BridgeDeviceConfigVariable.DETENTION_FRAME) +  "######## SCENEMARKTIME : DETENTIONTIME " + str(scenemark_time) + ":::" + str(BridgeDeviceConfigVariable.DETENTION_FRAME))
                            #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                            if(scenemark_time < int(BridgeDeviceConfigVariable.DETENTION_FRAME) or True == True):
                                if os.path.isfile(full_image_file_name) and os.path.isfile(thumbnail_image_file_name): # or True==True):
                                #try:
                                    StartTime = time.time()
                                    
                                    #print("####:::#### Performance Test SceneMarkManager Start ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)
                                    #print("#######################scenemark_file remove.....",scenemark_file)
                                    
                                    
                                    if(os.path.isfile(scenemark_file)):
                                        os.remove(scenemark_file)
                                    create_scenemark_sync(sm_meta_info)
                                    #print("#########create_scenemark_sync is done... ")
                        
                                    EndTime = time.time()
                                    #print("####:::#### Performance Test SceneMarkManager End ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)



                                    #debug_message = ("####### RESULT #########$$$$$$$$$$$ CameraID" + CameraID + ":::" + str(StartTime) + ":::" + str(EndTime) + ":::" + "[#" + str(EndTime-StartTime) + "#]" + ":::" + str(datetime.datetime.now()))
                                    #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                                    #for detected_event_item in sm_meta_info.DetectedEvent:
                                    #    debug_message = ("#####DETECTED EVENT ITEM " + detected_event_item)
                                    #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    

                                #except Exception as file_ex:
                                #    debug_message = (":::::: Error Message ::::::" + str(file_ex))
                                #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                                #    pass
                                else:
                                    #debug_message = ("####### IMAGE IS NOT GENERATED..." + thumbnail_image_file_name + ":::: " + full_image_file_name)
                                    #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)
                                    #if(scenemark_time > BridgeDeviceConfigVariable.DETENTION_FRAME): 
                                    #    if(os.path.isfile(scenemark_file)):
                                    #        os.remove(scenemark_file)
                                    pass
                            else:
                                debug_message = ("####### OLD SceneMark is removed..." + scenemark_file)
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)    
                                    
                                os.remove(scenemark_file)
    

        except Exception as ex:
            print(traceback.format_exc())
            debug_message = ("2222:::::: Error Message ::::::" + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
            pass
        
        time.sleep(TimeSleepProcess)


def main():
    print("==========================================")
    print("::::: Uploading SceneMark is started...::::")
    print("==========================================")
    
    upload_result_scenemark()
    
    #for CameraID in BridgeDeviceConfigVariable.range_list:
    #    threading.Thread(target=upload_result_scenemark2,args=(CameraID,)).start()
    
## LoadBridgeDeviceSecurityObject Disabled until it works 2020-09-24 DCJeong
def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable
    '''
    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager) > 1):
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