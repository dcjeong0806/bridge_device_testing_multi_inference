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


import sys

import configparser

import time
import sys
import math
import platform
import json
import threading
import os
import datetime
import cv2
import base64

from sys  import getsizeof
import copy
import numpy as np
from tempfile import mkdtemp
import os.path as path
import json
import os
import sysv_ipc
import subprocess
from BridgeDeviceInfo import check_bridge_device_process
from bridge_device_peoplenet_config import VariableConfigClass, DebugPrint
BridgeDeviceConfigVariable = VariableConfigClass()

def generate_image_key():
    while(True):
        i = 0 
        command = "/usr/bin/ipcs -m"
        shm_data_list = subprocess.check_output(command,shell=True,encoding='utf-8')
        shm_list = str(shm_data_list).split("\n")
        for item in shm_list:
            try:
                if(i > 2):
                    item = item.replace(" ","")
                    if(item.startswith("0x00000000")):
                        pass
                    else:
                        list_item = item.split(BridgeDeviceConfigVariable.UserAccount + "600")
                        if(len(list_item) == 2 and int(list_item[1]) == 680):
                            key = int(list_item[0][:10],16)
                            memory = sysv_ipc.SharedMemory(key)
                            image_info_variable = memory.read()

                            # Log Print
                            debug_message = "{}".format(image_info_variable)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGenerateImageManager)

                            BridgeDeviceID = image_info_variable[:36].decode()
                            CameraID = image_info_variable[36:40].decode()
                            FrameNumber = image_info_variable[40:50].decode() + ".jpeg"
                            Image_Shm_Key = int(image_info_variable[50:60])
                            Height = int(image_info_variable[60:64])
                            Width = int(image_info_variable[64:68])

                            # Log Print
                            debug_message = "key:{} Image_Shm_Key:{} BridgeDeviceID:{} CameraID:{} FrameNumber:{}".format(key,Image_Shm_Key,BridgeDeviceID,CameraID,FrameNumber)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGenerateImageManager)


                            camera_image_folder = BridgeDeviceConfigVariable.ImageSaveDirectory + "/" + BridgeDeviceID + "_" + CameraID
                            if not(os.path.isdir(camera_image_folder)):
                                os.mkdir(camera_image_folder)
                            memory.detach()
                            memory.remove()
                            memory_image = sysv_ipc.SharedMemory(Image_Shm_Key)
                            StartTime = time.time()
                            raw_image = memory_image.read()
                            frame_image = np.frombuffer(raw_image,dtype=np.uint8)
                            frame_image = frame_image.reshape(Height,Width,4)
                            full_image_file_name =  FrameNumber
                            cv2.imwrite(camera_image_folder + "/" + full_image_file_name, frame_image)
                            EndTime = time.time()
                            memory_image.detach()
                            memory_image.remove()
                            # Log Print
                            debug_message = "BridgeDeviceID:{} CameraID:{} FrameNumber:{} StartTime:{} EndTime:{}=={}".format(BridgeDeviceID,CameraID,FrameNumber,StartTime,EndTime,EndTime-StartTime)
                            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGenerateImageManager)
                i = i + 1 
            except Exception as ex:
                debug_message = "::: ERROR MESSAGE ::: = {}".format(str(ex))
                DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGenerateImageManager)
                pass

def main():
    print("==========================================")
    print("::::: Image Generating Server is started...::::")
    print("==========================================")


    global BridgeDeviceConfigVariable
    '''
    if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceGenerateImageManager) > 1):
        print("==========================================")
        print("there is same process running already. process is about to be terminated.")
        print("==========================================")
        sys.exit()
    '''
    generate_image_key()

main()