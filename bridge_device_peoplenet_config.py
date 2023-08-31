
import datetime
from collections import deque
from queue import Queue 
import getpass
from re import S
import syslog
import os 
import json
import copy
import traceback
from datetime import timezone, datetime


BridgeDeviceInferenceManager = "bridge_device_peoplenet_inferencing_manager"
BridgeDeviceGetSceneModeManager = "bridge_device_peoplenet_scenemode_manager"
BridgeDeviceEventManager = "bridge_device_peoplenet_event_manager"
BridgeDeviceEventFacilityManager = "bridge_device_peoplenet_event_facility_manager"
BridgeDeviceSceneMarkManager = "bridge_device_peoplenet_scenemark_manager"
BridgeDeviceSceneDataManager = "bridge_device_peoplenet_scenedata_manager"
BridgeDeviceFirmwareUpdateManager = "bridge_device_firmware_update_manager"
BridgeDeviceSceneraLibraryManager = "main"


def DebugPrint(key,message,mode,process_from):
    if(process_from == BridgeDeviceInferenceManager):
        mode = False
    elif(process_from == BridgeDeviceGetSceneModeManager):
        mode = False
    elif(process_from == BridgeDeviceEventManager):
        mode = True
    elif(process_from == BridgeDeviceSceneMarkManager):
        mode = True
    elif(process_from == BridgeDeviceSceneDataManager):
        mode = True
    elif(process_from == BridgeDeviceEventFacilityManager):
        mode = False

 
    #mode = True
    if(mode):
        log = "{} ::: [###::: {} :::###] = {}".format(str(datetime.utcnow()),key,message)
        #syslog.syslog(log)
        print(log)

def current_milli_time():
    return int(datetime.utcnow().timestamp() * 1000)

def decimal_fill(num,count):
    return str(int(num)).zfill(count)

class VariableConfigClass:
    #### Common 

    IsBoundingBox = True
    BoundingBoxRectangle = 2
    URI_DECODE_BIN = "uridecodebin"
    ACCESSTOKEN_MODE = 1 # 0:Microsoft, 1:TnmServer
    DEBUG = False


    debug_mode_file = "debug_mode.dat" ## mode 1 : DEBUG 0 : LIVE
    if(os.path.isfile(debug_mode_file)):
        with open(debug_mode_file,"r") as debug_mode_f:
            mode = int(debug_mode_f.readline().replace("\n",""))
            if(mode == 1):
                DEBUG = True
            else:
                DEBUG = False
            debug_mode_f.close()  
            print("### debug_mode ",mode)


    print("MODE==",DEBUG)


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



    
    ConfigJsonFile = "config.json"
    IsSelfCheckDone = False


    FireDetectFrame = 14
    FireDetectTime = 3000 #ms 
    Fire4TnmNotificationDelay = 5

    HatOffDetectFrame = 14 
    HatOffDetectTime = 3000 #ms
    DetectObject = "nohat"
    HatOff4TnMNotificationDelay = 15





    DeviceSeurityObjectFile = "DeviceSecurityObject.json"
    DevicePrivateKeyFile = "DevicePrivateKey.json"
    AUTHORITY="https://login.microsoftonline.com/485790a2-56da-46e0-9dc8-bbdb221444f5"
    CLIENT_ID="c2518e04-baca-4388-822c-d0a20b62617c"    ## BridgeDevice
    CLIENT_SECRET="OTc8Q~mspiGzzZYi1MBNLMGlm34~v63w1gMTiaJT"   ## BridgeDevice
    INGEST_RESOURCE_ID="api://359ff353-3e49-411d-9c08-3cf13ef6725a/.default" 
    SCENEMODE_API_ENDPOINT = "https://controller-tnmscenera.scenera.live/1.0/00000001-5eab-2e3d-8003-000100000000/control/0001/GetSceneMode"
    LOGIN_TOKEN_ENDPOINT = "/bridge-device/token"
    FIRMWAREAPI_ENDPOINT = "/noauth/GetFirmwareUpdate"
    DEVICESTATUS_ENDPOINT = "/noauth/device/status"
    SELF_CHECK_ENDPOINT = "/noauth/bridge-device/self-check/"
    SELF_CHECK_RESULT_API_ENDPOINT = "/noauth/bridge-device/self-check/{}/{}_{}/{}"
    SELF_CHECK_VIDEO_REQUEST_ENDPOINT  = "/noauth/bridge-device/self-check/video/{fileName}"



    if DEBUG :
 
        AUTHORITY="https://login.microsoftonline.com/485790a2-56da-46e0-9dc8-bbdb221444f5"
        CLIENT_ID="c2518e04-baca-4388-822c-d0a20b62617c"    ## BridgeDevice
        CLIENT_SECRET="OTc8Q~mspiGzzZYi1MBNLMGlm34~v63w1gMTiaJT"   ## BridgeDevice
        INGEST_RESOURCE_ID="api://359ff353-3e49-411d-9c08-3cf13ef6725a/.default" 
        DeviceSeurityObjectFile = "DeviceSecurityObject_DEV.json"
        ScenemodeEndPointFile = "scenemode_dev.dat"
        SCENEMODE_API_ENDPOINT = "https://controller-tnmscenera.scenera.live/1.0/00000001-5eab-2e3d-8003-000100000000/control/0001/GetSceneMode"
        LOGIN_TOKEN_ENDPOINT = "/bridge-device/token"
        FIRMWAREAPI_ENDPOINT = "/noauth/GetFirmwareUpdate"
        DEVICESTATUS_ENDPOINT = "/noauth/device/status"
        SELF_CHECK_ENDPOINT = "/noauth/bridge-device/self-check/"
        SELF_CHECK_RESULT_API_ENDPOINT = "/noauth/bridge-device/self-check/{}/{}_{}/{}"
        SELF_CHECK_VIDEO_REQUEST_ENDPOINT  = "/noauth/bridge-device/self-check/video/{fileName}"

        


        

    #if(os.path.isfile(ScenemodeEndPointFile)):
    #    with open(ScenemodeEndPointFile,"r") as scenemode_f:
    #        SCENEMODE_API_ENDPOINT = scenemode_f.readline().replace("\n","")
    #        scenemode_f.close()  



    NormalEnable = True 
    BridgeDeviceInferenceManager = BridgeDeviceInferenceManager
    BridgeDeviceGetSceneModeManager = BridgeDeviceGetSceneModeManager
    BridgeDeviceEventManager = BridgeDeviceEventManager
    BridgeDeviceSceneMarkManager = BridgeDeviceSceneMarkManager
    BridgeDeviceSceneDataManager = BridgeDeviceSceneDataManager
    BridgeDeviceEventFacilityManager = BridgeDeviceEventFacilityManager
    BridgeDeviceFirmwareUpdateManager = BridgeDeviceFirmwareUpdateManager
    BridgeDeviceSceneraLibraryManager = BridgeDeviceSceneraLibraryManager

    InferencingManagerEnable = NormalEnable
    EventManagerEnable = False
    SceneMarkManagerEnable = False
    SceneDataManagerEnable = False
    EventFacilityManagerEnable = False
    EllexiFallDownEnable = NormalEnable

    InferencingManagerEnable = True
    if(InferencingManagerEnable):
        EventManagerEnable = False
        SceneMarkManagerEnable = False
        SceneDataManagerEnable = False
        EventFacilityManagerEnable = False
        EllexiFallDownEnable = False

    UserAccount = getpass.getuser()
    
    EventPrintLog = False

    RootDirectory = "./content"
    ImageSaveDirectory = RootDirectory + "/image"
    VideoSaveDirectory = RootDirectory + "/video"
    ResultSaveDirectory =RootDirectory + "/result"
    SceneMarkDirectory = RootDirectory + "/scenemark"
    SceneDataDirectory = RootDirectory + "/scenedata"
    MetaDataDirectory  =  RootDirectory + "/normal_metadata"
    FMetaDataDirectory = RootDirectory + "/fmetadata"
    EllexiMetaDataDirectory = RootDirectory + "/normal_metadata"

    video_record_root = "./record/"
    video_recording_directory = video_record_root + "video/" 
    video_time_result_directory = video_record_root + "timeresult/"
    video_result_directory = video_record_root + "videoresult/"
    video_recording_time_file = "result.txt"  

    
    LOITERING = 1
    INTRUSION = 2
    REVINTRUSION = 16
    VIOLENCE = 24
    ABANDONMENT = 40
    SPEEDGATE = 100
    TAILGATE = 101

    Abandoned4Tnm = 201
    LoiteringPPE4Tnm = 202
    RoadBlockCar4Tnm = 203 
    TailgatingCar4Tnm = 204


    LoiteringKey = "Loitering"
    IntrusionKey = "Intrusion"
    RevIntrusionKey = "Revintrusion"
    ViolenceKey = "ViolenceX"
    AbandonmentKey = "Abandonment"
    SpeedGateKey = "Speedgate"
    TailGateKey = "Tailgate"
    Fire4TnmKey = "Fire"
    HatOff4Tnm = "Hatoff"
    FallDown4Ellexi = "Falldown"
    # ABM 
    TailgatingCar4TnmKey = "TailGatingABM"
    Abandoned4TnmKey = "Abandoned"
    TripNFall4TnmKey = "TripNFall"
    GateStuck4TnmKey = "GateStuck"
    RoadBlockCar4TnmKey = "RoadBlockCar"
    LoiteringPPE4TnmKey = "LoiteringPPE"

    EventClass = {"person":0, 
                  "bag": 1, 
                  "suitcase": 1, 
                  "handbag": 1, 
                  "box": 1, 
                  "car": 2, 
                  "truck": 2,  
                  "bus": 2
                  }

 

    #### Inferencing Manager
    BridgeDeviceID = ""
    IsBridgeDeviceRunning = False
    MAX_DISPLAY_LEN=64
    MUXER_OUTPUT_WIDTH=1920
    MUXER_OUTPUT_HEIGHT=80
    MUXER_BATCH_TIMEOUT_USEC=4000000 / 10
    #Resolution_Width = 1280
    #Resolution_Height = 720

    Resolution_Convert_Width = 1280
    Resolution_Convert_Height = 720

    #ImageSizeWidth = 1280
    #ImageSizeHeight = 720

    TILED_OUTPUT_WIDTH=1280
    TILED_OUTPUT_HEIGHT=720
    GST_CAPS_FEATURES_NVMM = "memory:NVMM"
 



    BrigdeDeviceConfigFile = "BridgeDeviceConfig.json"
    

    FullPathDirectory = "/opt/nvidia/deepstream/deepstream/sources/BridgeDevice/apps/bridge_device/"
    FirmwareLocalPath = "/home/ghosti/firmware/"
    FirmwareServerPath = "./"
    FirmwareBridgeDevicePath = "/home/ghosti/bridge_device/"
    FirmwareUpdateTime = 120

   
   
    TIME_TO_MERGE_META_DATA = 0.5
    VERSION = "1.0"
    IsBridgeDeviceRunning = False
    PIPELINE_INFO_LIST = []
    PIPELINE_RUNNING = False
    GENERATING_VIDEO_FPS = 1

    #### Get SceneMode Manager
    InferenceFPS = 8
    CameraFPS = 25
    DETENTION_FRAME = int(InferenceFPS * 60 * .5/GENERATING_VIDEO_FPS) # 5 minutes images 
    SceneModeRefreshTime = 30
    RTSP_ADDRESS = "192.168.0.28:1935"

    #Facility Config 
    StartCheckFrameRatio = 0.7
    EndCheckFrameRatio = 0.7
    REDUCE_ROI_RATIO = 0.2
    #Loitering Delay 
    DetectDelay = 30 
    ### DEBUG MODE TEST 
    DEBUG_MODE = False


    ### SpeedGate Config
    tailgate_box_ratio = 0.5
    tailgate_threshold_time = 1.1
 

   
    DetectedObjectMetaInfoList = []
    FakeSink = "N"
    AccessToken = ""
    Header = ""
    CameraList = []

    MAX_CAMERA_NODES = 10
    IsFakeSink = "N"
    range_list = None 
    range_list = []
    for i in range(1,MAX_CAMERA_NODES + 1):
        range_list.append(decimal_fill(i,4))
    print("range_list ",range_list)

    NumberOfNodes = str(len(range_list)) ### MAX_CAMERA_NODES 
    RepeatPeriod = "10" 

    RecentResultList = []
    ResultKey = {
        LoiteringKey:[0,"0000"],
        IntrusionKey:[0,"0000"],
        RevIntrusionKey:[0,"0000"],
        ViolenceKey:[0,"0000"],
        AbandonmentKey:[0,"0000"],
        SpeedGateKey:[0,"0000"],
        TailGateKey:[0,"0000"],
        Fire4TnmKey:[0,"0000"],
        HatOff4Tnm:[0,"0000"],
        FallDown4Ellexi:[0,"0000"],
        Abandoned4TnmKey:[0,"0000"],
        TailgatingCar4TnmKey:[0,"0000"],
        TripNFall4TnmKey:[0,"0000"],
        GateStuck4TnmKey:[0,"0000"],
        RoadBlockCar4TnmKey:[0,"0000"],
        LoiteringPPE4TnmKey:[0,"0000"]
    }

    for i in range(0, len(range_list)):
        RecentResultList.append(copy.deepcopy(ResultKey))
