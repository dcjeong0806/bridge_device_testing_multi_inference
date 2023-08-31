import signal
from jtop import jtop, JtopException
import os 
import pickle 
import json
import datetime
from datetime import time
import time
import requests
import msal
import sys
import urllib3
import subprocess
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID, GetDevicePassword
from bridge_device_peoplenet_config import VariableConfigClass, DebugPrint
from RestAPI import RestAPIPost, RstAPIGet, RestAPIGet_With_AccessToken, RestAPIPost_With_AccessToken_FirmWare

BridgeDeviceConfigVariable = VariableConfigClass()

### LIVE
AUTHORITY="https://login.microsoftonline.com/485790a2-56da-46e0-9dc8-bbdb221444f5"
CLIENT_ID="c2518e04-baca-4388-822c-d0a20b62617c"
CLIENT_SECRET="v5yRwNP~848QZ.242d3~Vg-6GPl5P5B7-S"
INGEST_RESOURCE_ID="api://0e0c2aef-941c-4b95-a17e-76c2e92a1616/.default"
API_ENDPOINT = "https://www.aiviewer.co.kr/noauth/device/status"

AUTHORITY = BridgeDeviceConfigVariable.AUTHORITY
CLIENT_ID = BridgeDeviceConfigVariable.CLIENT_ID
CLIENT_SECRET = BridgeDeviceConfigVariable.CLIENT_SECRET
INGEST_RESOURCE_ID = BridgeDeviceConfigVariable.INGEST_RESOURCE_ID
API_ENDPOINT = BridgeDeviceConfigVariable.DEVICESTATUS_ENDPOINT

'''
### DEV
if BridgeDeviceConfigVariable.DEBUG:
    AUTHORITY="https://login.microsoftonline.com/485790a2-56da-46e0-9dc8-bbdb221444f5"
    CLIENT_ID="c2518e04-baca-4388-822c-d0a20b62617c"
    CLIENT_SECRET="v5yRwNP~848QZ.242d3~Vg-6GPl5P5B7-S"
    INGEST_RESOURCE_ID="api://fd8edefb-abe4-418e-8185-365877eacd5d/.default"
    API_ENDPOINT = "https://tnmbss.scenera.live/noauth/device/status"
'''

def check_bridge_device_falldown_fight_process_status(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        print(process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith("./" + process_name)):    
                process_count = process_count + 1
                print(item + " is running...")
        return process_count
    except Exception as ex:
        print(str(ex))
        return process_count
        pass


def check_bridge_device_kill_process(process_name):
    now = datetime.datetime.now()
    now = now.strftime("%H:%M")
    print(now)
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        #print("?????" + process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith(process_name + ".pyc")):                
                item = item.replace("      "," ").replace("     "," ").replace("    "," ").replace("   "," ").replace("  "," ")
                print("##### " + item + " is running...")
                arr_list = item.split(" ")
                if(now != arr_list[4]):
                    os.system("kill -9 " + str(arr_list[1]))

        return process_count
    except Exception as ex:
        print(str(ex))
        return process_count
        pass




def check_bridge_device_process_status(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        print("?????" + process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith(process_name + ".pyc")):                
                process_count = process_count + 1
                print("##### " + item + " is running...")
        return process_count
    except Exception as ex:
        print(str(ex))
        return process_count
        pass


def check_application_status():
    ### INFERENCE MANAGER
    check_bridge_device_kill_process("bridge_device_peoplenet_device_status_manager")


    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceInferenceManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"InferenceManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("InferenceManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### EVENT MANAGER
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceEventManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"EventManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("EventManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### SCENEMARK MANAGER 
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceSceneMarkManager) == 0):
        status = "E"

    ApplicationStatus = {
        "ApplicationName":"SceneMarkManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("SceneMarkManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### SCENEDATA MANAGER 
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceSceneDataManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"SceneDataManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("SceneDataManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### FCILITY MANAGER
    status = "N"
    if(check_bridge_device_process_status(BridgeDeviceConfigVariable.BridgeDeviceEventFacilityManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"FacilityManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("FacilityManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)

    ### FALLDOWNFIGHT MANAGER
    status = "N"
    if(check_bridge_device_falldown_fight_process_status(BridgeDeviceConfigVariable.BridgeDeviceFallDownFightManager) == 0):
        status = "E"
    ApplicationStatus = {
        "ApplicationName":"FallDownFightManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("FallDownFightManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)
    
    
    ### FALLDOWNFIGHT MANAGER
    status = "N"
    #if(check_bridge_device_process(BridgeDeviceConfigVariable.SceneModeManager) == 0):
    #    status = "E"
    ApplicationStatus = {
        "ApplicationName":"SceneModeManager",
        "Status":status,
        "CheckTime":(str(datetime.datetime.now())).split('.')[0]
    }
    with open("SceneModeManager.dat","wb") as f:
        pickle.dump(ApplicationStatus,f)


def read_stats(jetson):
    
    try:
        check_application_status()
        now = datetime.datetime.now()
        minute = now.minute
        print("current time :::" , minute)
        if(minute % 1 == 0):
            stats = jetson.stats
            
            print(stats)
            print(stats["CPU1"])
            print(stats["CPU2"])
            print(stats["CPU3"])
            print(stats["CPU4"])
            print(stats["CPU5"])
            print(stats["CPU6"])
            print(stats["GPU"])
            print(stats["RAM"])
            print(stats["Temp GPU"])
            print(stats["Temp MCPU"])
            print(stats["Temp BCPU"])
            print(stats["uptime"])
            print(stats["SWAP"])
            print("\n\n")
            


            

            BridgeDeviceConfigVariable.BridgeDeviceID = None 
            if(os.path.isfile(BridgeDeviceConfigVariable.DeviceSeurityObjectFile)):
                with open(BridgeDeviceConfigVariable.DeviceSeurityObjectFile) as DeviceSecurityObject:
                    SecurityObject = json.load(DeviceSecurityObject)
                    DeviceInfo = GetDeviceSecurityObject(SecurityObject)
                    BridgeDeviceConfigVariable.BridgeDeviceID = GetDeviceID(DeviceInfo)
                    BridgeDeviceConfigVariable.BridgeDevicePassword = GetDevicePassword(DeviceInfo)
                

            if(BridgeDeviceConfigVariable.BridgeDeviceID is not None):
                AccessToken = None
                if(BridgeDeviceConfigVariable.ACCESSTOKEN_MODE == 1):
                    Data = {
                        "DeviceID":BridgeDeviceConfigVariable.BridgeDeviceID,
                        "DevicePass":BridgeDeviceConfigVariable.BridgeDevicePassword,
                        "AuthorityUri" : AUTHORITY.replace("https://",""),
                        "ClientID":CLIENT_ID,
                        "ClientSecret":CLIENT_SECRET,
                        "ResourceID":INGEST_RESOURCE_ID
                    }

                    headers = {'Accept': '*/*'}
                    print(BridgeDeviceConfigVariable.LOGIN_TOKEN_ENDPOINT)
                    print(json.dumps(Data))
                    result = requests.post(BridgeDeviceConfigVariable.LOGIN_TOKEN_ENDPOINT,json=Data,headers=headers,verify=False, stream=False).json()
                    print(result["token"])
                    AccessToken = result["token"]
                else:
                    authority = AUTHORITY
                    debug_message = ("### AUTHORITY = " +  AUTHORITY)   
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                    # This is who you are. In this case you are the registered app called "Controller"
                    client_id = CLIENT_ID
                    debug_message = ("### CLIENT_ID = " + CLIENT_ID)   
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
                    # This is the password associated with the privileges of "Controller", which amount to calling the Ingest
                    client_secret = CLIENT_SECRET
                    debug_message = ("### CLIENT_SECRET = " + CLIENT_SECRET)   
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

                    # This is the api you are calling and need to be authorised for, so Ingest. This is not the same as an endpoint but it's like api//the_client_idof_ingest
                    resource_id = INGEST_RESOURCE_ID
                    debug_message = ("### INGEST_RESOURCE_ID = " + INGEST_RESOURCE_ID)   
                    DebugPrint(sys._getframe().f_code.co_name,debug_message,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

                    # Set up the client with your password and it will recognise you are a registered client entry
                    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

                    # Get the token. You can do this because Ingest has allowed apps to connect to it and in the Azure portal I've granted the Controller access to it.
                    result = app.acquire_token_for_client(resource_id)
                    #print("### RESULT ", result)
                    AccessToken = str(result['access_token'])   
                    #print("AccessToken:::::",AccessToken) 





                FirmwareVersion = "0.0"

                if(os.path.isfile(BridgeDeviceConfigVariable.FirmwareVersionFileName)):
                    with open(BridgeDeviceConfigVariable.FirmwareVersionFileName,"r") as version_f:
                        FirmwareVersion = version_f.readline().replace("\n","")
                        version_f.close()
                else:
                    with open(BridgeDeviceConfigVariable.FirmwareVersionFileName,"w") as version_f:
                        version_f.write(FirmwareVersion)
                        version_f.close()

                date = str(datetime.datetime.now())
                date_list = date.split(".")
                ReportTime = date_list[0]
                Uptime = str(stats["uptime"]).replace("days","").replace("day","").replace(" ","")
                print("uptime ",Uptime)
                uptime_list = Uptime.split(",")

                print("#####",uptime_list)
                days = 0  
                time_list = uptime_list[0].split(":")
                if(len(uptime_list) > 1):
                    days = int(uptime_list[0]) * 3600 * 24
                    time_list = uptime_list[1].split(":")



                hh = int(time_list[0]) * 3600
                mm = int(time_list[1]) * 60
                ss = float(time_list[2])
                Uptime = int(days + hh + mm + ss)

                CPU = [
                    {
                        "Temperature":stats["Temp BCPU"],
                        "Usage":[stats["CPU1"],stats["CPU2"]]
                    },
                    {
                        "Temperature":stats["Temp MCPU"],
                        "Usage":[stats["CPU3"],stats["CPU4"],stats["CPU5"],stats["CPU6"]]
                    },
                ]

                GPU = [
                    {
                        "Temperature":stats["Temp GPU"],
                        "Usage":stats["GPU"]
                    }
                ]

                Memory = round((int(stats["RAM"]) / 1024),1)
                SwapMemory = round((int(stats["SWAP"]) / 1024),1)

                #time.sleep(10000)

                Application = []
                ApplicationList = ["InferenceManager","EventManager","SceneMarkManager","SceneDataManager","FacilityManager","FallDownFightManager","SceneModeManager"]

                for item in ApplicationList:
                    if(os.path.isfile(str(item) + ".dat")):
                        with open(str(item) + ".dat","rb") as f:
                            data = pickle.load(f)
                            Application.append(data)
                            os.remove(item+".dat")
                    else:
                        NoneData = {
                            "ApplicationName": str(item), 
                            "Status": "E", 
                            "CheckTime": str(datetime.datetime.now())
                        }
                        Application.append(NoneData)        

                RtspStatus = []
                RtspList = ["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"]
                for item in RtspList:
                    if(os.path.isfile(str(item) + ".dat")):
                        with open(str(item) + ".dat","rb") as f:
                            data = pickle.load(f)
                            RtspStatus.append(data)
                            os.remove(str(item) + ".dat")
                    else:
                        NoneData = {
                            "NodeID": BridgeDeviceConfigVariable.BridgeDeviceID + "_" + item, 
                            "Status": "E", 
                            "Fps":0,
                            "FpsStatus":"E",
                            "CheckTime": str(datetime.datetime.now())
                        }
                        RtspStatus.append(NoneData)   

                
                Data = {
                    "DeviceID":BridgeDeviceConfigVariable.BridgeDeviceID,
                    "FirmwareVersion":FirmwareVersion,
                    "ReportTime" : ReportTime,
                    "Uptime":Uptime,
                    "Resources":{
                        "CPU":CPU,
                        "GPU":GPU,
                        "Memory":Memory,
                        "SwapMemory":SwapMemory,
                        "Application":Application,
                        "RtspStatus":RtspStatus
                    }
                }

                headers = {'Authorization': AccessToken,
                            'Accept': '*/*'}

                print(json.dumps(Data))
                answer = requests.post(API_ENDPOINT,json=Data, headers=headers, verify=False, stream=False)
                print(answer)
    except Exception as ex:
        print("ERROR MESSAGE :::", str(ex))
        pass


    os.kill(os.getpid(),signal.SIGKILL)


# Open the jtop
jetson = jtop()
# Attach a function where you can read the status of your jetson
jetson.attach(read_stats)

try:
    jetson.loop_for_ever()
except JtopException as e:
    print(e)
except KeyboardInterrupt:
    print("Closed with CTRL-C")
except IOError:
    print("I/O error")
