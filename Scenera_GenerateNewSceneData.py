
class SceneDataValues:
    Version = ""
    DataID = ""
    FileType = ""
    FileName = ""
    PathURI = ""
    Section = 0
    LastSection = 0
    HashMethod = ""
    OriginalFileHash = ""
    SectionBase64 = ""
    RelatedSceneMarks = []


def CreateSceneData(objSD):
    dictSceneData = {
    "Version": objSD.Version, 
    "DataID":objSD.DataID,
    "FileType":objSD.FileType,
    "FileName":objSD.FileName,
    "PathURI":objSD.PathURI,
    "Section":objSD.Section,
    "LastSection":objSD.LastSection,
    "HashMethod":objSD.HashMethod,
    "OriginalFileHash":objSD.OriginalFileHash,
    "SectionBase64":objSD.SectionBase64,
    "RelatedSceneMarks": objSD.RelatedSceneMarks
    }
    return(dictSceneData)

