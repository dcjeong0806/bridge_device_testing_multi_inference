from PythonUtils import printDebug, GetDateTime

def CreateCMFHeaders(jsonBody, SourceEndPointID, DestinationEndPointID, strCommandType ):
    jsonRequestCMP = {}
    try:
        Version = "1.0"
        MessageType = "request"  
        CommandID = 0
        DateTimeStamp = GetDateTime() 
        jsonRequestCMP = { "Version": Version,"MessageType": MessageType, "SourceEndPointID": SourceEndPointID,"DestinationEndPointID": DestinationEndPointID,"DateTimeStamp": DateTimeStamp,"CommandID": CommandID,"CommandType": strCommandType,"Payload": jsonBody}

    except Exception as ex:
        print("Exception in SceneMode -> CreateCMFHeadersSceneMode:" + str(ex))

    return(jsonRequestCMP)
