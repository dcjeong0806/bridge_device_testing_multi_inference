import subprocess
import os
from bridge_device_peoplenet_config import VariableConfigClass, DebugPrint
BridgeDeviceConfigVariable = VariableConfigClass()

class BridgeDeviceInfoClass:
    MaxCameraConnection = 0
    BridgeDeviceID = ""
    drop_frame_interval = 0
    FakeSink = ""
    TOLERANCE = 0
    CameraList = []

class CameraMetaInfoClass:
    CameraType = ""
    AIModelType = ""
    BridgeDeviceID = ""
    Description = ""
    RTSP_URL = ""
    Distance = "Normal"
    IP = ""
    Port = ""
    Account_ID = ""
    Account_PWD = ""
    RTSP_Postfix = ""
    RTSP_URL = ""
    Reconnect_Interval = 0
    RecordTime = 0
    KeepAliveTime = 0
    CodecType = ""
    Confidence = 0
    drop_frame_interval = 0
    MediaFormat = []
    RecordTime = 0
    Use = "N"
    Encryption = "N"
    Detection_Area = []
    SceneMarkMode = []
    SceneModeConfig = []
    SceneMode = "Label"
    CameraID = ""
    ShowError = "N"
    DetentionTime = 0
    WorkTime = {}
    Skip_Area = []
    SceneMarkEndPoint = ""
    SceneMarkToken = ""
    SceneMarkAuthority = ""
    SceneDataEndPoint = ""
    SceneDataToken = ""
    SceneDataAuthority = ""

    AccessToken = ""
    SelfCheckYn = "N"
    SelfCheckReportTime = ""
    EventCode = ""

    ImageStatus = ["Start","Start","Start","Start","Start","Start","Start","Start","Start","Start"]
    EndObjectCount = [0,0,0,0,0,0,0,0,0,0]
    EndObjectResetCount = [0,0,0,0,0,0,0,0,0,0]
    StartObjectCount = [0,0,0,0,0,0,0,0,0,0]
    StartObjectResetCount = [0,0,0,0,0,0,0,0,0,0]
    StartFrameNumber = [0,0,0,0,0,0,0,0,0,0]
    EndFrameNumber = [0,0,0,0,0,0,0,0,0,0]

    ImageNameList = []
    FrameNumber = 0
    StartFrame = 0
    EndFrame = 0
    DetentionTime = 0 
    EndTimeStamp = 0 
    StartInferencingTime = 0
    ImageDataList = []
    ResolutionWidth = 1920
    ResolutionHeight = 1080
    CameraFPS = 25
    InferenceFPS = 8
    UseYn = ""

class AnalysisRegionClass:
    XCoord = 0
    YCoord = 0

class SchedulingClass:
    SchedulingType = "ScheduledWeekDay"
    StartTime = "00:00"
    EndTime = "00:00"

class SceneModeConfigClass:
    CustomAnalysisStage = ""
    AnalysisRegion = []
    Threshold = 0.7
    Scheduling = None
    AnalysisResult = {
        "Result":"UnDetected",
        "AdditionalInfo":[]
    }
    Resolution = ""

class PipeLineInfoClass:
    PIPELINE = None
    PIPELINE_THREAD = None

def check_bridge_device_falldown_fight_process(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        print(process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith("./" + process_name)):
                if(process_name != BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager):
                    pid_list = item.split(" ")
                    print(pid_list)
                    for pid in pid_list:
                        if(pid.isdecimal()):
                            command = "/bin/kill -9 " + pid
                            print(command)
                            os.system(command)
                            break
                    

                    '''
                    if(len(pid_list) > 4):
                        command = "/bin/kill -9 " + pid_list[5]
                        if(pid_list[3] != ""):
                            command = "/bin/kill -9 " + pid_list[3]
                        print(command + " is killed",item)
                        os.system(command)
                    '''
                
                process_count = process_count + 1
                print(item + " is running...")
        return process_count
    except Exception as ex:
        print(str(ex))
        return process_count
        pass

def check_bridge_device_process(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        #print(">>>>>>>>>>>>>>>>> check_bridge_device_process >>>>>>>>>>>>>>>>>>",process)
        process_list = str(process).split("\n")
        for item in process_list:
            pro_name = process_name + ".pyc"
            if pro_name in item:
                if(process_name != BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager):
                    pid_list = item.split(" ")
                    #print(">>>>>>>>>>>>>>>>> pid_list >>>>>>>>>>>>>>>>>>",pid_list)
                    for pid in pid_list:
                        if(pid.isdecimal()):
                            command = "/bin/kill -9 " + pid
                            os.system(command)
                            break
                    
                    '''
                    if(len(pid_list) > 4):
                        command = "/bin/kill -9 " + pid_list[5]
                        if(pid_list[3] != ""):
                            command = "/bin/kill -9 " + pid_list[3]
                        print(command + " is killed",item)
                        os.system(command)
                    '''
                
                process_count = process_count + 1
                #print(item + " is running...")
        return process_count
    except Exception as ex:
        #print(str(ex))
        return process_count
        pass

def kill_bridge_device_falldown_fight_process(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        print(process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith("./" + process_name)):
                if(process_name != BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager):
                    pid_list = item.split(" ")
                    print(pid_list)
                    for pid in pid_list:
                        if(pid.isdecimal()):
                            command = "/bin/kill -9 " + pid
                            print(command)
                            os.system(command)
                            break
                process_count = process_count + 1
                print(item + " is running...")
        return process_count
    except Exception as ex:
        print(str(ex))
        return process_count
        pass

def kill_bridge_device_process(process_name):
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        #print(process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith(process_name + ".pyc")):
                #if(process_name == BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager):
                pid_list = item.split(" ")
                #print(pid_list)
                for pid in pid_list:
                    if(pid.isdecimal()):
                        command = "/bin/kill -9 " + pid
                        print("kill_bridge_device_process::::",command)
                        os.system(command)
                        break

    except Exception as ex:
        print(str(ex))
        pass


def GetCameraID(index):
    camera_id = "000" + str(index)
    if(index > 9):
        camera_id = "00" + str(index)
    return camera_id
    
def parsing_camerainfo(camera_info,bridgedeviceid):
    #try:
    camera_meta_info = CameraMetaInfoClass()
    camera_meta_info.BridgeDeviceID = bridgedeviceid
    camera_meta_info.device_id = camera_meta_info.BridgeDeviceID
    camera_meta_info.CameraType = camera_info["CameraType"]
    camera_meta_info.AIModelType = camera_info["AIModelType"]
    camera_meta_info.IP = camera_info["IP"]
    camera_meta_info.Port = camera_info["Port"]
    camera_meta_info.RTSP_Postfix = camera_info["RTSP_Postfix"]
    camera_meta_info.Account_ID = camera_info["Account_ID"]
    camera_meta_info.Account_PWD = camera_info["Account_PWD"]
    camera_meta_info.RTSP_URL = camera_info["RTSP_URL"]
    camera_meta_info.Distance = camera_info["Distance"]
    camera_meta_info.Reconnect_Interval = camera_info["Reconnect_Interval"]
    camera_meta_info.KeepAliveTime = camera_info["KeepAliveTime"]
    camera_meta_info.CodecType = camera_info["CodecType"]
    camera_meta_info.Confidence = camera_info["Confidence"]
    camera_meta_info.ShowError = camera_info["ShowError"]
    camera_meta_info.drop_frame_interval = camera_info["drop_frame_interval"]
    camera_meta_info.SceneMarkToken = camera_info["SceneMarkToken"]
    camera_meta_info.SceneMarkEndPoint = camera_info["SceneMarkEndPoint"]
    camera_meta_info.SceneMarkAuthority = camera_info["SceneMarkAuthority"]
    camera_meta_info.SceneDataToken = camera_info["SceneDataToken"]
    camera_meta_info.SceneDataEndPoint = camera_info["SceneDataEndPoint"]
    camera_meta_info.SceneDataAuthority = camera_info["SceneDataAuthority"]
    camera_meta_info.ResolutionWidth = camera_info["ResolutionWidth"]
    camera_meta_info.ResolutionHeight = camera_info["ResolutionHeight"]
    camera_meta_info.CameraFPS = camera_info["CameraFPS"]
    camera_meta_info.InferenceFPS = camera_info["InferenceFPS"]
    camera_meta_info.SelfCheckReportTime = camera_info["SelfCheckReportTime"]
    camera_meta_info.SelfCheckYn = camera_info["SelfCheckYn"]
    camera_meta_info.AccessToken = camera_info["AccessToken"]
    camera_meta_info.EventCode = camera_info["EventCode"]

    if(camera_info["SceneModeConfig"]):
        camera_meta_info.SceneModeConfig = camera_info["SceneModeConfig"]

    camera_meta_info.MediaFormat = []
    for item in camera_info["MediaFormat"]:
        camera_meta_info.MediaFormat.append(item)


    camera_meta_info.SceneMarkMode = []
    for item in camera_info["SceneMarkMode"]:
        camera_meta_info.SceneMarkMode.append(item)

    camera_meta_info.RecordTime = camera_info["RecordTime"]
    camera_meta_info.Use = camera_info["Use"]
    camera_meta_info.Encryption = camera_info["Encryption"]
    camera_meta_info.Detection_Area = []
    for item in camera_info["Detection_Area"]:
        area = {
            "x1":item["x1"],
            "x2":item["x2"],
            "y1":item["y1"],
            "y2":item["y2"]
        }#######DetectedObjectMetaInfoList
        camera_meta_info.Detection_Area.append(area)
        
    camera_meta_info.CameraID = camera_info["CameraID"]
    camera_meta_info.camera_id = camera_meta_info.CameraID

    camera_meta_info.Description = camera_info["Description"]
    camera_meta_info.DetentionTime = camera_info["DetentionTime"]
    camera_meta_info.WorkTime = {
        "StartTime":camera_info["WorkTime"]["StartTime"],
        "EndTime": camera_info["WorkTime"]["EndTime"]
    }

    camera_meta_info.Skip_Area = []
    for item in camera_info["Skip_Area"]:
        area = {
            "x1":item["x1"],
            "x2":item["x2"],
            "y1":item["y1"],
            "y2":item["y2"]
        }
        camera_meta_info.Skip_Area.append(area)

    return camera_meta_info
    #except Exception as ex:
    #    print("#### PARSING CAMERA INFO::::",str(ex))
    #    pass

class DetectedMetaInfo:
    frame_num = 0
    origin_frame_num = 0 
    detected_time = 0
    device_id = ""
    camera_id = ""
    source_id = -1
    rtsp_url = ""
    video_file_name = []
    thumbnail_image_file_name = ""
    full_image_file_name = ""
    scenedata_name = ""
    scenemode = ""
    clip_video_directory = ""
    clip_image_directory = ""
    detected_object_info_list = []
    camera_info = CameraMetaInfoClass()
    IsNewSceneMode = False
    DetectedEvent = []
    VideoFileCommand = ""
    ImageFileList = ""
    SceneMarkID = ""
    SceneDataThumbnailID = ""
    SceneDataImageID  = ""
    SceneDataVideoID = ""
    FrameDetected = 0
    FrameStarted = 0 
    FrameEnded = 0 
    IsFacility = False
    IsUploadTwoImage = False
    SceneMarkIsDone = False
    SaveImageDirectory = ""
    SelfCheckYn = "N"
    SelfCheckReportTime = "0000-00-00 00:00:00"
    SelfInferenceCheck = "N"
    SelfEventCheck = "N"
    ProcessTimeList = None

class DetectedObjectInfo:
    top = 0
    left = 0
    width = 0
    height = 0 
    x1 = 0
    x2 = 0
    y1 = 0 
    y2 = 0
    detected_object = ""
    detected_time_ms = 0
    strBase64OfImage = ""
    confidence = 0

class SMDetectedObjectInfo:
    AlgorithmID = "12345678-1234-1234-1234-123456789abc"
    NICEItemType = "Human"
    CustomItemType = ""
    Resolution_Height = 0
    Resolution_Width = 0
    XCoordinate = 0
    YCoordinate = 0
