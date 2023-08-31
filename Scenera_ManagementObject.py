from PythonUtils import printDebug
from RestAPI import RestAPIPost
from Scenera_Utills import CreateCMFHeaders


class ManagementObjectClass:
    NICEAS = None
    FirmwareSourceCertificates = []
    AllowedTLSRootCertificates = []
    DeviceID = ""
    ExpiryDateTime = ""
    Version = 1.0
    FirmwareSourceID = ""
    DeviceCertificate = ""

class NICEASClass:
    NICEASEndPoint = None 
    NICEASID = ""
    NICEASName = ""
    RevokedJSONTokenIDs = []

class NICEASEndPointClass:
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

def GetManagementObject(strNICELAEAuthority, strBrigdeUUID, strNICELAEndPoint):  
    global dictManagementObject
    objManagementEndPoint = None

    try:
        dictPayload = { "Body": { "DeviceID" : strBrigdeUUID }}
        strCommandType = "/1.0/0000001-5eab-2e11-8003-000000000000/management/GetManagementObject"

        dictCMF = CreateCMFHeaders(dictPayload, strBrigdeUUID, strNICELAEndPoint, strCommandType )
        
        #printDebug(str(dictCMF))

        URL_NICELA = "http://" + strNICELAEAuthority + "/device/GetManagementObject"

        #print(URL_NICELA)
        
        dictReturn = RestAPIPost(URL_NICELA, dictCMF)
        dictPayload = dictReturn.get("Payload")
        dictManagementObject = dictPayload.get("Body")
        #printDebug(str(dictManagementObject)) 

        objManagementEndPoint = ProcessManagementObject(dictManagementObject)
        
    except Exception as ex:
        print("Exception in SceneMode.py -> GetSceneMode : " + str(ex)) 

    return(objManagementEndPoint)

def ProcessManagementObject(dictManagementObject):
    objManagementObjectClass = None
    try:
        objManagementObjectClass = ManagementObjectClass() #####

        objManagementObjectClass.DeviceCertificate = dictManagementObject.get("DeviceCertificate")
        objManagementObjectClass.DeviceID = dictManagementObject.get("DeviceID")
        objManagementObjectClass.Version = dictManagementObject.get("Version")
        objManagementObjectClass.ExpiryDateTime = dictManagementObject.get("ExpiryDateTime")
        objManagementObjectClass.FirmwareSourceID = dictManagementObject.get("FirmwareSourceID")
        objManagementObjectClass.AllowedTLSRootCertificates = dictManagementObject.get("AllowedTLSRootCertificates")
        objManagementObjectClass.FirmwareSourceCertificates = dictManagementObject.get("FirmwareSourceCertificates")
        
        dictNICEAS = dictManagementObject.get("NICEAS")
        
        objNICEAS = NICEASClass() #####

        objNICEAS.NICEASID = dictNICEAS.get("NICEASID")
        objNICEAS.NICEASName = dictNICEAS.get("NICEASName")
        objNICEAS.RevokedJSONTokenIDs = dictNICEAS.get("RevokedJSONTokenIDs")

        dictNICEASEndPoint = dictNICEAS.get("NICEASEndPoint")

        objNICEASEndPoint = NICEASEndPointClass() #####

        dictAppEndPoint = dictNICEASEndPoint.get("AppEndPoint")

        objAppEndPointClass = AppEndPointClass() ####

        objAppEndPointClass.APIVersion = dictAppEndPoint.get("APIVersion")
        objAppEndPointClass.EndPointID = dictAppEndPoint.get("EndPointID")
        objAppEndPointClass.AccessToken = dictAppEndPoint.get("AccessToken")
        objNICEASEndPoint.AppEndPoint = objAppEndPointClass

        
        dictNetEndPoint = dictNICEASEndPoint.get("NetEndPoint")

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
        objNICEASEndPoint.NetEndPoint = objNetEndPointClass

        objNICEAS.NICEASEndPoint = objNICEASEndPoint

        objManagementObjectClass.NICEAS = objNICEAS

    except Exception as ex:
        printDebug("Exception in SceneraBridgeLib -> StartSceneProcesses :" + str(ex))  
    
    return(objManagementObjectClass)
            
            
def GetManagementObjectInfo(objGetManagementObject):
    EndPointID = ""
    Authority = ""
    AccessToken = ""
    try:
        EndPointID = objGetManagementObject.NICEAS.NICEASEndPoint.NetEndPoint.EndPointID
        Authority = objGetManagementObject.NICEAS.NICEASEndPoint.NetEndPoint.Scheme[0].Authority   
        AccessToken = objGetManagementObject.NICEAS.NICEASEndPoint.NetEndPoint.Scheme[0].AccessToken 
    except Exception as ex:
        printDebug("Exception in Scenera_ManagementObject -> GetManagementObjectInfo :" + str(ex))  

    return(EndPointID,Authority,AccessToken)

#objGetManagementObject = GetManagentObject(dictManagementObject)
#EndPointID,Authority,AccessToken = GetManagementObjectInfo(objGetManagementObject)
