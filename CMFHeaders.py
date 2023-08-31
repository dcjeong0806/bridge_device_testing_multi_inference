def CreateCMFHeaders(jsonBody, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, accessToken):
    jsonRequestCMP = {}
    try:
        Version = "1.0"
        AccessToken = accessToken
        MessageType = "request"
        DestinationEndPointID = strCloudServerUUID
        SourceEndPointID = strBrigdeUUID
        CommandID = 4
        #/[Version]/[EndPointID]/data/[NodeID]/[PortID]/[API_NAME]
        CommandType = "/1.0/"+  strCloudServerUUID  + "/data/" + str(NodeID)  + "/" + str(PortID)  + "/SetSceneData"  
        #AccessToken = "dummy-access-token"
        DateTimeStamp = "2019-12-24T15:59:01.938Z"
        EncryptionOn = False
        #disctRequestCMP = {"Version": Version, "MessageType": MessageType, "SourceEndPointID": SourceEndPointID , "DestinationEndPointID": DestinationEndPointID, "CommandID" : CommandID , "CommandType" : CommandType, "AccessToken": AccessToken,"DateTimeStamp": DateTimeStamp, "EncryptionOn": EncryptionOn, "Payload":{"Body": jsonBody} }
        disctRequestCMP = {"Version": Version, "AccessToken":AccessToken, "MessageType": MessageType, "SourceEndPointID": SourceEndPointID , "DestinationEndPointID": DestinationEndPointID, "CommandID" : CommandID , "CommandType" : CommandType, "DateTimeStamp": DateTimeStamp, "EncryptionOn": EncryptionOn, "Payload":{"Body": jsonBody}}

        jsonRequestCMP = disctRequestCMP

    except Exception as ex:
        print("Exception in CreateCMFHeaders:" + str(ex))

    return(jsonRequestCMP)


def CreateCMFHeaders2(jsonBody, strBrigdeUUID, strCloudServerUUID, NodeID, PortID, accessToken,SelfCheckYn,SelfCheckReportTime):
    jsonRequestCMP = {}
    try:
        Version = "1.0"
        AccessToken = accessToken
        MessageType = "request"
        DestinationEndPointID = strCloudServerUUID
        SourceEndPointID = strBrigdeUUID
        CommandID = 4
        #/[Version]/[EndPointID]/data/[NodeID]/[PortID]/[API_NAME]
        CommandType = "/1.0/"+  strCloudServerUUID  + "/data/" + str(NodeID)  + "/" + str(PortID)  + "/SetSceneData"  
        #AccessToken = "dummy-access-token"
        DateTimeStamp = "2019-12-24T15:59:01.938Z"
        EncryptionOn = False
        #disctRequestCMP = {"Version": Version, "MessageType": MessageType, "SourceEndPointID": SourceEndPointID , "DestinationEndPointID": DestinationEndPointID, "CommandID" : CommandID , "CommandType" : CommandType, "AccessToken": AccessToken,"DateTimeStamp": DateTimeStamp, "EncryptionOn": EncryptionOn, "Payload":{"Body": jsonBody} }
        disctRequestCMP = { "SelfCheckYn":SelfCheckYn,"SelfCheckReportTime":SelfCheckReportTime, "Version": Version, "AccessToken":AccessToken, "MessageType": MessageType, "SourceEndPointID": SourceEndPointID , "DestinationEndPointID": DestinationEndPointID, "CommandID" : CommandID , "CommandType" : CommandType, "DateTimeStamp": DateTimeStamp, "EncryptionOn": EncryptionOn, "Payload":{"Body": jsonBody}}

        jsonRequestCMP = disctRequestCMP

    except Exception as ex:
        print("Exception in CreateCMFHeaders:" + str(ex))

    return(jsonRequestCMP)