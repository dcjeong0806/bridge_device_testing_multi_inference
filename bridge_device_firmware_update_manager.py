import paramiko
import os
import subprocess
import time
import ftplib
import json
import shutil
import msal
import time
import requests
import sys
import urllib3
import signal
import datetime

import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from RestAPI import RestAPIPost, RstAPIGet, RestAPIGet_With_AccessToken, RestAPIPost_With_AccessToken_FirmWare
from Scenera_DeviceSecurityObject import GetDeviceSecurityObject, GetDeviceID,GetDevicePassword, GetNICELAEndPointAuthority, GetNICELAEndPointEndPoint
from bridge_device_peoplenet_config import VariableConfigClass, DebugPrint
from BridgeDeviceInfo import kill_bridge_device_process, kill_bridge_device_falldown_fight_process

BridgeDeviceConfigVariable = VariableConfigClass()

new_version = 0
rebootstatus = "rebootstatus.dat"

### LIVE
#API_ENDPOINT = "https://www.aiviewer.co.kr/noauth/GetFirmwareUpdate"

'''
AUTHORITY="https://login.microsoftonline.com/485790a2-56da-46e0-9dc8-bbdb221444f5"
CLIENT_ID="c2518e04-baca-4388-822c-d0a20b62617c"
CLIENT_SECRET="v5yRwNP~848QZ.242d3~Vg-6GPl5P5B7-S"
INGEST_RESOURCE_ID="api://0e0c2aef-941c-4b95-a17e-76c2e92a1616/.default"


if BridgeDeviceConfigVariable.DEBUG:
    ### DEV
    API_ENDPOINT = "https://tnmbss.scenera.live/noauth/GetFirmwareUpdate"
    AUTHORITY="https://login.microsoftonline.com/485790a2-56da-46e0-9dc8-bbdb221444f5"
    CLIENT_ID="c2518e04-baca-4388-822c-d0a20b62617c"
    CLIENT_SECRET="v5yRwNP~848QZ.242d3~Vg-6GPl5P5B7-S"
    INGEST_RESOURCE_ID="api://fd8edefb-abe4-418e-8185-365877eacd5d/.default"
'''

AUTHORITY = BridgeDeviceConfigVariable.AUTHORITY
CLIENT_ID = BridgeDeviceConfigVariable.CLIENT_ID
CLIENT_SECRET = BridgeDeviceConfigVariable.CLIENT_SECRET
INGEST_RESOURCE_ID = BridgeDeviceConfigVariable.INGEST_RESOURCE_ID
API_ENDPOINT = BridgeDeviceConfigVariable.FIRMWAREAPI_ENDPOINT

def check_bridge_device_falldown_fight_process(process_name):
    process_count = 0
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        #print(process)
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

def check_bridge_device_process(process_name):
    try:
        process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
        #print(process)
        process_list = str(process).split("\n")
        for item in process_list:
            if(item.endswith(process_name + ".pyc")):
                #if(process_name == BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager):
                pid_list = item.split(" ")
                print(pid_list)
                for pid in pid_list:
                    if(pid.isdecimal()):
                        command = "/bin/kill -9 " + pid
                        print(command)
                        os.system(command)
                        break

    except Exception as ex:
        print(str(ex))
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


def update_firmware_sftp():
    global new_version
    global API_ENDPOINT
#while(True):
    try:
        check_bridge_device_kill_process(BridgeDeviceConfigVariable.BridgeDeviceFirmwareUpdateManager)
        total , used, free = shutil.disk_usage("/")
        if((free / total) * 100 < 10):
            #print(total,free,free/total)
            kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            kill_bridge_device_falldown_fight_process(BridgeDeviceConfigVariable.BridgeDeviceFallDownFightManager)



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
            print("AccessToken:::::",AccessToken) 

        filesize = 0
        version = 0.0
        new_version = 0.0
        if(os.path.isfile(BridgeDeviceConfigVariable.FirmwareVersionFileName)):
            with open(BridgeDeviceConfigVariable.FirmwareVersionFileName,"r") as version_f:
                version_f = open(BridgeDeviceConfigVariable.FirmwareVersionFileName,"r")
                version = version_f.readline().replace("\n","")
                version_f.close()
        else:
            with open(BridgeDeviceConfigVariable.FirmwareVersionFileName,"w") as version_f:
                version_f.write(str(new_version))
                version_f.close()
        
        if(version == ""):
            version = 0.0
        #BridgeDeviceConfigVariable.BridgeDeviceID = "0000000c-606a-ba9f-8002-00000000191f"

        if(os.path.isdir(BridgeDeviceConfigVariable.FirmwareLocalPath) == False):
            os.mkdir(BridgeDeviceConfigVariable.FirmwareLocalPath)

        #print("#### REQUEST",request)
        #response = RstAPIGet(API_ENDPOINT,request)
        RebootResult = ""
        if(os.path.isfile(rebootstatus)):
            RebootResult = "Y"
            os.remove(rebootstatus)

        URL =  API_ENDPOINT + "?DeviceID=" + BridgeDeviceConfigVariable.BridgeDeviceID + "&CurrentVer=" + str(version) + "&RebootYn=" + RebootResult
        print(URL)
        response = RestAPIPost_With_AccessToken_FirmWare(URL,"",AccessToken)
        print("#### RESPONSE",response)
        version = str(response.get("CurrentVer"))
        new_version = str(response.get("NewVer"))
        host = response.get("FTPIP")
        port = int(response.get("FTPPort"))
        userid = response.get("FTPUser")
        passwd = response.get("FTPPW")
        filename = response.get("File")
        filesize = response.get("FileSize")
        rebootyn = response.get("RebootYn")
        
        print("## VERSION", float(version) , float(new_version))

        if(float(version) > -1 and float(version) < float(new_version)):
            transport = paramiko.transport.Transport(host,port)
            print(transport.getpeername())
            transport.connect(username=userid,password=passwd)

            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(BridgeDeviceConfigVariable.FirmwareServerPath + filename, BridgeDeviceConfigVariable.FirmwareLocalPath + filename)

            print("download is done")
            command = "/bin/tar -xzvf " + BridgeDeviceConfigVariable.FirmwareLocalPath + filename + " -C " + BridgeDeviceConfigVariable.FirmwareLocalPath
            os.system(command)
            print("unzip is done")

            kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)
            if os.path.isfile(BridgeDeviceConfigVariable.FirmwareLocalPath + "falldown_fight_detector"):
                kill_bridge_device_falldown_fight_process(BridgeDeviceConfigVariable.BridgeDeviceFallDownFightManager)

            command = "/bin/rm -rf " + BridgeDeviceConfigVariable.FirmwareLocalPath + filename
            os.system(command)
            print("Removed....")

            if os.path.isfile(BridgeDeviceConfigVariable.FirmwareLocalPath + "falldown_fight_detector"):
                command = "/bin/chmod a+x " + BridgeDeviceConfigVariable.FirmwareLocalPath + "falldown_fight_detector " 
                os.system(command)
                print("process is restarted...")

            command = "/bin/mv " + BridgeDeviceConfigVariable.FirmwareLocalPath + "* " + BridgeDeviceConfigVariable.FirmwareBridgeDevicePath
            os.system(command)
            print("process is restarted...")

            with open(BridgeDeviceConfigVariable.FirmwareVersionFileName,"w") as version_f:
                version_f.write(str(new_version))
                version_f.close()
            
            sftp.close()
            transport.close()
            
            if(rebootyn == "Y"):
                with open(rebootstatus,"w") as rebootstatus_f:
                    rebootstatus_f.write("Y")
                    rebootstatus_f.close()
                os.system('sudo init 6')

            kill_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceFirmwareUpdateManager)
        else:
            print("current version is new !!!")
            if(rebootyn == "Y"):
                with open(rebootstatus,"w") as rebootstatus_f:
                    rebootstatus_f.write("Y")
                    rebootstatus_f.close()
                os.system('sudo init 6')
        os.kill(os.getpid(),signal.SIGKILL)
    except Exception as ex:
        print("Error Message :::" + str(ex))
        os.kill(os.getpid(),signal.SIGKILL)

    #time.sleep(BridgeDeviceConfigVariable.FirmwareUpdateTime)


def running_device_status_manager():
    kill_bridge_device_process("bridge_device_peoplenet_device_status_manager")
    os.system("python3 bridge_device_peoplenet_device_status_manager.pyc")
def LoadBridgeDeviceSecurityObject():
    global BridgeDeviceConfigVariable
    #if(check_bridge_device_process(BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager) > 1):
    #    print("==========================================")
    #    print("there is same process running already. process is about to be terminated.")
    #    print("==========================================")
    #    sys.exit()

    if(os.path.isfile(BridgeDeviceConfigVariable.DeviceSeurityObjectFile)):
        with open(BridgeDeviceConfigVariable.DeviceSeurityObjectFile) as DeviceSecurityObject:
            SecurityObject = json.load(DeviceSecurityObject)
            DeviceInfo = GetDeviceSecurityObject(SecurityObject)
            BridgeDeviceConfigVariable.BridgeDeviceID = GetDeviceID(DeviceInfo)
            BridgeDeviceConfigVariable.BridgeDevicePassword = GetDevicePassword(DeviceInfo)
            NICELAEndPoint = GetNICELAEndPointEndPoint(DeviceInfo)
            NICELAAuthorty = GetNICELAEndPointAuthority(DeviceInfo)
            #print(BridgeDeviceConfigVariable.BridgeDeviceID,NICELAEndPoint,NICELAAuthorty, "is called...")
            #BridgeDeviceConfigVariable.DebugLog("","ErrorMessage ::: " + BridgeDeviceConfigVariable.BridgeDeviceID,BridgeDeviceConfigVariable.DEBUG,BridgeDeviceConfigVariable.BridgeDeviceGetSceneModeManager)

            #ManagementInfo = GetManagementObject(NICELAAuthorty, BridgeDeviceID, NICELAEndPoint)
            if(BridgeDeviceConfigVariable.BridgeDeviceID):
                #running_device_status_manager_thread = threading.Thread(target=running_device_status_manager,args=())
                #running_device_status_manager_thread.daemon = False
                #running_device_status_manager_thread.start()
                update_firmware_sftp()


if(BridgeDeviceConfigVariable.BridgeDeviceID):
    pass
else:
    time.sleep(5)
    LoadBridgeDeviceSecurityObject()