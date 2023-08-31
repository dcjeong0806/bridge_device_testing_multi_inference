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
import traceback
import copy

fps_streams={}

people_count = 0 
BridgeDeviceConfigVariable = VariableConfigClass()
PIPELINE = None
CheckFrameRate = 5.0

IsSelfCheckDone = False


class obj_meta_info:
    width = 0 
    height = 0
    top = 0 
    left = 0 
    class_id = 0 
    confidence = 0 
    frame_number = 0
    classlist = None 

class overlaps_contains:
    overlaps = False
    contains = False

# tiler_sink_pad_buffer_probe  will extract metadata received on tiler src pad
# and update params for drawing rectangle, object information etc.

def save_image_data(frame_image,header,width,height,isblurred):
    image_info_variable = header
    BridgeDeviceID = image_info_variable[:36]
    CameraID = image_info_variable[36:40]
    FrameNumber = image_info_variable[40:50] + ".jpeg"
    camera_image_folder = BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + BridgeDeviceID + "_" + CameraID
    if not(os.path.isdir(camera_image_folder)):
        os.mkdir(camera_image_folder)

    full_image_file_name =  FrameNumber
    StartTime = time.time()
    cv2.imwrite(camera_image_folder + "/" + full_image_file_name, frame_image)
    EndTime = time.time()

    #print(":::::::: StartTime = " + str(StartTime) +   " EndTime = " + str(EndTime) + "::::" + str(EndTime-StartTime))  

def draw_bounding_boxes(image, face_list, screen_width, screen_height):
    
    for obj_meta in face_list:
        top=int(obj_meta.top)
        left=int(obj_meta.left)
        width=int(obj_meta.width)
        height=int(obj_meta.height)
        obj_name= obj_meta.classlist[obj_meta.class_id] + "(" + str(int(obj_meta.confidence)) + "%)"
        image=cv2.rectangle(image,(left,top),(left+width,top+height),(255,0,0,0),BridgeDeviceConfigVariable.BoundingBoxRectangle)
        image=cv2.putText(image,obj_name+' ',(left-10,top-10),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0,0),BridgeDeviceConfigVariable.BoundingBoxRectangle)

        if(obj_meta.classlist[obj_meta.class_id].lower() == "face"):
            y = int(obj_meta.top)
            x = int(obj_meta.left)
            width = int(obj_meta.width)
            height = int(obj_meta.height)
    
            ##//blurring
            
            #roi = image[y:y+height, x:x+width]
            #roi = cv2.GaussianBlur(roi,(23,23),90)
            #image[y:y+roi.shape[0],x:x+roi.shape[1]] = roi 
            
            ##//mosaic 
            ratio = 0.10
            small = cv2.resize(image[y:y+height,x:x+width], None, fx=ratio,fy=ratio, interpolation=cv2.INTER_NEAREST)
            image[y: y + height, x: x + width] = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)
    
    return image


def tiler_sink_pad_buffer_probe(pad,info,cameraIndex, camera_info):
    global people_count
    global IsSelfCheckDone
    face_list = None
    face_list = []
    camera_confidence = 0
    
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
    #print("===============>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> cameraIndex =======>" , camera_info) 
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

        frame_number = frame_meta.frame_num

        
        if(frame_number % BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS == 0):
            #print("####### CameraIdx ===>>>>",cameraIndex)
            if(len(camera_info.get("SceneModeConfig")) > 0):
                pass 
                #BridgeDeviceConfigVariable.Resolution_Convert_Width = camera_info.get("SceneModeConfig")[0].get("Resolution").get("Width")
                #BridgeDeviceConfigVariable.Resolution_Convert_Height = camera_info.get("SceneModeConfig")[0].get("Resolution").get("Height")

            header = "{}{}{}".format(camera_info.get("DeviceID"),camera_info.get("CameraID"),decimal_fill(frame_number,10))
        
        currenttime = str(int(current_milli_time() / 1000)) 
        detected_meta_info = None
        detected_meta_info = DetectedMetaInfo()
        detected_meta_info.ProcessTimeList = None
        detected_meta_info.SelfCheckReportTime = camera_info.get("SelfCheckReportTime")
        detected_meta_info.SelfCheckYn = camera_info.get("SelfCheckYn")
        detected_meta_info.detected_time = str(currenttime) # str(int(CameraList[camera_id].StartInferencingTime) + int(frame_number / MAX_FRAME_INTERVAL))
        detected_meta_info.source_id = cameraIndex
        ##xxprint("##### = " + str(frame_meta.source_frame_width) + ":" + str(frame_meta.source_frame_height))
        detected_meta_info.origin_frame_num = frame_meta.frame_num

        detected_meta_info.camera_id = camera_info.get("CameraID")
        #print("### camera id = " + str(cameraIndex) + "::::" + detected_meta_info.camera_id + " : " + str(len(BridgeDeviceConfigVariable.CameraList)))
        detected_meta_info.camera_info = None
        detected_meta_info.camera_info = camera_info

        detected_meta_info.device_id = camera_info.get("DeviceID")
        detected_meta_info.RTSP_URL = camera_info.get("rtsp_url")
        detected_meta_info.detected_object_info_list = []

        l_obj=frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta
        is_first_obj = True
        save_image = False

        ObjectIsDetected = False 
        while l_obj is not None:
            try: 
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            width = obj_meta.rect_params.width
            height = obj_meta.rect_params.height
            top = obj_meta.rect_params.top
            left = obj_meta.rect_params.left
            confidence = obj_meta.confidence * 100

            if(False):
                obj_meta.rect_params.border_color.set(1.0, 0.0, 0.0, 0.0)
                obj_meta.rect_params.width = 0
                obj_meta.rect_params.height = 0
                obj_meta.text_params.set_bg_clr = 2
                obj_meta.text_params.display_text = ""
                obj_meta.text_params.font_params.font_size = 0
                obj_meta.rect_params.width = 0
                obj_meta.rect_params.height = 0

            if(obj_meta.class_id > 12):
                obj_meta.class_id = 12 

            meta_info = None 
            meta_info = obj_meta_info()
            meta_info.width = width
            meta_info.height = height 
            meta_info.top = top
            meta_info.left = left
            meta_info.confidence = confidence
            meta_info.class_id = obj_meta.class_id
            meta_info.frame_number = frame_number
            meta_info.classlist = copy.deepcopy(camera_info.get("SceneMode").get("Inputs")[0].get("InferenceEngine").get("ClassList"))

            #print(meta_info.classlist)
            if is_first_obj:
                face_list = []
                is_first_obj = False
                save_image = True
                n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
        

            #if(BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id].lower() == "face" or BridgeDeviceConfigVariable.pgie_classes_str[obj_meta.class_id].lower() == "person"):
            #    face_list.append(meta_info)

            face_list.append(meta_info)
            if save_image:
                isDetected = True
                frame_normal = np.array(n_frame, copy=True, order='C')
                if(BridgeDeviceConfigVariable.IsBoundingBox):
                    frame_normal = draw_bounding_boxes(frame_normal,face_list,camera_info.get("SceneModeConfig")[0].get("Resolution").get("Width"),camera_info.get("SceneModeConfig")[0].get("Resolution").get("Height"))

                frame_normal = cv2.cvtColor(frame_normal, cv2.COLOR_RGBA2BGRA)
                save_image_data(frame_normal,
                                header,
                                camera_info.get("SceneModeConfig")[0].get("Resolution").get("Width"),
                                camera_info.get("SceneModeConfig")[0].get("Resolution").get("Height"),
                                True)
                ObjectIsDetected = True 


            current_millitime = str(int(current_milli_time() / 1000))

            scenedata_name = current_millitime + "" + str(frame_number) 
            scenedata_name = currenttime + str(frame_number)

            rect_parameters = obj_meta.rect_params
            confidence = str(int(obj_meta.confidence * 100))

            #print("#### CLASS LIST", camera_info.get("CameraID"),obj_meta.class_id,camera_info.get("SceneMode").get("Inputs")[0].get("InferenceEngine").get("ClassList"))
            detected_object = None


            detected_object = "Suitcase" #camera_info.get("SceneMode").get("Inputs")[0].get("InferenceEngine").get("ClassList")[obj_meta.class_id]
            xmin = int(rect_parameters.left)
            ymin = int(rect_parameters.top)
            xmax = xmin + int(rect_parameters.width)
            ymax = ymin + int(rect_parameters.height)

            detected_object_info = None
            detected_object_info = DetectedObjectInfo()
            detected_object_info.top = int(top) 
            detected_object_info.left = int(left) 
            detected_object_info.width = int(width) 
            detected_object_info.height = int(height) 


            detected_object_info.x1 = xmin 
            detected_object_info.x2 = xmax
            detected_object_info.y1 = ymin
            detected_object_info.y2 = ymax 
            detected_object_info.confidence = obj_meta.confidence
            detected_object_info.detected_object = detected_object


            detected_object_info.scenedata_name = scenedata_name
            detected_meta_info.scenedata_name = scenedata_name
            detected_object_info.detected_time_ms = current_milli_time()

            if(frame_number % BridgeDeviceConfigVariable.GENERATING_VIDEO_FPS == 0):
                pass
            else:
                frame_number = frame_number - 1

            detected_meta_info.frame_num = frame_number   
            full_image_file_name = decimal_fill(frame_number,10) + ".jpeg"
            thumbnail_image_file_name = full_image_file_name
            
            detected_meta_info.full_image_file_name = full_image_file_name
            detected_meta_info.thumbnail_image_file_name = thumbnail_image_file_name

            detected_meta_info.detected_object_info_list.append(detected_object_info)

            status = "CAMERA : " + camera_info.get("CameraID") + " TIME STAMP :" + currenttime,"FRAME_NUMBER : " + str(detected_meta_info.origin_frame_num) + ":" + str(frame_number)," DETECTED_OBJECT : " + detected_object + "(" + str(detected_object_info.confidence) + ") X : " + str(detected_object_info.left) + " Y : " + str(detected_object_info.top), "WIDTH : " + str(detected_object_info.width), "HEIGHT : " + str(detected_object_info.height)
            debug_message = status
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

            try: 
                l_obj=l_obj.next
            except StopIteration:
                break
    

        if(ObjectIsDetected == False):
            n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
            frame_copy = np.array(n_frame, copy=True, order='C')
            # convert the array into cv2 default color format
            frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_RGBA2BGRA)
            ###print(img_path)
            save_image_data(frame_copy,header,camera_info.get("SceneModeConfig")[0].get("Resolution").get("Width"),camera_info.get("SceneModeConfig")[0].get("Resolution").get("Height"),False)

        if(len(detected_meta_info.detected_object_info_list) > 0):
            #cameraIndex = int(camera_info.get("CameraID")) - 1
            BridgeDeviceConfigVariable.DetectedObjectMetaInfoList[cameraIndex].append(detected_meta_info)
        else:
            pass

        SelfCheckYn = BridgeDeviceConfigVariable.CameraList[0].get("SelfCheckYn")
        if(SelfCheckYn == "Y"):
            if(IsSelfCheckDone == False):
                IsSelfCheckDone = True
                
                SELF_CHECK_RESULT_API_ENDPOINT = BridgeDeviceConfigVariable.SELF_CHECK_RESULT_API_ENDPOINT.format(BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.CameraList[0].get("CameraID"),BridgeDeviceConfigVariable.CameraList[0].get("SceneModeConfig")[0]["CustomAnalysisStage"])

                Data = {
                    "reportTime":BridgeDeviceConfigVariable.CameraList[0].get("SelfCheckReportTime"),
                    "source":"BridgeDevice",
                    "target" : "InferenceEngine",
                    "result":"success"
                }
                headers = {'Authorization': BridgeDeviceConfigVariable.CameraList[0].AccessToken,'Accept': '*/*'}

                print(json.dumps(Data))
                answer = requests.post(SELF_CHECK_RESULT_API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
                print("#############INFERENCE MANAGER ANSWER",SELF_CHECK_RESULT_API_ENDPOINT,answer,len(BridgeDeviceConfigVariable.CameraList[0].SceneModeConfig))
            
            '''
            if(os.path.isfile("BridgeDeviceConfig.json.dat")):
                os.remove("BridgeDeviceConfig.json.dat")
            '''
        end_time=time.time()
        if(fps_streams["stream{0}".format(frame_meta.pad_index)].is_first):
            fps_streams["stream{0}".format(frame_meta.pad_index)].start_time=end_time
            fps_streams["stream{0}".format(frame_meta.pad_index)].is_first=False

        if(end_time-fps_streams["stream{0}".format(frame_meta.pad_index)].start_time > CheckFrameRate):
            #print("[" + str(camera_info.get("CameraFPS")) + ":" + str(camera_info.get("DropFrameInterval")) + "][" + camera_info.get("Distance") + "][" + camera_info.get("CameraID") + "]","Fps of stream",fps_streams["stream{0}".format(frame_meta.pad_index)].stream_id,"is ", float(fps_streams["stream{0}".format(frame_meta.pad_index)].frame_count)/CheckFrameRate)

            #print(str(frame_meta.pad_index) + ":::::::::===>", camera_info)
            print("[" + str(camera_info.get("CameraFPS")) + ":" + str(camera_info.get("DropFrameInterval")) + "][" + camera_info.get("Distance") + "][" + camera_info.get("CameraID") + "]","Fps of stream",fps_streams["stream{0}".format(frame_meta.pad_index)].stream_id,"is ", float(fps_streams["stream{0}".format(frame_meta.pad_index)].frame_count)/CheckFrameRate)

            FPS = float(fps_streams["stream{0}".format(frame_meta.pad_index)].frame_count)/CheckFrameRate #int(camera_info.CameraFPS) / int(camera_info.DropFrameInterval)            
            
            frame = int(FPS / 8 * 100)
            status = "N"
            if(frame < 80):
                status = "E"

            CameraStatus = {
                "NodeID":"{}_{}".format(camera_info.get("DeviceID"),camera_info.get("CameraID")),
                "Status":"N",
                "Fps":FPS,
                "FpsStatus":status,
                "CheckTime":(str(datetime.datetime.now())).split('.')[0]
            }
            with open(camera_info.get("CameraID") + ".dat","wb") as f:
                pickle.dump(CameraStatus,f)

            fps_streams["stream{0}".format(frame_meta.pad_index)].frame_count=0
            fps_streams["stream{0}".format(frame_meta.pad_index)].start_time=end_time
        else:
            fps_streams["stream{0}".format(frame_meta.pad_index)].frame_count=fps_streams["stream{0}".format(frame_meta.pad_index)].frame_count+1

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
        DROP_FRAME_INTERVAL = BridgeDeviceConfigVariable.CameraList[int(index)].get("DropFrameInterval")
        debug_message = "#######DROP_FRAME_INTERVAL : {}".format(BridgeDeviceConfigVariable.CameraList[int(index)].get("DropFrameInterval"))
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        Object.set_property("bufapi-version",True)
        Object.set_property("drop-frame-interval",DROP_FRAME_INTERVAL)
        print(debug_message)
    elif(name.find("nvv4l2decoder") != -1):    
        DROP_FRAME_INTERVAL = BridgeDeviceConfigVariable.CameraList[int(index)].get("DropFrameInterval")
        debug_message = "DROP_FRAME_INTERVAL : {}".format(BridgeDeviceConfigVariable.CameraList[int(index)].get("DropFrameInterval"))
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

def kill_application(camera_info, cameraIndex):
    global IsSelfCheckDone
    cameraIndex = 0 
    print("####### KILL APPLICATION #######")
    
    SelfCheckYn = "N" #camera_info.SelfCheckYn
    if(SelfCheckYn == "Y"):
        if(IsSelfCheckDone == False):
            IsSelfCheckDone = True
            SELF_CHECK_RESULT_API_ENDPOINT = BridgeDeviceConfigVariable.SELF_CHECK_RESULT_API_ENDPOINT.format(BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.camera_info.CameraID,camera_info.SceneModeConfig[0]["CustomAnalysisStage"])

            Data = {
                "reportTime":camera_info.SelfCheckReportTime,
                "source":"BridgeDevice",
                "target" : "InferenceEngine",
                "result":"fail"
            }
            headers = {'Authorization': camera_info.AccessToken,'Accept': '*/*'}

            print(json.dumps(Data))
            answer = requests.post(SELF_CHECK_RESULT_API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
            print("############# kill_application INFERENCE MANAGER ANSWER",SELF_CHECK_RESULT_API_ENDPOINT,answer)
            
        '''
        if(os.path.isfile("BridgeDeviceConfig.json.dat")):
            os.remove("BridgeDeviceConfig.json.dat")
        '''

    os.kill(os.getpid(),signal.SIGKILL)



def kill_application2():
    global IsSelfCheckDone
    global BridgeDeviceConfigVariable
    IsSelfCheckDone = False
    BridgeDeviceConfigVariable.CameraList = None
    SelfCheckYn = "N"
    for i in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
        camera_directory = "{}_{}".format(BridgeDeviceConfigVariable.BridgeDeviceID,decimal_fill(i+1,4))
        remove_files(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)

    if(os.path.isfile("CameraSelfCheckList.dat")):
        with open("CameraSelfCheckList.dat","rb") as f:
            unpickler = pickle.Unpickler(f)
            BridgeDeviceConfigVariable.CameraList = unpickler.load()
            camera_info = None
            #print("################### CAMERA LIST >>>>>>>>>>>>>>>>>>",len(BridgeDeviceConfigVariable.CameraList))
            if(len(BridgeDeviceConfigVariable.CameraList) > 0):
                camera_info = copy.deepcopy(BridgeDeviceConfigVariable.CameraList[0])
                if(len(BridgeDeviceConfigVariable.CameraList[0].SceneModeConfig) == 0):
                    del BridgeDeviceConfigVariable.CameraList[0]
                    if(len(BridgeDeviceConfigVariable.CameraList) > 0):
                        camera_info = copy.deepcopy(BridgeDeviceConfigVariable.CameraList[0])
                else:
                    BridgeDeviceConfigVariable.CameraList[0].SceneModeConfig.pop(0)

                

                
                #if(len(camera_info.SceneModeConfig) > 0):
                SelfCheckYn = camera_info.SelfCheckYn

                with open("CameraSelfCheckList.dat","wb") as f:
                    pickle.dump(BridgeDeviceConfigVariable.CameraList,f)
                
                if(len(BridgeDeviceConfigVariable.CameraList) == 0):
                    #print("\n\n\n################# DONE>>>>>>>>>>>>>>>>>>>>>>DONE>>>>>>>>\n\n\n")
                    if(os.path.isfile("CameraSelfCheckList.dat")):
                        os.remove("CameraSelfCheckList.dat")
                    if(os.path.isfile("BridgeDeviceConfig.json.dat")):
                        os.remove("BridgeDeviceConfig.json.dat")
                else:
                    pass
                    #print("########## CameraSelfCheckList ",len(BridgeDeviceConfigVariable.CameraList),len(camera_info.SceneModeConfig),camera_info.SceneModeConfig[0]["CustomAnalysisStage"])

            if(SelfCheckYn == "Y"):
                cameraIndex = 1
                if(camera_info is not None):
                    if(len(BridgeDeviceConfigVariable.CameraList) == 0):
                        pass
                    else:
                        kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceEventManager)
                        #kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager)

                    for i in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
                        camera_directory = "{}_{}".format(BridgeDeviceConfigVariable.BridgeDeviceID,decimal_fill(i+1,4))
                        remove_files(BridgeDeviceConfigVariable.MetaDataDirectory + "/" + camera_directory)


                    for item in camera_info.SceneModeConfig:
                        item["DetectDelay"] = 3
                    time.sleep(1)
                    #print("####### CUSTOMSTAGE",camera_info.SceneModeConfig[0]["CustomAnalysisStage"] , len(camera_info.SceneModeConfig))
                    PipeLineInfo = None
                    PipeLineInfo = PipeLineInfoClass()
                    PipeLineInfo.PIPELINE_THREAD = threading.Thread(target=detect_start,args=(camera_info,cameraIndex))
                    PipeLineInfo.PIPELINE_THREAD.setName(decimal_fill(cameraIndex,4))
                    PipeLineInfo.PIPELINE_THREAD.daemon = True
                    PipeLineInfo.PIPELINE_THREAD.start()
                    BridgeDeviceConfigVariable.PIPELINE_INFO_LIST.append(PipeLineInfo)

    if(SelfCheckYn == "Y"):
        pass
    else:
        os.kill(os.getpid(),signal.SIGKILL)

def detect_start(camera_info,cameraIndex):

    print("detect_start ====> started...", camera_info.get("CameraID"), cameraIndex)
    number_sources = 1
    GObject.threads_init()
    Gst.init(None)

    debug_message = "Creating Pipeline"
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    PIPELINE = None
    PIPELINE = Gst.Pipeline()
    try:
        BridgeDeviceConfigVariable.PIPELINE_INFO_LIST[cameraIndex].PIPELINE = PIPELINE
    except Exception as ex:
        kill_application(camera_info,cameraIndex)

    is_live = False

    if not PIPELINE:
        debug_message = "Unable to create Pipeline "
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)
    #xxprint("Creating streamux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        debug_message = "Unable to create NvStreamMux "
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    PIPELINE.add(streammux)
    #for i in range(number_sources):
    fps_streams["stream{0}".format(cameraIndex)]=GETFPS(cameraIndex)
    #xxprint("CreatingstrSceneDataEndPoint source_bin ",i," \n ")
    uri_name=camera_info.get("RTSP_URL")
    if(camera_info.get("SelfCheckYn") == "Y"):
        if(len(camera_info.get("SceneModeConfig")) > 0):
            CustomAnalysisStage = camera_info.get("SceneModeConfig")[0]["CustomAnalysisStage"] + "_" + camera_info.get("CameraID")
            uri_name = "file:///home/ghosti/falling_down.mp4"
            camera_info.RTSP_URL = uri_name
            BridgeDeviceConfigVariable.CameraList = None
            BridgeDeviceConfigVariable.CameraList = []
            BridgeDeviceConfigVariable.CameraList.append(camera_info)
    #uri_name = "file:///home/ghosti/bridge_device/bifc_20220406.mp4"
    #uri_name = "file:///home/ghosti/bridge_device/cars.mp4"
    
    #uri_name = "rtsp://admin:ygo1429@220.124.73.183/ch0" + str(int(cameraIndex) + 1) + "/0"
    #print("\n\n####### RTSP_URL",uri_name,"\n\n")
    debug_message = "CAMERA RTSP :: {} : {}".format(camera_info.get("CameraID"),uri_name)
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    sys.stderr.write("####" + debug_message + "#####")

    if uri_name.find("rtsp://") == 0 or  uri_name.find("rtspt://") == 0:
        is_live = True
    source_bin=create_source_bin(cameraIndex, uri_name)
    if not source_bin:
        debug_message = ("Unable to create source bin \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    PIPELINE.add(source_bin)
    padname="sink_%u" %(cameraIndex)
    sinkpad= streammux.get_request_pad(padname) 
    if not sinkpad:
        debug_message = ("Unable to create sink pad bin \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    srcpad=source_bin.get_static_pad("src")
    if not srcpad:
        debug_message = ("Unable to create src pad bin \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    srcpad.link(sinkpad)
    
    h264parser = Gst.ElementFactory.make("h264parse","h264-parser")


    if not h264parser:
        debug_message = ("Unable to create h264 parse\n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    #xxprint("Creating Decoder\n")
    decoder = Gst.ElementFactory.make("nvv4l2decoder","nvv4l2-decorder")
    if not decoder:
        debug_message = (" Unable to create Nvv4l2 Decoder\n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    #xxprint("Creating Pgie \n ")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        debug_message = (" Unable to create pgie \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
    if not nvvidconv1:
        debug_message = (" Unable to create nvvidconv1 \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    #xxprint("Creating filter1 \n ")
    #BridgeDeviceConfigVariable.Resolution_Convert_Width = 960
    #BridgeDeviceConfigVariable.Resolution_Convert_Height = 540

    if(len(camera_info.get("SceneModeConfig")) > 0):
        #BridgeDeviceConfigVariable.Resolution_Convert_Width = camera_info.get("SceneModeConfig")[0].get("Resolution").get("Width")
        #BridgeDeviceConfigVariable.Resolution_Convert_Height = camera_info.get("SceneModeConfig")[0].get("Resolution").get("Height")
        pass 
    
    convert_string = "video/x-raw(memory:NVMM),width={},height={},format=RGBA".format(camera_info.get("SceneModeConfig")[0].get("Resolution").get("Width"),camera_info.get("SceneModeConfig")[0].get("Resolution").get("Height"))    

    print("Convert_String=====>",convert_string)
    #convert_string = "application/x-rtp,width={},height={},format=RGBA".format(BridgeDeviceConfigVariable.Resolution_Convert_Width,BridgeDeviceConfigVariable.Resolution_Convert_Height)    
    #convert_string = "video/x-raw(memory:NVMM),format=(string)I420,width={},height={},format=RGBA".format(BridgeDeviceConfigVariable.Resolution_Convert_Width,BridgeDeviceConfigVariable.Resolution_Convert_Height)    

    caps1 = Gst.Caps.from_string(convert_string)    
    filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
    if not filter1:
        debug_message = (" Unable to get the caps filter1 \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    filter1.set_property("caps", caps1)
    #xxprint("Creating tiler \n ")
    tiler=Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
    
        debug_message = (" Unable to create tiler \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    #xxprint("Creating nvvidconv \n ")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        debug_message = (" Unable to create nvvidconv \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)


    #xxprint("Creating nvosd \n ")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        debug_message = (" Unable to create nvosd \n")
        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
        kill_application(camera_info,cameraIndex)

    
    if(is_aarch64()):
        #xxprint("Creating transform \n ")
        transform=Gst.ElementFactory.make("nvegltransform", "nvegl-transform")
        #transform=Gst.ElementFactory.make("queue", "queue")
        if not transform:
            debug_message = (" Unable to create transform \n")
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            kill_application(camera_info,cameraIndex)

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

        kill_application(camera_info,cameraIndex)


    if is_live:
        streammux.set_property('live-source', 1)


    BridgeDeviceConfigVariable.Resolution_Width = int(camera_info["ResolutionWidth"])
    BridgeDeviceConfigVariable.Resolution_Height = int(camera_info["ResolutionHeight"])
    BridgeDeviceConfigVariable.Resolution_Width = 1920
    BridgeDeviceConfigVariable.Resolution_Height = 1080
    debug_message = "CAMERA:{} WIDTH:{} HEIGHT:{}".format(camera_info.get("CameraID"),camera_info["ResolutionWidth"],camera_info["ResolutionHeight"])
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

    

    streammux.set_property('width', BridgeDeviceConfigVariable.Resolution_Width)
    streammux.set_property('height', BridgeDeviceConfigVariable.Resolution_Height)
    streammux.set_property('batch-size', number_sources)
    streammux.set_property('batched-push-timeout', BridgeDeviceConfigVariable.MUXER_BATCH_TIMEOUT_USEC) #4000000

    debug_message = "CAMERA:{} DISTANCE:{}".format(camera_info.get("CameraID"),camera_info.get("Distance"))
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    
    Distance = "./inference_engine/" + camera_info.get("Distance") + ".txt"
    print("#### #DISTANCE :::::: " , Distance)
    pgie.set_property('config-file-path', Distance)

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
        kill_application(camera_info,cameraIndex)

    else:
        tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, tiler_sink_pad_buffer_probe,cameraIndex, camera_info)
	

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
    debug_message = "###########  CAMERA IS DOWN " + camera_info.get("RTSP_URL")
    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
    sys.stderr.write(debug_message)

    PIPELINE.set_state(Gst.State.NULL)
    kill_application2()

def create_metadata(sm_meta_info_list):
    sm_meta_info = sm_meta_info_list[0]
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

    #if(sm_meta_info.camera_info.get("Distance").lower() == "normal_ellexi"):
    for item in sm_meta_info.camera_info.get("SceneModeConfig"):
        if(str(item.get("Analysis")).lower().startswith("falldown") and str(item.get("AnalysisVendor").lower().startswith("ellexi"))):
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
            
                if(os.path.isdir(DataDirectory) == False):
                    os.mkdir(DataDirectory)  
                DataFileName = "{}/{}.dat".format(DataDirectory,SceneMarkID)
                #print("#### DataFileName",DataFileName)

                with open(DataFileName,"wb") as f:
                    pickle.dump(sm_meta_info_list,f)

            for item in sm_meta_info.camera_info.get("SceneModeConfig"):
                #print(str(item.get("CustomAnalysisStage")))
                
                if str(item.get("CustomAnalysisStage")).lower().startswith("facility"):
                    FDataDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.FMetaDataDirectory,BridgeDeviceID,sm_meta_info.get("CameraID"))
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
            cameraIndex = 0 
            for detected_object_meta_info in BridgeDeviceConfigVariable.DetectedObjectMetaInfoList:
                CameraID = detected_object_meta_info[0].camera_id
                #CameraID = decimal_fill(cameraIndex + 1,4)
                cameraIndex = cameraIndex + 1
                #idx = -1 
                #CameraIdx = -1
                #for i in range(0,len(BridgeDeviceConfigVariable.CameraList)):
                #    if(CameraID == BridgeDeviceConfigVariable.CameraList[i].get("CameraID")):
                #        CameraIdx = i
                #        break
                #print("### CAMERA INDEX",CameraID,len(detected_object_meta_info))
                sm_meta_info_list = None
                sm_meta_info_list = []
                #print("### CAMERA INDEX",len(detected_object_meta_info),CameraIdx)
                if(len(detected_object_meta_info) > 0):# and CameraIdx > -1):
                    #print("#################### detected_object_meta_info",detected_object_meta_info)
                    StartTime = time.time()    
                    count = 0 
                    #for i in range(0,len(detected_object_meta_info)):
                    #print("###### BridgeDeviceConfigVariable.CameraList[CameraIdx].InferenceFPS * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA",BridgeDeviceConfigVariable.CameraList[CameraIdx].InferenceFPS * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA)

                    while detected_object_meta_info:
                        #if count < (BridgeDeviceConfigVariable.CameraList[CameraIdx].InferenceFPS * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA): 
                        #print("##### ===> count:::",count, 30 * BridgeDeviceConfigVariable.TIME_TO_MERGE_META_DATA)
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

                #print("##### CameraID =",CameraID,StartTime,EndTime,EndTime-StartTime, len(sm_meta_info_list))

                if(len(sm_meta_info_list) > 0):
                    create_metadata(sm_meta_info_list)
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
            print("=======================>>>>>>>sys.argv",sys.argv, len(sys.argv))

            CameraIDs = []
            for i in range(2,len(sys.argv)):
                CameraIDs.append(sys.argv[i])

            print("-=================dddd3333#######",CameraIDs)

            bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
            if(os.path.isfile(bridge_device_config_file_name) and os.path.getsize(bridge_device_config_file_name) > 0): ## checking configuration file is existed or not....
                with open(bridge_device_config_file_name,"rb") as f:
                    Config = json.loads(pickle.load(f))
                    if(Config):
                        BridgeDeviceInfo = Config["BridgeDeviceInfo"]
                        if(BridgeDeviceInfo["SelfCheckYn"] == "Y" and IsSelfCheckFirstTime == False):
                            #print("######### BridgeDeviceInfo SelfCheckYn Passed ",BridgeDeviceInfo["SelfCheckYn"] == "Y",isChanged, ProcessTimeSleep)
                            pass
                        else:
                            ProcessTimeSleep = 10

                            #if(len(BridgeDeviceConfigVariable.CameraList) != len(BridgeDeviceInfo["CameraList"])):
                            #    isChanged = True
                                
                            #if(len(BridgeDeviceConfigVariable.CameraList) == len(BridgeDeviceInfo["CameraList"])): ## checking camera information is changed or not
                            kk = 0 
                            if(len(BridgeDeviceConfigVariable.CameraList) == 0):
                                isChanged = True 
                            else:
                                if(len(BridgeDeviceConfigVariable.CameraList) != len(CameraIDs)):
                                    isChanged = True 

                            for item in BridgeDeviceConfigVariable.CameraList:
                                if(item.get("CameraID") in CameraIDs):
                                    pass 
                                else:
                                    isChanged = True 

                            for camera_meta_info in BridgeDeviceConfigVariable.CameraList:
                                for camera_info in BridgeDeviceInfo["CameraList"]:
                                    if(camera_info.get("CameraID") == camera_meta_info.get("CameraID")):
                                        if(camera_info.get("Distance").lower() != camera_meta_info.get("Distance").lower()):
                                            isChanged = True 
                                            debug_message = ("###### DISTANCE HAS BEEN CHANGED>>>>>>>>#########::::::::")
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                                            break

                                        if(camera_info.get("CameraFPS") != camera_meta_info.get("CameraFPS")):
                                            isChanged = True 
                                            debug_message = ("###### CAMERA FPS HAS BEEN CHANGED>>>>>>>>#########::::::::")
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                                            break

                                        if(camera_info.get("InferenceFPS") != camera_meta_info.get("InferenceFPS")):
                                            isChanged = True 
                                            debug_message = ("###### Inference FPS HAS BEEN CHANGED>>>>>>>>#########::::::::")
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                                            break

                                        if(camera_info.get("RTSP_URL") != camera_meta_info.get("RTSP_URL")):
                                            isChanged = True 
                                            debug_message = ("###### RTSP_URL HAS BEEN CHANGED>>>>>>>>#########::::::::")
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                                            break

                                        if(camera_info.get("DropFrameInterval") != camera_meta_info.get("DropFrameInterval")):
                                            isChanged = True 
                                            debug_message = ("###### DROP FRAME INTERVAL HAS BEEN CHANGED>>>>>>>>#########::::::::")
                                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
                                            break
                                        BridgeDeviceConfigVariable.CameraList[0] = camera_info
                                    
                          
                            if(BridgeDeviceConfigVariable.FakeSink != BridgeDeviceInfo["FakeSink"]):
                                isChanged = True
                                BridgeDeviceConfigVariable.FakeSink = BridgeDeviceInfo["FakeSink"]
                        
                    
                    
                    if(isChanged): ## if camera information has been changed.... reconfigration inference engine 
                        print("##### is changed......" + str(len(BridgeDeviceInfo["CameraList"])))
                        
                        #if(IsFirstTime == False):
                        #    os.kill(os.getpid(),signal.SIGKILL)
                        IsFirstTime = False
                        for PipeLineInfo in BridgeDeviceConfigVariable.PIPELINE_INFO_LIST:
                            if(PipeLineInfo.PIPELINE):
                                PipeLineInfo.PIPELINE.set_state(Gst.State.NULL)
                                PipeLineInfo.PIPELINE = None
                                debug_message = ("##### PIPELINE ALIVE......".format(PipeLineInfo))
                                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)

            
                            if(PipeLineInfo.PIPELINE_THREAD):
                                PipeLineInfo.PIPELINE_THREAD._stop

                        BridgeDeviceConfigVariable.PIPELINE_RUNNING = False
                        BridgeDeviceConfigVariable.IsBridgeDeviceRunning = False
                        BridgeDeviceConfigVariable.CameraList = None
                        BridgeDeviceConfigVariable.CameraList = []

                        print("########=====>", len(BridgeDeviceInfo["CameraList"]) , CameraIDs)

                        for CameraID in CameraIDs:
                            for item in BridgeDeviceInfo["CameraList"]:
                                print("========>>>>>>>>#####","CameraID ::: " , CameraID, "CameraID2 :::" + item.get("CameraID"))
                                if(int(CameraID) == int(item.get("CameraID"))):
                                    BridgeDeviceConfigVariable.CameraList.append(item)
                                    break 
                        
                        
                        print("########=====> CameraList ===>", len(BridgeDeviceConfigVariable.CameraList))



                        create_directory()     

                        cameraIndex = 0
                        if(BridgeDeviceInfo["SelfCheckYn"] == "Y"):
                            for camera_info in BridgeDeviceConfigVariable.CameraList:
                                for config_item in camera_info.SceneModeConfig:
                                    if(config_item["CustomAnalysisStage"] == "NewSceneMode"):
                                        camera_info.SceneModeConfig.pop(0)

                            file_list = []
                            IsSelfCheckFirstTime = False
                            if(len(BridgeDeviceConfigVariable.CameraList) > 0):
                                camera_info = copy.deepcopy(BridgeDeviceConfigVariable.CameraList[0])
                                if(len(camera_info.SceneModeConfig) > 0):
                                    CameraList = copy.deepcopy(BridgeDeviceConfigVariable.CameraList[0])
                                    SceneModeConfig = CameraList.SceneModeConfig[0]
                                    BridgeDeviceConfigVariable.CameraList[0].SceneModeConfig.pop(0)
                                    camera_info.SceneModeConfig = None 
                                    camera_info.SceneModeConfig = []
                                    camera_info.SceneModeConfig.append(SceneModeConfig)
                                    for scenemode_config_item in camera_info.SceneModeConfig:
                                        scenemode_config_item["DetectDelay"] = 1

                                    PipeLineInfo = PipeLineInfoClass()
                                    PipeLineInfo.PIPELINE_THREAD = threading.Thread(target=detect_start,args=(camera_info,cameraIndex))
                                    PipeLineInfo.PIPELINE_THREAD.setName(decimal_fill(cameraIndex,4))
                                    PipeLineInfo.PIPELINE_THREAD.daemon = True
                                    PipeLineInfo.PIPELINE_THREAD.start()
                                    BridgeDeviceConfigVariable.PIPELINE_INFO_LIST.append(PipeLineInfo)
                            with open("CameraSelfCheckList.dat","wb") as f:
                                pickle.dump(BridgeDeviceConfigVariable.CameraList,f)
                

                        else:
                            #for camera_info in BridgeDeviceConfigVariable.CameraList:
                            for i in range(0, len(BridgeDeviceConfigVariable.CameraList)):
                                camera_info = BridgeDeviceConfigVariable.CameraList[i]
                                
                                #IsNewSceneMode = False
                                #if(len(camera_info.get("SceneModeConfig")) >= 1):
                                #    for item in camera_info.get("SceneModeConfig"):
                                #        if(item["CustomAnalysisStage"] == "NewSceneMode"):
                                #            IsNewSceneMode = True

                            #if(IsNewSceneMode == False):
                                PipeLineInfo = PipeLineInfoClass()
                                PipeLineInfo.PIPELINE_THREAD = threading.Thread(target=detect_start,args=(camera_info,cameraIndex))
                                #print("\n\n\n#####+=====> Thread CameraID ",camera_info.get("CameraID") , "\n\n\n")
                                PipeLineInfo.PIPELINE_THREAD.setName(camera_info.get("CameraID"))
                                PipeLineInfo.PIPELINE_THREAD.daemon = True
                                PipeLineInfo.PIPELINE_THREAD.start()
                                BridgeDeviceConfigVariable.PIPELINE_INFO_LIST.append(PipeLineInfo)
                                cameraIndex = cameraIndex + 1
                            BridgeDeviceConfigVariable.PIPELINE_RUNNING = True

                        with open("CameraList.dat","wb") as f:
                            pickle.dump(BridgeDeviceConfigVariable.CameraList,f)
                            print("###### CAMERA LIST IS UPDATED")
                    else:
                        if(BridgeDeviceInfo["SelfCheckYn"] != "Y"):
                            pass 
                            '''
                            for item in BridgeDeviceInfo["CameraList"]:
                                new_camera_info = parsing_camerainfo(item,BridgeDeviceConfigVariable.BridgeDeviceID) 
                                for camera_info in BridgeDeviceConfigVariable.CameraList:
                                    if(new_camera_info.CameraID == camera_info.CameraID):
                                        camera_info.SceneModeConfig = new_camera_info.SceneModeConfig
                                        camera_info.SceneMarkEndPoint = new_camera_info.SceneMarkEndPoint
                                        camera_info.SceneMarkToken = new_camera_info.SceneMarkToken
                                        camera_info.SceneMarkAuthority = new_camera_info.SceneMarkAuthority
                                        camera_info.SceneDataEndPoint = new_camera_info.SceneDataEndPoint
                                        camera_info.SceneDataToken = new_camera_info.SceneDataToken
                                        camera_info.SceneDataAuthority = new_camera_info.SceneDataAuthority
                                        break
                            '''

                    #for camera in BridgeDeviceConfigVariable.CameraList:
                    #    print("####### CAMERAINFO #####",camera.CameraID,camera.SceneMarkToken)
                    
                    time.sleep(ProcessTimeSleep)
                    #for thread in threading.enumerate(): 
                    #    #xxprint("######## TRHEAD NAME ",thread.name,thread.is_alive())
            else:
                print("SceneMode configuration file is not generated yet. please check scenemode config retrieved correctly... ")
        except Exception as ex:
            debug_message = ("Message ::: Parsing Configuration File Error" + str(ex) + traceback.format_exc())
            print(debug_message)
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            pass
            time.sleep(ProcessTimeSleep)
        time.sleep(1)

def create_directory():
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

    #print("######+=====>sys.argv",sys.argv[2],sys.argv[3])
   
    ## Camera Configuration check 
    camera_check_thread = threading.Thread(target=check_cameras_configuration,args=())
    camera_check_thread.deamon = True
    camera_check_thread.setName("CameraCheckThread")
    camera_check_thread.start()
    #camera_check_thread.join()

    ## Uploading Scenemark and Scenedata Management
    
    BridgeDeviceConfigVariable.DetectedObjectMetaInfoList = []
    DetectedObjectMetaInfoList = []
    for i in range(0,len(BridgeDeviceConfigVariable.range_list)):
        BridgeDeviceConfigVariable.DetectedObjectMetaInfoList.append(copy.deepcopy(DetectedObjectMetaInfoList))

    item = None 
    NodeID = None 
    upload_scenemark_thread = threading.Thread(target=upload_scenemark_list,args=(item,NodeID))
    upload_scenemark_thread.daemon = True
    upload_scenemark_thread.start()

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