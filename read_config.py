from bridge_device_peoplenet_config import VariableConfigClass,DebugPrint,decimal_fill
BridgeDeviceConfigVariable = VariableConfigClass()
from BridgeDeviceInfo import CameraMetaInfoClass,kill_bridge_device_process, parsing_camerainfo, GetCameraID, SceneModeConfigClass, PipeLineInfoClass,check_bridge_device_process,SMDetectedObjectInfo, DetectedMetaInfo, DetectedObjectInfo
from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID, GetNICELAEndPointAuthority, GetNICELAEndPointEndPoint
from Scenera_ManagementObject import GetManagementObject, GetManagementObjectInfo
import pickle 
import json
import sys
import os
import threading
import time

def check_cameras_configuration():
    while(True):
        try:
            isChanged = False
            bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
            if(os.path.isfile(bridge_device_config_file_name)):
                with open(bridge_device_config_file_name,"rb") as f:
                    Config = json.loads(pickle.load(f))
                    if(Config):
                        BridgeDeviceInfo = Config["BridgeDeviceInfo"]
                        for item in BridgeDeviceInfo["CameraList"]:
                            ##### Parsing Camera Info 
                            camera_info = parsing_camerainfo(item,BridgeDeviceConfigVariable.BridgeDeviceID) 
                            print("####### CameraInfo",json.dumps(item),"\n\n\n")
                            break
                                

        except Exception as ex:
            debug_message = ("Message ::: Parsing Configuration File Error" + str(ex))
            print(debug_message)
            DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceInferenceManager)
            pass
        time.sleep(5)


def main():
    camera_check_thread = threading.Thread(target=check_cameras_configuration,args=())
    camera_check_thread.deamon = True
    camera_check_thread.setName("CameraCheckThread")
    camera_check_thread.start()

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