from PythonUtils import printDebug

class DeviceControlObjectClass:
    Version = 1.0
    DeviceID = ""
    ControlEndPoints = []
    RevokedJSONTokenIDs = []
    AllowedTLSRootCertificates = []

class ControlEndPointsClass:
    AppEndPoint = None
    NetEndPoint = None

class AppEndPointClass:
    APIVersion = ""
    EndPointID = ""
    AccessToken = ""

class NetEndPointClass:
    APIVersion = "" 
    EndPointID = ""
    Scheme = []

class SchemeClass:
    Protocol = ""
    Authority = ""
    AccessToken = ""
    Role = ""



def GetDeviceControlObject(dictDeviceControlObject):
    objDeviceControlObject = None
    try:
        objDeviceControlObject = DeviceControlObjectClass() #####

        objDeviceControlObject.Version = dictDeviceControlObject.get("Version")
        objDeviceControlObject.DeviceID = dictDeviceControlObject.get("DeviceID")
        objDeviceControlObject.RevokedJSONTokenIDs = dictDeviceControlObject.get("RevokedJSONTokenIDs")
        
        objDeviceControlObject.AllowedTLSRootCertificates = dictDeviceControlObject.get("AllowedTLSRootCertificates")
        
        
        listControlEndPoints = dictDeviceControlObject.get("ControlEndPoints")

        listControlEndPointsObjects = []
        for item in listControlEndPoints:
            objControlEndPointsClass = ControlEndPointsClass()

            dictAppEndPoint = item.get("AppEndPoint")

            objAppEndPointClass = AppEndPointClass() ####

            objAppEndPointClass.APIVersion = dictAppEndPoint.get("APIVersion")
            objAppEndPointClass.EndPointID = dictAppEndPoint.get("EndPointID")
            objAppEndPointClass.AccessToken = dictAppEndPoint.get("AccessToken")
            objControlEndPointsClass.AppEndPoint = objAppEndPointClass

            
            dictNetEndPoint = item.get("NetEndPoint")

            objNetEndPointClass = NetEndPointClass() ####

            objNetEndPointClass.APIVersion = dictNetEndPoint.get("APIVersion")
            objNetEndPointClass.EndPointID = dictNetEndPoint.get("EndPointID")
            
            listScheme = dictNetEndPoint.get("Scheme")
            for itemScheme in listScheme:
                objScheme = SchemeClass()
                objScheme.Protocol = itemScheme.get("Protocol")
                objScheme.Authority = itemScheme.get("Authority")
                objScheme.Role = itemScheme.get("Role")
                objScheme.AccessToken = itemScheme.get("AccessToken")
                objNetEndPointClass.Scheme.append(objScheme)
            objControlEndPointsClass.NetEndPoint = objNetEndPointClass

            listControlEndPointsObjects.append(objControlEndPointsClass)

        objDeviceControlObject.ControlEndPoints = listControlEndPointsObjects

    except Exception as ex:
        printDebug("Exception in SceneraBridgeLib -> StartSceneProcesses :" + str(ex))  
    
    return(objDeviceControlObject)
            
   
def GetDeviceControlObjectInfo(objDeviceControlObject):
    DeviceID = ""
    EndPointID = ""
    Authority = ""
    AccessToken = ""
    try:
        DeviceID = objDeviceControlObject.DeviceID
        EndPointID = objDeviceControlObject.ControlEndPoints[0].NetEndPoint.EndPointID
        Authority = objDeviceControlObject.ControlEndPoints[0].NetEndPoint.Scheme[0].Authority   
        AccessToken = objDeviceControlObject.ControlEndPoints[0].NetEndPoint.Scheme[0].AccessToken 
    except Exception as ex:
        printDebug("Exception in Scenera_ManagementObject -> GetManagementObjectInfo :" + str(ex))  

    return(DeviceID, EndPointID,Authority,AccessToken)

# https://scenera.atlassian.net/wiki/spaces/DEV/pages/370379337/NICE+Account+Service+Services#NICEAccountServiceServices-GetControlObject
dictDeviceControlObject = {
        "DeviceID": "00000001-5cdd-280b-8002-0df865fd7fca",
        "Version": "1.0",
        "ControlEndPoints": [
            {
                "AppEndPoint": {
                    "APIVersion": "1.0",
                    "EndPointID": "00000001-5eab-2e3d-8003-000100000001",
                    "X.509Certificate": [
                        "RFA3ZUd4d2FmYWFlOWxDbmZGMTlraWF4bzNvRHk0SHg="
                    ],
                    "AccessToken": "AccessToken obtained from Active Directory for the DataPipelineController"
                },
                "NetEndPoint": {
                    "APIVersion": "1.0",
                    "EndPointID": "00000001-5eab-2e3d-8003-000100000001",
                    "Scheme": [
                        {
                            "Protocol": "WebAPI",
                            "Authority": "controller.scenera.io",
                            "Role": "Client",
                            "AccessToken": "Same AccessToken as in AppEndPoint field obtained from Active Directory"
                        }
                    ]
                }
            }
        ],
        "RevokedJSONTokenIDs": [],
        "AllowedTLSRootCertificates": []
    }
    

#objDeviceControlObject = GetDeviceControlObject(dictDeviceControlObject)
#DeviceID, EndPointID, Authority, AccessToken = GetDeviceControlObjectInfo(objDeviceContrcreate_scenemark3olObject)
#print(DeviceID)