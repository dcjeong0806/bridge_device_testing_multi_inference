from PythonUtils import printDebug 

class DeviceSecurityObjectClass:
    Version = ""
    DeviceID = ""
    DevicePassword = ""
    NICELAEndPoint = None
    
class NICELAEndPointClass:
    APIVersion = "" 
    EndPointID = ""
    Scheme = []

class SchemeClass:
    Protocol = ""
    Authority = ""

def GetDeviceSecurityObject(dictDeviceSecurityObject):
    objDeviceSecurityObject = None
    try:
        objDeviceSecurityObject = DeviceSecurityObjectClass() #####
        objDeviceSecurityObject.DeviceID = dictDeviceSecurityObject.get("DeviceID")
        objDeviceSecurityObject.DevicePassword = dictDeviceSecurityObject.get("DevicePassword")
        objDeviceSecurityObject.Version = dictDeviceSecurityObject.get("Version")
        
        dictNICELAEndPoint = dictDeviceSecurityObject.get("NICELAEndPoint")
        objNICELAEndPoint = NICELAEndPointClass() #####

        objNICELAEndPoint.APIVersion = dictNICELAEndPoint.get("APIVersion")
        objNICELAEndPoint.EndPointID = dictNICELAEndPoint.get("EndPointID")
        
        listScheme = dictNICELAEndPoint.get("Scheme")
        for itemScheme in listScheme:
            objScheme = SchemeClass()
            objScheme.Protocol = itemScheme.get("Protocol")
            objScheme.Authority = itemScheme.get("Authority")
            objNICELAEndPoint.Scheme.append(objScheme)
        objDeviceSecurityObject.NICELAEndPoint = objNICELAEndPoint

    except Exception as ex:
        printDebug("Exception in Scenera_DeviceSecurityObject -> GetDeviceSecurityObject :" + str(ex))  
    
    return(objDeviceSecurityObject)
            


def GetDeviceID(objDeviceSecurityObject):
    try:
        strDeviceID = objDeviceSecurityObject.DeviceID
    except Exception as ex:
        printDebug("Exception in Scenera_DeviceSecurityObject -> GetDeviceID :" + str(ex))  
    return(strDeviceID)

def GetDevicePassword(objDeviceSecurityObject):
    try:
        strDevicePassword = objDeviceSecurityObject.DevicePassword
    except Exception as ex:
        printDebug("Exception in Scenera_DeviceSecurityObject -> GetDevicePassword :" + str(ex))  
    return(strDevicePassword)

def GetNICELAEndPointEndPoint(objDeviceSecurityObject):
    try:
        EndPointID = objDeviceSecurityObject.NICELAEndPoint.EndPointID
    except Exception as ex:
        printDebug("Exception in Scenera_DeviceSecurityObject -> GetNICELAEndPoint :" + str(ex))  
    return(EndPointID)

def GetNICELAEndPointAuthority(objDeviceSecurityObject):
    try:
        Authority = objDeviceSecurityObject.NICELAEndPoint.Scheme[0].Authority
    except Exception as ex:
        printDebug("Exception in Scenera_DeviceSecurityObject -> GetNICELAEndPoint :" + str(ex))  
    return(Authority)