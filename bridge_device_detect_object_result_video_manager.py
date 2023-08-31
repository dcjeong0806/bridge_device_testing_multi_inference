from locale import currency
import sys
import time
import json
import threading
import concurrent.futures
import os
import datetime
import shutil

from bridge_device_peoplenet_config import VariableConfigClass
BridgeDeviceConfigVariable = VariableConfigClass()

def check_video_recording():
    print("==========================================")
    print("::::: check_video_recording is started...::::")
    print("==========================================")

    
    try:
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
    except Exception as ex:
        pass
    
    while(True):
        try:
            camera_list = os.listdir(BridgeDeviceConfigVariable.video_time_result_directory)
            camera_list.sort()
            for camera_id in camera_list:
                video_recording_result_file_name = BridgeDeviceConfigVariable.video_time_result_directory + camera_id + "/" + BridgeDeviceConfigVariable.video_recording_time_file

                if(os.path.isfile(video_recording_result_file_name)):
                    f = open(video_recording_result_file_name,"r")
                    os.remove(video_recording_result_file_name)
                    record_time = f.readlines()
                    f.close()
                    
                    video_recording_file_list = "{}".format(BridgeDeviceConfigVariable.video_recording_directory + camera_id)
                    if(os.path.isdir(video_recording_file_list)):
                        file_list = os.listdir(video_recording_file_list)
                        file_list.sort()

                        for item in record_time:
                            currenttime = int(item)
                            yy = datetime.datetime.fromtimestamp(int(currenttime)).strftime("%Y")
                            mm = datetime.datetime.fromtimestamp(int(currenttime)).strftime("%m")
                            dd = datetime.datetime.fromtimestamp(int(currenttime)).strftime("%d")
                            
                            if(os.path.isdir(BridgeDeviceConfigVariable.video_result_directory + camera_id)):
                                pass
                            else:
                                os.mkdir(BridgeDeviceConfigVariable.video_result_directory + camera_id)

                            if(os.path.isdir(BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy)):
                                pass
                            else:
                                os.mkdir(BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy)

                            if(os.path.isdir(BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy + "/" + mm )):
                                pass
                            else:
                                os.mkdir(BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy + "/" + mm)

                            if(os.path.isdir(BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy + "/" + mm + "/" + dd )):
                                pass
                            else:
                                os.mkdir(BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy + "/" + mm + "/" + dd)
                            
                            for file_name in file_list:
                                file_name_time = file_name.replace(".mp4","")
                                start_time = int(file_name_time)
                                end_time = int(file_name_time) + 10
                                if(int(item) >= start_time and int(item) <= end_time):
                                    print(camera_id,file_name,start_time, end_time, item)
                                    if(os.path.isfile(BridgeDeviceConfigVariable.video_recording_directory + camera_id + "/" + file_name)):
                                        source_file = BridgeDeviceConfigVariable.video_recording_directory + camera_id + "/" + file_name
                                        destination_file = BridgeDeviceConfigVariable.video_result_directory + camera_id + "/" + yy + "/" + mm + "/" + dd + "/" + file_name
                                        shutil.move(source_file, destination_file)
                                    break
                                
                                '''
                                for delete_file_name in file_list: 
                                    file_name_time = delete_file_name.replace(".mp4","")
                                    file_name_time = int(file_name_time)
                                    if(file_name_time < int(item)):
                                        if(os.path.isfile(BridgeDeviceConfigVariable.video_recording_directory + camera_id + "/" + delete_file_name)):
                                            os.remove(BridgeDeviceConfigVariable.video_recording_directory + camera_id + "/" + delete_file_name)
                                '''
            
        except Exception as ex:
            pass
        time.sleep(10)


def remove_video_file():
    print("==========================================")
    print("::::: remove_video_file is started...::::")
    print("==========================================")
    try:
        if(os.path.isdir(BridgeDeviceConfigVariable.video_record_root)):
            pass
        else:
            os.mkdir(BridgeDeviceConfigVariable.video_record_root)
            

        if(os.path.isdir(BridgeDeviceConfigVariable.video_time_result_directory)):
            pass
        else:
            os.mkdir(BridgeDeviceConfigVariable.video_time_result_directory)

        if(os.path.isdir(BridgeDeviceConfigVariable.video_recording_directory)):
                pass
        else:
                os.mkdir(BridgeDeviceConfigVariable.video_recording_directory)
    except Exception as ex:
        pass

    while(True):
        try:
            camera_list = os.listdir(BridgeDeviceConfigVariable.video_time_result_directory)
            camera_list.sort()
    

            for camera_id in camera_list:
                video_recording_file_list = "{}".format(BridgeDeviceConfigVariable.video_recording_directory + camera_id)
                if(os.path.isdir(video_recording_file_list)):
                    file_list = os.listdir(video_recording_file_list)
                    file_list.sort()
                    for delete_file_name in file_list: 
                        file_name_time = delete_file_name.replace(".mp4","")
                        file_name_time = int(file_name_time)
                        currenttime = int(time.time())
                        if(file_name_time < currenttime - 120):
                            if(os.path.isfile(BridgeDeviceConfigVariable.video_recording_directory + camera_id + "/" + delete_file_name)):
                                os.remove(BridgeDeviceConfigVariable.video_recording_directory + camera_id + "/" + delete_file_name)
                currenttime = int(time.time())
                yy = datetime.datetime.fromtimestamp(int(currenttime)).strftime("%Y")
                mm = datetime.datetime.fromtimestamp(int(currenttime)).strftime("%m")
                dd = datetime.datetime.fromtimestamp(int(currenttime)).strftime("%d")
                video_result_file_list = "{}/{}/{}/{}".format(BridgeDeviceConfigVariable.video_result_directory + camera_id,yy,mm,dd)
                if(os.path.isdir(video_result_file_list)):
                    file_list = os.listdir(video_result_file_list)
                    file_list.sort()
                    for delete_file_name in file_list: 
                        file_name_time = delete_file_name.replace(".mp4","")
                        file_name_time = int(file_name_time)
                        currenttime = int(time.time())
                        if(file_name_time < currenttime - 120):
                            if(os.path.isfile(video_result_file_list + "/" + delete_file_name)):
                                os.remove(video_result_file_list + "/" + delete_file_name)
        except Exception as ex:
            pass

        time.sleep(10)

def main():
    remove_video_file_thread = threading.Thread(target=remove_video_file,args=())
    remove_video_file_thread.deamon = True
    remove_video_file_thread.setName("remove_video_file")
    remove_video_file_thread.start()

    check_video_recording()


main()

