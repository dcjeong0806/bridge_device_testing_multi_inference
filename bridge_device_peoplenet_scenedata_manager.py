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
from bridge_device_peoplenet_config import VariableConfigClass

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

import pickle 

import shutil

current_milli_time = lambda: int(round(time.time() * 1000))
from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint
BridgeDeviceConfigVariable = VariableConfigClass()

TimeSleepProcess = 1

def create_scenedata_sync(sm_meta_info):
    '''
    SCENERA_BRIDGE_LIBRARY_API_URL = "http://127.0.0.1:5001/"
    SetDeviceSecurityObject = SCENERA_BRIDGE_LIBRARY_API_URL + "SetDeviceSecurityObject"
    SetDevicePrivateKey = SCENERA_BRIDGE_LIBRARY_API_URL + "SetDevicePrivateKey"
    StopSceneraProcesses = SCENERA_BRIDGE_LIBRARY_API_URL + "StopSceneraProcesses"
    StartSceneraProcesses = SCENERA_BRIDGE_LIBRARY_API_URL + "StartSceneraProcesses" 
    IsFirstSceneModeReceived = SCENERA_BRIDGE_LIBRARY_API_URL + "IsFirstSceneModeReceived"
    GetSceneMode = SCENERA_BRIDGE_LIBRARY_API_URL + "GetSceneMode" 
    ClearDetectedObjects = SCENERA_BRIDGE_LIBRARY_API_URL + "ClearDetectedObjects"
    UpdateDetectedObjects = SCENERA_BRIDGE_LIBRARY_API_URL + "UpdateDetectedObjects"
    CreateVideoSceneDataID = SCENERA_BRIDGE_LIBRARY_API_URL + "CreateVideoSceneDataID"
    SendSceneMark = SCENERA_BRIDGE_LIBRARY_API_URL + "SendSceneMark"
    SendDetectedObjectsSceneData = SCENERA_BRIDGE_LIBRARY_API_URL + "SendDetectedObjectsSceneData"
    SendFullImageSceneData = SCENERA_BRIDGE_LIBRARY_API_URL + "SendFullImageSceneData"
    SendVideoSection = SCENERA_BRIDGE_LIBRARY_API_URL + "SendVideoSection"
    '''


    print("####################CREATE SCENEDATA SYNC",sm_meta_info.video_file_name)
    if len(sm_meta_info.video_file_name) > 0 and sm_meta_info.SceneMarkIsDone:
        BridgeDeviceUUID = sm_meta_info.device_id
        NodeID = int(sm_meta_info.camera_id)
        PortID = 1234
        TimeToUTC = 9 * 3600
        CameraID = str(int(sm_meta_info.camera_id))
        ##xxprint("###### == " + image_file_name)

        strCloudServerUUID = DeviceNodeID(BridgeDeviceUUID, NodeID)
        strCloudServerUUID = strCloudServerUUID.replace("_","-")

        for video_file_name in sm_meta_info.video_file_name:
            if(os.path.isfile(video_file_name)):
                #video_file_name = "./falldown.mp4"
                file_size = GetFileSizeBytes(video_file_name)
                i_chunk_size_bytes = 1500000
                i_chunk_number_rounded = int(file_size / i_chunk_size_bytes)
                i_number_of_bytes = i_chunk_number_rounded * i_chunk_size_bytes

                if file_size > i_number_of_bytes:
                    i_number_of_chunks = i_chunk_number_rounded + 1
                else:
                    i_number_of_chunks = i_chunk_number_rounded

                file_reconding = open(video_file_name, "rb")

                i_chunk_number = 1
            
                while i_chunk_number <= i_number_of_chunks:
                    bin_data = file_reconding.read(i_chunk_size_bytes)
                    b_base64_video = base64.b64encode(bin_data)
                    str_base64_video = b_base64_video.decode()
                    bin_video = base64.b64decode(str_base64_video)

                    headers = {"Content-type": "application/mp4"}
                    print("##### FILE SIZE ", file_size , "/" , len(bin_video), BridgeDeviceConfigVariable.SendVideoSection + "/" + str(i_chunk_number) +  "/" + str(i_number_of_chunks) + "/" + str(int(CameraID)))                                                        
                    r = requests.post(url = BridgeDeviceConfigVariable.SendVideoSection + "/" + str(i_chunk_number) +  "/" + str(i_number_of_chunks) + "/" + str(int(CameraID)),data = bin_video, headers=headers, timeout = 120, verify=False)  
                    retval = r.json()
                    print("SendVideoSection",retval)      

                    i_chunk_number += 1


def upload_result_scenedata():
    #xxprint(str(int(CameraID)).zfill(4) + " Thread is started...")
    while(True):
        try:
            for k in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
                CameraID = str(int(k+1)).zfill(4)
                UploadSceneDataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                if(os.path.isdir(UploadSceneDataDirectory)):
                    file_list = os.listdir(UploadSceneDataDirectory)
                    file_list.sort()
                    for item in file_list: 
                        scenedata_file = UploadSceneDataDirectory + "/" + item
                        if os.path.isfile(scenedata_file) and os.path.getsize(scenedata_file) > 0:
                            with open(scenedata_file,"rb") as f:
                                sm_meta_info = pickle.load(f)
                                currenttime = int(time.time())
                                #scenemark_time = currenttime - int(sm_meta_info.detected_time)
                                currenttime = int(time.time())
                                scenemark_time = (currenttime - int(sm_meta_info.detected_time)) * int(sm_meta_info.camera_info.get("InferenceFPS"))
                                debug_message = (str(BridgeDeviceConfigVariable.DETENTION_FRAME) +  "######## SCENEDATATIME : DETENTIONTIME " + str(scenemark_time) + ":::" + str(BridgeDeviceConfigVariable.DETENTION_FRAME))
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                    
                                #if(scenemark_time > BridgeDeviceConfigVariable.DETENTION_FRAME):
                                #    sm_meta_info.IsUploadTwoImage = True
                                #    os.remove(scenedata_file)
                                #    debug_message = ("####### OLD SceneData is removed..." + scenedata_file)
                                #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                                
                                
                                if sm_meta_info.IsUploadTwoImage == False :
                                    StartTime = time.time()
                                    #print(sm_meta_info.SaveImageDirectory)
                                    ImageDirectory = "{}/{}_{}".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                                    #print(ImageDirectory)
                                    if os.path.isdir(ImageDirectory):                                
                                        image_file_list = os.listdir(ImageDirectory)
                                        image_file_list.sort()
                                        ImageFileList = ""
                                        StartTime = time.time()
                                        StartFrame = sm_meta_info.FrameStarted
                                        EndFrame = sm_meta_info.FrameEnded
                                        IsImageGenerated = True
                                        ImageCount = 0
                                        #print("####",StartFrame,EndFrame)
                                        '''
                                        for frame in range(EndFrame-(sm_meta_info.camera_info.InferenceFPS * 2),EndFrame-(sm_meta_info.camera_info.InferenceFPS)):
                                            ImageEndFrame = "{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                                            if(os.path.isfile(ImageEndFrame)):
                                                #print(ImageEndFrame)
                                                ImageCount = ImageCount + 1
                                                IsImageGenerated = True
                                        '''
                                            
                                        if(IsImageGenerated):
                                            for frame in range(StartFrame,EndFrame):
                                                image_file  = "{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                                                debug_message = image_file
                                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    
                                                if(os.path.isfile(image_file)):
                                                    file_path = "../../../{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                                                    ImageFileList = ImageFileList + "file " + file_path + "\n"
                                            maketime = str(int(time.time()))
                                            ResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.ResultSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                                            if(os.path.isdir(ResultDirectory) == False):
                                                os.mkdir(ResultDirectory)

                                            image_list_file_name = ResultDirectory + "/image_file_list_{}_{}_{}.txt".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,maketime)
                                            f = open(image_list_file_name,"w")
                                            f.write(ImageFileList)
                                            f.close()
                                            video_file_name = "{}/{}_{}_{}_{}.mp4".format(ResultDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(sm_meta_info.FrameDetected),maketime)  

                                            video_generate_command ="/usr/bin/ffmpeg -r {}  -f concat -safe 0 -i {} -preset:v ultrafast -y {}".format(str(sm_meta_info.camera_info.get("InferenceFPS") / BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS),image_list_file_name,video_file_name)
                                            #video_generate_command ="/usr/bin/ffmpeg -r 15  -f concat -safe 0 -i {} -preset:v ultrafast -y {}".format(image_list_file_name,video_file_name)
                                            
                                            sm_meta_info.VideoFileCommand = video_generate_command

                                            debug_message = video_generate_command
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    

                                            sm_meta_info.scenedata_name = str(int(time.time() * 1000))
                                            sm_meta_info.video_file_name = [] 
                                            sm_meta_info.video_file_name.append(video_file_name)
                                            sm_meta_info.ImageFileList = image_list_file_name
                                            EndTime = time.time()

                                            #xxprint("##### Generating Image File List ",StartTime, EndTime, EndTime-StartTime)

                                            if(os.path.isfile(sm_meta_info.ImageFileList)):
                                                try:
                                                    StartTime = time.time()
                                                    result = os.system(sm_meta_info.VideoFileCommand) 
                                                    EndTime = time.time()
                                                    debug_message = ("######## FFMPEG VIDEO GENERATING TIME" + CameraID + ":::" + str(StartTime) + ":::" + str(EndTime) + "[#" + str(EndTime-StartTime) + "#]" + ":::" + str(datetime.datetime.now()))
                                                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    
                                                    if(result == 0):
                                                        ##xxprint("######## file name",sm_meta_info.video_file_name[0])
                                                        if(os.path.isfile(sm_meta_info.video_file_name[0])):
                                                            #print("###################[UPLOADING SCENEMARK START]  ==============================================")
                                                            #print(sm_meta_info.SceneMarkID,datetime.datetime.now())
                                                            #print("###################[[UPLOADING SCENEMARK FILE END]  ==============================================")
                                                            #print("\n\n")
                                                            #print("####:::#### Performance Test SceneDataManager Start ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)

                                                            
                                                            create_scenedata_sync(sm_meta_info)
                                                            if(os.path.isfile(scenedata_file)):
                                                                os.remove(scenedata_file)
                                                                os.remove(sm_meta_info.video_file_name[0])
                                                
                                                                #os.remove(sm_meta_info.ImageFileList)
                                                            #print("####:::#### Performance Test SceneDataManager End ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)

                                                    else:
                                                        os.path.isfile(sm_meta_info.ImageFileList)
                                                        os.remove(scenedata_file)
                                                    
                                                    EndTime = time.time()
                                                    #print("####### RESULT ######### CameraID",CameraID,StartTime,EndTime,"[#" + str(EndTime-StartTime) + "#]",datetime.datetime.now(),"\n")

                                                except Exception as file_ex:
                                                    debug_message = (":::::: Error Message ::::::" + str(file_ex))
                                                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)  
                                                    pass
                                            else:
                                                os.remove(scenedata_file)
                
        except Exception as ex:
            debug_message = (":::::: Error Message ::::::" + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)  
            pass
        time.sleep(TimeSleepProcess)


def upload_scenedata(sm_meta_info,scenedata_file, ImageDirectory, CameraID):
    image_file_list = os.listdir(ImageDirectory)
    image_file_list.sort()
    ImageFileList = ""
    StartTime = time.time()
    StartFrame = sm_meta_info.FrameStarted
    EndFrame = sm_meta_info.FrameEnded
    IsImageGenerated = True
    ImageCount = 0
    #print("####",StartFrame,EndFrame)
    '''
    for frame in range(EndFrame-(sm_meta_info.camera_info.InferenceFPS * 2),EndFrame-(sm_meta_info.camera_info.InferenceFPS)):
    ImageEndFrame = "{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
    if(os.path.isfile(ImageEndFrame)):
        #print(ImageEndFrame)
        ImageCount = ImageCount + 1
        IsImageGenerated = True
    '''

    if(IsImageGenerated):
        TimeDiff = sm_meta_info.DetentionTime - (int(time.time()) - int(sm_meta_info.EndTimeStamp))
        print("\n\n\n\n\n\n\n#####+=======> >>>>>>>> detention time ", TimeDiff, sm_meta_info.DetentionTime , sm_meta_info.EndTimeStamp, int(time.time()) , scenedata_file , "\n\n\n\n\n\n\n")
        
        if(TimeDiff > 0):
            time.sleep(sm_meta_info.DetentionTime)
        for frame in range(StartFrame,EndFrame):
            image_file  = "{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
            debug_message = image_file
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    
            if(os.path.isfile(image_file)):
                file_path = "../../../{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                ImageFileList = ImageFileList + "file " + file_path + "\n"
        maketime = str(int(time.time()))
        ResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.ResultSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
        if(os.path.isdir(ResultDirectory) == False):
            os.mkdir(ResultDirectory)

        image_list_file_name = ResultDirectory + "/image_file_list_{}_{}_{}.txt".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,maketime)
        f = open(image_list_file_name,"w")
        f.write(ImageFileList)
        f.close()
        video_file_name = "{}/{}_{}_{}_{}.mp4".format(ResultDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(sm_meta_info.FrameDetected),maketime)  

        video_generate_command ="/usr/bin/ffmpeg -r {}  -f concat -safe 0 -i {} -preset:v ultrafast -y {}".format(str(sm_meta_info.camera_info.get("InferenceFPS") / BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS),image_list_file_name,video_file_name)
        #video_generate_command ="/usr/bin/ffmpeg -r 15  -f concat -safe 0 -i {} -preset:v ultrafast -y {}".format(image_list_file_name,video_file_name)
        
        sm_meta_info.VideoFileCommand = video_generate_command

        debug_message = video_generate_command
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    

        sm_meta_info.scenedata_name = str(int(time.time() * 1000))
        sm_meta_info.video_file_name = [] 
        sm_meta_info.video_file_name.append(video_file_name)
        sm_meta_info.ImageFileList = image_list_file_name
        EndTime = time.time()

        #xxprint("##### Generating Image File List ",StartTime, EndTime, EndTime-StartTime)

        if(os.path.isfile(sm_meta_info.ImageFileList)):
            try:
                StartTime = time.time()
                result = os.system(sm_meta_info.VideoFileCommand) 
                EndTime = time.time()
                debug_message = ("######## FFMPEG VIDEO GENERATING TIME" + CameraID + ":::" + str(StartTime) + ":::" + str(EndTime) + "[#" + str(EndTime-StartTime) + "#]" + ":::" + str(datetime.datetime.now()))
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    
                if(result == 0):
                    ##xxprint("######## file name",sm_meta_info.video_file_name[0])
                    if(os.path.isfile(sm_meta_info.video_file_name[0])):
                        #print("###################[UPLOADING SCENEMARK START]  ==============================================")
                        #print(sm_meta_info.SceneMarkID,datetime.datetime.now())
                        #print("###################[[UPLOADING SCENEMARK FILE END]  ==============================================")
                        #print("\n\n")
                        #print("####:::#### Performance Test SceneDataManager Start ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)

                        
                        threading.Thread(target=create_scenedata_sync,args=(sm_meta_info,)).start()
                        #create_scenedata_sync(sm_meta_info)
                        #if(os.path.isfile(scenedata_file)):
                        #    os.remove(scenedata_file)
                        #    os.remove(sm_meta_info.video_file_name[0])
            
                            #os.remove(sm_meta_info.ImageFileList)
                        #print("####:::#### Performance Test SceneDataManager End ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)

                else:
                    os.path.isfile(sm_meta_info.ImageFileList)
                    
                
                EndTime = time.time()
                #print("####### RESULT ######### CameraID",CameraID,StartTime,EndTime,"[#" + str(EndTime-StartTime) + "#]",datetime.datetime.now(),"\n")

            except Exception as file_ex:
                debug_message = (":::::: Error Message ::::::" + str(file_ex))
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)  
                pass
        else:
            os.remove(scenedata_file)

def upload_result_scenedata2(CameraID):
    #xxprint(str(int(CameraID)).zfill(4) + " Thread is started...")
    while(True):
        try:
            UploadSceneDataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            if(os.path.isdir(UploadSceneDataDirectory)):
                file_list = os.listdir(UploadSceneDataDirectory)
                file_list.sort()
                for item in file_list: 
                    scenedata_file = UploadSceneDataDirectory + "/" + item
                    if os.path.isfile(scenedata_file) and os.path.getsize(scenedata_file) > 0:
                        with open(scenedata_file,"rb") as f:
                            sm_meta_info = pickle.load(f)
                            os.remove(scenedata_file)
                            currenttime = int(time.time())
                            #scenemark_time = currenttime - int(sm_meta_info.detected_time)
                            currenttime = int(time.time())
                            scenemark_time = (currenttime - int(sm_meta_info.detected_time)) * int(sm_meta_info.camera_info.get("InferenceFPS"))
                            debug_message = (str(BridgeDeviceConfigVariable.DETENTION_FRAME) +  "######## SCENEDATATIME : DETENTIONTIME " + str(scenemark_time) + ":::" + str(BridgeDeviceConfigVariable.DETENTION_FRAME))
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                
                            #if(scenemark_time > BridgeDeviceConfigVariable.DETENTION_FRAME):
                            #    sm_meta_info.IsUploadTwoImage = True
                            #    os.remove(scenedata_file)
                            #    debug_message = ("####### OLD SceneData is removed..." + scenedata_file)
                            #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                            
                            
                            if sm_meta_info.IsUploadTwoImage == False :
                                StartTime = time.time()
                                #print(sm_meta_info.SaveImageDirectory)
                                ImageDirectory = "{}/{}_{}".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                                #print(ImageDirectory)
                                if os.path.isdir(ImageDirectory):                                
                                   threading.Thread(target=upload_scenedata,args=(sm_meta_info,scenedata_file, ImageDirectory, CameraID,)).start()


            
        except Exception as ex:
            debug_message = (":::::: Error Message ::::::" + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)  
            pass



        time.sleep(TimeSleepProcess)

def upload_result_scenedata3(CameraID):
    #xxprint(str(int(CameraID)).zfill(4) + " Thread is started...")
    while(True):
        try:
            UploadSceneDataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.SceneDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            if(os.path.isdir(UploadSceneDataDirectory)):
                file_list = os.listdir(UploadSceneDataDirectory)
                file_list.sort()
                for item in file_list: 
                    scenedata_file = UploadSceneDataDirectory + "/" + item
                    if os.path.isfile(scenedata_file) and os.path.getsize(scenedata_file) > 0:
                        with open(scenedata_file,"rb") as f:
                            sm_meta_info = pickle.load(f)
                            currenttime = int(time.time())
                            #scenemark_time = currenttime - int(sm_meta_info.detected_time)
                            currenttime = int(time.time())
                            scenemark_time = (currenttime - int(sm_meta_info.detected_time)) * int(sm_meta_info.camera_info.get("InferenceFPS"))
                            debug_message = (str(BridgeDeviceConfigVariable.DETENTION_FRAME) +  "######## SCENEDATATIME : DETENTIONTIME " + str(scenemark_time) + ":::" + str(BridgeDeviceConfigVariable.DETENTION_FRAME))
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                
                            #if(scenemark_time > BridgeDeviceConfigVariable.DETENTION_FRAME):
                            #    sm_meta_info.IsUploadTwoImage = True
                            #    os.remove(scenedata_file)
                            #    debug_message = ("####### OLD SceneData is removed..." + scenedata_file)
                            #    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)                    
                            
                            
                            if sm_meta_info.IsUploadTwoImage == False :
                                StartTime = time.time()
                                #print(sm_meta_info.SaveImageDirectory)
                                ImageDirectory = "{}/{}_{}".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                                #print(ImageDirectory)
                                if os.path.isdir(ImageDirectory):                                
                                    image_file_list = os.listdir(ImageDirectory)
                                    image_file_list.sort()
                                    ImageFileList = ""
                                    StartTime = time.time()
                                    StartFrame = sm_meta_info.FrameStarted
                                    EndFrame = sm_meta_info.FrameEnded
                                    IsImageGenerated = True
                                    ImageCount = 0
                                    #print("####",StartFrame,EndFrame)
                                    '''
                                    for frame in range(EndFrame-(sm_meta_info.camera_info.InferenceFPS * 2),EndFrame-(sm_meta_info.camera_info.InferenceFPS)):
                                        ImageEndFrame = "{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                                        if(os.path.isfile(ImageEndFrame)):
                                            #print(ImageEndFrame)
                                            ImageCount = ImageCount + 1
                                            IsImageGenerated = True
                                    '''
                                        
                                    if(IsImageGenerated):
                                        print("#####+=======> >>>>>>>> detention time ", sm_meta_info.DetentionTime , sm_meta_info.EndTimeStamp, int(time.time()))
                                        TimeDiff = int(time.time()) - int(sm_meta_info.EndTimeStamp)
                                        if(TimeDiff > 0):
                                            time.sleep(sm_meta_info.DetentionTime)
                                        for frame in range(StartFrame,EndFrame):
                                            image_file  = "{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                                            debug_message = image_file
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    
                                            if(os.path.isfile(image_file)):
                                                file_path = "../../../{}/{}_{}/{}.jpeg".format(sm_meta_info.SaveImageDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(int(frame)).zfill(10))
                                                ImageFileList = ImageFileList + "file " + file_path + "\n"
                                        maketime = str(int(time.time()))
                                        ResultDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.ResultSaveDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
                                        if(os.path.isdir(ResultDirectory) == False):
                                            os.mkdir(ResultDirectory)

                                        image_list_file_name = ResultDirectory + "/image_file_list_{}_{}_{}.txt".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,maketime)
                                        f = open(image_list_file_name,"w")
                                        f.write(ImageFileList)
                                        f.close()
                                        video_file_name = "{}/{}_{}_{}_{}.mp4".format(ResultDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,str(sm_meta_info.FrameDetected),maketime)  

                                        video_generate_command ="/usr/bin/ffmpeg -r {}  -f concat -safe 0 -i {} -preset:v ultrafast -y {}".format(str(sm_meta_info.camera_info.get("InferenceFPS") / BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS),image_list_file_name,video_file_name)
                                        #video_generate_command ="/usr/bin/ffmpeg -r 15  -f concat -safe 0 -i {} -preset:v ultrafast -y {}".format(image_list_file_name,video_file_name)
                                        
                                        sm_meta_info.VideoFileCommand = video_generate_command

                                        debug_message = video_generate_command
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    

                                        sm_meta_info.scenedata_name = str(int(time.time() * 1000))
                                        sm_meta_info.video_file_name = [] 
                                        sm_meta_info.video_file_name.append(video_file_name)
                                        sm_meta_info.ImageFileList = image_list_file_name
                                        EndTime = time.time()

                                        #xxprint("##### Generating Image File List ",StartTime, EndTime, EndTime-StartTime)

                                        if(os.path.isfile(sm_meta_info.ImageFileList)):
                                            try:
                                                StartTime = time.time()
                                                result = os.system(sm_meta_info.VideoFileCommand) 
                                                EndTime = time.time()
                                                debug_message = ("######## FFMPEG VIDEO GENERATING TIME" + CameraID + ":::" + str(StartTime) + ":::" + str(EndTime) + "[#" + str(EndTime-StartTime) + "#]" + ":::" + str(datetime.datetime.now()))
                                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)    
                                                if(result == 0):
                                                    ##xxprint("######## file name",sm_meta_info.video_file_name[0])
                                                    if(os.path.isfile(sm_meta_info.video_file_name[0])):
                                                        #print("###################[UPLOADING SCENEMARK START]  ==============================================")
                                                        #print(sm_meta_info.SceneMarkID,datetime.datetime.now())
                                                        #print("###################[[UPLOADING SCENEMARK FILE END]  ==============================================")
                                                        #print("\n\n")
                                                        #print("####:::#### Performance Test SceneDataManager Start ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)

                                                        
                                                        create_scenedata_sync(sm_meta_info)
                                                        if(os.path.isfile(scenedata_file)):
                                                            os.remove(scenedata_file)
                                                            os.remove(sm_meta_info.video_file_name[0])
                                            
                                                            #os.remove(sm_meta_info.ImageFileList)
                                                        #print("####:::#### Performance Test SceneDataManager End ####:::####", time.time(), sm_meta_info.camera_info.CameraID,sm_meta_info.frame_num)

                                                else:
                                                    os.path.isfile(sm_meta_info.ImageFileList)
                                                    os.remove(scenedata_file)
                                                
                                                EndTime = time.time()
                                                #print("####### RESULT ######### CameraID",CameraID,StartTime,EndTime,"[#" + str(EndTime-StartTime) + "#]",datetime.datetime.now(),"\n")

                                            except Exception as file_ex:
                                                debug_message = (":::::: Error Message ::::::" + str(file_ex))
                                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)  
                                                pass
                                        else:
                                            os.remove(scenedata_file)
            
        except Exception as ex:
            debug_message = (":::::: Error Message ::::::" + str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager)  
            pass



        time.sleep(TimeSleepProcess)




def main():
    print("==========================================")
    print("::::: Uploading SceneData is started...::::")
    print("==========================================")
    #upload_result_scenedata()
    for CameraID in BridgeDeviceConfigVariable.range_list:
        threading.Thread(target=upload_result_scenedata2,args=(CameraID,)).start()
    



## LoadBridgeDeviceSecurityObject Disabled until it works 2020-09-24 DCJeong
def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable
    '''
    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager) > 1):
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