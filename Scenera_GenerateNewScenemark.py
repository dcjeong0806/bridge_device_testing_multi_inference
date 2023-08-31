
import json
from PythonUtils import printDebug

# Device ID (DeviceId):
# a GUID / UUID, globally unique

# Device Node Id (DeviceNodeId):
# {DeviceID}-{NodeId}, where NodeId is a 4 digit hex number unique on the device

# SceneMark Id:
# SMK_{DeviceNodeID}_{ItemNumber}, where ItemNumber is a sequential number, 64 bit, padded with zeros, unique to the device node

# SceneData Id (DataID):
# SDT_{DeviceNodeID}_{ItemNumber}, where ItemNumber is a sequential number, 64 bit, padded with zeros, unique to the device node


class SceneMarkValues:
    SceneMarkID = ""
    TimeStamp = ""
    NodeID = ""
    PortID = ""
    Version = "1.0"
    DestinationID = ""
    SceneMarkStatus = "Active"
    SceneMode = "Human"

    Status = "Upload in Progress"

    Thumbnail_SceneMarkID = ""

    CustomAnalysisID =  ""
    AnalysisDescription = "Yolo v3 configured to detect Human"
    ProcessingStatus = "Detect"
    AlgorithmID = "12345678-1234-1234-1234-123456789abc"
    NICEItemType = "Human"
    CustomItemType = ""
    Resolution_Height = 86
    Resolution_Width = 116
    XCoordinate = 289
    YCoordinate = 69
    DetectedObjects_ThumbnailSceneDataID = ""
    DetectedObjects_Thumbnail_dictEncryption = {}
    
    DetectedObjects_Image_SceneDataID = ""
    DetectedObjects_Image_dictEncryption = {}

    DetectedObjects_Video_SceneDataID = ""
    DetectedObjects_Video_dictEncryption = {}
    
    SceneDataID = ""
    TimeStamp = ""
    SourceNodeID = ""
    SourceNodeDescription = "Description of Node that generated SceneData"
    
    Video_Duration = "30"
    
    Thumbnail_DataType = "RGBStill"
    DetectedObjects_Image_DataType = "RGBStill"
    DetectedObjects_Video_DataType = "RGBVideo"
    

    Thumbnail_MediaFormat  = "JPEG"
    DetectedObjects_Image_MediaFormat = "JPEG"
    DetectedObjects_Video_MediaFormat = "H.264"

    DetectedObjects_Image_SceneDataURI = ""
    #DetectedObjects_Video_MediaFormat = ""
    DetectedObjects_Video_SceneDataURI = ""

    ProcessTimeList = None


def CreateSceneMark2(objSM,SelfCheckYn,SelfCheckReportTime):
    #if(objSM.sm_meta_info.camera_info.ShowError == "Y"):
    #    print_string = "####### {} : {} : {} : {}".format(objSM.DetectedObjects_Thumbnail_SceneDataID, objSM.TimeStamp, objSM.SourceNodeID,objSM.DetectedObjects_Thumbnail_MediaFormat)
    #    print(print_string)

    detected_objects_list = []
    for item in objSM.detected_object_info_list:
        init_string = {
            "AlgorithmID": item.AlgorithmID,
            "NICEItemType": item.NICEItemType,
            "CustomItemType" : item.CustomItemType,
            "BoundingBox": {"XCoordinate": item.XCoordinate,"YCoordinate": item.YCoordinate,"Height": item.Resolution_Height,"Width": item.Resolution_Width},
            "ThumbnailSceneDataID":objSM.DetectedObjects_Thumbnail_SceneDataID,
            "RelatedSceneData": [objSM.DetectedObjects_Image_SceneDataID, objSM.DetectedObjects_Video_SceneDataID]
        }
        init_item_string = json.dumps(init_string)
        init_item_dict = json.loads(init_item_string)
        detected_objects_list.append(init_item_dict)

    scenedata_list = []
    init_string = {
            "SceneDataID": objSM.DetectedObjects_Thumbnail_SceneDataID,
            "TimeStamp": objSM.TimeStamp,
            "SourceNodeID": objSM.SourceNodeID,
            "SourceNodeDescription": objSM.SourceNodeDescription,
            "DataType": objSM.DetectedObjects_Thumbnail_DataType,
            "Status": objSM.Status,
            "Encryption": {
                "EncryptionOn": "False"
            },
            "MediaFormat": objSM.DetectedObjects_Thumbnail_MediaFormat,
            "SceneDataURI": objSM.DetectedObjects_Thumbnail_SceneDataURI,
        }
    init_item_string = json.dumps(init_string)
    init_item_dict = json.loads(init_item_string)
    #print(init_item_dict)

    scenedata_list.append(init_item_dict)


    init_string = {
            "SceneDataID": objSM.DetectedObjects_Image_SceneDataID,
            "TimeStamp": objSM.TimeStamp,
            "SourceNodeID": objSM.SourceNodeID,
            "SourceNodeDescription": objSM.SourceNodeDescription,
            "DataType": objSM.DetectedObjects_Image_DataType,
            "Status": objSM.Status,
            "Encryption": {
                "EncryptionOn": "False"
            },
            "MediaFormat": objSM.DetectedObjects_Image_MediaFormat,
            "SceneDataURI": objSM.DetectedObjects_Image_SceneDataURI,
        }
    init_item_string = json.dumps(init_string)
    init_item_dict = json.loads(init_item_string)
    #print(init_item_dict)

    scenedata_list.append(init_item_dict)

    init_string = {
        "SceneDataID": objSM.DetectedObjects_Video_SceneDataID,
        "TimeStamp": objSM.TimeStamp,
        "SourceNodeID": objSM.SourceNodeID,
        "SourceNodeDescription": objSM.SourceNodeDescription,
        "DataType": objSM.DetectedObjects_Video_DataType,
        "Status": objSM.Status,
        "Duration": objSM.Video_Duration,
        "Encryption": {
            "EncryptionOn": "False"
        },
        "MediaFormat": objSM.DetectedObjects_Video_MediaFormat,
        "SceneDataURI": objSM.DetectedObjects_Video_SceneDataURI,
    }

    init_item_string = json.dumps(init_string)
    init_item_dict = json.loads(init_item_string)
    scenedata_list.append(init_item_dict)
    #print(init_item_dict)
    

    dictSceneMark = {
        "SelfCheckYn":SelfCheckYn,
        "SelfCheckReportTime":SelfCheckReportTime,    
        "SceneMarkID": objSM.SceneMarkID,
        "TimeStamp": objSM.TimeStamp,
        "NodeID": objSM.NodeID,
        "PortID": objSM.PortID,
        "Version": objSM.Version,
        "DestinationID": objSM.DestinationID,
        "SceneMarkStatus": objSM.SceneMarkStatus,
        "VersionControl":{
            "VersionList":[]
        },
        "SceneModeConfig":objSM.SceneModeConfig,
        "AnalysisList": [{
            "VersionNumber": 1,
            "SceneMode": objSM.SceneMode,
            "CustomAnalysisID": objSM.CustomAnalysisID,
            "AnalysisDescription": objSM.AnalysisDescription,
            "ProcessingStatus": objSM.ProcessingStatus
        }],
        "ThumbnailList": [{
            "VersionNumber": 1,
            "SceneDataID" : objSM.DetectedObjects_Thumbnail_SceneDataID
        }],
        "DetectedObjects": detected_objects_list,
        "SceneDataList": scenedata_list
    }

    return(dictSceneMark)


def CreateSceneMark(objSM):
    #if(objSM.sm_meta_info.camera_info.ShowError == "Y"):
    #    print_string = "####### {} : {} : {} : {}".format(objSM.DetectedObjects_Thumbnail_SceneDataID, objSM.TimeStamp, objSM.SourceNodeID,objSM.DetectedObjects_Thumbnail_MediaFormat)
    #    print(print_string)

    detected_objects_list = []
    for item in objSM.detected_object_info_list:
        init_string = {
            "AlgorithmID": item.AlgorithmID,
            "NICEItemType": item.NICEItemType,
            "CustomItemType" : item.CustomItemType,
            "BoundingBox": {"XCoordinate": item.XCoordinate,"YCoordinate": item.YCoordinate,"Height": item.Resolution_Height,"Width": item.Resolution_Width},
            "ThumbnailSceneDataID":objSM.DetectedObjects_Thumbnail_SceneDataID,
            "RelatedSceneData": [objSM.DetectedObjects_Image_SceneDataID, objSM.DetectedObjects_Video_SceneDataID]
        }
        init_item_string = json.dumps(init_string)
        init_item_dict = json.loads(init_item_string)
        detected_objects_list.append(init_item_dict)

    scenedata_list = []
    init_string = {
            "SceneDataID": objSM.DetectedObjects_Thumbnail_SceneDataID,
            "TimeStamp": objSM.TimeStamp,
            "SourceNodeID": objSM.SourceNodeID,
            "SourceNodeDescription": objSM.SourceNodeDescription,
            "DataType": objSM.DetectedObjects_Thumbnail_DataType,
            "Status": objSM.Status,
            "Encryption": {
                "EncryptionOn": "False"
            },
            "MediaFormat": objSM.DetectedObjects_Thumbnail_MediaFormat,
            "SceneDataURI": objSM.DetectedObjects_Thumbnail_SceneDataURI,
        }
    init_item_string = json.dumps(init_string)
    init_item_dict = json.loads(init_item_string)
    #print(init_item_dict)

    scenedata_list.append(init_item_dict)


    init_string = {
            "SceneDataID": objSM.DetectedObjects_Image_SceneDataID,
            "TimeStamp": objSM.TimeStamp,
            "SourceNodeID": objSM.SourceNodeID,
            "SourceNodeDescription": objSM.SourceNodeDescription,
            "DataType": objSM.DetectedObjects_Image_DataType,
            "Status": objSM.Status,
            "Encryption": {
                "EncryptionOn": "False"
            },
            "MediaFormat": objSM.DetectedObjects_Image_MediaFormat,
            "SceneDataURI": objSM.DetectedObjects_Image_SceneDataURI,
        }
    init_item_string = json.dumps(init_string)
    init_item_dict = json.loads(init_item_string)
    #print(init_item_dict)

    scenedata_list.append(init_item_dict)

    init_string = {
        "SceneDataID": objSM.DetectedObjects_Video_SceneDataID,
        "TimeStamp": objSM.TimeStamp,
        "SourceNodeID": objSM.SourceNodeID,
        "SourceNodeDescription": objSM.SourceNodeDescription,
        "DataType": objSM.DetectedObjects_Video_DataType,
        "Status": objSM.Status,
        "Duration": objSM.Video_Duration,
        "Encryption": {
            "EncryptionOn": "False"
        },
        "MediaFormat": objSM.DetectedObjects_Video_MediaFormat,
        "SceneDataURI": objSM.DetectedObjects_Video_SceneDataURI,
    }

    init_item_string = json.dumps(init_string)
    init_item_dict = json.loads(init_item_string)
    scenedata_list.append(init_item_dict)
    #print(init_item_dict)
    

    dictSceneMark = {

        "SceneMarkID": objSM.SceneMarkID,
        "TimeStamp": objSM.TimeStamp,
        "NodeID": objSM.NodeID,
        "PortID": objSM.PortID,
        "Version": objSM.Version,
        "DestinationID": objSM.DestinationID,
        "SceneMarkStatus": objSM.SceneMarkStatus,
        "VersionControl":{
            "VersionList":[]
        },
        "SceneModeConfig":objSM.SceneModeConfig,
        "AnalysisList": [{
            "VersionNumber": 1,
            "SceneMode": objSM.SceneMode,
            "CustomAnalysisID": objSM.CustomAnalysisID,
            "AnalysisDescription": objSM.AnalysisDescription,
            "ProcessingStatus": objSM.ProcessingStatus
        }],
        "ThumbnailList": [{
            "VersionNumber": 1,
            "SceneDataID" : objSM.DetectedObjects_Thumbnail_SceneDataID
        }],
        "DetectedObjects": detected_objects_list,
        "SceneDataList": scenedata_list,
        "ProcessTimeList":objSM.ProcessTimeList
    }

    return(dictSceneMark)




'''
def CreateSceneMark(objSM):
    dictSceneMark = {}
    try:
        dictSceneMark = {
            "SceneMarkID": objSM.SceneMarkID,
            "TimeStamp": objSM.TimeStamp,
            "NodeID": objSM.NodeID,
            "PortID": objSM.PortID,
            "Version": objSM.Version,
            "DestinationID": objSM.DestinationID,
            "SceneMarkStatus": objSM.SceneMarkStatus,
            "VersionControl": {
            #"DataPipelineInstanceID": "d22b831b-4e08-4205-b2e7-52da898ae977",
            "VersionList": [ 
                # {
                #     "VersionNumber": 1,
                #     "DateTimeStamp": objSM.TimeStamp,
                #     "NodeID": objSM.NodeID
                #     #"NodeID": "NopNode"
                #     }
                ]
            },
            "AnalysisList": [{
                "VersionNumber": 1,
                "SceneMode": objSM.SceneMode,
                "CustomAnalysisID": objSM.CustomAnalysisID,
                "AnalysisDescription": objSM.AnalysisDescription,
                "ProcessingStatus": objSM.ProcessingStatus
            }],
            "ThumbnailList": [{
                "VersionNumber": 1,
                "SceneDataID" : objSM.Thumbnail_SceneDataID
            }],
            "DetectedObjects": [{
                "AlgorithmID": objSM.AlgorithmID,
                "NICEItemType": objSM.NICEItemType,
                "CustomItemType" : objSM.CustomItemType,
                "BoundingBox": {"XCoordinate": objSM.XCoordinate,"YCoordinate": objSM.YCoordinate,"Height": objSM.Resolution_Height,"Width": objSM.Resolution_Width},
                "ThumbnailSceneDataID" : objSM.DetectedObjects_ThumbnailSceneDataID,
                "RelatedSceneData": [objSM.DetectedObjects_Image_SceneDataID, objSM.DetectedObjects_Video_SceneDataID]
            }],
            "SceneDataList": [{
                "SceneDataID": objSM.Thumbnail_SceneDataID,
                "TimeStamp": objSM.TimeStamp,
                "SourceNodeID": objSM.SourceNodeID,
                "SourceNodeDescription": objSM.SourceNodeDescription,
                "DataType": objSM.Thumbnail_DataType,
                "Status": objSM.Status,
                "Encryption":  objSM.DetectedObjects_Thumbnail_dictEncryption,
                "MediaFormat": objSM.Thumbnail_MediaFormat,
                "SceneDataURI": objSM.Thumbnail_SceneDataURI,
                },
                {
                "SceneDataID": objSM.DetectedObjects_Image_SceneDataID,
                "TimeStamp": objSM.TimeStamp,
                "SourceNodeID": objSM.SourceNodeID,
                "SourceNodeDescription": objSM.SourceNodeDescription,
                "DataType": objSM.DetectedObjects_Image_DataType,
                "Status": objSM.Status,
                "Encryption": objSM.DetectedObjects_Image_dictEncryption,
                "MediaFormat": objSM.DetectedObjects_Image_MediaFormat,
                "SceneDataURI": objSM.DetectedObjects_Image_SceneDataURI,
                },
                {
                "SceneDataID": objSM.DetectedObjects_Video_SceneDataID,
                "TimeStamp": objSM.TimeStamp,
                "SourceNodeID": objSM.SourceNodeID,
                "SourceNodeDescription": objSM.SourceNodeDescription,
                "DataType": objSM.DetectedObjects_Video_DataType,
                "Duration": objSM.Video_Duration,
                "Status": objSM.Status,
                "Encryption": objSM.DetectedObjects_Video_dictEncryption,
                "MediaFormat": objSM.DetectedObjects_Video_MediaFormat,
                "SceneDataURI": objSM.DetectedObjects_Video_SceneDataURI,
                }]
        }
    except Exception as ex:
        printDebug("Exception in Scenera_CreateNewScenemark.py -> CreateSceneMark : " + str(ex)) 

    return(dictSceneMark)
'''

