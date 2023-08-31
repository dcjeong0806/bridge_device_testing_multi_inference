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
from BridgeDeviceInfo import CameraMetaInfoClass,kill_bridge_device_process, parsing_camerainfo, GetCameraID, SceneModeConfigClass, PipeLineInfoClass,check_bridge_device_process,SMDetectedObjectInfo, DetectedMetaInfo, DetectedObjectInfo
from PythonUtils import printDebug, GetFileSizeBytes
from CMFHeaders import CreateCMFHeaders
from Scenera_SceneMode import GetSceneMode
from Scenera_BridgeLib import GetSceneDataInfo, GetSceneMarkInfo, GetSceneDataVideoInfo, GetVideoURL,GetDateTime, DeviceNodeID, DevicePortID, CreateSceneMarkID, CreateSceneDataID
from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID, GetNICELAEndPointAuthority, GetNICELAEndPointEndPoint
from Scenera_ManagementObject import GetManagementObject, GetManagementObjectInfo
from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint,decimal_fill

from collections import deque
import aiohttp
import sys
sys.path.append('../')
import gi
import configparser
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
from gi.repository import GLib
from ctypes import *
import time
import sys
import math
import platform
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call
from common.FPS import GETFPS
import json
import threading
import concurrent.futures
import os
import datetime
import cv2
import pyds
import base64
import calendar

from sys  import getsizeof
import copy
import numpy as np
import os.path as path
import subprocess

import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import matplotlib.path as mpltPath
from shapely.geometry import  Polygon
import pickle 
import shutil
import sysv_ipc
current_milli_time = lambda: int(round(time.time() * 1000))
import signal

import io

fps_streams={}


people_count = 0 
BridgeDeviceConfigVariable = VariableConfigClass()
PIPELINE = None
CheckFrameRate = 5.0

previous_currenttime = [0,0,0,0,0,0,0,0,0,0]

class overlaps_contains:
    overlaps = False
    contains = False

# tiler_sink_pad_buffer_probe  will extract metadata received on tiler src pad
# and update params for drawing rectangle, object information etc.

def save_image_data(shm_key,frame_image,header,data_key_number):
    '''
    memory = sysv_ipc.SharedMemory(int(data_key_number), size=len(header), flags=sysv_ipc.IPC_CREAT)
    memory.write(header)
    memory.detach()

    memory = sysv_ipc.SharedMemory(int(shm_key), size=frame_image.size, flags=sysv_ipc.IPC_CREAT)
    memory.write(frame_image)
    memory.detach()
    '''
    #cv2.imwrite("./content/image/" + header + ".jpg",frame_image)

    # Log Print
    image_info_variable = header
    #debug_message = "{}".format(image_info_variable)
    #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGenerateImageManager)

    BridgeDeviceID = image_info_variable[:36]
    CameraID = image_info_variable[36:40]
    FrameNumber = image_info_variable[40:50] + ".jpeg"
    Image_Shm_Key = int(image_info_variable[50:60])
    Height = int(image_info_variable[60:64])
    Width = int(image_info_variable[64:68])

    camera_image_folder = BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + BridgeDeviceID + "_" + CameraID
    if not(os.path.isdir(camera_image_folder)):
        os.mkdir(camera_image_folder)

    full_image_file_name =  FrameNumber
    StartTime = time.time()
    #resize_frame = cv2.resize(frame_image,(int(VariableConfigClass.ImageSizeWidth),int(VariableConfigClass.ImageSizeHeight)), interpolation = cv2.INTER_CUBIC)
    #cv2.imwrite(camera_image_folder + "/" + full_image_file_name, resize_frame)
    cv2.imwrite(camera_image_folder + "/" + full_image_file_name, frame_image)
    EndTime = time.time()

    #print(":::::::: StartTime = " + str(StartTime) +   " EndTime = " + str(EndTime) + "::::" + str(EndTime-StartTime))  


def draw_bounding_boxes(image,obj_meta,confidence):
    confidence='{0:.2f}'.format(confidence)
    confidence = int(confidence*100)
    rect_params=obj_meta.rect_params
    top=int(rect_params.top)
    left=int(rect_params.left)
    width=int(rect_params.width)
    height=int(rect_params.height)
    obj_name=pgie_classes_str[obj_meta.class_id]
    image=cv2.rectangle(image,(left,top),(left+width,top+height),(0,0,255,0),2)
    image=cv2.putText(image,obj_name+' '+str(confidence) + "%",(left-10,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255,0),2)
    return image

    
def tiler_sink_pad_buffer_probe(pad,info,cameraIndex):
    global people_count
    global previous_currenttime 
   
    camera_confidence = 0

    #print("###### BridgeDeviceConfigVariable.CameraList ",len(BridgeDeviceConfigVariable.CameraList),len(BridgeDeviceConfigVariable.CameraList[0].SceneModeConfig),BridgeDeviceConfigVariable.CameraList[0].SceneModeConfig[0]["CustomAnalysisStage"])
    
    frame_number=0
    num_rects=0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        return
        
    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list

    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break
        frame_number=frame_meta.frame_num
        currenttime = str(int(time.time()) - (9 * 3600 * 0))
        #print("####### Performance Test Inference ########",time.time(),frame_number,BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id)

        if(frame_number % BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS == 0 and True == False):
            #StartTime = time.time()
            #frame_image=pyds.get_nvds_buf_surface(hash(gst_buffer),frame_meta.batch_id)
            #frame_image=np.array(frame_image,copy=True,order='C')
            #frame_image=cv2.cvtColor(frame_image,cv2.COLOR_RGBA2BGRA)
            
            if(BridgeDeviceConfigVariable.SHM_KEY_NUMBER > 256*256*256*127*2):
                BridgeDeviceConfigVariable.SHM_KEY_NUMBER = 256*256*256*128

            BridgeDeviceConfigVariable.SHM_KEY_NUMBER = BridgeDeviceConfigVariable.SHM_KEY_NUMBER + 1

            if(BridgeDeviceConfigVariable.SHM_DATA_KEY_NUMBER > 256*256*256*127*1):
                BridgeDeviceConfigVariable.SHM_DATA_KEY_NUMBER = 0
                
            BridgeDeviceConfigVariable.SHM_DATA_KEY_NUMBER = BridgeDeviceConfigVariable.SHM_DATA_KEY_NUMBER + 1
            
            header = "{}{}{}{}{}{}".format(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].device_id,BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id,decimal_fill(frame_number,10),str(BridgeDeviceConfigVariable.SHM_KEY_NUMBER),decimal_fill(BridgeDeviceConfigVariable.Resolution_Convert_Height,4),decimal_fill(BridgeDeviceConfigVariable.Resolution_Convert_Width,4))



            #save_image_data(BridgeDeviceConfigVariable.SHM_KEY_NUMBER,frame_image,header,BridgeDeviceConfigVariable.SHM_DATA_KEY_NUMBER)
            
            #EndTime = time.time()
            #print(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id,StartTime,EndTime,EndTime-StartTime)
            # Log Print
            #debug_message = "header:{} ".format(header)
            #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

        #### display frame number ####
        '''
        display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        display_meta_rect_params = 0 
        py_nvosd_text_params = display_meta.text_params[0]
        py_nvosd_text_params.display_text = currenttime + "::::::[" + str(frame_number) + "]"
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        py_nvosd_text_params.font_params.font_color.red = 1.0
        py_nvosd_text_params.font_params.font_color.green = 1.0
        py_nvosd_text_params.font_params.font_color.blue = 1.0
        py_nvosd_text_params.font_params.font_color.alpha = 1.0
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.red = 0.0
        py_nvosd_text_params.text_bg_clr.green = 0.0
        py_nvosd_text_params.text_bg_clr.blue = 0.0
        py_nvosd_text_params.text_bg_clr.alpha = 1.0
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        display_meta_rect_params = 0
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        '''
        
        detected_meta_info = None
        detected_meta_info = DetectedMetaInfo()
        detected_meta_info.ProcessTimeList = None
     
        detected_meta_info.detected_time = str(currenttime) # str(int(CameraList[camera_id].StartInferencingTime) + int(frame_number / MAX_FRAME_INTERVAL))
        detected_meta_info.source_id = frame_meta.source_id
        ##xxprint("##### = " + str(frame_meta.source_frame_width) + ":" + str(frame_meta.source_frame_height))
        detected_meta_info.origin_frame_num = frame_meta.frame_num

        detected_meta_info.camera_id = BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id
        ##xxprint("### camera id = " + detected_meta_info.camera_id + " : " + str(len(CameraList)))
        detected_meta_info.camera_info = None
        detected_meta_info.camera_info = BridgeDeviceConfigVariable.CameraList[frame_meta.source_id]

        for item in detected_meta_info.camera_info.SceneModeConfig:
            CustomAnalysisStage = item["CustomAnalysisStage"]
            if(CustomAnalysisStage.lower() is not "newscenemode"):
                camera_confidence = item["Threshold"]
                break


        
        scenemarkmode_list = ""
        for scenemode in detected_meta_info.camera_info.SceneMarkMode:
            scenemarkmode_list = scenemarkmode_list + " " + scenemode

        confidence = detected_meta_info.camera_info.Confidence / 100
        camera_start_time = int(detected_meta_info.camera_info.WorkTime["StartTime"])
        camera_end_time = int(detected_meta_info.camera_info.WorkTime["EndTime"])
        worktime_check = int(time.strftime("%H%M"))

        
        detected_meta_info.device_id = BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].device_id
        detected_meta_info.RTSP_URL = BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].RTSP_URL
        detected_meta_info.detected_object_info_list = []

        #detected_object_info = None
        #detected_object_info = DetectedObjectInfo()
        #detected_object_info.detected_object = "no object"
        #detected_meta_info.detected_object_info_list.append(detected_object_info)
        

        ##xxprint("FrameNumber",frame_meta.frame_num)

        l_obj=frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta
        is_first_obj = True
        save_image = False




        #CameraList[camera_id].ObjectCount = 0 ### for Facility 
        #if l_obj is not None:
        while l_obj is not None:
            try: 
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            confidence = detected_meta_info.camera_info.Confidence / 100
                            
            #obj_meta.rect_params.border_color.set(0.0, 0.0, 0.0, 0.0)
            #obj_meta.rect_params.width=0
            #obj_meta.rect_params.height=0
            #obj_meta.text_params.display_text=""
            #obj_meta.text_params.set_bg_clr = 0
            width = obj_meta.rect_params.width
            height = obj_meta.rect_params.height
            top = obj_meta.rect_params.top
            left = obj_meta.rect_params.left

            
            #if(obj_meta.confidence > confidence or True  == True):
            
            # display detected object with confidence
            '''
            obj_meta.rect_params.border_color.set(0.0, 0.0, 1.0, 0.0)
            obj_meta.rect_params.width = width
            obj_meta.rect_params.height = height
            obj_meta.text_params.set_bg_clr = 1
            obj_meta.text_params.display_text = "{} : {}%".format(BridgeDeviceConfigVariable.pgie_classes_str_peoplenet[obj_meta.class_id],str(int(obj_meta.confidence*100)))
            obj_meta.text_params.font_params.font_size = 8
            '''

            current_millitime = str(int(current_milli_time() / 1000))

            scenedata_name = current_millitime + "" + str(frame_number) 
            scenedata_name = currenttime + str(frame_number)

            text_parameters = obj_meta.text_params
            rect_parameters = obj_meta.rect_params
            top = str(int(rect_parameters.top))
            left = str(int(rect_parameters.left))
            width = str(int(rect_parameters.width))
            height = str(int(rect_parameters.height))
            confidence = str(int(obj_meta.confidence * 100))
        
            if(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "far_car"):
                BridgeDeviceConfigVariable.pgie_classes_str = BridgeDeviceConfigVariable.pgie_classes_str_yolo
            elif(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "normal_car"):
                BridgeDeviceConfigVariable.pgie_classes_str = BridgeDeviceConfigVariable.pgie_classes_str_deepstream
            elif(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "normal_ellexi"):
                BridgeDeviceConfigVariable.pgie_classes_str = BridgeDeviceConfigVariable.pgie_classes_str_ellexi
            elif(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "normal_tnmfire"):
                BridgeDeviceConfigVariable.pgie_classes_str = BridgeDeviceConfigVariable.pgie_classes_str_fire
            elif(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "far"):
                BridgeDeviceConfigVariable.pgie_classes_str = BridgeDeviceConfigVariable.pgie_classes_str_peoplenet
            elif(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "normal"):
                BridgeDeviceConfigVariable.pgie_classes_str = BridgeDeviceConfigVariable.pgie_classes_str_peoplenet


            detected_object = None
            #print("DETECTED_OBJECT :::::::::",detected_meta_info.camera_id,obj_meta.class_id)
            #print("ClassID",BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id])

     
            detected_object = BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id]

            
            xmin = int(rect_parameters.left)
            ymin = int(rect_parameters.top)
            xmax = xmin + int(rect_parameters.width)
            ymax = ymin + int(rect_parameters.height)

            detected_object_info = None
            detected_object_info = DetectedObjectInfo()
            #detected_object_info.top = int(rect_parameters.top) #+ int(rect_parameters.height)
            #detected_object_info.left = int(rect_parameters.left) 
            #detected_object_info.width = int(rect_parameters.width) 
            #detected_object_info.height = int(rect_parameters.height) 

            detected_object_info.top = int(int(rect_parameters.height) * 0.1)
            detected_object_info.left = int(rect_parameters.left) 
            detected_object_info.width = int(rect_parameters.width) 
            detected_object_info.height = int(int(rect_parameters.height) * 0.9)



            detected_object_info.x1 = xmin 
            detected_object_info.x2 = xmax
            detected_object_info.y1 = ymin
            detected_object_info.y2 = ymax 
            detected_object_info.confidence = obj_meta.confidence
            detected_object_info.detected_object = BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id]


            #if(detected_meta_info.camera_info.Distance.lower() == "normal_car"):
            #    detected_object_info.detected_object = BridgeDeviceConfigVariable.pgie_classes_str_deepstream[obj_meta.class_id]
            #elif(detected_meta_info.camera_info.Distance.lower() == "far_car"):
            #    detected_object_info.detected_object = BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id]
            #else:
            #detected_object_info.detected_object = BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id]


            detected_object_info.scenedata_name = scenedata_name
            detected_meta_info.scenedata_name = scenedata_name
            detected_object_info.detected_time_ms = current_milli_time()

            if(frame_number % BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS == 0):
                pass
            else:
                frame_number = frame_number - 1

            detected_meta_info.frame_num = frame_number
            #if(detected_object.lower() == "person"):
   
            full_image_file_name = decimal_fill(frame_number,10) + ".jpeg"
            thumbnail_image_file_name = full_image_file_name
            
            BridgeDeviceConfigVariable.CameraList[cameraIndex - 1].ImageNameList.append(full_image_file_name)

            detected_meta_info.full_image_file_name = full_image_file_name
            detected_meta_info.thumbnail_image_file_name = thumbnail_image_file_name

            if(camera_confidence <= detected_object_info.confidence):
                if(detected_meta_info.camera_info.Distance.lower() == "normal_car"):
                    if(detected_object_info.detected_object.lower() == "car"):
                        detected_object_info.detected_object = "person"
                        detected_meta_info.detected_object_info_list.append(detected_object_info)
                        status = "CAMERA : " + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.origin_frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + detected_object + "(" + str(detected_object_info.confidence) + ") X : " + str(detected_object_info.left) + " Y : " + str(detected_object_info.top), "WIDTH : " + str(detected_object_info.width), "HEIGHT : " + str(detected_object_info.height)
                        debug_message = status
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                elif(detected_meta_info.camera_info.Distance.lower() == "far_car"):
                    if(detected_object.lower() == "person"):
                        detected_meta_info.detected_object_info_list.append(detected_object_info)
                        status = "CAMERA : " + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.origin_frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + detected_object + "(" + str(detected_object_info.confidence) + ") X : " + str(detected_object_info.left) + " Y : " + str(detected_object_info.top) + "::" + str(detected_object_info.height + detected_object_info.top), "WIDTH : " + str(detected_object_info.width), "HEIGHT : " + str(detected_object_info.height)
                        debug_message = status
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                elif(detected_meta_info.camera_info.Distance.lower() == "normal_tnmfire"):
                        if(detected_object.lower() == "fire"):
                            detected_meta_info.detected_object_info_list.append(detected_object_info)
                            status = "CAMERA : " + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.origin_frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + detected_object + "(" + str(detected_object_info.confidence) + ") X : " + str(detected_object_info.left) + " Y : " + str(detected_object_info.top), "WIDTH : " + str(detected_object_info.width), "HEIGHT : " + str(detected_object_info.height)
                            debug_message = status
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                elif(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].Distance.lower() == "normal_ellexi"):
                        if(detected_object.lower() == "lying" or True == True):
                            detected_meta_info.detected_object_info_list.append(detected_object_info)
                            status = "CAMERA : " + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.origin_frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + detected_object + "(" + str(detected_object_info.confidence) + ") X : " + str(detected_object_info.left) + " Y : " + str(detected_object_info.top), "WIDTH : " + str(detected_object_info.width), "HEIGHT : " + str(detected_object_info.height)
                            debug_message = status
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                            #bounding_value = "#{} : {} : {} : {} : {} : {} : {}".format(detected_meta_info.origin_frame_num,detected_object_info.left,detected_object_info.top,detected_object_info.width,detected_object_info.height,detected_object_info.confidence,detected_object)
                            #print(bounding_value)
                else:
                    if(detected_object.lower() == "person"):
                        if(detected_object_info.width > 40 and detected_object_info.height > 40):
                            detected_meta_info.detected_object_info_list.append(detected_object_info)
                            status = "CAMERA : " + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.origin_frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + detected_object + "(" + str(detected_object_info.confidence) + ") X : " + str(detected_object_info.left) + " Y : " + str(detected_object_info.top), "WIDTH : " + str(detected_object_info.width), "HEIGHT : " + str(detected_object_info.height)
                            debug_message = status
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)



            try: 
                l_obj=l_obj.next
            except StopIteration:
                break
    

        if(len(detected_meta_info.detected_object_info_list) > 0):
            cameraIndex = int(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id) - 1
            BridgeDeviceConfigVariable.DetectedObjectMetaInfoList[cameraIndex].append(detected_meta_info)

            if(int(previous_currenttime[cameraIndex]) < int(currenttime)):
                print(BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id,previous_currenttime[cameraIndex],currenttime)
                #if(os.path.isdir(video_result_directory)):
                #    pass
                #else:
                #    os.mkdir(video_result_directory)

                VideoCameraID = BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].device_id + "_" + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].camera_id
                #if(os.path.isdir(video_result_directory + "/" + VideoCameraID)):
                #    pass
                #else:
                #    os.mkdir(video_result_directory + "/" + VideoCameraID)

                file_name = BridgeDeviceConfigVariable.video_time_result_directory + VideoCameraID + "/" + BridgeDeviceConfigVariable.video_recording_time_file
                print(file_name)
                with open(file_name, 'a') as fd:
                    fd.write(f'{currenttime}\n')
                    fd.close()
                previous_currenttime[cameraIndex] = currenttime

        else:
            pass
            #detected_meta_info.detected_object_info_list = []
            #detected_object_info = None
            #detected_object_info = DetectedObjectInfo()
            #detected_object_info.detected_object = "no object"
            #detected_meta_info.detected_object_info_list.append(detected_object_info)
            #BridgeDeviceConfigVariable.DetectedObjectMetaInfoList[cameraIndex].append(detected_meta_info)

            #print("no object=========>>>>>",len(detected_meta_info.detected_object_info_list))

            #for item in detected_meta_info.detected_object_info_list:
            #    status = "CAMERAID :" + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + item.detected_object + "(" + str(detected_object_info.confidence) + ")", "X : " + str(item.left) + " Y : " + str(item.top), "WIDTH : " + str(item.width), "HEIGHT : " + str(item.height) + " RTSP URL :" + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].RTSP_URL
            #    debug_message = "header:{} ".format(status)
                #DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                #print("CAMERAID :" + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].CameraID + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + item.detected_object + "(" + str(detected_object_info.confidence) + ")", "X : " + str(item.left) , "Y : " + str(item.top), "WIDTH : " + str(item.width), "HEIGHT : " + str(item.height) + " RTSP URL :" + BridgeDeviceConfigVariable.CameraList[frame_meta.source_id].RTSP_URL) 
                #if(item.detected_object.lower() == "person"):
                #    print(str(detected_meta_info.frame_num).zfill(5),str(item.width).zfill(4),str(item.height).zfill(4),item.detected_object)
        '''
        display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        display_meta_rect_params = 0 
        py_nvosd_text_params = display_meta.text_params[0]
        py_nvosd_text_params.display_text = currenttime + "::::::[" + str(frame_number) + "]" + "::::"
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 200
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 20
        py_nvosd_text_params.font_params.font_color.red = 1.0
        py_nvosd_text_params.font_params.font_color.green = 1.0
        py_nvosd_text_params.font_params.font_color.blue = 1.0
        py_nvosd_text_params.font_params.font_color.alpha = 1.0
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.red = 0.0
        py_nvosd_text_params.text_bg_clr.green = 0.0
        py_nvosd_text_params.text_bg_clr.blue = 0.0
        py_nvosd_text_params.text_bg_clr.alpha = 1.0
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        display_meta_rect_params = 0
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        '''
 
        fps_streams["stream{0}".format(frame_meta.pad_index)].get_fps()


        try:
            l_frame=l_frame.next

        except StopIteration:
            break


    return Gst.PadProbeReturn.OK



def cb_newpad(decodebin, decoder_src_pad,data,index):
    debug_message = ""
    print("######## cb_newpad",index)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    try:
        caps=decoder_src_pad.get_current_caps()
        if(BridgeDeviceConfigVariable.URI_DECODE_BIN == "uridecodebin3"):
            caps = decodebin.get_property("caps")            
        print("### CAPS",caps)

        gststruct=caps.get_structure(0)
        gstname=gststruct.get_name()
        source_bin=data
        features=caps.get_features(0)

        # Need to check if the pad created by the decodebin is for video and not
        # audio.
        print("gstname=",gstname)

        if(gstname.find("video")!=-1):
            # Link the decodebin pad only if decodebin has picked nvidia
            # decoder plugin nvdec_*. We do this by checking if the pad caps contain
            # NVMM memory features.
            print("features=",features)

            if features.contains("memory:NVMM"):
                print("######",source_bin,"######")

                # Get the source bin ghost pad
                bin_ghost_pad=source_bin.get_static_pad("src")
                print("######AA",bin_ghost_pad,"AA######")
                if not bin_ghost_pad.set_target(decoder_src_pad):
                    debug_message = ("Failed to link decoder src pad to source bin ghost pad\n")
                    kill_application(index)
            else:
                debug_message = (" Error: Decodebin did not pick nvidia decoder plugin.\n")
                kill_application(index)

    except Exception as ex:
        debug_message = "111::: ERROR MESSAGE :::" + str(ex)
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(index)

def decodebin_child_added(child_proxy,Object,name,user_data,index):
    print("######## decodebin_child_added",index)

    debug_message = "Decodebin child added:{} :: {}".format(name,index)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

    print(debug_message)
    if(name.find("decodebin") != -1):
        Object.connect("child-added",decodebin_child_added,user_data,index)   

    if(is_aarch64() and name.find("nvv4l2decoder") != -1):
        DROP_FRAME_INTERVAL = BridgeDeviceConfigVariable.CameraList[int(index)].drop_frame_interval
        debug_message = "#######DROP_FRAME_INTERVAL : {}".format(BridgeDeviceConfigVariable.CameraList[int(index)].drop_frame_interval)
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        Object.set_property("bufapi-version",True)
        Object.set_property("drop-frame-interval",DROP_FRAME_INTERVAL)
        print(debug_message)
    elif(name.find("nvv4l2decoder") != -1):    
        DROP_FRAME_INTERVAL = BridgeDeviceConfigVariable.CameraList[int(index)].drop_frame_interval
        debug_message = "DROP_FRAME_INTERVAL : {}".format(BridgeDeviceConfigVariable.CameraList[int(index)].drop_frame_interval)
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        Object.set_property("drop-frame-interval",DROP_FRAME_INTERVAL)
        print(debug_message)
      
def create_source_bin(index,uri):
    try:
        # Create a source GstBin to abstract this bin's content from the rest of the
        # pipeline
        bin_name="source-bin-%02d" %index
        debug_message = bin_name
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        nbin=Gst.Bin.new(bin_name)
        if not nbin:
            #debug_message = (" Unable to create source bin \n")
            debug_message = "Unable to create source bin"
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            kill_application(index)

        # Source element for reading from the uri.
        # We will use decodebin and let it figure out the container format of the
        # stream and the codec and plug the appropriate demux and decode plugins.
        uri_decode_bin=Gst.ElementFactory.make(BridgeDeviceConfigVariable.URI_DECODE_BIN, "uri-decode-bin")

        if not uri_decode_bin:
            #debug_message = (" Unable to create uri decode bin \n")
            debug_message = "Unable to create uri decode bin"
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            kill_application(index)

        # We set the input uri to the source element
        uri_decode_bin.set_property("uri",uri)
      

    
        # Connect to the "pad-added" signal of the decodebin which generates a
        # callback once a new prtsp://192.168.0.11:1935/vod/mp4:highway.mp4ad for raw data has beed created by the decodebin
        uri_decode_bin.connect("pad-added",cb_newpad,nbin,index)
        uri_decode_bin.connect("child-added",decodebin_child_added,nbin,index)

        # We need to create a ghost pad for the source bin which will act as a proxy
        # for the video decoder src pad. The ghost pad will not have a target right
        # now. Once the decode bin creates the video datadecoder and generates the
        # cb_newpad callback, we will set the ghost pad target to the video decoderGetFileSizeBytes
        # src pad.
        Gst.Bin.add(nbin,uri_decode_bin)
        bin_pad=nbin.add_pad(Gst.GhostPad.new_no_target("src",Gst.PadDirection.SRC))
        if not bin_pad:
            debug_message = "Failed to add ghost pad in source bin"
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            #debug_message = (" Failed to add ghost pad in source bin \n")
            kill_application(index)
            return None
        return nbin
    except Exception as ex:
        print("#########ERROR CODE",ex)
        kill_application()

def kill_application():
    os.kill(os.getpid(),signal.SIGKILL)

def kill_application(cameraIndex):
    cameraIndex = 0 
    print("####### KILL APPLICATION #######")

    os.kill(os.getpid(),signal.SIGKILL)



def kill_application2():
    global BridgeDeviceConfigVariable
    BridgeDeviceConfigVariable.CameraList = None

    os.kill(os.getpid(),signal.SIGKILL)




def detect_start(camera_info,cameraIndex):
    number_sources = 1
    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    debug_message = "Creating Pipeline"
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    PIPELINE = None
    PIPELINE = Gst.Pipeline()
    try:
        BridgeDeviceConfigVariable.PIPELINE_INFO_LIST[cameraIndex-1].PIPELINE = PIPELINE
    except Exception as ex:
        kill_application(cameraIndex)

    is_live = False

    if not PIPELINE:
        debug_message = "Unable to create Pipeline "
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)
    #xxprint("Creating streamux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        debug_message = "Unable to create NvStreamMux "
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    PIPELINE.add(streammux)
    #for i in range(number_sources):
    fps_streams["stream{0}".format(cameraIndex - 1)]=GETFPS(cameraIndex - 1)
    #xxprint("CreatingstrSceneDataEndPoint source_bin ",i," \n ")
    uri_name=camera_info.RTSP_URL
 
    debug_message = "CAMERA RTSP :: {} : {}".format(str(cameraIndex).zfill(4),uri_name)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    sys.stderr.write("####" + debug_message + "#####")

    if uri_name.find("rtsp://") == 0 or  uri_name.find("rtspt://") == 0:
        is_live = True
    source_bin=create_source_bin(cameraIndex - 1, uri_name)
    if not source_bin:
        debug_message = ("Unable to create source bin \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    PIPELINE.add(source_bin)
    padname="sink_%u" %(cameraIndex-1)
    sinkpad= streammux.get_request_pad(padname) 
    if not sinkpad:
        debug_message = ("Unable to create sink pad bin \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    srcpad=source_bin.get_static_pad("src")
    if not srcpad:
        debug_message = ("Unable to create src pad bin \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    srcpad.link(sinkpad)
    
    h264parser = Gst.ElementFactory.make("h264parse","h264-parser")


    if not h264parser:
        debug_message = ("Unable to create h264 parse\n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    


    #xxprint("Creating Decoder\n")
    decoder = Gst.ElementFactory.make("nvv4l2decoder","nvv4l2-decorder")
    if not decoder:
        debug_message = (" Unable to create Nvv4l2 Decoder\n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    #xxprint("Creating Pgie \n ")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        debug_message = (" Unable to create pgie \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
    if not nvvidconv1:
        debug_message = (" Unable to create nvvidconv1 \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    #xxprint("Creating filter1 \n ")
    #BridgeDeviceConfigVariable.Resolution_Convert_Width = 960
    #BridgeDeviceConfigVariable.Resolution_Convert_Height = 540
    convert_string = "video/x-raw(memory:NVMM),width={},height={},format=RGBA".format(BridgeDeviceConfigVariable.Resolution_Convert_Width,BridgeDeviceConfigVariable.Resolution_Convert_Height)    
    #convert_string = "application/x-rtp,width={},height={},format=RGBA".format(BridgeDeviceConfigVariable.Resolution_Convert_Width,BridgeDeviceConfigVariable.Resolution_Convert_Height)    
    #convert_string = "video/x-raw(memory:NVMM),format=(string)I420,width={},height={},format=RGBA".format(BridgeDeviceConfigVariable.Resolution_Convert_Width,BridgeDeviceConfigVariable.Resolution_Convert_Height)    

    caps1 = Gst.Caps.from_string(convert_string)    
    filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
    if not filter1:
        debug_message = (" Unable to get the caps filter1 \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    filter1.set_property("caps", caps1)
    #xxprint("Creating tiler \n ")
    tiler=Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
    
        debug_message = (" Unable to create tiler \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    #xxprint("Creating nvvidconv \n ")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        debug_message = (" Unable to create nvvidconv \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)


    #xxprint("Creating nvosd \n ")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        debug_message = (" Unable to create nvosd \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    
    if(is_aarch64()):
        #xxprint("Creating transform \n ")
        transform=Gst.ElementFactory.make("nvegltransform", "nvegl-transform")
        #transform=Gst.ElementFactory.make("queue", "queue")
        if not transform:
            debug_message = (" Unable to create transform \n")
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

            kill_application(cameraIndex)

    if BridgeDeviceConfigVariable.FakeSink == "Y":
        IsGraphicalMode = False
    else:
        IsGraphicalMode = True 

    if IsGraphicalMode:
        sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
        #sink = Gst.ElementFactory.make("nvoverlaysink", "nvvideo-renderer")
    else:
        sink = Gst.ElementFactory.make("fakesink","nvvideo-renderer")

    if not sink:
        debug_message = (" Unable to create egl sink \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

        kill_application(cameraIndex)


    if is_live:
        streammux.set_property('live-source', 1)

    for item in camera_info.SceneModeConfig:
        if(item["CustomAnalysisStage"] == "NewSceneMode"):
            pass
        else:
            ScreenSize = item["Resolution"].split("x")
            BridgeDeviceConfigVariable.Resolution_Width = int(ScreenSize[0])
            BridgeDeviceConfigVariable.Resolution_Height = int(ScreenSize[1])
            #BridgeDeviceConfigVariable.Resolution_Width = 960
            #BridgeDeviceConfigVariable.Resolution_Height = 540
            debug_message = "CAMERA:{} WIDTH:{} HEIGHT:{}".format(camera_info.CameraID,ScreenSize[0],ScreenSize[1])
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

            break

    streammux.set_property('width', BridgeDeviceConfigVariable.Resolution_Width)
    streammux.set_property('height', BridgeDeviceConfigVariable.Resolution_Height)
    streammux.set_property('batch-size', number_sources)
    streammux.set_property('batched-push-timeout', BridgeDeviceConfigVariable.MUXER_BATCH_TIMEOUT_USEC) #4000000

    debug_message = "CAMERA:{} DISTANCE:{}".format(camera_info.CameraID,camera_info.Distance)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    if(camera_info.Distance.lower() == "far"):
        pgie.set_property('config-file-path', BridgeDeviceConfigVariable.InferenceEngineConfigFile_540)
    elif(camera_info.Distance.lower() == "normal_car"):
        pgie.set_property('config-file-path', BridgeDeviceConfigVariable.InferenceEngineConfigFileDeepStream)
    elif(camera_info.Distance.lower() == "far_car"):
        pgie.set_property('config-file-path', BridgeDeviceConfigVariable.InferenceYoloEngineConfigFileYolo)
    elif(camera_info.Distance.lower() == "normal_ellexi"):
        pgie.set_property('config-file-path', BridgeDeviceConfigVariable.InferenceYoloEngineConfigFileYolo_Ellexi)
    elif(camera_info.Distance.lower() == "normal_tnmfire"):
        pgie.set_property('config-file-path', BridgeDeviceConfigVariable.InferenceYoloEngineConfigFileYolo_Fire)
    else:
        pgie.set_property('config-file-path', BridgeDeviceConfigVariable.InferenceEngineConfigFile_270)
    

    pgie.set_property("batch-size",number_sources)
    pgie_batch_size=pgie.get_property("batch-size")

    #if(pgie_batch_size != number_sources):
        ##xxprint("WARNING: Overriding infer-config batch-size",pgie_batch_size," with number of sources ", number_sources," \n")
    #    pgie.set_property("batch-size",number_sources)
    #pgie_batch_size=pgie.get_property("batch-size")
    #if(pgie_batch_size != number_sources):
    #    #xxprint("WARNING: Overriding infer-config batch-size",pgie_batch_size," with number of sources ", number_sources," \n")

    tiler_rows=int(math.sqrt(number_sources))
    tiler_columns=int(math.ceil((1.0*number_sources)/tiler_rows))
    tiler.set_property("rows",tiler_rows)
    tiler.set_property("columns",tiler_columns)
    tiler.set_property("width", BridgeDeviceConfigVariable.TILED_OUTPUT_WIDTH)
    tiler.set_property("height", BridgeDeviceConfigVariable.TILED_OUTPUT_HEIGHT)
    sink.set_property("qos",0)
    sink.set_property("sync", 0)
    if not is_aarch64():
        # Use CUDA unified memory in the pipeline so frames
        # can be easily accessed on CPU in Python.
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        streammux.set_property("nvbuf-memory-type", mem_type)
        nvvidconv.set_property("nvbuf-memory-type", mem_type)
        nvvidconv1.set_property("nvbuf-memory-type", mem_type)
        tiler.set_property("nvbuf-memory-type", mem_type)
    else:
        mem_type = 0
        streammux.set_property("nvbuf-memory-type", mem_type)
        nvvidconv.set_property("nvbuf-memory-type", mem_type)
        nvvidconv1.set_property("nvbuf-memory-type", mem_type)
        tiler.set_property("nvbuf-memory-type", mem_type)
    
    PIPELINE.add(h264parser)
    PIPELINE.add(decoder)
    PIPELINE.add(pgie)
    PIPELINE.add(tiler)
    PIPELINE.add(nvvidconv)
    PIPELINE.add(filter1)
    PIPELINE.add(nvvidconv1)
    PIPELINE.add(nvosd)
    ## graphical
    if IsGraphicalMode:
        if is_aarch64():
            PIPELINE.add(transform)

    PIPELINE.add(sink)

    ##xxprint("Linking elements in the Pipeline \n")
    streammux.link(pgie)       
    pgie.link(nvvidconv1)
    nvvidconv1.link(filter1)
    filter1.link(tiler)
    tiler.link(nvvidconv)
    nvvidconv.link(nvosd)


    ##graphical 
    if IsGraphicalMode:
        if is_aarch64():
            nvosd.link(transform)
            transform.link(sink)
        else:
            nvosd.link(sink)
    else:
        ##non graphical
        nvosd.link(sink)
    # create an event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()
    bus = PIPELINE.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)

    tiler_sink_pad=tiler.get_static_pad("sink")
    if not tiler_sink_pad:
        debug_message = (" Unable to get src pad \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(cameraIndex)

    else:
        status_f = open("status.dat","w")
        status_f.write("4")
        status_f.close()
        tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, tiler_sink_pad_buffer_probe,0)
	

    PIPELINE.set_state(Gst.State.PLAYING)
    BridgeDeviceConfigVariable.IsBridgeDeviceRunning = True
    BridgeDeviceConfigVariable.IsRTSPDown = False

    try:
        loop.run()
    except Exception as ex:
        print("###### PIPELINE GET STATE = ", ex)

        pass
    # cleanup
    ##xxprint("Exiting app\n")
    debug_message = "###########  CAMERA IS DOWN " + camera_info.RTSP_URL
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    sys.stderr.write(debug_message)

    PIPELINE.set_state(Gst.State.NULL)
    kill_application2()


def create_metadata(sm_meta_info_list,cameraIdx):
    sm_meta_info = sm_meta_info_list[0]

    '''
    if(sm_meta_info.camera_id == "0006"):
        for item in sm_meta_info_list:
            item.camera_info.SceneModeConfig[0]["AnalysisRegion"]["ROICoords"][0]["Coords"]  = None
            item.camera_info.SceneModeConfig[0]["AnalysisRegion"]["ROICoords"][0]["Coords"]  = []

            item.camera_info.SceneModeConfig[0]["AnalysisRegion"]["ROICoords"][0]["Coords"].append({"XCoord": 0, "YCoord": 0})
            item.camera_info.SceneModeConfig[0]["AnalysisRegion"]["ROICoords"][0]["Coords"].append({"XCoord": 1920, "YCoord": 0})
            item.camera_info.SceneModeConfig[0]["AnalysisRegion"]["ROICoords"][0]["Coords"].append({"XCoord": 1920, "YCoord":1080})
            item.camera_info.SceneModeConfig[0]["AnalysisRegion"]["ROICoords"][0]["Coords"].append({"XCoord": 0, "YCoord": 1080})
    '''

   

    BridgeDeviceID = sm_meta_info.device_id
    CameraID = sm_meta_info.camera_id
    NodeID = int(sm_meta_info.camera_id)
    PortID = 1234
    TimeToUTC = 9 * 3600
    Instance = current_milli_time()
    SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(NodeID), Instance)



    #print("######### META DATA ############",StartTime, EndTime, EndTime - StartTime)

    # Generate MetaData for Facility 
    StartTime = time.time()

    if(sm_meta_info.camera_info.Distance.lower() == "normal_ellexi"):
        EllexiDataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.EllexiMetaDataDirectory,BridgeDeviceID,sm_meta_info.camera_id)
        SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(NodeID), Instance)
        if(os.path.isdir(EllexiDataDirectory) == False):
            os.mkdir(EllexiDataDirectory)  
        DataFileName = "{}/{}.dat".format(EllexiDataDirectory,SceneMarkID)
        with open(DataFileName,"wb") as f:
            pickle.dump(sm_meta_info_list,f)
    else:
        #for item in sm_meta_info_list:
        #    if(len(item.detected_object_info_list) == 1):
        #        sm_meta_info_list.remove(item)
        #print("sm_meta_info_list============>",len(sm_meta_info_list))
        if(len(sm_meta_info_list) > 0):
            DataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.MetaDataDirectory,BridgeDeviceID,sm_meta_info.camera_id)
        
            #print("#### DataDirectory",DataDirectory)
            if(os.path.isdir(DataDirectory) == False):
                os.mkdir(DataDirectory)  
            DataFileName = "{}/{}.dat".format(DataDirectory,SceneMarkID)

            with open(DataFileName,"wb") as f:
                pickle.dump(sm_meta_info_list,f)

        for item in sm_meta_info.camera_info.SceneModeConfig:
            if item["CustomAnalysisStage"].lower().startswith("facility"):
                FDataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.FMetaDataDirectory,BridgeDeviceID,sm_meta_info.camera_id)
                Instance = current_milli_time()
                SceneMarkID = CreateSceneMarkID(BridgeDeviceID, int(NodeID), Instance)
                if(os.path.isdir(FDataDirectory) == False):
                    os.mkdir(FDataDirectory)  
                DataFileName = "{}/{}.dat".format(FDataDirectory,SceneMarkID)
                with open(DataFileName,"wb") as f:
                    pickle.dump(sm_meta_info_list,f)
                break
    EndTime = time.time()
    #print("######### FACILITY  META DATA ############",StartTime, EndTime, EndTime - StartTime)

def upload_scenemark_list(detected_object_meta_info, cameraIndex):
    detected_time = 0
    count = 0 

    while(True):
        try:
            CameraID = decimal_fill(cameraIndex + 1,4)
            idx = -1 
            CameraIdx = -1
            for i in range(0,len(BridgeDeviceConfigVariable.CameraList)):
                if(CameraID == BridgeDeviceConfigVariable.CameraList[i].CameraID):
                    CameraIdx = i
                    break
            #print("### CAMERA INDEX",CameraIdx)
            sm_meta_info_list = None
            sm_meta_info_list = []
            if(len(detected_object_meta_info) > 0 and CameraIdx > -1):
                StartTime = time.time()    
                count = 0 
                #for i in range(0,len(detected_object_meta_info)):
                #print("###### BridgeDeviceConfigVariable.CameraList[CameraIdx].InferenceFPS * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA",BridgeDeviceConfigVariable.CameraList[CameraIdx].InferenceFPS * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA)

                while detected_object_meta_info:
                    #if count < (BridgeDeviceConfigVariable.CameraList[CameraIdx].InferenceFPS * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA): 
                    if count < (30 * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA): 

                        sm_meta_info = detected_object_meta_info.pop(0)
                        
                        #print("### FRAMENUMBER######",sm_meta_info.frame_num,len(sm_meta_info.detected_object_info_list))
                        #sm_meta_info = detected_object_meta_info.popleft()
                        clip_image_directory = "{}/{}_{}".format(BridgeDeviceConfigVariable.ImageSaveDirectory,sm_meta_info.device_id,sm_meta_info.camera_id)
                        sm_meta_info.clip_image_directory = clip_image_directory 
                        sm_meta_info_list.append(sm_meta_info)
                    else: 
                        break
                    count = count + 1
                EndTime = time.time()

            #print("##### CameraID =",CameraID,StartTime,EndTime,EndTime-StartTime)

            #if(len(sm_meta_info_list) > 0):
            #    create_metadata(sm_meta_info_list,idx)
        except Exception as ex:
            debug_message = ":::: ERROR MESSAGE :::".format(str(ex))
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            pass

        time.sleep(BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA)

def check_cameras_configuration():
    BridgeDeviceConfigVariable.PIPELINE_INFO_LIST = []
    IsFirstTime = True
    ProcessTimeSleep = 10
    IsSelfCheckFirstTime = True
    while(True):
        try:
            isChanged = False
            bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
            if(os.path.isfile(bridge_device_config_file_name)):
                with open(bridge_device_config_file_name,"rb") as f:
                    Config = json.loads(pickle.load(f))
                    if(Config):
                        BridgeDeviceInfo = Config["BridgeDeviceInfo"]
                        if(IsSelfCheckFirstTime == False):
                            #print("######### BridgeDeviceInfo SelfCheckYn Passed ",BridgeDeviceInfo["SelfCheckYn"] == "Y",isChanged, ProcessTimeSleep)
                            pass
                        else:
                            ProcessTimeSleep = 10
                            if(len(BridgeDeviceConfigVariable.CameraList) > 0):
                                for item in BridgeDeviceInfo["CameraList"]:
                                    ##### Parsing Camera Info 
                                    camera_info = parsing_camerainfo(item,BridgeDeviceConfigVariable.BridgeDeviceID) 
                    
                                    if(camera_info.Use == "Y" and camera_info.CameraType == BridgeDeviceConfigVariable.CameraType and camera_info.AIModelType == BridgeDeviceConfigVariable.AIModelType): ## check already using 
                                        isExisted = False
                                        for camera_meta_info in BridgeDeviceConfigVariable.CameraList:
                                            if(camera_info.RTSP_URL == camera_meta_info.RTSP_URL and camera_info.CameraID == camera_meta_info.camera_id):
                                                isExisted = True
                                                break

                                        if(isExisted == False):  
                                            isChanged = True   
                                            #CameraList.append(camera_info)
                                        else:
                                            ##xxprint("camera_info.use = {},{}".format(camera_info.Use,camera_info.SceneMarkMode))
                                            for camera_item in BridgeDeviceConfigVariable.CameraList:
                                                if int(camera_item.CameraID) == int(camera_info.CameraID):
                                                    camera_item.WorkTime = {
                                                        "StartTime":camera_info.WorkTime["StartTime"],
                                                        "EndTime":camera_info.WorkTime["EndTime"]
                                                    }
                                                    ##xxprint("CameraID = {} : {}".format(camera_item.CameraID,camera_item.CameraID))
                                                    camera_item.SceneMarkMode = []
                                                    for scenemode in camera_info.SceneMarkMode:
                                                        camera_item.SceneMarkMode.append(scenemode)

                                                    camera_item.Confidence = camera_info.Confidence
                                                    camera_item.SceneModeConfig = camera_info.SceneModeConfig
                                                
                                                    camera_item.ShowError = camera_info.ShowError
                                                    camera_item.Detection_Area = []
                                                    for item in camera_info.Detection_Area:
                                                        area = {
                                                            "x1":item["x1"],
                                                            "x2":item["x2"],
                                                            "y1":item["y1"],
                                                            "y2":item["y2"]
                                                        }
                                                        camera_item.Detection_Area.append(area)
                                                    
                                                    camera_item.Skip_Area = []
                                                    for item in camera_info.Skip_Area:
                                                        area = {
                                                            "x1":item["x1"],
                                                            "x2":item["x2"],
                                                            "y1":item["y1"],
                                                            "y2":item["y2"]
                                                        }
                                                        camera_item.Skip_Area.append(area)
                                                    break
                                    else:
                                        for camera_meta_info in BridgeDeviceConfigVariable.CameraList:
                                            if(camera_info.RTSP_URL == camera_meta_info.RTSP_URL and camera_info.CameraID == camera_meta_info.camera_id):
                                                isChanged = True
                                                #CameraList.remove(camera_meta_info)
                                                break
                            else:
                                for item in BridgeDeviceInfo["CameraList"]:
                                    camera_info = parsing_camerainfo(item,BridgeDeviceConfigVariable.BridgeDeviceID)    
                                    if(camera_info.Use == "Y" and camera_info.CameraType == BridgeDeviceConfigVariable.CameraType and camera_info.AIModelType == BridgeDeviceConfigVariable.AIModelType):
                                        isChanged = True
                            
                            if(len(BridgeDeviceConfigVariable.CameraList) != len(BridgeDeviceInfo["CameraList"])):
                                isChanged = True
                                
                            if(len(BridgeDeviceConfigVariable.CameraList) == len(BridgeDeviceInfo["CameraList"])):
                                kk = 0 
                                for camera_meta_info in BridgeDeviceConfigVariable.CameraList:
                                    camera_info = parsing_camerainfo(BridgeDeviceInfo["CameraList"][kk],BridgeDeviceConfigVariable.BridgeDeviceID) 
                                    if(camera_info.Distance.lower() != camera_meta_info.Distance.lower()):
                                        isChanged = True 
                                        debug_message = ("###### DISTANCE HAS BEEN CHANGED>>>>>>>>#########::::::::")
                                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                                        break
                                    kk = kk + 1

                            BridgeDeviceConfigVariable.TOLERANCE = int(BridgeDeviceInfo["TOLERANCE"])
                            if(BridgeDeviceConfigVariable.FakeSink != BridgeDeviceInfo["FakeSink"]):
                                isChanged = True
                                BridgeDeviceConfigVariable.FakeSink = BridgeDeviceInfo["FakeSink"]
                        
                    
                    
                    if(isChanged):# and len(BridgeDeviceInfo["CameraList"]) > 0):
                        ##xxprint("##### is changed......" + str(len(CameraList)))
                        
                        if(IsFirstTime == False):
                            os.kill(os.getpid(),signal.SIGKILL)
                        IsFirstTime = False
                        for PipeLineInfo in BridgeDeviceConfigVariable.PIPELINE_INFO_LIST:
                            if(PipeLineInfo.PIPELINE):
                                PipeLineInfo.PIPELINE.set_state(Gst.State.NULL)
                                PipeLineInfo.PIPELINE = None
                                debug_message = ("##### PIPELINE ALIVE......".format(PipeLineInfo))
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

            
                            if(PipeLineInfo.PIPELINE_THREAD):
                                PipeLineInfo.PIPELINE_THREAD._stop
                        '''        
                        if(PIPELINE):
                            if(os.path.isfile("status.dat")):
                                os.remove("status.dat")
                            PIPELINE.set_state(Gst.State.NULL)
                        '''
                        if(os.path.isfile("status.dat")):
                            os.remove("status.dat")
                        BridgeDeviceConfigVariable.PIPELINE_RUNNING = False
                        BridgeDeviceConfigVariable.IsBridgeDeviceRunning = False
                        BridgeDeviceConfigVariable.CameraList = []


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

                        #if(os.path.isdir("./content")):
                        #    shutil.rmtree("./content")

                        '''
                        if(os.path.isdir(BridgeDeviceConfigVariable.ImageSaveDirectory)):
                            shutil.rmtree(BridgeDeviceConfigVariable.ImageSaveDirectory,ignore_errors=True)

                        if(os.path.isdir(BridgeDeviceConfigVariable.ResultSaveDirectory)):
                            shutil.rmtree(BridgeDeviceConfigVariable.ResultSaveDirectory,ignore_errors=True)
                        
                        if(os.path.isdir(BridgeDeviceConfigVariable.SceneMarkDirectory)):
                            shutil.rmtree(BridgeDeviceConfigVariable.SceneMarkDirectory,ignore_errors=True)

                        if(os.path.isdir(BridgeDeviceConfigVariable.MetaDataDirectory)):
                            shutil.rmtree(BridgeDeviceConfigVariable.MetaDataDirectory,ignore_errors=True)

                        if(os.path.isdir(BridgeDeviceConfigVariable.SceneDataDirectory)):
                            shutil.rmtree(BridgeDeviceConfigVariable.SceneDataDirectory,ignore_errors=True)
                        '''
                        
                        if(os.path.isdir(BridgeDeviceConfigVariable.video_record_root)):
                            pass
                        else:
                            os.mkdir(BridgeDeviceConfigVariable.video_record_root)

                        if(os.path.isdir(BridgeDeviceConfigVariable.video_result_directory)):
                            pass
                        else:
                            os.mkdir(BridgeDeviceConfigVariable.video_result_directory)

                        if(os.path.isdir(BridgeDeviceConfigVariable.video_time_result_directory)):
                            pass
                        else:
                            os.mkdir(BridgeDeviceConfigVariable.video_time_result_directory)



                        if(os.path.isdir(BridgeDeviceConfigVariable.RootDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.RootDirectory)

                        if(os.path.isdir(BridgeDeviceConfigVariable.ImageSaveDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.ImageSaveDirectory)

                        if(os.path.isdir(BridgeDeviceConfigVariable.ResultSaveDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.ResultSaveDirectory)

                        if(os.path.isdir(BridgeDeviceConfigVariable.SceneMarkDirectory)  == False):
                            os.mkdir(BridgeDeviceConfigVariable.SceneMarkDirectory)

                        if(os.path.isdir(BridgeDeviceConfigVariable.MetaDataDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.MetaDataDirectory)

                        if(os.path.isdir(BridgeDeviceConfigVariable.FMetaDataDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.FMetaDataDirectory)           

                        if(os.path.isdir(BridgeDeviceConfigVariable.SceneDataDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.SceneDataDirectory)
                        
                        if(os.path.isdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory) == False):
                            os.mkdir(BridgeDeviceConfigVariable.EllexiMetaDataDirectory)
                        
                        for i in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
                            camera_directory = "{}_{}".format(BridgeDeviceConfigVariable.BridgeDeviceID,decimal_fill(i+1,4))
                            if(os.path.isdir(BridgeDeviceConfigVariable.video_time_result_directory + camera_directory)):
                                pass
                            else:
                                os.mkdir(BridgeDeviceConfigVariable.video_time_result_directory + camera_directory)

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
                                
                        #command = "ipcs -m | grep " + BridgeDeviceConfigVariable.UserAccount +  " | awk '{print $2}' | while read line ; do ipcrm -m $line; done"
                        #os.system(command)
            
                        #for i in range(0,len(BridgeDeviceConfigVariable.CameraList)):
                        cameraIndex = 1

                        for camera_info in BridgeDeviceConfigVariable.CameraList:
                            for config_item in camera_info.SceneModeConfig:
                                if(config_item["CustomAnalysisStage"] == "NewSceneMode"):
                                    camera_info.SceneModeConfig.pop(0)

                        file_list = []
                        for camera_info in BridgeDeviceConfigVariable.CameraList:
                            IsNewSceneMode = False
                            if(len(camera_info.SceneModeConfig) == 1):
                                for item in camera_info.SceneModeConfig:
                                    if(item["CustomAnalysisStage"] == "NewSceneMode"):
                                        IsNewSceneMode = True

                            if(IsNewSceneMode == False):
                                    PipeLineInfo = PipeLineInfoClass()
                                    PipeLineInfo.PIPELINE_THREAD = threading.Thread(target=detect_start,args=(camera_info,cameraIndex))
                                    PipeLineInfo.PIPELINE_THREAD.setName(decimal_fill(cameraIndex,4))
                                    PipeLineInfo.PIPELINE_THREAD.daemon = True
                                    PipeLineInfo.PIPELINE_THREAD.start()
                                    BridgeDeviceConfigVariable.PIPELINE_INFO_LIST.append(PipeLineInfo)
                                    cameraIndex = cameraIndex + 1
                        BridgeDeviceConfigVariable.PIPELINE_RUNNING = True
                   
       

                    #for camera in BridgeDeviceConfigVariable.CameraList:
                    #    print("####### CAMERAINFO #####",camera.CameraID,camera.SceneMarkToken)
                    
                    time.sleep(ProcessTimeSleep)
                    #for thread in threading.enumerate(): 
                    #    #xxprint("######## TRHEAD NAME ",thread.name,thread.is_alive())

        except Exception as ex:
            debug_message = ("Message ::: Parsing Configuration File Error" + str(ex))
            print(debug_message)
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            pass
            time.sleep(ProcessTimeSleep)

def remove_files(directory):
    file_list = os.listdir(directory)
    file_list.sort()
    for i in range(len(file_list)):
        if os.path.isfile(directory + "/" + file_list[i]):
            os.remove(directory + "/" + file_list[i])

def main():
    print("==========================================")
    print("::::: Inferencing Engine is started...::::")
    print("==========================================")

    BridgeDeviceConfigVariable.SceneMarkList = []


    #status_f = open("version.dat","w")
    #status_f.write(BridgeDeviceConfigVariable.VERSION)
    #status_f.close()

   
    ## Camera Configuration check 
    camera_check_thread = threading.Thread(target=check_cameras_configuration,args=())
    camera_check_thread.deamon = True
    camera_check_thread.setName("CameraCheckThread")
    camera_check_thread.start()
    #camera_check_thread.join()

    ## Uploading Scenemark and Scenedata Management
    
    BridgeDeviceConfigVariable.DetectedObjectMetaInfoList = []
    DetectedObjectMetaInfoList0 = []
    DetectedObjectMetaInfoList1 = []
    DetectedObjectMetaInfoList2 = []
    DetectedObjectMetaInfoList3 = []
    DetectedObjectMetaInfoList4 = []
    DetectedObjectMetaInfoList5 = []
    DetectedObjectMetaInfoList6 = []
    DetectedObjectMetaInfoList7 = []
    DetectedObjectMetaInfoList8 = []
    DetectedObjectMetaInfoList9 = []

    BridgeDeviceConfigVariable.DetectedObjectMetaInfoList = [
            DetectedObjectMetaInfoList0,
            DetectedObjectMetaInfoList1,
            DetectedObjectMetaInfoList2,
            DetectedObjectMetaInfoList3,
            DetectedObjectMetaInfoList4,
            DetectedObjectMetaInfoList5,
            DetectedObjectMetaInfoList6,
            DetectedObjectMetaInfoList7,
            DetectedObjectMetaInfoList8,
            DetectedObjectMetaInfoList9
        ]


    #print("################ LEN LEN LEN ",type(BridgeDeviceConfigVariable.DetectedObjectMetaInfoList[0].append('dkkdkd')))

    NodeID = 0 
    for item in BridgeDeviceConfigVariable.DetectedObjectMetaInfoList:
        upload_scenemark_thread = threading.Thread(target=upload_scenemark_list,args=(item,NodeID))
        upload_scenemark_thread.daemon = True
        upload_scenemark_thread.start()
        NodeID  = NodeID + 1
## LoadBridgeDeviceSecurityObject Disabled until it works 2020-09-24 DCJeong
def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable
    '''
    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceInferenceManager) > 1):
        print("==========================================")
        print("there is same process running already. process is about to be terminated.")
        print("==========================================")
        os.kill(os.getpid(),signal.SIGKILL)
    '''
    if(os.path.isfile(BridgeDeviceConfigVariable.DeviceSeurityObjectFile)):
        with open(BridgeDeviceConfigVariable.DeviceSeurityObjectFile) as DeviceSecurityObject:
            SecurityObject = json.load(DeviceSecurityObject)
            DeviceInfo = GetDeviceSecurityObject(SecurityObject)
            BridgeDeviceConfigVariable.BridgeDeviceID = GetDeviceID(DeviceInfo)
            NICELAEndPoint = GetNICELAEndPointEndPoint(DeviceInfo)
            NICELAAuthorty = GetNICELAEndPointAuthority(DeviceInfo)
            #xxprint(BridgeDeviceConfigVariable.BridgeDeviceID,NICELAEndPoint,NICELAAuthorty, "is called...")
            #ManagementInfo = GetManagementObject(NICELAAuthorty, BridgeDeviceID, NICELAEndPoint)
            if(BridgeDeviceConfigVariable.BridgeDeviceID):
                main()
            ##xxprintDebug(str(ManagementInfo))

LoadBridgeDeviceSecurityObject()

#xxprint("DeviceID = " + BridgeDeviceConfigVariable.BridgeDeviceID)
###################### STARTS ###############################
if(BridgeDeviceConfigVariable.BridgeDeviceID):
    pass
    #main()
else:
    time.sleep(5)
    LoadBridgeDeviceSecurityObject()