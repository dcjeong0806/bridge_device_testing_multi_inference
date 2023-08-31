from ast import Pass
from asyncio import open_connection
from cProfile import run
from posixpath import split
from xml.dom.pulldom import parseString
from Scenera_GenerateNewScenemark import CreateSceneMark, SceneMarkValues
from Scenera_GenerateNewSceneData import CreateSceneData, SceneDataValues
from BridgeDeviceInfo import CameraMetaInfoClass, parsing_camerainfo, GetCameraID, SceneModeConfigClass, PipeLineInfoClass,check_bridge_device_falldown_fight_process,check_bridge_device_process,kill_bridge_device_falldown_fight_process,kill_bridge_device_process,SMDetectedObjectInfo, DetectedMetaInfo, DetectedObjectInfo
from PythonUtils import printDebug, GetFileSizeBytes
from CMFHeaders import CreateCMFHeaders
from Scenera_SceneMode import GetSceneMode
from Scenera_BridgeLib import GetSceneDataInfo, GetSceneMarkInfo, GetSceneDataVideoInfo, GetVideoURL,GetDateTime, DeviceNodeID,DeviceNodeID_INT, DevicePortID,DevicePortID_INT, CreateSceneMarkID, CreateSceneDataID
from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID, GetDevicePassword, GetNICELAEndPointAuthority, GetNICELAEndPointEndPoint
from Scenera_ManagementObject import GetManagementObject, GetManagementObjectInfo
from RestAPI import RestAPIPost, RstAPIGet, RestAPIGet_With_AccessToken, RestAPIPost_With_AccessToken_FirmWare
from bridge_device_peoplenet_config import VariableConfigClass, DebugPrint, current_milli_time
import threading
import time
import json
import urllib3
import pickle 
import os
import signal
import subprocess
import sys
import datetime
from datetime import timezone
import requests
import base64
from dotenv import load_dotenv
import msal
from requests import get 
import psutil

#import paho.mqtt.client as mqtt 
from collections import deque

import traceback

from typing import Iterable, Dict 
import logging
logger = logging
import getpass
#start_time 1900-01-01 00:00:00 end_time 1900-01-01 23:59:00  start time : 00:00:00 end time : 23:59:00 detect time : 10:36:48.644124
#start_time 1900-01-01 10:00:00 end_time 1900-01-01 06:00:00 start_time : 10:00:00 end time 06:00:00 detect time : 10:48:09.712898


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SubscribedObjectInfoList = deque()
TimeSleepProcess = 1

BridgeDeviceConfigVariable = VariableConfigClass()
BridgeDeviceRestreamManager = "bridge_device_peoplenet_restream_manager"

IsFacility = False

def decimal_fill(num,count):
    return str(int(num)).zfill(count)

def check_schedule(SceneModeConfig):
    whatdayistoday = datetime.datetime.now().weekday()
    IsSkipSceneMarkProcessing = False
    try:
        for item in SceneModeConfig:
            #if(item["CustomAnalysisStage"] != "NewSceneMode" and not item["CustomAnalysisStage"].lower().startswith("falldown") and not item["CustomAnalysisStage"].lower().startswith("violence") and not item["CustomAnalysisStage"].lower().startswith("fire4nextk")):
            if(item["CustomAnalysisStage"] != "NewSceneMode" and not item["CustomAnalysisStage"].lower().startswith("falldown4nextk") and not item["CustomAnalysisStage"].lower().startswith("violence4nextk_exit") and not item["CustomAnalysisStage"].lower().startswith("fire4nextk")):
                ScheduledWeekDay = item["Scheduling"][0]
                ScheduledWeekend = item["Scheduling"][1]
                currentdetecttime = int(time.strftime("%H%M"))

                #ScheduledWeekDay["StartTime"] = "23:59"
                #ScheduledWeekDay["EndTime"] = "04:00"
                #ScheduledWeekend["StartTime"] = "20:00"
                #ScheduledWeekend["EndTime"] = "04:00"
                #whatdayistoday = 0 
                #currentdetecttime = "05:00"
        
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

                '''
                for item2 in item["Scheduling"]:
                    Scheduling = item2
                    SchedulingType = Scheduling["SchedulingType"]


                    if(whatdayistoday >= 0 and whatdayistoday < 4 and SchedulingType == "ScheduledWeekDay"): ### Monday ~ Thurseday 
                        StartTime = int(Scheduling["StartTime"].replace(":",""))
                        EndTime = int(Scheduling["EndTime"].replace(":",""))
                        detectedtime = int(time.strftime("%H%M"))
                        if EndTime < StartTime:
                            if detectedtime >=0 and detectedtime <= EndTime:
                                detectedtime = detectedtime + 2400
                            EndTime = EndTime + 2400
                        

                        if StartTime <= detectedtime and EndTime >= detectedtime:
                            IsSkipSceneMarkProcessing = True
                            #print(item["CustomAnalysisStage"],IsSkipSceneMarkProcessing,StartTime,detectedtime,EndTime)

                            #break
                    elif(whatdayistoday > 4 and whatdayistoday < 7 and SchedulingType == "ScheduledWeekEnd"):
                        StartTime = int(Scheduling["StartTime"].replace(":",""))
                        EndTime = int(Scheduling["EndTime"].replace(":",""))
                        detectedtime = int(time.strftime("%H%M"))

                        if EndTime < StartTime:
                            if detectedtime >=0 and detectedtime <= EndTime:
                                detectedtime = detectedtime + 2400
                            EndTime = EndTime + 2400
                        

                        if StartTime <= detectedtime and EndTime >= detectedtime:
                            IsSkipSceneMarkProcessing = True
                            break
                #if(IsSkipSceneMarkProcessing):
                #    break
                '''
    except Exception as ex:
        debug_message = "::: ###ERROR MESSAGE ::: = {}".format(str(ex))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        pass    

    return IsSkipSceneMarkProcessing

def check_schedule2(
    scenemode_config: Iterable[Dict[str, str]], 
    detect_time: datetime.datetime = datetime.datetime.now(),
    custom_analysis_prefix: str = None
) -> bool:
    
    weekend = (
        detect_time.weekday() > 4
    )
    
    schedule_index = 1 if weekend else 0 

    for config in scenemode_config: 
        try:
            custom_stage = config.get("CustomAnalysisStage") or ""
            if custom_stage.lower() == "newscenemode":
                continue 

            if not custom_stage.startswith(custom_analysis_prefix or ""):
                continue

            if not config.get("Scheduling"):
                continue 

            schedule = config["Scheduling"][schedule_index]
            start_time = datetime.datetime.strptime(schedule["StartTime"], "%H:%M")
            end_time = datetime.datetime.strptime(schedule["EndTime"], "%H:%M")

            print("start_time", start_time, "end_time", end_time, start_time.time(), end_time.time(), detect_time.time())

            if start_time.time() <= detect_time.time() <= end_time.time():
                logger.info(
                    "detect time: %s falls within schedule: %s",
                    detect_time.strftime("%A %H:%M:%S"),
                    schedule,
                )
                return True

        except (IndexError, KeyError, ValueError ) as _e:
            logger.error("mangled schedule, invalid: %s\n%s", _e, config.get("Scheduling"))
    
    logger.debug(
        "detection at %s with custom analysis prefix %s is not within the scenemode's schedules",
        detect_time.strftime("%A %H:%M:%S"),
        custom_analysis_prefix,
        scenemode_config,
    )



    return False

def download(url, file_name):
    # open in binary mode
    #url = url.replace("//scenera.live","//tnmbss.scenera.live")
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)


def delete_video_image():
    debug_message = "{} is running....".format(sys._getframe().f_code.co_name)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
    while(True):
        try:
            #for i in range(0,len(BridgeDeviceConfigVariable.range_list)):
            for i in BridgeDeviceConfigVariable.range_list:
                #camera_number = i + 1
                #CameraID = str(int(camera_number)).zfill(4)
                CameraID = i 
                if(BridgeDeviceConfigVariable.BridgeDeviceID != ""):
                    #if(BridgeDeviceConfigVariable.InferencingManagerEnable or True == True):
                    ### Delete Event Image 
                    clip_image_directory = "{}/{}_{}".format(BridgeDeviceConfigVariable.ImageSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                    if(os.path.isdir(clip_image_directory) ):   
                        file_list = os.listdir(clip_image_directory)
                        file_list.sort()
                        frame_number = 0
                        for f in file_list:
                            filename = f.replace(".jpeg","").replace("_blurred","").replace("_360","")
                            frame_number = int(filename) - BridgeDeviceConfigVariable.DETENTION_FRAME

                        for f in file_list:
                            filename = f.replace(".jpeg","").replace("_blurred","").replace("_360","")
                            current_frame = int(filename)

                            if(current_frame < frame_number):
                                os.remove(clip_image_directory + "/" + f)
                                debug_message = "Remove Normal Image : {}/{}".format(clip_image_directory,f)
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                    else:
                    #### Remove Fire Image
                        if(os.path.isdir(BridgeDeviceConfigVariable.FireImageSaveDirectory)):
                            clip_fire_image_directory = "{}{}_{}".format(BridgeDeviceConfigVariable.FireImageSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                            if(os.path.isdir(clip_fire_image_directory) ):   
                                file_list = os.listdir(clip_fire_image_directory)
                                file_list.sort()
                                frame_number = 0
                                for f in file_list:
                                    f_list = f.split("_")
                                    filename = f_list[2]
                                    frame_number = int(filename) - BridgeDeviceConfigVariable.DETENTION_FRAME

                                for f in file_list:
                                    f_list = f.split("_")
                                    filename = f_list[2]
                                    current_frame = int(filename)
                                    if(current_frame < frame_number):
                                        os.remove(clip_fire_image_directory + "/" + f)
                                        debug_message = "Remove Fire Image : {}/{}".format(clip_fire_image_directory,f)
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                        
                        if(os.path.isdir(BridgeDeviceConfigVariable.FightFallDownVideoSaveDirectory)):
                            clip_falldown_fight_image_directory = "{}/{}_{}".format(BridgeDeviceConfigVariable.FightFallDownVideoSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                            if(os.path.isdir(clip_falldown_fight_image_directory) ):   
                                file_list = os.listdir(clip_falldown_fight_image_directory)
                                file_list.sort()
                                frame_number = 0
                                for f in file_list:
                                    filename = f.replace(".jpeg","")
                                    frame_number = int(filename) - BridgeDeviceConfigVariable.DETENTION_FRAME

                                for f in file_list:
                                    filename = f.replace(".jpeg","")
                                    current_frame = int(filename)
                                    if(current_frame < frame_number):
                                        os.remove(clip_falldown_fight_image_directory + "/" + f)
                                        debug_message = "Remove FallDown and Fight Image : {}/{}".format(clip_falldown_fight_image_directory,f)
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                    
                    #SMK_00000004-605d-a92e-8002-000000000014_0005_1796379b65b.dat
                    if(os.path.isdir(BridgeDeviceConfigVariable.MetaDataDirectory)):
                            metadata_directory = "{}{}_{}".format(BridgeDeviceConfigVariable.MetaDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                            if(os.path.isdir(metadata_directory) ):   
                                file_list = os.listdir(metadata_directory)
                                file_list.sort()
                                frame_number = 0
                                for f in file_list:
                                    f_list = f.split("_")
                                    filename = f_list[3].replace(".dat","")
                                    frame_number = int(int(filename,16) / 1000) - BridgeDeviceConfigVariable.DETENTION_FRAME

                                for f in file_list:
                                    f_list = f.split("_")
                                    filename = f_list[3].replace(".dat","")
                                    current_frame = int(filename)
                                    if(current_frame < frame_number):
                                        os.remove(metadata_directory + "/" + f)
                                        debug_message = "Remove MetaData File : {}/{}".format(metadata_directory,f)
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                        

        except Exception as ex:
            debug_message = "::: delete_video_image ERROR MESSAGE ::: = {}".format(str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            pass
        time.sleep(TimeSleepProcess)

def remove_files(directory):
    file_list = os.listdir(directory)
    file_list.sort()
    for i in range(len(file_list)):
        if os.path.isfile(directory + "/" + file_list[i]):
            os.remove(directory + "/" + file_list[i])


def check_bridge_device_process_status(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        #print("?????" + process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith(process_name + ".pyc")):                
                process_count = process_count + 1
                print("##### " + item + " is running...")
        return process_count
    except Exception as ex:
        print(str(ex))
        return process_count
        pass

def check_application_status():
    ### INFERENCE MANAGER
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceInferenceManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"InferenceManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("InferenceManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### EVENT MANAGER
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceEventManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"EventManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("EventManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### SCENEMARK MANAGER 
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager) == 0):
        status = "E"

    ApplicationStatus = {
        "ApplicationName":"SceneMarkManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("SceneMarkManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### SCENEDATA MANAGER 
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"SceneDataManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("SceneDataManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### FCILITY MANAGER
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"FacilityManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("FacilityManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    
    ### FALLDOWNFIGHT MANAGER
    status = "N"
    #if(check_bridge_device_process(BridgeDeviceConfigVariable.SceneModeManager) == 0):
    #    status = "E"
    ApplicationStatus = {
        "ApplicationName":"SceneModeManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("SceneModeManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

'''
def running_inference_manager():
    while(True):
        try:
            check_count = check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            #print("INFERENCE CHECK COUNT ", check_count)
            if( check_count == 0):
                os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceInferenceManager + ".pyc")
        except Exception as ex:
            print("running_inference_manager :::",str(ex))
        time.sleep(TimeSleepProcess)
'''

def check_bridge_device_process_inference(rtsp_camera_list, CameraList, process_name):
    IsProcessExisted = False 
    for proc in psutil.process_iter(['pid', 'name', 'username',"cmdline"]):
        if(proc.info["username"] == getpass.getuser() and proc.info["name"] == "python3" and len(proc.info["cmdline"]) > 2):
            if(proc.info["cmdline"][2] == rtsp_camera_list[2]): ## checking if same inference engine up or not 
                if(proc.info["cmdline"] == rtsp_camera_list):
                    print("########SAME RTSP_CAMERA_LIST =====>", rtsp_camera_list, proc.info["cmdline"])
                    IsProcessExisted = True 
                    break 
                else:
                    print("########DIFFERENT RTSP_CAMERA_LIST =====>", rtsp_camera_list, proc.info["cmdline"])
                    psutil.Process(proc.info["pid"]).kill()


    
    if(IsProcessExisted and False == True):
        for proc in psutil.process_iter(['pid', 'name', 'username',"cmdline"]):
            if(proc.info["username"] == getpass.getuser() and proc.info["name"] == "python3"):
                if(proc.info["cmdline"] == rtsp_camera_list):
                    pass 
                else:
                    if(proc.info["cmdline"][2] == rtsp_camera_list[2]):
                        if(len(proc.info["cmdline"]) != len(rtsp_camera_list[1])):
                            psutil.Process(proc.info["pid"]).kill()
                            break 

    
    for proc in psutil.process_iter(['pid', 'name', 'username',"cmdline"]):
        IsInferenceRunning = False 

        if(proc.info["username"] == getpass.getuser() and proc.info["name"] == "python3" and len(proc.info["cmdline"]) > 2):
            for inference_info in CameraList:
                if inference_info == proc.info["cmdline"][2] : 
                    IsInferenceRunning = True 
                    break 

            if(IsInferenceRunning == False):
                print(proc.info["pid"], proc.info["cmdline"])
                psutil.Process(proc.info["pid"]).kill()         
                
    if(len(CameraList) == 0):
        for proc in psutil.process_iter(['pid', 'name', 'username',"cmdline"]):
            if(proc.info["username"] == getpass.getuser() and proc.info["name"] == "python3" and len(proc.info["cmdline"]) > 1):
                if(process_name == proc.info["cmdline"][1]):
                    print(proc.info["pid"], proc.info["cmdline"])
                    psutil.Process(proc.info["pid"]).kill()  
                           

 
                            



    '''
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep '" + process_name + "'"],shell=True,encoding='utf-8')
        #print(">>>>>>>>>>>>>>>>> check_bridge_device_process >>>>>>>>>>>>>>>>>>\n",process)
        process_list = str(process.replace(" " , "")).split("\n")
        #print(process_name.replace(" ",""), ">>>>>>>>>>>>>>>>> process list .....  >>>>>>>>>>>>>>>>>>",process_list)

        for i in range(0, len(process_list)):
            #print("--------->>>>>>", i , process_list[i].replace("'",":"))

            process_list_item = str(process_list[i]).replace(" ","").replace("'",":")
            process_name = process_name.replace(" ","")
            
            #print("Input =====>>>>>", i , process_list_item, process_name)
            if(process_name in process_list_item and process_list_item != "" and "sh-c" not in process_list_item and "grep" not in process_list_item):
                #print("##########################============>>>>", process_list_item + " is running..." + process_name)
                process_count = process_count + 1
                
        return process_count
    except Exception as ex:
        #print(str(ex))
        return process_count
    '''
    
    return IsProcessExisted 



def start_inferencing(camera_meta_info, camera_list):
    os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceInferenceManager + "_each.py " + camera_meta_info + " " + camera_list)

def running_inference_manager2():
    while(True):
        try:
            CameraList = None 
            CameraList = {} 
            bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
            if(os.path.isfile(bridge_device_config_file_name) and os.path.getsize(bridge_device_config_file_name) > 0): ## checking configuration file is existed or not....
                with open(bridge_device_config_file_name,"rb") as f:
                    Config = json.loads(pickle.load(f))
                    if(Config):
                        BridgeDeviceInfo = Config["BridgeDeviceInfo"]

                        for camera_meta_info in BridgeDeviceInfo["CameraList"]:
                            CameraList[camera_meta_info.get("Distance")] = []

                        for camera_meta_info in BridgeDeviceInfo["CameraList"]:
                            CameraList[camera_meta_info.get("Distance")].append(camera_meta_info.get("CameraID"))
            
            #print("CameraList =====>>>>>>>",CameraList)
            process_name = BridgeDeviceConfigVariable.BridgeDeviceInferenceManager + "_each.py"
            if(len(CameraList) > 0):
                for inference_info in CameraList:
                    camera_list = "" 
            

                    rtsp_camera_list = []
                    rtsp_camera_list.append("python3")
                    rtsp_camera_list.append(process_name)
                    rtsp_camera_list.append(inference_info)
        
                    for camera in CameraList[inference_info]:
                        camera_list = camera_list + camera + " "
                        rtsp_camera_list.append(camera)
                    camera_list = camera_list.rstrip()
                    
                    #print("###### INFERENCE ENGINE ===>>>>>", BridgeDeviceConfigVariable.BridgeDeviceInferenceManager + "_each.py " + inference_info + " " + camera_list + "::::")
                    #check_count = check_bridge_device_process_inference(inference_info, BridgeDeviceConfigVariable.BridgeDeviceInferenceManager + "_each.py " + inference_info + " " + camera_list)
                    IsProcessExisted = check_bridge_device_process_inference(rtsp_camera_list, CameraList, process_name)

                    #print("INFERENCE CHECK COUNT ", check_count)
                    if(IsProcessExisted == False):
                        threading.Thread(target=start_inferencing,args=(inference_info,camera_list,)).start()
                        #os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceInferenceManager + "_each.py " + camera_meta_info.get("FrameWork") + " " + camera_meta_info.get("CameraID"))
                        #pass
            else:
                 for proc in psutil.process_iter(['pid', 'name', 'username',"cmdline"]):
                    if(proc.info["username"] == getpass.getuser() and proc.info["name"] == "python3" and len(proc.info["cmdline"]) > 1):
                        if(process_name == proc.info["cmdline"][1]):
                            print(proc.info["pid"], proc.info["cmdline"])
                            psutil.Process(proc.info["pid"]).kill()  




        except Exception as ex:
            print("running_inference_manager :::",str(ex) , traceback.format_exc())
        time.sleep(10)
        #time.sleep(TimeSleepProcess)


def running_event_manager():
    while(True):
        #print("####### EVENT MANAGER>>>>>>>>>>")
        try:
            if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventManager) == 0):
                os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceEventManager + ".pyc")
        except Exception as ex:
            print("running_event_manager :::",str(ex))
        time.sleep(TimeSleepProcess)

def running_scenemark_manager():
    while(True):
        try:
            if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager) == 0):
                os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager + ".pyc")
        except Exception as ex:
            print("running_scenemark_manager :::",str(ex))
        time.sleep(TimeSleepProcess)

def running_scenedata_manager():
    while(True):
        try:
            if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager) == 0):
                os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager + ".pyc")
            #time.sleep(2)
        except Exception as ex:
            print("Srunning_scenemark_manager :::",str(ex))
        time.sleep(10)

def running_event_facility_manager():
    while(True):
        try:
            if(IsFacility):
                if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager) == 0):
                    os.system("python3 " + BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager + ".pyc")
            else:
                kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
        except Exception as ex:
            print("running_event_facility_manager :::",str(ex))
        time.sleep(TimeSleepProcess)


def check_new_scenemode(SceneModeConfig,CameraID,rtsp_url,camera_info):
    for item in SceneModeConfig:
        #print(item.get("CustomAnalysisStage"))
        if(str(item.get("CustomAnalysisStage")).lower() == "newscenemode"):
            headers = {'Accept': '*/*'}

            NewSceneModeImageFile = "{}_{}.jpeg".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            command = "/usr/bin/ffmpeg -rtsp_transport tcp -i '{}' -vframes 1 -q:v 2 -y {}".format(rtsp_url.replace("rtspt","rtsp"),NewSceneModeImageFile)
            os.system(command)
            print("##### command " , command)

            print("CameraID ====>>>>>>>>" , CameraID)
            r = requests.get(url = BridgeDeviceConfigVariable.ClearDetectedObjects + "/" + str(int(CameraID)), headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.ClearDetectedObjects,retval)

            
            with open(NewSceneModeImageFile, "rb") as f:
                data = f.read()
                r = requests.post(url = BridgeDeviceConfigVariable.UpdateDetectedObjects + "/0.9/10/20/30/40/1280/720/" + str(int(CameraID)) + "/Human/Male/" + str(CameraID), data = data, headers=headers, timeout = 120, verify=False)  
                retval = r.json()
                print(BridgeDeviceConfigVariable.UpdateDetectedObjects,retval)
            

            r = requests.get(url = BridgeDeviceConfigVariable.CreateVideoSceneDataID + "/12/1280/720/" + str(int(CameraID)), headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.CreateVideoSceneDataID,retval)

            r = requests.get(url = BridgeDeviceConfigVariable.SendSceneMark + "/" + str(int(CameraID)) + "/1/Express/ItemPresenceCustom", headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.SendSceneMark,retval)


            r = requests.get(url = BridgeDeviceConfigVariable.SendDetectedObjectsSceneData + "/1280/720/" + str(int(CameraID)), headers=headers, timeout = 120, verify=False)  
            retval = r.json()
            print(BridgeDeviceConfigVariable.SendDetectedObjectsSceneData,retval)

            with open(NewSceneModeImageFile, "rb") as f:
                data = f.read()
                r = requests.post(url = BridgeDeviceConfigVariable.SendFullImageSceneData + "/1280/720/" + str(int(CameraID)),data = data, headers=headers, timeout = 120, verify=False)  
                retval = r.json()
                print(BridgeDeviceConfigVariable.SendFullImageSceneData,retval)

def running_scenera_library_manager():
    while(True):
        try:
            check_count = check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneraLibraryManager)
            #print("INFERENCE CHECK COUNT ", check_count)
            if( check_count == 0):
                os.system("python3 /home/ghosti/bridge_device/library_process/library/" + BridgeDeviceConfigVariable.BridgeDeviceSceneraLibraryManager + ".py")
        except Exception as ex:
            print("Scenera Library has been running already :::",str(ex))
        time.sleep(TimeSleepProcess)

def get_accesstoken(BSSAuthority):
    try:        
        AccessToken = None
        if(BridgeDeviceConfigVariable.ACCESSTOKEN_MODE == 1):
            Data = {
                "DeviceID":BridgeDeviceConfigVariable.BridgeDeviceID,
                "DevicePass":BridgeDeviceConfigVariable.BridgeDevicePassword,
                "AuthorityUri" : BridgeDeviceConfigVariable.AUTHORITY.replace("https://",""),
                "ClientID":BridgeDeviceConfigVariable.CLIENT_ID,
                "ClientSecret":BridgeDeviceConfigVariable.CLIENT_SECRET,
                "ResourceID":BridgeDeviceConfigVariable.INGEST_RESOURCE_ID
            }

            headers = {'Accept': '*/*'}
            print("######BridgeDeviceConfigVariable.LOGIN_TOKEN_ENDPOINT=","https://" + BSSAuthority + BridgeDeviceConfigVariable.LOGIN_TOKEN_ENDPOINT)
            print("#####DATA",json.dumps(Data))
            result = requests.post("https://" + BSSAuthority  + BridgeDeviceConfigVariable.LOGIN_TOKEN_ENDPOINT,json=Data,headers=headers,verify=False, stream=False).json()
            print("######### TOKEN ################",result["token"])
            AccessToken = result["token"]
        else:
            authority = BridgeDeviceConfigVariable.AUTHORITY
            debug_message = ("### AUTHORITY = " +  BridgeDeviceConfigVariable.AUTHORITY)   
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            # This is who you are. In this case you are the registered app called "Controller"
            client_id = BridgeDeviceConfigVariable.CLIENT_ID
            debug_message = ("### CLIENT_ID = " +  BridgeDeviceConfigVariable.CLIENT_ID)   
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            # This is the password associated with the privileges of "Controller", which amount to calling the Ingest
            client_secret = BridgeDeviceConfigVariable.CLIENT_SECRET
            debug_message = ("### CLIENT_SECRET = " +  BridgeDeviceConfigVariable.CLIENT_SECRET)   
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        
            # This is the api you are calling and need to be authorised for, so Ingest. This is not the same as an endpoint but it's like api//the_client_idof_ingest
            resource_id = BridgeDeviceConfigVariable.INGEST_RESOURCE_ID
            debug_message = ("### INGEST_RESOURCE_ID = " +  BridgeDeviceConfigVariable.INGEST_RESOURCE_ID)   
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        
            # Set up the client with your password and it will recognise you are a registered client entry
            app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

            # Get the token. You can do this because Ingest has allowed apps to connect to it and in the Azure portal I've granted the Controller access to it.
            result = app.acquire_token_for_client(resource_id)
            print(result)
            AccessToken = str(result['access_token'])
        
        debug_message = ("### access_token = " +  str(AccessToken))   
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
    except Exception as ex:
        debug_message = "::: Token Error MESSAGE ::: = {}".format(str(ex))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        pass
    return AccessToken

def get_selfcheck(AccessToken, BSSAuthority):
    response = None
    try:
        SELF_CHECK_ENDPOINT = "https://" + BSSAuthority + BridgeDeviceConfigVariable.SELF_CHECK_ENDPOINT + BridgeDeviceConfigVariable.BridgeDeviceID
        debug_message = ("### API ENDPOINT = " +  SELF_CHECK_ENDPOINT)   
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        response = RestAPIGet_With_AccessToken(SELF_CHECK_ENDPOINT,None,AccessToken)
        return response 
    except Exception as ex:
        debug_message = "::: SelfCheck Error MESSAGE ::: = {}".format(str(ex))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        pass
    return response




def start_get_scenemode():
    global scenemode   

    response = None
    SelfCheckReportTime = None
    SelfCheckYn = None
    AccessToken = None
    IsFirstTime = True
    ConnectingServerFailCount = 0
    BSSAuthority = "" 
    while(True):
        try:
            AccessToken = None
            IsFacility = False
            IsSelfCheckMode = False

            print("############# IS FIRST TIME ",IsFirstTime, "BSSAuthority=" + BSSAuthority)
            if(BSSAuthority is not ""):
                AccessToken = get_accesstoken(BSSAuthority)

                print("############# IS FIRST TIME AccessToken ",AccessToken, "BSSAuthority=" + BSSAuthority)
                if(AccessToken is not None and AccessToken is not ""):
                    response = get_selfcheck(AccessToken, BSSAuthority)
                    print("##>>>>>>>>>RESPONSE",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),response)
        except Exception as ex:
            print("### ERROR ", str(ex), traceback.format_exc())
            pass 
        
        try:
            if(response is not None):
                SelfCheckYn = response["SelfCheckYn"]
                SelfCheckReportTime = response["SelfCheckReportTime"]

            print(">>>>>> SELF CHECK YN =",SelfCheckYn)
            if(SelfCheckYn != "Y" and SelfCheckYn != "N"):
                IsSelfCheckMode = False
            elif(SelfCheckYn == "Y"):
                if(IsFirstTime):
                    kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                    kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager)
                    kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                    kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)
                    kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)
                    IsFirstTime = False
            else:
                bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
                if(os.path.isfile(bridge_device_config_file_name)):
                    with open(bridge_device_config_file_name,"rb") as f:
                        Config = json.loads(pickle.load(f))
                        if(Config):
                            BridgeDeviceInfo = Config["BridgeDeviceInfo"]
                            if(BridgeDeviceInfo["SelfCheckYn"] == "Y"):
                                IsSelfCheckMode = True
                else:
                    IsSelfCheckMode = False

            if(IsSelfCheckMode):
                pass
            else:
                try:
                    if(SelfCheckYn == "Y"):
                        create_directory()
                        SelfCheckConfig = response["SelfCheckConfig"]
                        for item in SelfCheckConfig:
                            SceneModeConfig = item["SceneModeConfig"]
                            NodeID = item["NodeID"].split("_")[1]

                            for item2 in SceneModeConfig:
                                CustomAnalysisStageUrl = item2["CustomAnalysisStageUrl"]
                                CustomAnalysisStage = item2["Analysis"] + "_" + NodeID + ".mp4"
                                if(CustomAnalysisStage.lower() != "newscenemode"):
                                    download(CustomAnalysisStageUrl,CustomAnalysisStage)
                except Exception as ex:
                    debug_message = "::: SelfCheck Error MESSAGE ::: = {}".format(str(ex))
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                    pass

                headers = {'Accept': '*/*'}
                r = requests.get(url = BridgeDeviceConfigVariable.IsFirstSceneModeReceived, headers=headers, timeout = 120, verify=False)  
                retval = r.json()

                camera_info_list = None
                camera_info_list = []
                if(ConnectingServerFailCount > 5):
                    print("Scenera Library Server Restarts ...............")
                    start_scenera_library_server()
                    ConnectingServerFailCount = 0 

                if(retval.get("IsFirstSceneModeReceived") == True):
                    try:
                        ConnectingServerFailCount = 0 
                        count = 0
                        print("#########################  BridgeDeviceConfigVariable.range_list",BridgeDeviceConfigVariable.range_list)
                        for cameraid in BridgeDeviceConfigVariable.range_list:
                            print("\n\n\n ####################################### ", cameraid)
                            count = count + 1
                            CameraID = GetCameraID(int(cameraid))
            
                            SceneMarkEndPoint = ""
                            SceneMarkToken = ""
                            SceneMarkAuthority = ""

                            SceneVideoEndPoint = ""
                            SceneVideoToken = ""
                            SceneVideoAuthority = ""

                            SceneImageEndPoint = ""
                            SceneImageToken = ""
                            SceneImageAuthority = ""

                            CameraFPS = 0
                            InferenceFPS = 0
                            UseYn = "N" 
                            DROP_FRAME_INTERVAL = 0 
                            Distance = "peoplenetnormal_tnm_person" + "_1.0"
                            rtsp_url = ""
                            SceneModeData = None 
                            OutputWidth = 640
                            OutputHeight = 360
                            MaxChunkSize = 1500000
    
                            print("##### SCENEMODE ", BridgeDeviceConfigVariable.GetSceneMode + "/" + str(int(cameraid)))    
                            r = requests.get(url = BridgeDeviceConfigVariable.GetSceneMode + "/" + str(int(cameraid)), headers=headers, timeout = 120, verify=False)  
                        
                            SceneModeData = r.json()
                            #print(cameraid , r.json())
                            debug_message = SceneModeData
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)


                            if(SceneModeData is not None):
                                Inputs = SceneModeData.get("Inputs")
                                Outputs = SceneModeData.get("Outputs")
                                Mode = SceneModeData.get("Mode")
                                BSSAuthority = Mode.get("BSSAuthority")
 
                                ClassList = None 
                                ResolutionWidth = 0 
                                ResolutionHeight = 0 

                                for item in Inputs:
                                    if(item.get("Active") == True):
                                        UseYn = "Y"

                                    DROP_FRAME_INTERVAL = int(item.get("DropFrameInterval"))
                                    CameraFPS = int(item.get("InputFrameRate"))
                                    InferenceFPS = int(CameraFPS / DROP_FRAME_INTERVAL)
                                    
                                    type_list = item.get("InferenceEngine").get("Type").split("_")
                                    FrameWork = type_list[0] 
                                    Distance = item.get("InferenceEngine").get("Type") + "_" + item.get("InferenceEngine").get("Version")
                                    rtsp_url = item.get("VideoEndPoint").get("VideoURI")
                                    ClassList = item.get("InferenceEngine").get("ClassList")
                                    ResolutionWidth = item.get("Resolution").get("Width")
                                    ResolutionHeight = item.get("Resolution").get("Height")
                                    break 

                                if(UseYn == "Y"):
                                    for item in Outputs:
                                        if(str(item.get("Type")) == "Video"):
                                            SceneVideoEndPoint = item.get("DestinationEndPointList")[0].get("AppEndPoint").get("EndPointID")
                                            SceneVideoAuthority = item.get("DestinationEndPointList")[0].get("NetEndPoint").get("Scheme")[0].get("Authority")
                                            SceneVideoToken = item.get("DestinationEndPointList")[0].get("AppEndPoint").get("AccessToken")
                                            OutputWidth = item.get("Resolution").get("Width")
                                            OutputHeight = item.get("Resolution").get("Height")
                                        elif(str(item.get("Type")) == "Image"): 
                                            SceneImageEndPoint = item.get("DestinationEndPointList")[0].get("AppEndPoint").get("EndPointID")
                                            SceneImageAuthority = item.get("DestinationEndPointList")[0].get("NetEndPoint").get("Scheme")[0].get("Authority")
                                            SceneImageToken = item.get("DestinationEndPointList")[0].get("AppEndPoint").get("AccessToken")
                                            
                                    SceneMarkEndPoint = Mode.get("SceneMarkOutputList")[0].get("SceneMarkOutputEndPoint").get("EndPointID")
                                    SceneMarkAuthority = Mode.get("SceneMarkOutputList")[0].get("SceneMarkOutputEndPoint").get("Scheme")[0].get("Authority") 
                                    SceneMarkToken = Mode.get("SceneMarkOutputList")[0].get("SceneMarkOutputEndPoint").get("AccessToken")

                                    #print(SceneMarkEndPoint)
                                    #print("\n\n\n")
                                    SelfCheckReportTime = ""
                                    SelfCheckYn = ""

                                    ### check newscenemode and upload newscenemode....

                                    try:
                                        camera_info = {
                                            "AccessToken" : SceneMarkToken,
                                            "SelfCheckReportTime":SelfCheckReportTime,
                                            "SelfCheckYn":SelfCheckYn,
                                            "RTSP_URL" : rtsp_url,
                                            "ResolutionWidth":ResolutionWidth,
                                            "ResolutionHeight":ResolutionHeight,
                                            "CameraFPS":CameraFPS,
                                            "InferenceFPS":InferenceFPS,
                                            "Distance":Distance,
                                            "FrameWork": FrameWork,
                                            "ClassList":ClassList,
                                            "DropFrameInterval":DROP_FRAME_INTERVAL,
                                            "SceneMode":SceneModeData,
                                            "CameraID":CameraID,
                                            "DeviceID" : BridgeDeviceConfigVariable.BridgeDeviceID,
                                            "SceneModeConfig":Mode.get("SceneModeConfig"),
                                            "SceneMarkEndPoint":SceneMarkEndPoint,
                                            "SceneMarkToken":SceneMarkToken,
                                            "SceneMarkAuthority":SceneMarkAuthority,
                                            "SceneVideoEndPoint":SceneVideoEndPoint,
                                            "SceneVideoToken":SceneVideoToken,
                                            "SceneVideoAuthority":SceneVideoAuthority,
                                            "SceneImageEndPoint":SceneImageEndPoint,
                                            "SceneImageToken":SceneImageToken,
                                            "SceneImageAuthority":SceneImageAuthority,
                                            }
                                        check_new_scenemode(Mode.get("SceneModeConfig"),CameraID,rtsp_url, camera_info)
                                        if(check_schedule(Mode.get("SceneModeConfig")) or SelfCheckYn == "Y"):
                                            camera_info_list.append(camera_info)
                                    except Exception as ex:
                                        print("EEEEEEEERRRORR ", str(ex))
                                        debug_message = "########::: #####ERROR MESSAGE####### ::: = {} {}".format(str(file_ex),traceback.format_exc())
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                                        print(debug_message)
                                
                        BridgeDeviceInfo = {
                            "BridgeDeviceInfo" : {
                                "SelfCheckYn" : SelfCheckYn,
                                "BSSAuthority" : BSSAuthority,
                                "ProcessInBridgeDevice":"N",
                                "MaxCameraConnection":BridgeDeviceConfigVariable.MAX_CAMERA_NODES,
                                "BridgeDeviceID":BridgeDeviceConfigVariable.BridgeDeviceID,
                                "FakeSink":BridgeDeviceConfigVariable.IsFakeSink,
                                "CameraList": camera_info_list
                            }
                        }

                        BridgeDeviceInfo = json.dumps(BridgeDeviceInfo)
                        with open(BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat","wb") as f:
                            pickle.dump(BridgeDeviceInfo,f)
                       
                    except Exception as file_ex:
                        debug_message = "########::: #####ERROR MESSAGE####### ::: = {} {}".format(str(file_ex),traceback.format_exc())
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                        print(debug_message)
                        pass
                else:
                    ConnectingServerFailCount += 1

        except Exception as ex:
            print("### ERROR ", str(ex), traceback.format_exc())
        time.sleep(30)      
        
def start_scenera_library_server():
    while(True):
        if(BridgeDeviceConfigVariable.BridgeDeviceID):
            try:
                if(os.path.isfile(BridgeDeviceConfigVariable.DeviceSeurityObjectFile)):
                    with open(BridgeDeviceConfigVariable.DeviceSeurityObjectFile) as DeviceSecurityObject:
                        data = json.load(DeviceSecurityObject)
                        headers = {'Accept': '*/*'}
                        r = requests.post(url = BridgeDeviceConfigVariable.SetDeviceSecurityObject, json = data, headers=headers, timeout = 120, verify=False)  
                        retval = r.json() 
                        print(BridgeDeviceConfigVariable.SetDeviceSecurityObject,retval)
                        if(retval.get("status") == "success"):
                            if(os.path.isfile(BridgeDeviceConfigVariable.DevicePrivateKeyFile)):
                                with open(BridgeDeviceConfigVariable.DevicePrivateKeyFile) as DevicePrivateKey:
                                    deviceprivatekey = json.load(DevicePrivateKey)
                                    r = requests.post(url = BridgeDeviceConfigVariable.SetDevicePrivateKey, json = deviceprivatekey, headers=headers, timeout = 120, verify=False)  
                                    retval = r.json() 
                                    print(BridgeDeviceConfigVariable.SetDevicePrivateKey,retval)
                                    if(retval.get("status") == "success"):
                                        r = requests.get(url = BridgeDeviceConfigVariable.StopSceneraProcesses,headers=headers, timeout = 120, verify=False) 
                                        print(r.json())
                                        print(BridgeDeviceConfigVariable.StopSceneraProcesses,retval)
                                        time.sleep(5) 
                                        r = requests.get(url = BridgeDeviceConfigVariable.StartSceneraProcesses + "/" + BridgeDeviceConfigVariable.NumberOfNodes + "/" + BridgeDeviceConfigVariable.RepeatPeriod ,headers=headers, timeout = 120, verify=False)  
                                        retval = r.json()
                                        print(BridgeDeviceConfigVariable.StartSceneraProcesses,retval)
                                        if(retval.get("status") == "success"):
                                            print("Scenera Library Server starts ...............")
                                            break
            except Exception as ex:
                print("Scenera Library is not on yet",str(ex))
                continue 
        time.sleep(TimeSleepProcess)
    return True 

def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable
    process_count = 1


    '''
    with open("./config.json") as config_f:
        config = json.load(config_f)
        display_mode = config["display_mode"]
        camera_list = config["camera_list"]
        if(display_mode == "Y"):
            process_count = 1
    '''


    #if "bridge_device_peoplenet_inferencing_manager_each.pyyolov80001" in "bridge_device_peoplenet_inferencing_manager_each.pyyolov80001""ghosti2564925615017:11pts/000:00:00/bin/sh-cps-ef|grep:" : 
    #    print("in ------> bridge_device_peoplenet_inferencing_manager_each.pyyolov80001")
    #else:
    #    print("not in ------> bridge_device_peoplenet_inferencing_manager_each.pyyolov80001")

    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager) > process_count):
        print("==========================================")
        print("there is same process running already. process is about to be terminated.")
        print("==========================================")
        sys.exit()

    command = "pkill -9 -ef main.py"
    os.system(command)
    
    running_scenera_library_manager_thread = threading.Thread(target=running_scenera_library_manager,args=())
    running_scenera_library_manager_thread.daemon = True
    running_scenera_library_manager_thread.start()

    print("#############",BridgeDeviceConfigVariable.DeviceSeurityObjectFile)
    if(os.path.isfile(BridgeDeviceConfigVariable.DeviceSeurityObjectFile)):
        with open(BridgeDeviceConfigVariable.DeviceSeurityObjectFile) as DeviceSecurityObject:
            SecurityObject = json.load(DeviceSecurityObject)
            DeviceInfo = GetDeviceSecurityObject(SecurityObject)
            BridgeDeviceConfigVariable.BridgeDeviceID = GetDeviceID(DeviceInfo)
            BridgeDeviceConfigVariable.BridgeDevicePassword = GetDevicePassword(DeviceInfo)
            #NICELAEndPoint = GetNICELAEndPointEndPoint(DeviceInfo)
            #NICELAAuthorty = GetNICELAEndPointAuthority(DeviceInfo)
            #print(BridgeDeviceConfigVariable.BridgeDeviceID,NICELAEndPoint,NICELAAuthorty, "is called...")
            #BridgeDeviceConfigVariable.DebugLog("","ErrorMessage ::: " + BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

            #ManagementInfo = GetManagementObject(NICELAAuthorty, BridgeDeviceID, NICELAEndPoint)
            #print(BridgeDeviceConfigVariable.BridgeDeviceID)
            #print(SecurityObject)

            if(start_scenera_library_server()):
                main()

def create_scenemark_for_new_scenemode(sm_meta_info):
    sm_meta_info.clip_image_directory = "."
    detected_object_info = DetectedObjectInfo()
    detected_object_info.top = 0
    detected_object_info.left = 0
    detected_object_info.width = 0
    detected_object_info.height = 0
    detected_object_info.x1 = 0 
    detected_object_info.x2 = 0
    detected_object_info.y1 = 0
    detected_object_info.y2 = 0
    detected_object_info.confidence = 0
    detected_object_info.detected_object = "None"
    detected_object_info.scenedata_name = ""
    sm_meta_info.detected_object_info_list = []
    sm_meta_info.detected_object_info_list.append(detected_object_info)

    image_file_name = sm_meta_info.clip_image_directory +"/" + sm_meta_info.full_image_file_name 
    

    debug_message = ("######################### new image file name " + image_file_name)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)



    if os.path.isfile(image_file_name):
        BridgeDeviceUUID = sm_meta_info.device_id
        NodeID = int(sm_meta_info.camera_id)
        PortID = 1234
        TimeToUTC = 9 * 3600

        strCloudServerUUID = DeviceNodeID(BridgeDeviceUUID, NodeID)
        strCloudServerUUID = strCloudServerUUID.replace("_","-")
        iSecondsToRecord = 0

        strCloudURL = "https://" + BridgeDeviceUUID
    
        Instance = current_milli_time()

        objSM = SceneMarkValues()
        objSM.SceneModeConfig = [{"CustomAnalysisStage": "NewSceneMode"}]
 
        objSM.sm_meta_info = sm_meta_info
        objSM.Version = "1.0"
        objSM.TimeStamp = datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time) - TimeToUTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        objSM.SceneMarkID = CreateSceneMarkID(BridgeDeviceUUID, int(NodeID), Instance)
        objSM.DestinationID = "00000001-5cdd-280b-8003-00020000ffff"
        objSM.SceneMarkStatus = "Active"
        objSM.NodeID = DeviceNodeID(BridgeDeviceUUID, NodeID)
        objSM.PortID = DevicePortID(BridgeDeviceUUID, NodeID, PortID)

        objSM.SceneMode = sm_meta_info.camera_info.SceneMode #"Label"
        objSM.Status = "Upload in Progress"
        objSM.CustomAnalysisID =  ""
        objSM.AnalysisDescription = "DeepStream Resnet-10 Detects {}".format(sm_meta_info.scenemode)
        objSM.ProcessingStatus = "Detect"
     
        #if(sm_meta_info.ProcessTimeList == None):
        sm_meta_info.ProcessTimeList = []


        ''' # PROCESS TIME LIST 
        timedone = {
            "Process":"BD_SCENEMARK_ST",
            "TimeStamp":str(datetime.datetime.utcnow())
        }
        if(sm_meta_info.ProcessTimeList == None):
            sm_meta_info.ProcessTimeList = []
        sm_meta_info.ProcessTimeList.append(timedone)
        objSM.ProcessTimeList = None
        objSM.ProcessTimeList = sm_meta_info.ProcessTimeList
        '''
        objSM.ProcessTimeList = []

        objSM.sm_meta_info = sm_meta_info



        objSM.detected_object_info_list = []
        for detected_info in sm_meta_info.detected_object_info_list:
            detected_object_info = SMDetectedObjectInfo()
            detected_object_info.AlgorithmID = "12345678-1234-1234-1234-123456789abc"
            detected_object_info.CustomItemType = detected_info.detected_object
            detected_object_info.NICEItemType = "Custom"
            detected_object_info.Resolution_Height = detected_info.height
            detected_object_info.Resolution_Width = detected_info.width
            detected_object_info.XCoordinate = detected_info.x1
            detected_object_info.YCoordinate = detected_info.y1
            detected_object_info.scenedata_name = detected_info.scenedata_name
            objSM.detected_object_info_list.append(detected_object_info)

        objSM.Video_Duration = str(iSecondsToRecord)

        objSM.DateTimeStamp = objSM.TimeStamp #datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time - TimeToUTC)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        objSM.SceneDataList_TimeStamp = objSM.DateTimeStamp


        objSM.SourceNodeID = DeviceNodeID(BridgeDeviceUUID,NodeID)
        #objSM.TimeStamp = datetime.datetime.fromtimestamp(int(sm_meta_info.detected_time - TimeToUTC)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        currenttime = str(current_milli_time())

        objSM.DetectedObjects_Image_DataType = "RGBStill"
        objSM.DetectedObjects_Image_MediaFormat = "JPEG"
        objSM.DetectedObjects_Image_SceneDataURI =  strCloudURL + "/" + objSM.NodeID.replace("_","-") + "/" + currenttime + ".jpeg"
        DetectedObjects_Image_SceneDataID = CreateSceneDataID(BridgeDeviceUUID,int(NodeID),int(currenttime) + 1)
        objSM.DetectedObjects_Image_SceneDataID = "{}".format(DetectedObjects_Image_SceneDataID)


        currenttime = str(current_milli_time())
        objSM.DetectedObjects_Thumbnail_DataType = "RGBStill"
        objSM.DetectedObjects_Thumbnail_MediaFormat  = "JPEG"
        objSM.DetectedObjects_Thumbnail_SceneDataURI = strCloudURL + "/" + objSM.NodeID.replace("_","-") + "/" + currenttime + ".jpeg"
        DetectedObjects_Thumbnail_SceneDataID = CreateSceneDataID(BridgeDeviceUUID,int(NodeID),int(currenttime) + 2)
        objSM.DetectedObjects_Thumbnail_SceneDataID = "{}".format(DetectedObjects_Thumbnail_SceneDataID)



        objSM.DetectedObjects_Video_SceneDataID = objSM.DetectedObjects_Image_SceneDataID


        StartTime = time.time()
        scenemark_endpoint = "https://{}/1.0/123-1234/data/0000/0000/setSceneMark".format(sm_meta_info.camera_info.SceneMarkAuthority)
        scenedata_endpoint = "https://{}/1.0/uuid/data/0000/0002/setSceneData".format(sm_meta_info.camera_info.SceneDataAuthority)

        debug_message = ("scenmark_endpoint={}\nscenedata_endpoint={}".format(scenemark_endpoint,scenedata_endpoint))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

        try:
            dictNiceSceneMark = {} #Scenera
            dictNiceSceneMark = CreateSceneMark(objSM)
            dictNiceSceneMark = (((dictNiceSceneMark)))
            AccessToken = sm_meta_info.camera_info.SceneMarkToken
            scenemark = CreateCMFHeaders(str(dictNiceSceneMark), BridgeDeviceUUID, strCloudServerUUID, NodeID, PortID, AccessToken)

            scenemark = json.dumps(scenemark)
            scenemark = scenemark.replace("'",'\\"').replace('\0', '')
            
            print("\n\n\n #####+++++++++++++>>>>>>>>>>>>>>> NEW SCENEMODE +++++++++++++",scenemark,"\n\n\n")

            header = {'Authorization': 'Bearer ' + AccessToken,
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'}

            answer = requests.post(scenemark_endpoint,data=scenemark, headers=header, verify=False, stream=False).json()

            debug_message = "SceneMark is Done : {} , Reply Status Code : {}".format(objSM.SceneMarkID,str(answer))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            print(debug_message)

            image_file_name = sm_meta_info.clip_image_directory +"/" + sm_meta_info.full_image_file_name 
            with open(image_file_name,"rb") as image_file:
                fileSize = GetFileSizeBytes(image_file_name)
                iChunkSizeBytes = 1500000
                iChunkNumberRounded = int(fileSize / iChunkSizeBytes)
                iNumberOfBytes = iChunkNumberRounded * iChunkSizeBytes

                if fileSize > iNumberOfBytes:
                    iNumberOfChunks = iChunkNumberRounded + 1
                else:
                    iNumberOfChunks = iChunkNumberRounded

                iChunkNumber = 1

                ##xxprint("iNumberOfChunks={}".format(str(iNumberOfChunks)))
                while iChunkNumber <= iNumberOfChunks:
                    strBase64 = str(base64.b64encode(image_file.read(iChunkSizeBytes)).decode())
                    objSD = SceneDataValues()
                    objSD.Version = "1.0"
                    objSD.DataID = objSM.DetectedObjects_Image_SceneDataID
                    objSD.FileType = "Image"
                    objSD.FileName = sm_meta_info.full_image_file_name 
                    objSD.PathURI = objSM.DetectedObjects_Image_SceneDataURI
                    objSD.Section = iChunkNumber
                    objSD.LastSection = iNumberOfChunks 
                    objSD.HashMethod = "SHA256"
                    objSD.OriginalFileHash="ABCDEFGHIJKLMNO" + currenttime
                    objSD.SectionBase64 = strBase64
                    objSD.RelatedSceneMarks = []
                    objSD.RelatedSceneMarks.append(objSM.SceneMarkID)

                    dictNiceSceneData = CreateSceneData(objSD)
                    AccessToken = sm_meta_info.camera_info.SceneDataToken
                    scenedata = CreateCMFHeaders(str(dictNiceSceneData), BridgeDeviceUUID, strCloudServerUUID, NodeID, PortID, AccessToken)
                    scenedata = json.dumps(scenedata)
                    scenedata = scenedata.replace("'",'\\"').replace('\0', '')


                    #answer = requests.post(scenedata_endpoint,data=scenedata, headers=header, verify=False, stream=False).json() 
                    header = {'Authorization': 'Bearer ' + AccessToken,
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'}              
                    #print(scenedata)
                    answer = requests.post(scenedata_endpoint,data=scenedata, headers=header, verify=False, stream=False).json()


                    EndTime = time.time()
                    print("### iChunkNumber",iChunkNumber)

                    debug_message = "SceneData is Done : {},{} , Reply Status Code : {}".format(objSM.SceneMarkID,objSD.DataID,str(answer))
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)         
                    iChunkNumber = iChunkNumber + 1
    
            image_file_name = sm_meta_info.clip_image_directory + "/" + sm_meta_info.thumbnail_image_file_name 
            with open(image_file_name,"rb") as image_file:
                fileSize = GetFileSizeBytes(image_file_name)
                iChunkSizeBytes = 1500000
                iChunkNumberRounded = int(fileSize / iChunkSizeBytes)
                iNumberOfBytes = iChunkNumberRounded * iChunkSizeBytes

                if fileSize > iNumberOfBytes:
                    iNumberOfChunks = iChunkNumberRounded + 1
                else:
                    iNumberOfChunks = iChunkNumberRounded

                iChunkNumber = 1

                ##xxprint("iNumberOfChunks={}".format(str(iNumberOfChunks)))
                while iChunkNumber <= iNumberOfChunks:
                    strBase64 = str(base64.b64encode(image_file.read(iChunkSizeBytes)).decode())
                    objSD = SceneDataValues()
                    objSD.Version = "1.0"
                    objSD.DataID = objSM.DetectedObjects_Thumbnail_SceneDataID
                    objSD.FileType = "Image"
                    objSD.FileName = sm_meta_info.thumbnail_image_file_name
                    objSD.PathURI = objSM.DetectedObjects_Thumbnail_SceneDataURI
                    objSD.Section = iChunkNumber
                    objSD.LastSection = iNumberOfChunks 
                    objSD.HashMethod = "SHA256"
                    objSD.OriginalFileHash="ABCDEFGHIJKLMNO" + currenttime
                    objSD.SectionBase64 = strBase64
                    objSD.RelatedSceneMarks = []
                    objSD.RelatedSceneMarks.append(objSM.SceneMarkID)

                    dictNiceSceneData = CreateSceneData(objSD)
                    AccessToken = sm_meta_info.camera_info.SceneDataToken

                    scenedata = CreateCMFHeaders(str(dictNiceSceneData), BridgeDeviceUUID, strCloudServerUUID, NodeID, PortID, AccessToken)
                    scenedata = json.dumps(scenedata)
                    scenedata = scenedata.replace("'",'\\"').replace('\0', '')

                    header = {'Authorization': 'Bearer ' + AccessToken,
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'}
                    
                    answer = requests.post(scenedata_endpoint,data=scenedata, headers=header, verify=False, stream=False).json()
                    print("### Thumbnail iChunkNumber",iChunkNumber)
                    debug_message = "SceneData Thumbnail is Done : {},{} , Reply Status Code : {}".format(objSM.SceneMarkID,objSD.DataID,str(answer))
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                    iChunkNumber = iChunkNumber + 1

                    #print("SceneData Thumbnail is Done : " + objSM.SceneMarkID + ":" + objSD.DataID)


            EndTime = time.time()
            #xxprint("{} : {} : {} : {}".format(objSM.NodeID,str(StartTime),str(EndTime),str(EndTime-StartTime)))

        except Exception as ex:
            debug_message = ":::: ERROR MESSAGE ::: {}".format(str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            pass

def new_scenemode_upload(detected_object_meta_info):
    while(True):
        try:
            if(len(detected_object_meta_info) > 0):
                for item in detected_object_meta_info:
                    create_scenemark_for_new_scenemode(item)
                    detected_object_meta_info.remove(item)
        except Exception as ex:
            debug_message = ":::: ERROR MESSAGE :::".format(str(e))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            pass
        time.sleep(TimeSleepProcess)

def create_directory():
    try:
        if(os.path.isdir(BridgeDeviceConfigVariable.RootDirectory) == False):
            os.mkdir(BridgeDeviceConfigVariable.RootDirectory)

        if(os.path.isdir(BridgeDeviceConfigVariable.ImageSaveDirectory) == False):
            os.mkdir(BridgeDeviceConfigVariable.ImageSaveDirectory)

        if(os.path.isdir(BridgeDeviceConfigVariable.ResultSaveDirectory) == False):
            os.mkdir(BridgeDeviceConfigVariable.ResultSaveDirectory)

        if(os.path.isdir(BridgeDeviceConfigVariable.SceneMarkDirectory)  == False):
            os.mkdir(BridgeDeviceConfigVariable.SceneMarkDirectory)

        if(os.path.isdir(BridgeDeviceConfigVariable.MetaDataDirectory) == False):
            print("###",BridgeDeviceConfigVariable.MetaDataDirectory)
            os.mkdir(BridgeDeviceConfigVariable.MetaDataDirectory)

        if(os.path.isdir(BridgeDeviceConfigVariable.FMetaDataDirectory) == False):
            os.mkdir(BridgeDeviceConfigVariable.FMetaDataDirectory)           

        if(os.path.isdir(BridgeDeviceConfigVariable.SceneDataDirectory) == False):
            os.mkdir(BridgeDeviceConfigVariable.SceneDataDirectory)
        
        if(os.path.isdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory) == False):
            os.mkdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory)

        for i in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
            camera_directory = "{}_{}".format(BridgeDeviceConfigVariable.BridgeDeviceID,decimal_fill(i+1,4))

            if(os.path.isdir(BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + camera_directory)):
                #shutil.rmtree(BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + camera_directory)
                remove_files(BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.SceneMarkDirectory + "/" + camera_directory)):
                remove_files(BridgeDeviceConfigVariable.SceneMarkDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.SceneMarkDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.SceneMarkDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)):
                remove_files(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory + "/" + camera_directory)):
                remove_files(BridgeDeviceConfigVariable.EllexiMetaDataDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.FMetaDataDirectory + "/" + camera_directory)):
                remove_files(BridgeDeviceConfigVariable.FMetaDataDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.FMetaDataDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.SceneDataDirectory + "/" + camera_directory)):
                remove_files(BridgeDeviceConfigVariable.SceneDataDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.SceneDataDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.SceneDataDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.ResultSaveDirectory + "/" + camera_directory)):
                remove_files(BridgeDeviceConfigVariable.ResultSaveDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.ResultSaveDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.ResultSaveDirectory + "/" + camera_directory)

            if(os.path.isdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory)):
                remove_files(BridgeDeviceConfigVariable.EllexiMetaDataDirectory + "/" + camera_directory)
                #shutil.rmtree(BridgeDeviceConfigVariable.ResultSaveDirectory + "/" + camera_directory)
            else:
                os.mkdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory + "/" + camera_directory)
    except Exception as ex:
        debug_message = "########::: #####ERROR MESSAGE####### ::: = {}".format(str(ex) + str(traceback.format_exc()))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
        print(debug_message)
                           
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("####connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))

def on_publish_server(client, userdata, mid):
    print("In on_pub callback mid= ", mid)

def on_connect_server(client, userdata, flags, rc):
    if rc == 0:
        print("ssconnected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect_server(client, userdata, flags, rc=0):
    print("disconnected")

def kill_bridge_device_rtsp_process(process_name):
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        print(process)
        process_list = str(process).split("\n")
        for item in process_list:
            if( "/usr/bin/python3 " + process_name + ".pyc" in item):
                #if(process_name == BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager):
                pid_list = item.split(" ")
                print(pid_list)
                for pid in pid_list:
                    if(pid.isdecimal()):
                        command = "/bin/kill -9 " + pid
                        print("kill_bridge_device_process::::",command)
                        os.system(command)
                        break

    except Exception as ex:
        print(str(ex))
        pass


def on_message(client, userdata, msg):
    print("+======== CONTROL DATA FROM  ============")
    print(str(msg.payload.decode("utf-8")))
    #kill_bridge_device_rtsp_process(BridgeDeviceRestreamManager)
    SubscribedObjectInfoList.append(msg)
    print("+======== CONTROL DATA FROM  ============\n\n")

def running_subscribe_manager():
    global BridgeDeviceRestreamManager
    while True:
        try:
            metadata = json.loads(SubscribedObjectInfoList.pop().payload.decode("utf-8"))
            

            device_list = metadata["NodeID"].split("_")
            device_id = device_list[0]
            camera_id = device_list[1]
            status = metadata["Command"]
            rtsp_url = metadata["RtspURL"]    
            bdnumber = metadata["BdNumber"]
            port = 10000 + int(camera_id) + (bdnumber - 1) * 10



            try: 
                process = subprocess.check_output(["netstat | grep " + str(port)],shell=True,encoding='utf-8')
                print(process)
                process_list = str(process).split("\n")
                for item in process_list:
                    pid_list = item.split(" ")
                    for pid in pid_list:
                        print(pid)
                    
            except Exception as ex:
                print(str(ex))
                pass
            
            if(rtsp_url != "" and  status == "ON"):
                command = "/usr/bin/python3 " + BridgeDeviceRestreamManager + ".pyc " + rtsp_url + " " + str(port) + " " + device_id + "_" + camera_id  + " " + str(current_milli_time()) + " " + str(bdnumber)
                print(command)
                result = os.system(command)
                print("result == " , result)



        except Exception as ex:
            pass
        time.sleep(TimeSleepProcess)
'''
def running_mqtt_manager():
    try:
        client = mqtt.Client()
        client.on_connect = on_connect 
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe  
        client.on_message = on_message 
        client.connect("20.194.104.191",1883)
        client.subscribe("/REQUEST/STREAMING/" + BridgeDeviceConfigVariable.BridgeDeviceID,1)
        client.loop_forever()
    except Exception as ex:
        pass 
'''

def main():
    print("==========================================")
    print("::::: SceneMode is started..... :::::")
    print("==========================================")

    bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
    if(os.path.isfile(bridge_device_config_file_name)):
        os.remove(bridge_device_config_file_name)
        
    ApplicationList = ["InferenceManager.dat","EventManager.dat","SceneMarkManager.dat","SceneDataManager.dat","FacilityManager.dat","FallDownFightManager.dat","SceneModeManager.dat"]
    for item in ApplicationList:
        if(os.path.isfile(str(item))):
            os.remove(item)
            
    for item in BridgeDeviceConfigVariable.range_list:
        if(os.path.isfile(str(item) + ".dat")):
            os.remove(str(item) + ".dat")
    
    # Image Management ::: Remove Image older than 
    delete_video_image_thread = threading.Thread(target=delete_video_image,args=())
    delete_video_image_thread.daemon = True
    delete_video_image_thread.start()
    
    if(BridgeDeviceConfigVariable.InferencingManagerEnable):
        # Inference Management 
        running_inference_manager_thread = threading.Thread(target=running_inference_manager2,args=())
        running_inference_manager_thread.daemon = True
        running_inference_manager_thread.start()
    else:
        create_directory()

    if(BridgeDeviceConfigVariable.EventManagerEnable):
        # Event Management ::: Normal Event
        running_event_manager_thread = threading.Thread(target=running_event_manager,args=())
        running_event_manager_thread.daemon = True
        running_event_manager_thread.start()
    
    if(BridgeDeviceConfigVariable.EventFacilityManagerEnable and BridgeDeviceConfigVariable.InferencingManagerEnable):
        # Event Management ::: Facility Event
        running_event_facility_manager_thread = threading.Thread(target=running_event_facility_manager,args=())
        running_event_facility_manager_thread.daemon = True
        running_event_facility_manager_thread.start()
    
    if(BridgeDeviceConfigVariable.SceneMarkManagerEnable):
        # SceneMark Management 
        running_scenemark_manager_thread = threading.Thread(target=running_scenemark_manager,args=())
        running_scenemark_manager_thread.daemon = True
        running_scenemark_manager_thread.start()

    if(BridgeDeviceConfigVariable.SceneDataManagerEnable):
        # SceneData Management 
        running_scenedata_manager_thread = threading.Thread(target=running_scenedata_manager,args=())
        running_scenedata_manager_thread.daemon = True
        running_scenedata_manager_thread.start()


    running_subscribe_manager_thread = threading.Thread(target=running_subscribe_manager,args=())
    running_subscribe_manager_thread.daemon = True
    running_subscribe_manager_thread.start()

    start_get_scenemode()

LoadBridgeDeviceSecurityObject()

if(BridgeDeviceConfigVariable.BridgeDeviceID):
    pass
else:
    time.sleep(5)
    LoadBridgeDeviceSecurityObject()
