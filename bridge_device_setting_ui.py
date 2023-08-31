import sys
import os
import subprocess
import pickle
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import *
from netaddr import IPAddress
import socket
import fcntl
import struct
import re
import yaml


#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("bridge_device_setting_ui.ui")[0]

status_scenemode = None
status_inference = None
status_event = None
status_facility = None
status_scenemark = None
status_scenedata = None
status_falldownfight = None
status_firesmoke = None
camera_01 = None
camera_02 = None
camera_03 = None
camera_04 = None
camera_05 = None
camera_06 = None
camera_07 = None
camera_08 = None
camera_09 = None
camera_10 = None

BridgeDeviceInferenceManager = "bridge_device_peoplenet_inferencing_manager"
BridgeDeviceGetSceneModeManager = "bridge_device_peoplenet_scenemode_manager"
BridgeDeviceEventManager = "bridge_device_peoplenet_event_manager"
BridgeDeviceEventFacilityManager = "bridge_device_peoplenet_event_facility_manager"
BridgeDeviceSceneMarkManager = "bridge_device_peoplenet_scenemark_manager"
BridgeDeviceSceneDataManager = "bridge_device_peoplenet_scenedata_manager"
BridgeDeviceFallDownFightManager = "falldown_fight_detector"
BridgeDeviceFireManager = "fire_smoke_detector"

DeviceSecurityObject_DEV_FILE = "/home/ghosti/bridge_device/DeviceSecurityObject_DEV.json"
DeviceSecurityObject_FILE = "/home/ghosti/bridge_device/DeviceSecurityObject.json"
bridge_mode_file = "/home/ghosti/bridge_device/bridge_mode.dat"
debug_mode_file = "/home/ghosti/bridge_device/debug_mode.dat"
network_setting_file = "/etc/netplan/01-netcfg.yaml"
config_file = "/home/ghosti/bridge_device/config.json"

lan1_dhcp = False
lan2_dhcp = False

class Worker(QThread):

    def check_bridge_device_falldown_fight_process_status(self,process_name):
        process_count = 0
        try:
            process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
            #print(process)
            process_list = str(process).split("\n")
            for item in process_list:
                if(item.endswith("./" + process_name)):    
                    process_count = process_count + 1
                    #print(item + " is running...")
            return process_count
        except Exception as ex:
            print(str(ex))
            return process_count
            pass

    def check_bridge_device_process(self,process_name):
        process_count = 0
        try:
            process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
            process_list = str(process).split("\n")
            #print("PROCESS LIST :::",process_list)
            for item in process_list:
                if(item.endswith(process_name + ".pyc")):
                    process_count = process_count + 1

            #print(process_name,process_count)
            return process_count
        except Exception as ex:
            return process_count
            pass

    def run(self):
        while True:
            try:
                RtspList = ["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"]
                i = 0
                for item in RtspList:
                    if(os.path.isfile(str(item) + ".dat")):
                        with open(str(item) + ".dat","rb") as f:
                            data = pickle.load(f)
                            if(i == 0):
                                camera_01.setText(str(data["Fps"]))
                            elif(i == 1):
                                camera_02.setText(str(data["Fps"]))
                            elif(i == 2):
                                camera_03.setText(str(data["Fps"]))
                            elif(i == 3):
                                camera_04.setText(str(data["Fps"]))
                            elif(i == 4):
                                camera_05.setText(str(data["Fps"]))
                            elif(i == 5):
                                camera_06.setText(str(data["Fps"]))
                            elif(i == 6):
                                camera_07.setText(str(data["Fps"]))
                            elif(i == 7):
                                camera_08.setText(str(data["Fps"]))
                            elif(i == 8):
                                camera_09.setText(str(data["Fps"]))
                            elif(i == 9):
                                camera_10.setText(str(data["Fps"]))
                    i = i + 1
                
                # if(self.check_bridge_device_falldown_fight_process_status(BridgeDeviceFallDownFightManager)):
                #     status_falldownfight.setText("On")
                # else:
                #     status_falldownfight.setText("Off")

                # if(self.check_bridge_device_falldown_fight_process_status(BridgeDeviceFireManager)):
                #     status_firesmoke.setText("On")
                # else:
                #     status_firesmoke.setText("Off")

                if(self.check_bridge_device_process(BridgeDeviceGetSceneModeManager)):
                    status_scenemode.setText("On")
                else:
                    status_scenemode.setText("Off")

                if(self.check_bridge_device_process(BridgeDeviceInferenceManager)):
                    status_inference.setText("On")
                else:
                    status_inference.setText("Off")

                if(self.check_bridge_device_process(BridgeDeviceEventManager)):
                    status_event.setText("On")
                else:
                    status_event.setText("Off")

                if(self.check_bridge_device_process(BridgeDeviceEventFacilityManager)):
                    status_facility.setText("On")
                else:
                    status_facility.setText("Off")
                    
                if(self.check_bridge_device_process(BridgeDeviceSceneMarkManager)):
                    status_scenemark.setText("On")
                else:
                    status_scenemark.setText("Off")

                if(self.check_bridge_device_process(BridgeDeviceSceneDataManager)):
                    status_scenedata.setText("On")
                else:
                    status_scenedata.setText("Off")     
            except Exception as ex:
                print("1111 ERROR MESSAGE ::: ", str(ex))




#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :

    def check_bridge_device_process(self,process_name):
        process_count = 0
        try:
            process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
            process_list = str(process).split("\n")
            #print("PROCESS LIST :::",process_list)
            for item in process_list:
                if(item.endswith(process_name + ".pyc")):
                    process_count = process_count + 1

            #print(process_name,process_count)
            return process_count
        except Exception as ex:
            return process_count
            pass
    def __init__(self) :
        super().__init__()
        self.setupUi(self)


        if(self.check_bridge_device_process("bridge_device_setting_ui") > 1):
            print("==========================================")
            print("there is same process running already. process is about to be terminated.")
            print("==========================================")
            sys.exit()

        global lan1_dhcp
        global lan2_dhcp
        global status_scenemode
        global status_inference
        global status_event
        global status_facility
        global status_scenemark
        global status_scenedata
        global status_falldownfight
        global status_firesmoke
        global camera_01
        global camera_02
        global camera_03
        global camera_04
        global camera_05
        global camera_06
        global camera_07
        global camera_08
        global camera_09
        global camera_10


        global BridgeDeviceInferenceManager 
        global BridgeDeviceGetSceneModeManager 
        global BridgeDeviceEventManager 
        global BridgeDeviceEventFacilityManager 
        global BridgeDeviceSceneMarkManager 
        global BridgeDeviceSceneDataManager 
        global BridgeDeviceFallDownFightManager
        global BridgeDeviceFireManager


        global DeviceSecurityObject_DEV_FILE
        global DeviceSecurityObject_FILE
        global bridge_mode_file
        global debug_mode_file
        global network_setting_file
        global config_file


        status_scenemode = self.status_scenemode
        status_inference = self.status_inference
        status_event = self.status_event
        status_facility = self.status_facility
        status_scenemark = self.status_scenemark
        status_scenedata = self.status_scenedata
        #status_falldownfight = self.status_falldownfight
        #status_firesmoke = self.status_firesmoke

        camera_01 = self.camera_01
        camera_02 = self.camera_02
        camera_03 = self.camera_03
        camera_04 = self.camera_04
        camera_05 = self.camera_05
        camera_06 = self.camera_06
        camera_07 = self.camera_07
        camera_08 = self.camera_08
        camera_09 = self.camera_09
        camera_10 = self.camera_10

        self.locate_window_center()
        self.read_current_setting1()
        self.load_test_operation_mode_deviceid()
        #self.load_test_operation_mode_deviceid_test()
        self.BtnSaveSetting.clicked.connect(self.savesetting)
        self.chk_display_on.stateChanged.connect(self.change_display_mode)
        self.btnSaveDeviceID.clicked.connect(self.savedeviceid)
        self.btnPlayVod.clicked.connect(self.playvod)
        #self.operation_mode_01.clicked.connect(self.load_test_operation_mode_deviceid)
        #self.operation_mode_02.clicked.connect(self.load_test_operation_mode_deviceid)

        
        self.groupbox1.setVisible(False)
        self.groupbox2.setVisible(False)
        #self.groupbox3.setVisible(False)
        #self.groupbox4.setVisible(False)
        self.groupbox6.setVisible(False)
        self.groupbox7.setVisible(False)
        self.BtnSaveSetting.setVisible(False)
        self.txtDeviceID.setVisible(False)
        self.txtDevicePassword.setVisible(False)
        self.btnSaveDeviceID.setVisible(False)

        self.groupbox5.setTitle("")
        self.btnLogin.setVisible(True)
        self.txtPassword.setVisible(True)    
        self.txtPassword.setEchoMode(QLineEdit.Password)
        self.txtPassword.returnPressed.connect(self.lockthescreen)



        self.btnLogin.clicked.connect(self.lockthescreen)    

        self.worker = Worker(self)
        self.worker.start()




    def lockthescreen(self):
        if(self.txtPassword.text() == "ghosti"):
            self.groupbox1.setVisible(True)
            self.groupbox2.setVisible(True)
            #self.groupbox3.setVisible(True)
            #self.groupbox4.setVisible(True)
            self.groupbox6.setVisible(True)
            self.groupbox7.setVisible(True)
            self.BtnSaveSetting.setVisible(True)
            self.txtDeviceID.setVisible(True)
            self.txtDevicePassword.setVisible(True)
            self.btnSaveDeviceID.setVisible(True)

            self.groupbox5.setTitle("DeviceSecurityObject")
            self.btnLogin.setVisible(False)
            self.txtPassword.setVisible(False)  

            RtspList = ["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"]
            for item in RtspList:
                if(os.path.isfile(str(item) + ".dat")):
                    os.remove(str(item) + ".dat")
        else:
            QMessageBox.question(self, 'Alert', 'Please check password!!!', QMessageBox.Ok)


    # def load_test_operation_mode_deviceid(self):
    #     if(self.operation_mode_01.isChecked()):
    #         if(os.path.isfile(DeviceSecurityObject_DEV_FILE)):
    #             with open(DeviceSecurityObject_DEV_FILE) as test_f:
    #                 test = json.load(test_f)
    #                 self.txtDeviceID.setText(test["DeviceID"])
    #                 self.txtDevicePassword.setText(test["DevicePassword"])
    #                 test_f.close()

    #     elif(self.operation_mode_02.isChecked()):
    #         if(os.path.isfile(DeviceSecurityObject_FILE)):
    #             with open(DeviceSecurityObject_FILE) as operation_f:
    #                 operation = json.load(operation_f)
    #                 self.txtDeviceID.setText(operation["DeviceID"])
    #                 self.txtDevicePassword.setText(operation["DevicePassword"])
    #                 operation_f.close()
    def load_test_operation_mode_deviceid(self):
        if(os.path.isfile(DeviceSecurityObject_FILE)):
            with open(DeviceSecurityObject_FILE) as operation_f:
                operation = json.load(operation_f)
                print(operation)
                self.txtDeviceID.setText(operation["DeviceID"])
                self.txtDevicePassword.setText(operation["DevicePassword"])
                operation_f.close()
    def load_test_operation_mode_deviceid_test(self):
        if(os.path.isfile(DeviceSecurityObject_DEV_FILE)):
            with open(DeviceSecurityObject_DEV_FILE) as test_f:
                test = json.load(test_f)
                self.txtDeviceID.setText(test["DeviceID"])
                self.txtDevicePassword.setText(test["DevicePassword"])
                test_f.close()

    def savedeviceid(self):
        deviceid = self.txtDeviceID.text()
        password = self.txtDevicePassword.text()

        if(deviceid and password):
            data = {'DeviceCertificate': ['MIICsjCCARqgAwIBAgIGAYhnAu0tMA0GCSqGSIb3DQEBDQUAMC8xLTArBgNVBAMMJDAwMDAwMDAwLTVjZGQtMjgwYi04MDAyLTAwMDAwMDAwMDAwMDAgFw0yMzA1MjkxMDE3MDVaGA8yMTIzMDUwNTEwMTcwNVowLzEtMCsGA1UEAwwkMDAwMDAwMDAtNjQ3NC03YmEwLTgwMDItMDAwMDAwMDAwMDBiMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEB/TQm6BCEz93CVhF422GYJ/z9f6dy0kiS/aVjClpNzSNr++fCE1MQAYXJV4UzANCjzstxMsB4tLLfyoR9sKyXaMdMBswDgYDVR0PAQH/BAQDAgOYMAkGA1UdEwQCMAAwDQYJKoZIhvcNAQENBQADggGBADrOpfbCeYEkUFm//KVp1+QVrdCPIUQuKl/N86x3Qyf7Xvjx867p8xi0bHWSdrx/ve0hJzg+c4YzVzRJxdFyPHoawDNy0xkdGpiYHcJlz11lxGhVt7zC0vmcTvIzFYu2jCh6zpjtsnjv5oC0co1WeYJXYlalsh5v3AILbAdw2go4DkiTsgk1BkDnaSFeYkfN0nbw+d3TF0vbfVX8yU+sBEdVgdJYPIOIWIWAdd5VEYhpm+S7Uw6rr6tb4W+8VHLhGUHKjC8ogNWhl9vkvgXUuDBMnNYWqz56GjxVpHJyPmL+gEKlKRKSBkZqx7AJRRl7AGnsEdiJIog8aciwL8FEP0f4hR/GznjkEaDxkkcPXWPorzRP/EM6BdKqYVsrM8/d83aTYDS0JaVY3pDqUoXv4BtgIC9jx5RrIxnnHT7EpUuuY057gDVLgm0ntBY6/MI4tc0bHhY1vgXoF42o0TzL4IP4+4TBoLYmjwOa72H4xSKcUJeOJiXwBWCP1oE5wdKfnw==', 
                                    'MIIEKzCCApOgAwIBAgIGAYXNXFd4MA0GCSqGSIb3DQEBDQUAMFcxCzAJBgNVBAYTAkpQMRswGQYDVQQKDBJOSUNFIExpY2Vuc2luZyBMTEMxKzApBgNVBAMMIk5JQ0UgTEEgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwIBcNMjMwMTIwMDQwNzM5WhgPMjEyMDEyMzEwODAwMDBaMC8xLTArBgNVBAMTJDAwMDAwMDAwLTVjZGQtMjgwYi04MDAyLTAwMDAwMDAwMDAwMDCCAaIwDQYJKoZIhvcNAQEBBQADggGPADCCAYoCggGBAMYVgLQPb8OHcB7dAr9c72s0iMJOhqn7r65Ollg5y/NAfIdvR9z9NC9O4M+69TzklPuyLZc7fUFan9E3kUfAAX9PnGzkFcXbi8Fmjozu7AU/3EjsOOFS8WILvGo+nEXmnKf/7XmGYoMm+iKP2Lc8IJQqBcz5Cs6wEJnGVGPpkiRD3nqa947wIhIVSkpmjo6X7VHWqiNy7iD+Ja+uHW+fwBKwE1BSS9jmJQp4iJgCUcrTe9/mEByfKx3zVhNd9AnpWdiEXZTCYPTfMjTKawV8GfozFiLIvTW0+jysCh6Dv1tbEwvo18p4sktD31CZ70122iGJ4IMh8nB7j8rAZst6mXwB3O/ZXw+Ow8nooWnPcyTe38CUS+VcNk5ONUAmoX+elBIh29nl34RZ39Buvt4mJzCrlcROpPFPyKDcLNnF+TAeFbJk2O+MbJ5B1RtCyku46/Mg/l8jDUKCKq9OnMJ5ugQqqmDSKGGLklYGt8PdhY+pKZgA+Lt5dwwqF8yTDDN0vQIDAQABoyMwITAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBvjANBgkqhkiG9w0BAQ0FAAOCAYEAa75j1xPCMW0Dnq+DH/9x0AgXKtJIu2TEPlW178wPaJNnXo1cMmF/fuEyKMMFt7B4O28R11TyrRhWOZ5cz14hSVuCqHDubpfJIKCjAO95ZGdlBv9E6XrPIo+zfAdDn+O5GaJ6glbxhQwu45Ovn047z5/XQzD5nFTCOf5NOtsyhK/SXuqQp7xA5219bg9DCwCc4AeVZqYx2mDPGE7urjEMVDlrznHaYIHPGraXCpDyQ963Tl44nKF4GsMJpiGripbOz33gy0noeZED5zso0y7N/kkIKdI1Cvbc79fGFXwCrV7DLRMNn0rCZ3LVqYyXqDTOJ8MRtj6VdIw9+7/nD7IR7zW9Ft72BFvvhRRaOjU2kqe427DrC7L94IvW5XWJK5RFBoswL1YQPPXky2W4gyIYx5UA/ND4kvLYEjTgejv44C/FYiVgS+1+5e/ieuDV9O9/i+ThYwCLiRaU2Vny4mFm+/flUaJ1fXrHkrHcdDbfxf8VNAJw23NDFyqCnroeZF/n'],
                    'DevicePassword': password,
                    'Version': '1.0',
                    'DeviceID': deviceid,
                    'DevicePrivateKey': {
                    'EncryptedKey': 'eyJhbGciOiJFQ0RILUVTK0EyNTZLVyIsImVuYyI6IkEyNTZHQ00iLCJlcGsiOnsia3R5IjoiRUMiLCJ4Ijoia1VsQ2pCRGJKX2h6eGsxWlE1c3c3YmdMcC1VNVF6Q1YyTjhGSzBUalN6MCIsInkiOiI5R2Nwd3BRMGl4V0lVMWljU1hMWDBsS081cnFqMWdTeWx1cFJOYjlQbEJRIiwiY3J2IjoiUC0yNTYifX0.7mVfbdlbQxIGxXZiYhknkU1XenuxsRajppIIrfGcHJUO0vxFHNEgrw.acCEljrs8H-tKnNL.0hGVj9Bs3MOX0ixy1-hpATEhgSkuDJpFgCe3cgUuh0_Zsml965AUX_DpOs-1ao6k3Css72rp347_YrUP8XmqPPQOrZyrSDXY-syfrpwi_xuAKtq6UaqW64ieT-k-wL4BTfsVmK37hZoedekU4C-0f2uOWQE5CLmSQwFpJIRUJPX19LwDk7h8wp3jVSaBswpYT3d59ubDbLaJdMzwLw_CL4FqQA8OxgpMr1pv55AD6J0.bS8tdKMDN0KSJcfwXHaUBQ',
                    'EncryptionKeyID': '00000003-6474-7b3f-8002-000000000000-00000001'
                    }, 
                    'AllowedTLSRootCertificates': ['MIIDxTCCAq2gAwIBAgIBADANBgkqhkiG9w0BAQsFADCBgzELMAkGA1UEBhMCVVMxEDAOBgNVBAgTB0FyaXpvbmExEzARBgNVBAcTClNjb3R0c2RhbGUxGjAYBgNVBAoTEUdvRGFkZHkuY29tLCBJbmMuMTEwLwYDVQQDEyhHbyBEYWRkeSBSb290IENlcnRpZmljYXRlIEF1dGhvcml0eSAtIEcyMB4XDTA5MDkwMTAwMDAwMFoXDTM3MTIzMTIzNTk1OVowgYMxCzAJBgNVBAYTAlVTMRAwDgYDVQQIEwdBcml6b25hMRMwEQYDVQQHEwpTY290dHNkYWxlMRowGAYDVQQKExFHb0RhZGR5LmNvbSwgSW5jLjExMC8GA1UEAxMoR28gRGFkZHkgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgLSBHMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAL9xYgjx+lk09xvJGKP3gElY6SKDE6bFIEMBO4Tx5oVJnyfq9oQbTqC023CYxzIBsQU+B07u9PpPL1kwIuerGVZr4oAH/PMWdYA5UXvl+TW2dE6pjYIT5LY/qQOD+qK+ihVqf94Lw7YZFAXK6sOoBJQ7RnwyDfMAZiLIjWltNowRGLfTshxgtDj6AozO091GB94KPutdfMh8+7ArU6SSYmlRJQVhGkSBjCypQ5Yj36w6gZoOKcUcqeldHraenjAKOc7xiID7S13MMuyFYkMlNAJWJwGRtDtwKj9useiciAF9n9T521NtYJ2/LOdYq7hfRvzOxBsDPAnrSTFcaUaz4EcCAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYEFDqahQcQZyi27/a9BUFuIMGU2g/eMA0GCSqGSIb3DQEBCwUAA4IBAQCZ21151fmXWWcDYfF+OwYxdS2hII5PZYe096acvNjpL9DbWu7PdIxztDhC2gV7+AJ1uP2lsdeu9tfeE8tTEH6KRtGX+rcuKxGrkLAngPnon1rpN5+r5N9ss4UXnT3ZJE95kTXWXwTrgIOrmgIttRD02JDHBHNA7XIloKmf7J6raBKZV8aPEjoJpL1E/QYVN8Gb5DKj7Tjo2GTzLH4U/ALqn83/B2gX2yKQOC16jdFU8WnjXzPKej17CuPKf1855eJ1usV2GDPOLPAvTK33sefOT6jEm0pUBsV/fdUID+Ic/n4XuKxe9tQWskMJDE32p2u0mYRlynqI4uJEvlz36hz1', 
                                                    'MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBhMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBDQTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVTMRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5jb20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsBCSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7PT19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAOBgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbRTLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUwDQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/EsrhMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJFPnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0lsYSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQkCAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4='], 
                                                    'NICELARootCertificate': ['MIIEnTCCAwWgAwIBAgIQR9T5iX2mR6yDqA4CSNS3BDANBgkqhkiG9w0BAQsFADBXMQswCQYDVQQGEwJKUDEbMBkGA1UEChMSTklDRSBMaWNlbnNpbmcgTExDMSswKQYDVQQDEyJOSUNFIExBIFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5MCAXDTIyMTIxMDAwNTQxNloYDzIxMjIxMjEwMDEwNDE2WjBXMQswCQYDVQQGEwJKUDEbMBkGA1UEChMSTklDRSBMaWNlbnNpbmcgTExDMSswKQYDVQQDEyJOSUNFIExBIFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAwOfBRcShdRp2GhI9vxAJ2KlXiBw2gpR7SoMq9TKxGNbbB46AW6b1fymHJhGin1PlWVv9brVrA/XP9VLUAEGRPHU/LvuPWM/IsUjtEfVN/O1VIN/ABwFmXdAJCO+kGGqz9nPBsncmytEcKnEzU2+RD9f/mwoxJVWGv/p48IlYRdDVAQE2t4nrNP/A3DJxKgluDd3FIqxdhUDI5pQ/dGGbVoUcombP2oi2Iv5+2idFCjoTxSYdvKIzzQusNCGDNq9ln0SLaeMugHt+Mv5/tW5asPBGonYPMt1gwI6a2iyAOj+f/XM00rI96EhJgg7S554B94zxW/OdLuNtkpyqYdcI2qxShylBzPXCV+2uHfSacen5fs38muPFWvwCS0wCYHtzI5fsx9Ivba3DLugPxNByPsUaNeZoNqN+05ulRBWjPVbkFJTqbyKH+1SSzqm4dKQdeweOU+kFIfSbHdK16Kg3S0Nqg+PnSFN8dK0eGOW/pfmeRKKtuXr0xljxVDLH1kUFAgMBAAGjYzBhMA4GA1UdDwEB/wQEAwIBBjAPBgNVHRMBAf8EBTADAQH/MB8GA1UdIwQYMBaAFBnXm5gqEeu45Yq0cnO300bBkbS/MB0GA1UdDgQWBBQZ15uYKhHruOWKtHJzt9NGwZG0vzANBgkqhkiG9w0BAQsFAAOCAYEAcYK4gsa9DLCtq8XXzqLIV9F4GGnMZy4auhZGqnzGcaRUPfPBQ/mVNhceBOByHxRTHx4bKNiu6WkB8CMblguW4UsR4mP0ar3COFggSM6B12ypkJrEF35s1L/TEIPIZ6UzbmKO2fm4+E/t8qDgcYwV7CmAzA+0gHB5iMLw81EIdayVEJRTZoIDmnAdJnmn2wx0B3xK2Ct2a4QmcnrZM5sQmcNJ8iI8rknYE0iupPY2L6L1RWzK3dXSd35DLMVwJ4veb1sF6B0brfpEWX8NHGSjP8XuuBtguxftdgFljgEHWFqpMKg3CPm7eZQxkGA5cM31d4xM+GZ5JJB9WvEQLxNEeB90IyU7vfneYgpyRmC9vGXgVk8z3OeNwmZI6b0XWONC8s7kn2Cg7RrJ2sDe1h8uSO7XkCU9fPgYWeSBhFbhJNhkDgDoNOqNsAthxsnTsQwcM75U3bFMIfabOFr6isw8Kg25EYplRAPPSX/XLswtPR4HOsrPyma1KdUx/TiWwopN'], 
                                                    'NICELAEndPoint': 
                                                        {'EndPointID': '00000000-5cdd-280b-8002-000000000000',
                                                            'Scheme': [{'Role': 'Client',
                                                                        'Authority': 'nicela-japan-nodejs.scenera.live:443',
                                                                        'AccessToken': 'eyJhbGciOiJSUzUxMiIsIng1YyI6WyJNSUlFS3pDQ0FwT2dBd0lCQWdJR0FZWE5YRmQ0TUEwR0NTcUdTSWIzRFFFQkRRVUFNRmN4Q3pBSkJnTlZCQVlUQWtwUU1Sc3dHUVlEVlFRS0RCSk9TVU5GSUV4cFkyVnVjMmx1WnlCTVRFTXhLekFwQmdOVkJBTU1JazVKUTBVZ1RFRWdVbTl2ZENCRFpYSjBhV1pwWTJGMFpTQkJkWFJvYjNKcGRIa3dJQmNOTWpNd01USXdNRFF3TnpNNVdoZ1BNakV5TURFeU16RXdPREF3TURCYU1DOHhMVEFyQmdOVkJBTVRKREF3TURBd01EQXdMVFZqWkdRdE1qZ3dZaTA0TURBeUxUQXdNREF3TURBd01EQXdNRENDQWFJd0RRWUpLb1pJaHZjTkFRRUJCUUFEZ2dHUEFEQ0NBWW9DZ2dHQkFNWVZnTFFQYjhPSGNCN2RBcjljNzJzMGlNSk9ocW43cjY1T2xsZzV5L05BZklkdlI5ejlOQzlPNE0rNjlUemtsUHV5TFpjN2ZVRmFuOUUza1VmQUFYOVBuR3prRmNYYmk4Rm1qb3p1N0FVLzNFanNPT0ZTOFdJTHZHbytuRVhtbktmLzdYbUdZb01tK2lLUDJMYzhJSlFxQmN6NUNzNndFSm5HVkdQcGtpUkQzbnFhOTQ3d0loSVZTa3Btam82WDdWSFdxaU55N2lEK0phK3VIVytmd0JLd0UxQlNTOWptSlFwNGlKZ0NVY3JUZTkvbUVCeWZLeDN6VmhOZDlBbnBXZGlFWFpUQ1lQVGZNalRLYXdWOEdmb3pGaUxJdlRXMCtqeXNDaDZEdjF0YkV3dm8xOHA0c2t0RDMxQ1o3MDEyMmlHSjRJTWg4bkI3ajhyQVpzdDZtWHdCM08vWlh3K093OG5vb1duUGN5VGUzOENVUytWY05rNU9OVUFtb1grZWxCSWgyOW5sMzRSWjM5QnV2dDRtSnpDcmxjUk9wUEZQeUtEY0xObkYrVEFlRmJKazJPK01iSjVCMVJ0Q3lrdTQ2L01nL2w4akRVS0NLcTlPbk1KNXVnUXFxbURTS0dHTGtsWUd0OFBkaFkrcEtaZ0ErTHQ1ZHd3cUY4eVRERE4wdlFJREFRQUJveU13SVRBUEJnTlZIUk1CQWY4RUJUQURBUUgvTUE0R0ExVWREd0VCL3dRRUF3SUJ2akFOQmdrcWhraUc5dzBCQVEwRkFBT0NBWUVBYTc1ajF4UENNVzBEbnErREgvOXgwQWdYS3RKSXUyVEVQbFcxNzh3UGFKTm5YbzFjTW1GL2Z1RXlLTU1GdDdCNE8yOFIxMVR5clJoV09aNWN6MTRoU1Z1Q3FIRHVicGZKSUtDakFPOTVaR2RsQnY5RTZYclBJbyt6ZkFkRG4rTzVHYUo2Z2xieGhRd3U0NU92bjA0N3o1L1hRekQ1bkZUQ09mNU5PdHN5aEsvU1h1cVFwN3hBNTIxOWJnOURDd0NjNEFlVlpxWXgybURQR0U3dXJqRU1WRGxyem5IYVlJSFBHcmFYQ3BEeVE5NjNUbDQ0bktGNEdzTUpwaUdyaXBiT3ozM2d5MG5vZVpFRDV6c28weTdOL2trSUtkSTFDdmJjNzlmR0ZYd0NyVjdETFJNTm4wckNaM0xWcVl5WHFEVE9KOE1SdGo2VmRJdzkrNy9uRDdJUjd6VzlGdDcyQkZ2dmhSUmFPalUya3FlNDI3RHJDN0w5NEl2VzVYV0pLNVJGQm9zd0wxWVFQUFhreTJXNGd5SVl4NVVBL05ENGt2TFlFalRnZWp2NDRDL0ZZaVZnUysxKzVlL2lldURWOU85L2krVGhZd0NMaVJhVTJWbnk0bUZtKy9mbFVhSjFmWHJIa3JIY2REYmZ4ZjhWTkFKdzIzTkRGeXFDbnJvZVpGL24iXX0.eyJWZXJzaW9uIjoiMS4wIiwiRW5mb3JjZUVuY3J5cHRpb24iOnRydWUsImlzcyI6IjAwMDAwMDAwLTVjZGQtMjgwYi04MDAyLTAwMDAwMDAwMDAwMCIsInN1YiI6IjAwMDAwMDAwLTY0NzQtN2JhMC04MDAyLTAwMDAwMDAwMDAwYiIsImF1ZCI6IjAwMDAwMDAwLTVjZGQtMjgwYi04MDAzLTAwMDAwMDAwMDAwMCIsImV4cCI6IjIwMzMtMDUtMjlUMTA6MTc6MDYuNjQwWiIsIm5iZiI6IjIwMjMtMDUtMjlUMTA6MTc6MDYuNjQwWiIsImlhdCI6IjIwMjMtMDUtMjlUMTA6MTc6MDYuNjQwWiIsImp0aSI6IjAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA0OTYiLCJQZXJtaXNzaW9ucyI6WyJNYW5hZ2VtZW50Il19.jEmgzpQWVpYSD2lkJ7eHV7WlLLgaaPYXst5GgyGEm0nSAm9lESVNxvi09ij2PAArnkgwIayWLI-GbOs2DHzx46eijpZ33jCPhD2kpgiNBgUh12EY59oOnpOzn-5GTubS-dlGJJBiMnWSbhwTXYZyICr70oPcRbmME2HnYt6NI3PdNLuJ0UOY3g1ugQxkuIVKpsoLKcaK-XiJzt6vg3_zrYjuKGwdhXwdvec_PZbtBX5AHFn628EiN2UbUubXBxkAvgn7vZFVMfMWkhV9id-ol1A7hPqMyJM8oC5hjJBSR09p5gVeAQS1IXl6bHWSzl082FBg_6J-dUm68UpJSO9bn86InBJixFes-9fZKYY3TeRyl1bFGmWhLHIT8azuanxnUvgoO2pLQngE8NZ3YyMhLS8fvLms5m0xwuWfo8Dxaeuk40H1RrXYjVEIqf7IIl6p9RXDqtJk2VsluI8J4yB-ki9YXS18tIr3Ws7V09FXgxg3s-hzT-b42Yp0Tihqyt_P', 
                                                                        'Protocol': 'WebAPI'}],
                                                                        'APIVersion': '1.0'}
            }
                                                                                             
            

            # if(self.operation_mode_01.isChecked()):
            #     reply = QMessageBox.question(self,"Information","테스트모드의 DeviceID를 변경합니까?",QMessageBox.Yes | QMessageBox.No)
            #     if(reply == QMessageBox.Yes):
            #         with open("DeviceSecurityObject_DEV.json","w") as test_f:
            #             json.dump(data,test_f)
            #             test_f.close()
            #             QMessageBox.question(self, 'Information', 'DeviceID를 변경하였습니다.', QMessageBox.Ok)
            # elif(self.operation_mode_02.isChecked()):
            reply = QMessageBox.question(self,"Information","Will you change the Device ID?",QMessageBox.Yes | QMessageBox.No)
            if(reply == QMessageBox.Yes):
                with open("DeviceSecurityObject.json","w") as operation_f:
                    json.dump(data,operation_f)
                    operation_f.close()
                    QMessageBox.question(self, 'Information', 'DeviceID Changed', QMessageBox.Ok)

        else:
            QMessageBox.question(self, 'Warning', 'Please check DeviceID or Password', QMessageBox.Ok)

        


    def kill_bridge_device_process(self,process_name):
        try:
            process = subprocess.check_output(["ps -ef | grep " + process_name],shell=True,encoding='utf-8')
            print(process)
            process_list = str(process).split("\n")
            for item in process_list:
                if(item.endswith(process_name + ".pyc")):
                    pid_list = item.split(" ")
                    for pid in pid_list:
                        if(pid.isdecimal()):
                            command = " echo 'ghosti' | sudo -S /bin/kill -9 " + pid
                            print("kill_bridge_device_process::::",command, process_name+".pyc")
                            os.system(command)
                            break
        except Exception as ex:
            print(str(ex))
            pass 

    def playvod(self):
        IsChecked = False
        if(self.opt_camera_0001.isChecked()):
            IsChecked = True
            DisplayCamera = "0001"
        elif(self.opt_camera_0002.isChecked()):
            IsChecked = True
            DisplayCamera = "0002"
        elif(self.opt_camera_0003.isChecked()):
            IsChecked = True
            DisplayCamera = "0003"
        elif(self.opt_camera_0004.isChecked()):
            IsChecked = True
            DisplayCamera = "0004"
        elif(self.opt_camera_0005.isChecked()):
            IsChecked = True
            DisplayCamera = "0005"
        elif(self.opt_camera_0006.isChecked()):
            IsChecked = True
            DisplayCamera = "0006"
        elif(self.opt_camera_0007.isChecked()):
            IsChecked = True
            DisplayCamera = "0007"
        elif(self.opt_camera_0008.isChecked()):
            IsChecked = True
            DisplayCamera = "0008"
        elif(self.opt_camera_0009.isChecked()):
            IsChecked = True
            DisplayCamera = "0009"
        elif(self.opt_camera_0010.isChecked()):
            IsChecked = True
            DisplayCamera = "0010"

        if(self.chk_display_on.isChecked() and IsChecked):
            with open(config_file,"w") as config_f:
                data = {
                    "camera_list":[DisplayCamera],
                    "display_mode":"Y"
                }
                json.dump(data,config_f)
                config_f.close()

            self.kill_bridge_device_process(BridgeDeviceGetSceneModeManager)
            print(":::::" + "python3 " + BridgeDeviceGetSceneModeManager + ".pyc")
            #os.system("python3 " + BridgeDeviceGetSceneModeManager + ".pyc")

            self.p = QProcess()
            self.p.start("python3",[BridgeDeviceGetSceneModeManager + ".pyc"])
            QMessageBox.question(self, 'Information', 'Video will be start \n Please wait for a moment!!!', QMessageBox.Ok)

        else:
            QMessageBox.question(self, 'Warning', 'There is no chosen camera!!!', QMessageBox.Ok)


    def change_display_mode(self):
        RtspList = ["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"]
        for item in RtspList:
            if(os.path.isfile(str(item) + ".dat")):
                os.remove(str(item) + ".dat")

        if(self.chk_display_on.isChecked()):
            self.opt_camera_0001.setEnabled(True)
            self.opt_camera_0002.setEnabled(True)
            self.opt_camera_0003.setEnabled(True)
            self.opt_camera_0004.setEnabled(True)
            self.opt_camera_0005.setEnabled(True)
            self.opt_camera_0006.setEnabled(True)
            self.opt_camera_0007.setEnabled(True)
            self.opt_camera_0008.setEnabled(True)
            self.opt_camera_0009.setEnabled(True)
            self.opt_camera_0010.setEnabled(True)  
            self.kill_bridge_device_process(BridgeDeviceGetSceneModeManager)
            self.kill_bridge_device_process(BridgeDeviceInferenceManager)
            self.kill_bridge_device_process(BridgeDeviceEventManager)
            self.kill_bridge_device_process(BridgeDeviceSceneMarkManager)
            self.kill_bridge_device_process(BridgeDeviceSceneDataManager)
            self.kill_bridge_device_process(BridgeDeviceEventFacilityManager)

            
            self.camera_01.setText("0.0")
            self.camera_02.setText("0.0")
            self.camera_03.setText("0.0")
            self.camera_04.setText("0.0")
            self.camera_05.setText("0.0")
            self.camera_06.setText("0.0")
            self.camera_07.setText("0.0")
            self.camera_08.setText("0.0")
            self.camera_09.setText("0.0")
            self.camera_10.setText("0.0")

        else:
            self.opt_camera_0001.setChecked(False)
            self.opt_camera_0002.setChecked(False)
            self.opt_camera_0003.setChecked(False)
            self.opt_camera_0004.setChecked(False)
            self.opt_camera_0005.setChecked(False)
            self.opt_camera_0006.setChecked(False)
            self.opt_camera_0007.setChecked(False)
            self.opt_camera_0008.setChecked(False)
            self.opt_camera_0009.setChecked(False)
            self.opt_camera_0010.setChecked(False)

            self.opt_camera_0001.setEnabled(False)
            self.opt_camera_0002.setEnabled(False)
            self.opt_camera_0003.setEnabled(False)
            self.opt_camera_0004.setEnabled(False)
            self.opt_camera_0005.setEnabled(False)
            self.opt_camera_0006.setEnabled(False)
            self.opt_camera_0007.setEnabled(False)
            self.opt_camera_0008.setEnabled(False)
            self.opt_camera_0009.setEnabled(False)
            self.opt_camera_0010.setEnabled(False)
            self.kill_bridge_device_process(BridgeDeviceGetSceneModeManager)
            self.kill_bridge_device_process(BridgeDeviceInferenceManager)
            self.kill_bridge_device_process(BridgeDeviceEventManager)
            self.kill_bridge_device_process(BridgeDeviceSceneMarkManager)
            self.kill_bridge_device_process(BridgeDeviceSceneDataManager)
            self.kill_bridge_device_process(BridgeDeviceEventFacilityManager)
            self.camera_01.setText("0.0")
            self.camera_02.setText("0.0")
            self.camera_03.setText("0.0")
            self.camera_04.setText("0.0")
            self.camera_05.setText("0.0")
            self.camera_06.setText("0.0")
            self.camera_07.setText("0.0")
            self.camera_08.setText("0.0")
            self.camera_09.setText("0.0")
            self.camera_10.setText("0.0")

            with open("/home/ghosti/bridge_device/config.json","w") as write_config_f:
                data = {
                    "camera_list":["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"],
                    "display_mode":"N"
                }

                json.dump(data,write_config_f)
                write_config_f.close()
            QMessageBox.question(self, 'Information', 'Video will be end\n Please wait for a moment!!!', QMessageBox.Ok)

    def locate_window_center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def getsubnet(self,subnet_bits):
        subnet_range = ["255.255.255.255"
                        ,"255.255.255.254"
                        ,"255.255.255.252"
                        ,"255.255.255.248"
                        ,"255.255.255.240"
                        ,"255.255.255.224"
                        ,"255.255.255.192"
                        ,"255.255.255.128"
                        ,"255.255.255.0"
                        ,"255.255.254.0"
                        ,"255.255.252.0"
                        ,"255.255.248.0"
                        ,"255.255.240.0"
                        ,"255.255.224.0"
                        ,"255.255.192.0"
                        ,"255.255.128.0"
                        ,"255.255.0.0"
                        ,"255.254.0.0"
                        ,"255.252.0.0"
                        ,"255.248.0.0"
                        ,"255.240.0.0"
                        ,"255.224.0.0"
                        ,"255.192.0.0"
                        ,"255.128.0.0"
                        ,"255.0.0.0"
                        ,"254.0.0.0"
                        ,"252.0.0.0"
                        ,"248.0.0.0"
                        ,"240.0.0.0"
                        ,"224.0.0.0"
                        ,"192.0.0.0"
                        ,"128.0.0.0"
                        ,"0.0.0.0"]

        return subnet_range[32 - subnet_bits]
    def get_ip_address(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip_address = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            return ip_address
        except OSError:
            return None

    def get_netmask(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            netmask = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x891b,  # SIOCGIFNETMASK
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            return netmask
        except OSError:
            return None

    def get_gateway(self):
        try:
            with open('/proc/net/route') as f:
                for line in f:
                    fields = line.strip().split()
                    if fields[1] == '00000000':
                        gateway = socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))
                        return gateway
        except OSError:
            return None
    # def get_dns_servers(self):
    #     try:
    #         with open('/etc/resolv.conf') as f:
    #             for line in f:
    #                 if line.startswith('nameserver'):
    #                     dns_server = line.split()[1]
    #                     yield dns_server
    #     except OSError:
    #         return None
    def get_dns_servers(self, interface):
        try:
            output = subprocess.check_output(['systemd-resolve', '--status', interface]).decode('utf-8')
            matches = re.findall(r'^\s+DNS Servers:\s+(.*?)\s*$\n\s+(.*?)\s*$', output, flags=re.MULTILINE)
            print(matches)
            if len(matches) == 0 :
                return None
            matches = matches[0]
            print(matches)
            dns_servers=[]
            if matches:
                for i in matches :
                    dns_servers.append(i)
                return dns_servers
            else:
                return None
        except subprocess.CalledProcessError:
            return None

    def get_interface_dns_info(self,interface):
        dns_info = {}

        dns_servers = self.get_dns_servers(interface)

        return dns_servers

    def get_network_interface_info(self):
        interface_info = {}

        for ifname in ['eth0', 'eth1']:
            print(ifname)
            ip_address = self.get_ip_address(ifname)
            netmask = self.get_netmask(ifname)
            gateway = self.get_gateway()
            dns = self.get_interface_dns_info(ifname)
            #if ip_address is not None:
            interface_info[ifname] = {
                'ip_address': ip_address,
                'netmask': netmask,
                'gateway': gateway,
                'dns' : dns
            }
            # elif ip_address is None :
            #     return None
        return interface_info

    def read_current_setting(self):
        if(os.path.isfile(network_setting_file)):
            with open(network_setting_file,"r") as network_f:
                lines = network_f.readlines()
                for i in range(0,len(lines)):
                    if(i == 5):
                        line_split = lines[i].replace(" ","").replace("\n","").split(":")
                        #print(line_split)
                        if line_split[-1].lower() == 'true' :
                            lan2_dhcp = True
                            self.lan2_dhcp_rb.setChecked(True)
                            self.lan2_static_rb.setChecked(False)
                        elif line_split[-1].lower() == 'false' or line_split[-1].lower() == 'no' :
                            lan2_dhcp = False
                            self.lan2_dhcp_rb.setChecked(False)
                            self.lan2_static_rb.setChecked(True)
                        print(str(lan2_dhcp).lower())
                    if(i == 7):
                        line_split = lines[i].replace("[","").replace("]","").split(":")
                        line_split_ip_and_subnet = line_split[1].split("/")
                        ip_address = line_split_ip_and_subnet[0].split(".")
                        self.lan2_ip_01.setText(str(ip_address[0]).strip())
                        self.lan2_ip_02.setText(str(ip_address[1]).strip())
                        self.lan2_ip_03.setText(str(ip_address[2]).strip())
                        self.lan2_ip_04.setText(str(ip_address[3]).strip())

                        subnet = self.getsubnet(int(line_split_ip_and_subnet[1]))
                        ip_address = subnet.split(".")
                        self.lan2_subnet_01.setText(str(ip_address[0]).strip())
                        self.lan2_subnet_02.setText(str(ip_address[1]).strip())
                        self.lan2_subnet_03.setText(str(ip_address[2]).strip())
                        self.lan2_subnet_04.setText(str(ip_address[3]).strip())

                    elif(i == 8):
                        line_split = lines[i].replace("[","").replace("]","").split(":")
                        line_split_ip_and_subnet = line_split[1].split("/")
                        ip_address = line_split_ip_and_subnet[0].split(".")
                        self.lan2_gateway_01.setText(str(ip_address[0]).strip())
                        self.lan2_gateway_02.setText(str(ip_address[1]).strip())
                        self.lan2_gateway_03.setText(str(ip_address[2]).strip())
                        self.lan2_gateway_04.setText(str(ip_address[3]).strip())

                    elif(i == 10):
                        line_split = lines[i].replace("[","").replace("]","").split(":")
                        line_split_dns = line_split[1].split(",")
                        if(len(line_split_dns) == 1):
                            ip_address = line_split_dns[0].split(".")
                            self.lan2_dns1_01.setText(str(ip_address[0]).strip())
                            self.lan2_dns1_02.setText(str(ip_address[1]).strip())
                            self.lan2_dns1_03.setText(str(ip_address[2]).strip())
                            self.lan2_dns1_04.setText(str(ip_address[3]).strip())
                        elif(len(line_split_dns) == 2):
                            ip_address = line_split_dns[0].split(".")
                            self.lan2_dns1_01.setText(str(ip_address[0]).strip())
                            self.lan2_dns1_02.setText(str(ip_address[1]).strip())
                            self.lan2_dns1_03.setText(str(ip_address[2]).strip())
                            self.lan2_dns1_04.setText(str(ip_address[3]).strip())
                            ip_address = line_split_dns[1].split(".")
                            self.lan2_dns2_01.setText(str(ip_address[0]).strip())
                            self.lan2_dns2_02.setText(str(ip_address[1]).strip())
                            self.lan2_dns2_03.setText(str(ip_address[2]).strip())
                            self.lan2_dns2_04.setText(str(ip_address[3]).strip())
                    if(i == 14):
                        line_split = lines[i].replace(" ","").replace("\n","").split(":")
                        if line_split[-1].lower() == 'true' :
                            lan1_dhcp = True
                            self.lan1_dhcp_rb.setChecked(True)
                            self.lan1_static_rb.setChecked(False)
                        elif line_split[-1].lower() == 'false' or line_split[-1].lower() == 'no' :
                            lan1_dhcp = False
                            self.lan1_dhcp_rb.setChecked(False)
                            self.lan1_static_rb.setChecked(True)
                    elif(i == 15):
                        line_split = lines[i].replace("[","").replace("]","").replace("\n","").replace(" ","").split(":")
                        print("############",lines[i])
                        line_split_ip_and_subnet = line_split[1].split("/")
                        print("############line_split_ip_and_subnet",line_split[1])

                        ip_address = line_split_ip_and_subnet[0].split(".")
                        self.lan1_ip_01.setText(str(ip_address[0]).strip())
                        self.lan1_ip_02.setText(str(ip_address[1]).strip())
                        self.lan1_ip_03.setText(str(ip_address[2]).strip())
                        self.lan1_ip_04.setText(str(ip_address[3]).strip())

                        subnet = self.getsubnet(int(line_split_ip_and_subnet[1]))
                        ip_address = subnet.split(".")
                        self.lan1_subnet_01.setText(str(ip_address[0]).strip())
                        self.lan1_subnet_02.setText(str(ip_address[1]).strip())
                        self.lan1_subnet_03.setText(str(ip_address[2]).strip())
                        self.lan1_subnet_04.setText(str(ip_address[3]).strip())

                    elif(i == 16):
                        line_split = lines[i].replace("[","").replace("]","").split(":")
                        line_split_ip_and_subnet = line_split[1].split("/")
                        ip_address = line_split_ip_and_subnet[0].split(".")
                        self.lan1_gateway_01.setText(str(ip_address[0]).strip())
                        self.lan1_gateway_02.setText(str(ip_address[1]).strip())
                        self.lan1_gateway_03.setText(str(ip_address[2]).strip())
                        self.lan1_gateway_04.setText(str(ip_address[3]).strip())

                    elif(i == 18):
                        line_split = lines[i].replace("[","").replace("]","").split(":")
                        line_split_dns = line_split[1].split(",")
                        if(len(line_split_dns) == 1):
                            ip_address = line_split_dns[0].split(".")
                            self.lan1_dns1_01.setText(str(ip_address[0]).strip())
                            self.lan1_dns1_02.setText(str(ip_address[1]).strip())
                            self.lan1_dns1_03.setText(str(ip_address[2]).strip())
                            self.lan1_dns1_04.setText(str(ip_address[3]).strip())
                        elif(len(line_split_dns) == 2):
                            ip_address = line_split_dns[0].split(".")
                            self.lan1_dns1_01.setText(str(ip_address[0]).strip())
                            self.lan1_dns1_02.setText(str(ip_address[1]).strip())
                            self.lan1_dns1_03.setText(str(ip_address[2]).strip())
                            self.lan1_dns1_04.setText(str(ip_address[3]).strip())
                            ip_address = line_split_dns[1].split(".")
                            self.lan1_dns2_01.setText(str(ip_address[0]).strip())
                            self.lan1_dns2_02.setText(str(ip_address[1]).strip())
                            self.lan1_dns2_03.setText(str(ip_address[2]).strip())
                            self.lan1_dns2_04.setText(str(ip_address[3]).strip())

                network_f.close()
        network_info = self.get_network_interface_info()
        if(self.lan1_dhcp_rb.isChecked() ) :
            ip = network_info["eth1"]["ip_address"].split('.')
            netmask = network_info["eth1"]["netmask"].split('.')
            gateway = network_info["eth1"]["gateway"].split('.')
            dns1 = network_info["eth1"]["dns"][0].split('.')
            dns2 = network_info["eth1"]["dns"][1].split('.')
            print(ip)
            print(netmask)
            print(gateway)
            print(dns1, dns2)
            self.lan1_ip_01.setText(str(ip[0]).strip())
            self.lan1_ip_02.setText(str(ip[1]).strip())
            self.lan1_ip_03.setText(str(ip[2]).strip())
            self.lan1_ip_04.setText(str(ip[3]).strip())
            self.lan1_subnet_01.setText(str(netmask[0]).strip())
            self.lan1_subnet_02.setText(str(netmask[1]).strip())
            self.lan1_subnet_03.setText(str(netmask[2]).strip())
            self.lan1_subnet_04.setText(str(netmask[3]).strip())
            self.lan1_gateway_01.setText(str(gateway[0]).strip())
            self.lan1_gateway_02.setText(str(gateway[1]).strip())
            self.lan1_gateway_03.setText(str(gateway[2]).strip())
            self.lan1_gateway_04.setText(str(gateway[3]).strip())
            self.lan1_dns1_01.setText(str(dns1[0]).strip())
            self.lan1_dns1_02.setText(str(dns1[1]).strip())
            self.lan1_dns1_03.setText(str(dns1[2]).strip())
            self.lan1_dns1_04.setText(str(dns1[3]).strip())
            self.lan1_dns2_01.setText(str(dns2[0]).strip())
            self.lan1_dns2_02.setText(str(dns2[1]).strip())
            self.lan1_dns2_03.setText(str(dns2[2]).strip())
            self.lan1_dns2_04.setText(str(dns2[3]).strip())
            
        if(self.lan2_dhcp_rb.isChecked()) :
            ip = network_info["eth0"]["ip_address"].split('.')
            netmask = network_info["eth0"]["netmask"].split('.')
            gateway = network_info["eth0"]["gateway"].split('.')
            dns1 = network_info["eth0"]["dns"][0].split('.')
            dns2 = network_info["eth0"]["dns"][1].split('.')
            self.lan2_ip_01.setText(str(ip[0]).strip())
            self.lan2_ip_02.setText(str(ip[1]).strip())
            self.lan2_ip_03.setText(str(ip[2]).strip())
            self.lan2_ip_04.setText(str(ip[3]).strip())
            self.lan2_subnet_01.setText(str(netmask[0]).strip())
            self.lan2_subnet_02.setText(str(netmask[1]).strip())
            self.lan2_subnet_03.setText(str(netmask[2]).strip())
            self.lan2_subnet_04.setText(str(netmask[3]).strip())
            self.lan2_gateway_01.setText(str(gateway[0]).strip())
            self.lan2_gateway_02.setText(str(gateway[1]).strip())
            self.lan2_gateway_03.setText(str(gateway[2]).strip())
            self.lan2_gateway_04.setText(str(gateway[3]).strip())
            self.lan2_dns1_01.setText(str(dns1[0]).strip())
            self.lan2_dns1_02.setText(str(dns1[1]).strip())
            self.lan2_dns1_03.setText(str(dns1[2]).strip())
            self.lan2_dns1_04.setText(str(dns1[3]).strip())
            self.lan2_dns2_01.setText(str(dns2[0]).strip())
            self.lan2_dns2_02.setText(str(dns2[1]).strip())
            self.lan2_dns2_03.setText(str(dns2[2]).strip())
            self.lan2_dns2_04.setText(str(dns2[3]).strip())
        # if(os.path.isfile(bridge_mode_file)):
        #     with open(bridge_mode_file,"r") as bridge_mode_f:
        #         lines = bridge_mode_f.readlines()
        #         bridge_mode = lines[0]
        #         bridge_mode_f.close()

        #         print("Current Bridge Mode ::: ",bridge_mode)

                #if(bridge_mode):
                    #if(int(bridge_mode) == 1):
                    #    self.bridge_mode_01.setChecked(True)
                    #elif(int(bridge_mode) == 2):
                    #    self.bridge_mode_02.setChecked(True)
                    #elif(int(bridge_mode) == 3):
                    #    self.bridge_mode_03.setChecked(True)
                #else:
                #    print("Default Current Bridge Mode ::: ",bridge_mode)

                    #self.bridge_mode_01.setChecked(True)

        # if(os.path.isfile(debug_mode_file)):
        #     with open(debug_mode_file,"r") as operation_mode_f:
        #         lines = operation_mode_f.readlines()
        #         operation_mode = lines[0]
        #         operation_mode_f.close()

        #         print("Current Operation Mode ::: ",operation_mode)

        #         if(operation_mode):
        #             if(int(operation_mode) == 1):
        #                 self.operation_mode_01.setChecked(True)
        #             elif(int(operation_mode) == 0):
        #                 self.operation_mode_02.setChecked(True)
        #         else:
        #             self.operation_mode_01.setChecked(True)
        '''
        if(os.path.isfile(config_file)):
            with open(config_file) as config_f:
                config = json.load(config_f)


                display_mode = config["display_mode"]
                camera_list = config["camera_list"]
                if(display_mode == "Y"):
                    self.chk_display_on.setChecked(True)
                    self.opt_camera_0001.setEnabled(True)
                    self.opt_camera_0002.setEnabled(True)
                    self.opt_camera_0003.setEnabled(True)
                    self.opt_camera_0004.setEnabled(True)
                    self.opt_camera_0005.setEnabled(True)
                    self.opt_camera_0006.setEnabled(True)
                    self.opt_camera_0007.setEnabled(True)
                    self.opt_camera_0008.setEnabled(True)
                    self.opt_camera_0009.setEnabled(True)
                    self.opt_camera_0010.setEnabled(True) 
                    camera = camera_list[0]
                    if(int(camera) == 1):
                        self.opt_camera_0001.setChecked(True)
                    elif(int(camera) == 2):
                        self.opt_camera_0002.setChecked(True)
                    elif(int(camera) == 3):
                        self.opt_camera_0003.setChecked(True)
                    elif(int(camera) == 4):
                        self.opt_camera_0004.setChecked(True)
                    elif(int(camera) == 5):
                        self.opt_camera_0005.setChecked(True)   
                    elif(int(camera) == 6):
                        self.opt_camera_0006.setChecked(True)
                    elif(int(camera) == 7):
                        self.opt_camera_0007.setChecked(True)
                    elif(int(camera) == 8):
                        self.opt_camera_0008.setChecked(True)
                    elif(int(camera) == 9):
                        self.opt_camera_0009.setChecked(True)
                    elif(int(camera) == 10):
                        self.opt_camera_0010.setChecked(True)
                else:
                    self.chk_display_on.setChecked(False)
                    self.opt_camera_0001.setChecked(False)
                    self.opt_camera_0002.setChecked(False)
                    self.opt_camera_0003.setChecked(False)
                    self.opt_camera_0004.setChecked(False)
                    self.opt_camera_0005.setChecked(False)
                    self.opt_camera_0006.setChecked(False)
                    self.opt_camera_0007.setChecked(False)
                    self.opt_camera_0008.setChecked(False)
                    self.opt_camera_0009.setChecked(False)
                    self.opt_camera_0010.setChecked(False)
            
                config_f.close()
        '''

        # if(self.operation_mode_01.isChecked()):
        #     if(os.path.isfile(DeviceSecurityObject_DEV_FILE)):
        #         with open(DeviceSecurityObject_DEV_FILE) as test_f:
        #             test = json.load(test_f)
        #             self.txtDeviceID.setText(test["DeviceID"])
        #             self.txtDevicePassword.setText(test["DevicePassword"])
        #             test_f.close()

        # elif(self.operation_mode_02.isChecked()):
        #     if(os.path.isfile(DeviceSecurityObject_FILE)):
        #         with open(DeviceSecurityObject_FILE) as operation_f:
        #             operation = json.load(operation_f)
        #             self.txtDeviceID.setText(operation["DeviceID"])
        #             self.txtDevicePassword.setText(operation["DevicePassword"])
        #             operation_f.close()

        with open(config_file,"w") as write_config_f:
            data = {
                "camera_list":["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"],
                "display_mode":"N"
            }
            json.dump(data,write_config_f)
            write_config_f.close()

            self.opt_camera_0001.setChecked(False)
            self.opt_camera_0002.setChecked(False)
            self.opt_camera_0003.setChecked(False)
            self.opt_camera_0004.setChecked(False)
            self.opt_camera_0005.setChecked(False)
            self.opt_camera_0006.setChecked(False)
            self.opt_camera_0007.setChecked(False)
            self.opt_camera_0008.setChecked(False)
            self.opt_camera_0009.setChecked(False)
            self.opt_camera_0010.setChecked(False)
            self.chk_display_on.setChecked(False)
            self.opt_camera_0001.setEnabled(False)
            self.opt_camera_0002.setEnabled(False)
            self.opt_camera_0003.setEnabled(False)
            self.opt_camera_0004.setEnabled(False)
            self.opt_camera_0005.setEnabled(False)
            self.opt_camera_0006.setEnabled(False)
            self.opt_camera_0007.setEnabled(False)
            self.opt_camera_0008.setEnabled(False)
            self.opt_camera_0009.setEnabled(False)
            self.opt_camera_0010.setEnabled(False) 


    def read_current_setting1(self):

        RtspList = ["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"]
        for item in RtspList:
            if(os.path.isfile(str(item) + ".dat")):
                os.remove(str(item) + ".dat")
        if(os.path.isfile(network_setting_file)):
            with open(network_setting_file) as network_f:
                network_setting = yaml.load(network_f)
                eth0_setting = network_setting['network']['ethernets']['eth0'] 
                #{'dhcp4': False, 'dhcp6': False, 'addresses': ['172.30.1.239/24'], 'gateway4': '172.30.1.254', 'nameservers': {'addresses': ['168.126.63.1', '168.126.63.2']}}
                eth1_setting = network_setting['network']['ethernets']['eth1']
                #{'dhcp4': False, 'dhcp6': False, 'addresses': ['172.30.1.239/24'], 'gateway4': '172.30.1.254', 'nameservers': {'addresses': ['168.126.63.1', '168.126.63.2']}}
                if eth0_setting['dhcp4'] == True :
                    self.lan2_dhcp_rb.setChecked(True)
                elif eth0_setting['dhcp4'] == False or str(eth0_setting['dhcp']).lower() == 'no' :
                    self.lan2_static_rb.setChecked(True)
                if eth1_setting['dhcp4'] == True :
                    self.lan1_dhcp_rb.setChecked(True)
                elif eth1_setting['dhcp4'] == False or str(eth1_setting['dhcp']).lower() == 'no' :
                    self.lan1_static_rb.setChecked(True)
                network_info = self.get_network_interface_info()
                if(self.lan1_dhcp_rb.isChecked() and network_info['eth1']['ip_address'] is not None) :
                    ip = network_info["eth1"]["ip_address"].split('.')
                    netmask = network_info["eth1"]["netmask"].split('.')
                    gateway = network_info["eth1"]["gateway"].split('.')
                    dns1 = network_info["eth1"]["dns"][0].split('.')
                    dns2 = network_info["eth1"]["dns"][1].split('.')
                    print(ip)
                    print(netmask)
                    print(gateway)
                    print(dns1, dns2)
                    self.lan1_ip_01.setText(str(ip[0]).strip())
                    self.lan1_ip_02.setText(str(ip[1]).strip())
                    self.lan1_ip_03.setText(str(ip[2]).strip())
                    self.lan1_ip_04.setText(str(ip[3]).strip())
                    self.lan1_subnet_01.setText(str(netmask[0]).strip())
                    self.lan1_subnet_02.setText(str(netmask[1]).strip())
                    self.lan1_subnet_03.setText(str(netmask[2]).strip())
                    self.lan1_subnet_04.setText(str(netmask[3]).strip())
                    self.lan1_gateway_01.setText(str(gateway[0]).strip())
                    self.lan1_gateway_02.setText(str(gateway[1]).strip())
                    self.lan1_gateway_03.setText(str(gateway[2]).strip())
                    self.lan1_gateway_04.setText(str(gateway[3]).strip())
                    self.lan1_dns1_01.setText(str(dns1[0]).strip())
                    self.lan1_dns1_02.setText(str(dns1[1]).strip())
                    self.lan1_dns1_03.setText(str(dns1[2]).strip())
                    self.lan1_dns1_04.setText(str(dns1[3]).strip())
                    self.lan1_dns2_01.setText(str(dns2[0]).strip())
                    self.lan1_dns2_02.setText(str(dns2[1]).strip())
                    self.lan1_dns2_03.setText(str(dns2[2]).strip())
                    self.lan1_dns2_04.setText(str(dns2[3]).strip())
                elif(self.lan1_static_rb.isChecked()):
                    ip ,netmask = eth1_setting["addresses"][0].split('/')
                    netmask = self.getsubnet(int(netmask)).split('.')
                    ip = ip.split('.')
                    gateway = eth1_setting["gateway4"].split('.')
                    dns1 = eth1_setting['nameservers']['addresses'][0].split('.')
                    dns2 = eth1_setting['nameservers']['addresses'][1].split('.')
                    self.lan1_ip_01.setText(str(ip[0]).strip())
                    self.lan1_ip_02.setText(str(ip[1]).strip())
                    self.lan1_ip_03.setText(str(ip[2]).strip())
                    self.lan1_ip_04.setText(str(ip[3]).strip())
                    self.lan1_subnet_01.setText(str(netmask[0]).strip())
                    self.lan1_subnet_02.setText(str(netmask[1]).strip())
                    self.lan1_subnet_03.setText(str(netmask[2]).strip())
                    self.lan1_subnet_04.setText(str(netmask[3]).strip())
                    self.lan1_gateway_01.setText(str(gateway[0]).strip())
                    self.lan1_gateway_02.setText(str(gateway[1]).strip())
                    self.lan1_gateway_03.setText(str(gateway[2]).strip())
                    self.lan1_gateway_04.setText(str(gateway[3]).strip())
                    self.lan1_dns1_01.setText(str(dns1[0]).strip())
                    self.lan1_dns1_02.setText(str(dns1[1]).strip())
                    self.lan1_dns1_03.setText(str(dns1[2]).strip())
                    self.lan1_dns1_04.setText(str(dns1[3]).strip())
                    self.lan1_dns2_01.setText(str(dns2[0]).strip())
                    self.lan1_dns2_02.setText(str(dns2[1]).strip())
                    self.lan1_dns2_03.setText(str(dns2[2]).strip())
                    self.lan1_dns2_04.setText(str(dns2[3]).strip())

                    
                
                if(self.lan2_dhcp_rb.isChecked() and network_info['eth0']['ip_address'] is not None) :
                    '''
                    ip = network_info["eth0"]["ip_address"].split('.')
                    netmask = network_info["eth0"]["netmask"].split('.')
                    gateway = network_info["eth0"]["gateway"].split('.')
                    dns1 = network_info["eth0"]["dns"][0].split('.')
                    dns2 = network_info["eth0"]["dns"][1].split('.')
                    self.lan2_ip_01.setText(str(ip[0]).strip())
                    self.lan2_ip_02.setText(str(ip[1]).strip())
                    self.lan2_ip_03.setText(str(ip[2]).strip())
                    self.lan2_ip_04.setText(str(ip[3]).strip())
                    self.lan2_subnet_01.setText(str(netmask[0]).strip())
                    self.lan2_subnet_02.setText(str(netmask[1]).strip())
                    self.lan2_subnet_03.setText(str(netmask[2]).strip())
                    self.lan2_subnet_04.setText(str(netmask[3]).strip())
                    self.lan2_gateway_01.setText(str(gateway[0]).strip())
                    self.lan2_gateway_02.setText(str(gateway[1]).strip())
                    self.lan2_gateway_03.setText(str(gateway[2]).strip())
                    self.lan2_gateway_04.setText(str(gateway[3]).strip())
                    self.lan2_dns1_01.setText(str(dns1[0]).strip())
                    self.lan2_dns1_02.setText(str(dns1[1]).strip())
                    self.lan2_dns1_03.setText(str(dns1[2]).strip())
                    self.lan2_dns1_04.setText(str(dns1[3]).strip())
                    self.lan2_dns2_01.setText(str(dns2[0]).strip())
                    self.lan2_dns2_02.setText(str(dns2[1]).strip())
                    self.lan2_dns2_03.setText(str(dns2[2]).strip())
                    self.lan2_dns2_04.setText(str(dns2[3]).strip())
                    '''
                elif(self.lan2_static_rb.isChecked()):
                    ip ,netmask = eth0_setting["addresses"][0].split('/')
                    netmask = self.getsubnet(int(netmask)).split('.')
                    ip = ip.split('.')
                    gateway = eth0_setting["gateway4"].split('.')
                    dns1 = eth0_setting['nameservers']['addresses'][0].split('.')
                    dns2 = eth0_setting['nameservers']['addresses'][1].split('.')
                    self.lan2_ip_01.setText(str(ip[0]).strip())
                    self.lan2_ip_02.setText(str(ip[1]).strip())
                    self.lan2_ip_03.setText(str(ip[2]).strip())
                    self.lan2_ip_04.setText(str(ip[3]).strip())
                    self.lan2_subnet_01.setText(str(netmask[0]).strip())
                    self.lan2_subnet_02.setText(str(netmask[1]).strip())
                    self.lan2_subnet_03.setText(str(netmask[2]).strip())
                    self.lan2_subnet_04.setText(str(netmask[3]).strip())
                    self.lan2_gateway_01.setText(str(gateway[0]).strip())
                    self.lan2_gateway_02.setText(str(gateway[1]).strip())
                    self.lan2_gateway_03.setText(str(gateway[2]).strip())
                    self.lan2_gateway_04.setText(str(gateway[3]).strip())
                    self.lan2_dns1_01.setText(str(dns1[0]).strip())
                    self.lan2_dns1_02.setText(str(dns1[1]).strip())
                    self.lan2_dns1_03.setText(str(dns1[2]).strip())
                    self.lan2_dns1_04.setText(str(dns1[3]).strip())
                    self.lan2_dns2_01.setText(str(dns2[0]).strip())
                    self.lan2_dns2_02.setText(str(dns2[1]).strip())
                    self.lan2_dns2_03.setText(str(dns2[2]).strip())
                    self.lan2_dns2_04.setText(str(dns2[3]).strip())
                
                
        with open(config_file,"w") as write_config_f:
            data = {
                "camera_list":["0001","0002","0003","0004","0005","0006","0007","0008","0009","0010"],
                "display_mode":"N"
            }
            json.dump(data,write_config_f)
            write_config_f.close()

            self.opt_camera_0001.setChecked(False)
            self.opt_camera_0002.setChecked(False)
            self.opt_camera_0003.setChecked(False)
            self.opt_camera_0004.setChecked(False)
            self.opt_camera_0005.setChecked(False)
            self.opt_camera_0006.setChecked(False)
            self.opt_camera_0007.setChecked(False)
            self.opt_camera_0008.setChecked(False)
            self.opt_camera_0009.setChecked(False)
            self.opt_camera_0010.setChecked(False)
            self.chk_display_on.setChecked(False)
            self.opt_camera_0001.setEnabled(False)
            self.opt_camera_0002.setEnabled(False)
            self.opt_camera_0003.setEnabled(False)
            self.opt_camera_0004.setEnabled(False)
            self.opt_camera_0005.setEnabled(False)
            self.opt_camera_0006.setEnabled(False)
            self.opt_camera_0007.setEnabled(False)
            self.opt_camera_0008.setEnabled(False)
            self.opt_camera_0009.setEnabled(False)
            self.opt_camera_0010.setEnabled(False) 


    def check_blank(self,lineedit):
        reply = QMessageBox.question(self, 'Warning!', 'There is no entered IP Addres!!!', QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            lineedit.setFocus()

    def savesetting(self):
        print("Save Setting!!!")
        if self.lan1_static_rb.isChecked() :
            lan1_ip_01 = int(self.lan1_ip_01.text())
            lan1_ip_02 = int(self.lan1_ip_02.text())
            lan1_ip_03 = int(self.lan1_ip_03.text())
            lan1_ip_04 = int(self.lan1_ip_04.text())

            lan1_subnet_01 = int(self.lan1_subnet_01.text())
            lan1_subnet_02 = int(self.lan1_subnet_02.text())
            lan1_subnet_03 = int(self.lan1_subnet_03.text())
            lan1_subnet_04 = int(self.lan1_subnet_04.text())

            lan1_gateway_01 = int(self.lan1_gateway_01.text())
            lan1_gateway_02 = int(self.lan1_gateway_02.text())
            lan1_gateway_03 = int(self.lan1_gateway_03.text())
            lan1_gateway_04 = int(self.lan1_gateway_04.text())
        if self.lan2_static_rb.isChecked() :
            lan2_ip_01 = int(self.lan2_ip_01.text())
            lan2_ip_02 = int(self.lan2_ip_02.text())
            lan2_ip_03 = int(self.lan2_ip_03.text())
            lan2_ip_04 = int(self.lan2_ip_04.text())

            lan2_subnet_01 = int(self.lan2_subnet_01.text())
            lan2_subnet_02 = int(self.lan2_subnet_02.text())
            lan2_subnet_03 = int(self.lan2_subnet_03.text())
            lan2_subnet_04 = int(self.lan2_subnet_04.text())

            lan2_gateway_01 = int(self.lan2_gateway_01.text())
            lan2_gateway_02 = int(self.lan2_gateway_02.text())
            lan2_gateway_03 = int(self.lan2_gateway_03.text())
            lan2_gateway_04 = int(self.lan2_gateway_04.text())

        #print(lan1_ip_01,lan1_ip_02,lan1_ip_03,lan1_ip_04)

        IsDataEmpty = False

        if(self.lan1_ip_01.text() == "" and self.lan1_static_rb.isChecked()):
           IsDataEmpty = True
           self.check_blank(self.lan1_ip_01)
        elif(self.lan1_ip_02.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_ip_02)
        elif(self.lan1_ip_03.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_ip_03)
        elif(self.lan1_ip_04.text() ==  "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_ip_04)
        elif(self.lan1_subnet_01.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_subnet_01)
        elif(self.lan1_subnet_02.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_subnet_02)
        elif(self.lan1_subnet_03.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_subnet_03)
        elif(self.lan1_subnet_04.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_subnet_04)
        elif(self.lan1_gateway_01.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_gateway_01)
        elif(self.lan1_gateway_02.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_gateway_02)
        elif(self.lan1_gateway_03.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_gateway_03)
        elif(self.lan1_gateway_04.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan1_gateway_04)
        elif(self.lan2_ip_01.text() == "" and self.lan1_static_rb.isChecked()):
           IsDataEmpty = True
           self.check_blank(self.lan2_ip_01)
        elif(self.lan2_ip_02.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_ip_02)
        elif(self.lan2_ip_03.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_ip_03)
        elif(self.lan2_ip_04.text() == "" and self.lan1_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_ip_04)
        elif(self.lan2_subnet_01.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_subnet_01)
        elif(self.lan2_subnet_02.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_subnet_02)
        elif(self.lan2_subnet_03.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_subnet_03)
        elif(self.lan2_subnet_04.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_subnet_04)
        elif(self.lan2_gateway_01.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_gateway_01)
        elif(self.lan2_gateway_02.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_gateway_02)
        elif(self.lan2_gateway_03.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_gateway_03)
        elif(self.lan2_gateway_04.text() == "" and self.lan2_static_rb.isChecked()):
            IsDataEmpty = True
            self.check_blank(self.lan2_gateway_04)
            
            
        IsChecked = False
        DisplayCamera = "0000"
        if(self.chk_display_on.isChecked()):
            if(self.opt_camera_0001.isChecked()):
                IsChecked = True
                DisplayCamera = "0001"
            elif(self.opt_camera_0002.isChecked()):
                IsChecked = True
                DisplayCamera = "0002"
            elif(self.opt_camera_0003.isChecked()):
                IsChecked = True
                DisplayCamera = "0003"
            elif(self.opt_camera_0004.isChecked()):
                IsChecked = True
                DisplayCamera = "0004"
            elif(self.opt_camera_0005.isChecked()):
                IsChecked = True
                DisplayCamera = "0005"
            elif(self.opt_camera_0006.isChecked()):
                IsChecked = True
                DisplayCamera = "0006"
            elif(self.opt_camera_0007.isChecked()):
                IsChecked = True
                DisplayCamera = "0007"
            elif(self.opt_camera_0008.isChecked()):
                IsChecked = True
                DisplayCamera = "0008"
            elif(self.opt_camera_0009.isChecked()):
                IsChecked = True
                DisplayCamera = "0009"
            elif(self.opt_camera_0010.isChecked()):
                IsChecked = True
                DisplayCamera = "0010"

        bridge_mode = 1
        operation_mode = 1
        
        
        if(IsDataEmpty == False):
            reply = QMessageBox.question(self,"Information","Will you reboot this bridge device?",QMessageBox.Yes | QMessageBox.No)
            if(reply  == QMessageBox.Yes):
                with open(network_setting_file,"w") as network_f:
                    if(self.lan1_dhcp_rb.isChecked()) :
                        lan1_dhcp = True
                    elif(self.lan1_static_rb.isChecked()) :
                        lan1_dhcp = False
                    if(self.lan2_dhcp_rb.isChecked()) :
                        lan2_dhcp = True
                    elif(self.lan2_static_rb.isChecked()) :
                        lan2_dhcp = False
                    if(self.lan1_static_rb.isChecked()) :
                        lan1_ip = "{}.{}.{}.{}".format(str(lan1_ip_01),str(lan1_ip_02),str(lan1_ip_03),str(lan1_ip_04))
                        lan1_gateway = "{}.{}.{}.{}".format(str(lan1_gateway_01),str(lan1_gateway_02),str(lan1_gateway_03),str(lan1_gateway_04))
                        lan1_subnet = "{}.{}.{}.{}".format(str(lan1_subnet_01),str(lan1_subnet_02),str(lan1_subnet_03),str(lan1_subnet_04))
                        subnet1 = IPAddress(lan1_subnet).netmask_bits()
                        lan1_ip = lan1_ip + "/" + str(subnet1)
                        lan1_dns1_01 = self.lan1_dns1_01.text()
                        lan1_dns1_02 = self.lan1_dns1_02.text()
                        lan1_dns1_03 = self.lan1_dns1_03.text()
                        lan1_dns1_04 = self.lan1_dns1_04.text()


                        lan1_dns2_01 = self.lan1_dns2_01.text()
                        lan1_dns2_02 = self.lan1_dns2_02.text()
                        lan1_dns2_03 = self.lan1_dns2_03.text()
                        lan1_dns2_04 = self.lan1_dns2_04.text()
                        lan1_dns1 = None
                        lan1_dns2 = None
                        if(lan1_dns1_01 and lan1_dns1_02 and lan1_dns1_03 and lan1_dns1_04):
                            lan1_dns1 = "{}.{}.{}.{}".format(lan1_dns1_01,lan1_dns1_02,lan1_dns1_03,lan1_dns1_04)
                        if(lan1_dns2_01 and lan1_dns2_02 and lan1_dns2_03 and lan1_dns2_04):
                            lan1_dns2 = "{}.{}.{}.{}".format(lan1_dns2_01,lan1_dns2_02,lan1_dns2_03,lan1_dns2_04)

                        lan1_dns = "8.8.8.8,4.4.4.4"
                        if(lan1_dns1 is not None and lan1_dns2 is not None):
                            lan1_dns = "{}.{}.{}.{},{}.{}.{}.{}".format(lan1_dns1_01,lan1_dns1_02,lan1_dns1_03,lan1_dns1_04,lan1_dns2_01,lan1_dns2_02,lan1_dns2_03,lan1_dns2_04)
                        elif(lan1_dns1 is not None and lan1_dns2 is None):
                            lan1_dns = "{}.{}.{}.{}".format(lan1_dns1_01,lan1_dns1_02,lan1_dns1_03,lan1_dns1_04)
                        elif(lan1_dns1 is None and lan1_dns2 is not None):
                            lan1_dns = "{}.{}.{}.{}".format(lan1_dns2_01,lan1_dns2_02,lan1_dns2_03,lan1_dns2_04)


                    if(self.lan2_static_rb.isChecked()) :
                        lan2_ip = "{}.{}.{}.{}".format(str(lan2_ip_01),str(lan2_ip_02),str(lan2_ip_03),str(lan2_ip_04))
                        lan2_gateway = "{}.{}.{}.{}".format(str(lan2_gateway_01),str(lan2_gateway_02),str(lan2_gateway_03),str(lan2_gateway_04))
                        lan2_subnet = "{}.{}.{}.{}".format(str(lan2_subnet_01),str(lan2_subnet_02),str(lan2_subnet_03),str(lan2_subnet_04))
                        subnet2 = IPAddress(lan2_subnet).netmask_bits()
                        lan2_ip = lan2_ip + "/" + str(subnet2)
                        lan2_dns1_01 = self.lan2_dns1_01.text()
                        lan2_dns1_02 = self.lan2_dns1_02.text()
                        lan2_dns1_03 = self.lan2_dns1_03.text()
                        lan2_dns1_04 = self.lan2_dns1_04.text()

                        lan2_dns2_01 = self.lan2_dns2_01.text()
                        lan2_dns2_02 = self.lan2_dns2_02.text()
                        lan2_dns2_03 = self.lan2_dns2_03.text()
                        lan2_dns2_04 = self.lan2_dns2_04.text()
                        lan2_dns1 = None
                        lan2_dns2 = None
                        if(lan2_dns1_01 and lan2_dns1_02 and lan2_dns1_03 and lan2_dns1_04):
                            lan2_dns1 = "{}.{}.{}.{}".format(lan2_dns1_01,lan2_dns1_02,lan2_dns1_03,lan2_dns1_04)
                        if(lan2_dns2_01 and lan2_dns2_02 and lan2_dns2_03 and lan2_dns2_04):
                            lan2_dns2 = "{}.{}.{}.{}".format(lan2_dns2_01,lan2_dns2_02,lan2_dns2_03,lan2_dns2_04)

                        lan2_dns = "8.8.8.8,4.4.4.4"
                        if(lan2_dns1 is not None and lan2_dns2 is not None):
                            lan2_dns = "{}.{}.{}.{},{}.{}.{}.{}".format(lan2_dns1_01,lan2_dns1_02,lan2_dns1_03,lan2_dns1_04,lan2_dns2_01,lan2_dns2_02,lan2_dns2_03,lan2_dns2_04)
                        elif(lan2_dns1 is not None and lan2_dns2 is None):
                            lan2_dns = "{}.{}.{}.{}".format(lan2_dns1_01,lan2_dns1_02,lan2_dns1_03,lan2_dns1_04)
                        elif(lan2_dns1 is None and lan2_dns2 is not None):
                            lan2_dns = "{}.{}.{}.{}".format(lan2_dns2_01,lan2_dns2_02,lan2_dns2_03,lan2_dns2_04)

                    
                    if(self.lan1_dhcp_rb.isChecked() and self.lan2_dhcp_rb.isChecked()) :
                        setting_network = "network:\n  version: 2\n  renderer: networkd\n  ethernets:\n    eth0:\n      dhcp4: {}\n    eth1:\n      dhcp4: {}".format(str(lan2_dhcp).lower(),str(lan1_dhcp).lower())
                    elif(self.lan1_dhcp_rb.isChecked() and self.lan2_static_rb.isChecked()):
                        setting_network = "network:\n  version: 2\n  renderer: networkd\n  ethernets:\n    eth0:\n      dhcp4: {}\n      dhcp6: no\n      addresses: [{}]\n      gateway4: {}\n      nameservers:\n        addresses: [{}]\n\n    eth1:\n      dhcp4: {}".format(str(lan2_dhcp).lower(),lan2_ip,lan2_gateway,lan2_dns,str(lan1_dhcp).lower())
                    elif(self.lan1_static_rb.isChecked() and self.lan2_dhcp_rb.isChecked()):
                        setting_network = "network:\n  version: 2\n  renderer: networkd\n  ethernets:\n    eth0:\n      dhcp4: {}\n    eth1:\n      dhcp4: {}\n      dhcp6: no\n      addresses: [{}]\n      gateway4: {}\n      nameservers:\n        addresses: [{}]".format(str(lan2_dhcp).lower(),str(lan1_dhcp).lower(),lan1_ip,lan1_gateway,lan1_dns)
                    elif(self.lan1_static_rb.isChecked() and self.lan2_static_rb.isChecked()):
                        setting_network = "network:\n  version: 2\n  renderer: networkd\n  ethernets:\n    eth0:\n      dhcp4: {}\n      dhcp6: no\n      addresses: [{}]\n      gateway4: {}\n      nameservers:\n        addresses: [{}]\n\n    eth1:\n      dhcp4: {}\n      dhcp6: no\n      addresses: [{}]\n      gateway4: {}\n      nameservers:\n        addresses: [{}]".format(str(lan2_dhcp).lower(),lan2_ip,lan2_gateway,lan2_dns,str(lan1_dhcp).lower(),lan1_ip,lan1_gateway,lan1_dns)

                    network_f.write(setting_network)
                    network_f.close()

                #if(self.bridge_mode_01.isChecked()):
                #    bridge_mode = 1
                #elif(self.bridge_mode_02.isChecked()):
                #    bridge_mode = 2
                #elif(self.bridge_mode_03.isChecked()):
                #    bridge_mode = 3

                # print("bridge_mode :::",bridge_mode)
                # with open(bridge_mode_file,"w") as bridge_mode_f:
                #     bridge_mode_f.write(str(1))
                #     bridge_mode_f.close()

                # #if(self.operation_mode_01.isChecked()):
                # #    operation_mode = 1
                # #elif(self.operation_mode_02.isChecked()):
                # #    operation_mode = 0
                # print("operation_mode:::",operation_mode)

                with open(debug_mode_file,"w") as operation_mode_f:
                    operation_mode_f.write(str(0))
                    #operation_mode_f.write(str(1))
                    operation_mode_f.close()

                with open(config_file,"w") as config_f:
                    data = {
                        "camera_list":[DisplayCamera],
                        "display_mode":"Y"
                    }

                    json.dump(data,config_f)
                    config_f.close()

                os.system('echo "ghosti" | sudo -S init 6')


            else:
                pass
     

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
