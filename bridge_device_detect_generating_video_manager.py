import os 
import subprocess
import threading
import time
import json
import pickle
from bridge_device_peoplenet_config import VariableConfigClass
BridgeDeviceConfigVariable = VariableConfigClass()
ArrThreadList = []

CameraList = []


def kill_process_of_ffmpeg(camera_name):
    ffmpeg_process_list = subprocess.check_output(["ps -ef | grep ffmpeg | grep " + camera_name],shell=True,encoding='utf-8')
    print("################## ps -ef | grep ffmpeg | grep " + camera_name)
    print(ffmpeg_process_list)
    list_ffmpeg = str(ffmpeg_process_list).split("\n")
    for item in list_ffmpeg:
        list_pid = item.split(' ')
        for pid in list_pid:
            if(pid.isnumeric()): 
                os.system("kill -9 " + str(pid))
                break


def kill_process_of_ffmpeg_all():
    ffmpeg_process_list = subprocess.check_output([" ps -ef | grep ffmpeg "],shell=True,encoding='utf-8')
    print("################## ps -ef | grep ffmpeg ")
    print(ffmpeg_process_list)
    list_ffmpeg = str(ffmpeg_process_list).split("\n")
    for item in list_ffmpeg:
        list_pid = item.split(' ')
        for pid in list_pid:
            if(pid.isnumeric()): 
                os.system("kill -9 " + str(pid))
                break


#/usr/bin/ffmpeg -use_wallclock_as_timestamps 1 -rtsp_transport tcp -i 'rtsp://admin:admin@192.168.0.110' -c:a aac -c:v copy -flags +global_header -strftime 1 -f segment -map 0:0 -map 0:1 -segment_time 2 -reset_timestamps 1 -y ./content/video/00000001-5cdd-280b-8002-00010000ffe2_0002/00000001-5cdd-280b-8002-00010000ffe2_0002_%Y%m%d%H%M%S_%s.mp4



def generating_clip_video(camera_id, rtsp_url, record_time, width, height, fps):
    print(BridgeDeviceConfigVariable.video_recording_directory  + ":" + camera_id + ":" + rtsp_url + ":" + str(width) + ":" + str(height) + ":" + str(fps))
    command = "/usr/bin/ffmpeg -use_wallclock_as_timestamps 1 -rtsp_transport tcp -i '{}' -framerate {} -video_size {} -c:a aac -c:v copy -fflags +genpts -flags +global_header -strftime 1 -f segment -segment_time {} -reset_timestamps 1 -y {}/{}/%s.mp4".format(rtsp_url, str(fps), str(width) + "x" + str(height), record_time, BridgeDeviceConfigVariable.video_recording_directory,camera_id)

    print(command)
    os.system(command)
    print("###### Start Generating Video Clip with {}".format(camera_id))

def manage_camera_rtsp():
    
    if(os.path.isdir(BridgeDeviceConfigVariable.video_record_root)):
        pass
    else:
        os.mkdir(BridgeDeviceConfigVariable.video_record_root)


    if not(os.path.isdir(BridgeDeviceConfigVariable.video_recording_directory)):
        os.mkdir(BridgeDeviceConfigVariable.video_recording_directory)

    while(True):
        bridge_device_config_file_name = "./" + BridgeDeviceConfigVariable.BrigdeDeviceConfigFile + ".dat"
        #print(bridge_device_config_file_name)
        if(os.path.isfile(bridge_device_config_file_name)):
            with open(bridge_device_config_file_name,"rb") as f:
                Config = json.loads(pickle.load(f))
                if(Config):
                    BridgeDeviceInfo = Config["BridgeDeviceInfo"]
                    BridgeDeviceID = BridgeDeviceInfo["BridgeDeviceID"]
                    #print("######BridgeDeviceID " + BridgeDeviceID)
                    ###################################################################################
                    for thread_info in ArrThreadList:
                        is_camera_open = False
                        for CameraInfo in BridgeDeviceInfo["CameraList"]:
                            CameraID = BridgeDeviceID + "_" + CameraInfo["CameraID"]

                            #print("###############{} : {}".format(CameraID,thread_info.getName()))
                            if CameraID == thread_info.getName():
                                is_camera_open = True
                                break
                        
                        if(is_camera_open == False):
                            CameraID = thread_info.getName()
                            #print(CameraID + " is removed .....###########")
                            if thread_info.is_alive:
                                thread_info._stop
                            ArrThreadList.remove(thread_info)
                            kill_process_of_ffmpeg(CameraID)
                    ###################################################################################

                    for CameraInfo in BridgeDeviceInfo["CameraList"]:
                        StartTime = int(CameraInfo["WorkTime"]["StartTime"])
                        EndTime = int(CameraInfo["WorkTime"]["EndTime"])
                        CurrentTime = int(time.strftime("%H%M"))
                        Use = CameraInfo["Use"]
                        if(StartTime > 0 and EndTime > 0):
                            if(StartTime >= CurrentTime and EndTime >= CurrentTime):
                                pass
                            else:
                                if(Use == "Y"):
                                    Use = "N"
                        
                        if(Use == "N"):
                            for CameraThread in ArrThreadList:
                                CameraID = BridgeDeviceID + "_" + CameraInfo["CameraID"]
                                if(CameraID == CameraThread.getName()):
                                    ArrThreadList.remove(CameraThread)
                                    kill_process_of_ffmpeg(CameraID)
                        
                    ###################################################################################
                    #print("\n#{} Cameras running on BridgeDevice {}\n".format(str(len(ArrThreadList)),BridgeDeviceID))

                    for CameraInfo in BridgeDeviceInfo["CameraList"]:
                        #IP = CameraInfo["IP"]
                        #PORT = 0
                        #if(CameraInfo["Port"]):
                        #    PORT = int(CameraInfo["Port"])
                        #URL = CameraInfo["RTSP_Postfix"]
                        RTSP_URL = CameraInfo["RTSP_URL"].replace("rtspt","rtsp")
                        ResolutionWidth = CameraInfo["ResolutionWidth"]
                        ResolutionHeight = CameraInfo["ResolutionHeight"]
                        CameraFPS = CameraInfo["CameraFPS"]
                        RecordTime = CameraInfo["RecordTime"]
                        RecordTime = 10
                        CameraID = BridgeDeviceID + "_" + CameraInfo["CameraID"]
                        #Account_ID = CameraInfo["Account_ID"]
                        #Account_PWD = CameraInfo["Account_PWD"]
                        Use = CameraInfo["Use"]
                        CurrentTime = int(time.time() / 1000)
                        StartTime = int(CameraInfo["WorkTime"]["StartTime"])
                        EndTime = int(CameraInfo["WorkTime"]["EndTime"])
                        CurrentTime = int(time.strftime("%H%M"))

                        if StartTime > 0 and EndTime > 0:
                            if(StartTime >= CurrentTime and EndTime >= CurrentTime):
                                pass
                            else:
                                if(Use == "Y"):
                                    Use = "N"
                        if(Use == "Y"): ## Using Camera or not
                            if len(ArrThreadList) > 0:
                                check_camera_thread_running = False
                                for thread_info in ArrThreadList:
                                    if str(thread_info.getName()) == CameraID:
                                        check_camera_thread_running = True
                                        #print(CameraID + " is existed.....#######")
                                        break
                                
                                if check_camera_thread_running == False:
                                    if not(os.path.isdir(BridgeDeviceConfigVariable.video_recording_directory + "/" + CameraID)):
                                        os.mkdir(BridgeDeviceConfigVariable.video_recording_directory + "/" + CameraID)
                                    ffmpeg_thread = threading.Thread(target=generating_clip_video,args=(CameraID,RTSP_URL,RecordTime,ResolutionWidth,ResolutionHeight,CameraFPS))
                                    ffmpeg_thread.daemon = True
                                    ffmpeg_thread.start()
                                    ffmpeg_thread.setName(CameraID)
                                    ArrThreadList.append(ffmpeg_thread)  
                                
                            else:
                                if not(os.path.isdir(BridgeDeviceConfigVariable.video_recording_directory + "/" + CameraID)):
                                    os.mkdir(BridgeDeviceConfigVariable.video_recording_directory + "/" + CameraID)
                                ffmpeg_thread = threading.Thread(target=generating_clip_video,args=(CameraID,RTSP_URL,RecordTime,ResolutionWidth,ResolutionHeight,CameraFPS))
                                ffmpeg_thread.daemon = True
                                ffmpeg_thread.start()
                                ffmpeg_thread.setName(CameraID)
                                ArrThreadList.append(ffmpeg_thread)   
                    ###################################################################################
                
    
        time.sleep(3)
             
   
def check_status_thread():

    kill_process_of_ffmpeg_all()

    main_thread = threading.Thread(target=manage_camera_rtsp,args=())
    main_thread.daemon = True
    main_thread.start()

    print("########  check_status_thread is started .......")
    while(True):
        time.sleep(1)
        for thread_info in ArrThreadList:
            if thread_info.is_alive():
                CameraID = thread_info.getName()
                #print("############################ " + thread_info.getName() + " alive ........")
            else:
                #print("############################" + thread_info.getName() + " not alive......")
                CamearID = thread_info.getName()
                #print(CamearID + " is removed .....###########")
                if thread_info.is_alive:
                    thread_info._stop
                ArrThreadList.remove(thread_info)
                kill_process_of_ffmpeg(CamearID)



check_status_thread()
