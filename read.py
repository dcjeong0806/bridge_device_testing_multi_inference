
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

from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint,decimal_fill
BridgeDeviceConfigVariable = VariableConfigClass()
current_milli_time = lambda: int(round(time.time() * 1000))

import matplotlib.path as mpltPath
from shapely.geometry import  Polygon
import pickle 
#kIsSelfCheckDone = [False,False,False,False,False,False,False,False,False,False]
IsSelfCheckDone = False

class person_object:
    xmax = 0 
    xmin = 0 
    ymax = 0 
    ymin = 0 
    strObjectType = ""

class overlaps_contains:
    overlaps = False
    contains = False

def scenemark_metadata_event_manager(CameraID):
    print("CMEAR",CameraID)
    global IsSelfCheckDone
    for k in range(0,BridgeDeviceConfigVariable.MAX_CAMERA_NODES):
            CameraID = str(int(k+1)).zfill(4)
            MetaFileDirectory = "{}/{}_{}".format(BridgeDeviceConfigVariable.EllexiMetaDataDirectory,BridgeDeviceConfigVariable.BridgeDeviceID,CameraID)
            if(os.path.isdir(MetaFileDirectory)):
                file_list = os.listdir(MetaFileDirectory)
                file_list.sort()
                print(MetaFileDirectory,len(file_list))
                for item in file_list:
                    metadata_file = MetaFileDirectory + "/" + item
                    if os.path.isfile(metadata_file) and os.path.getsize(metadata_file) > 0:
                        StartTime = time.time()
                        with open(metadata_file,"rb") as f:
                            unpickler = pickle.Unpickler(f)
                            sm_meta_info = unpickler.load()
                            #if(os.path.isfile(metadata_file)):
                            #    os.remove(metadata_file)

                            json_val = json.dumps(sm_meta_info[0].camera_info[0])

                            print("json_val = %s" % json_val)
                            
            
                        EndTime = time.time()   

                        debug_message = ("META DATA PROCESSING.... {}_{} {} : {} : {} ".format(BridgeDeviceConfigVariable.BridgeDeviceID,CameraID,StartTime,EndTime,EndTime-StartTime))      
                        DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceEventManager)



def main():
    print("==========================================")
    print("::::: Algorithm Analysis is started...::::")
    print("==========================================")

        #threading.Thread(target=generate_result_scenemark_metadata,args=("",)).start()
    threading.Thread(target=scenemark_metadata_event_manager,args=("",)).start()

    #threading.Thread(target=scenemark_facility_metadata_event_manager,args=("",)).start()
    #threading.Thread(target=generate_result_scenemark_facility_metadata,args=(BridgeDeviceConfigVariable.FacilitySceneMarkList,)).start()
## LoadBridgeDeviceSecurityObject Disabled until it works 2020-09-24 DCJeong
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


