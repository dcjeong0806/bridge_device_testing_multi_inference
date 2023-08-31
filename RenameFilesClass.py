from os import walk, remove
import os
from os.path import isfile, join, getctime, getmtime
import time
from time import sleep
import threading
import datetime


def modification_date(filename):
    t = getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def DeleteFile(strPathFilename):
    try:
        os.remove(strPathFilename)
        #print("### Delete File:" + strPathFilename)
    except Exception as ex:
        print("Exception in DeleteFile:" + strPathFilename + " Exception:" + str(ex))

def printDebug(strMessage):
    strTime = time.strftime("%H:%M:%S")
    print(strTime + " : " + strMessage)


def RenameFilesThread(rootFolder):
    strStatus = ""
    try:
        for (dirpath, dirnames, filenames) in walk(rootFolder):
            for file in filenames:
                time.sleep(0.1)
                if ("__pycache__" in dirpath):
                    if ("cpython" in file) and ("pyc" in file):
                        try:
                            print("Process File : " + file)
                            listFileSplit = file.split(".")
                            newFile = listFileSplit[0] + "." + listFileSplit[2]
                            origPathFile = os.path.join(dirpath, file)
                            newPathFile = os.path.join(dirpath, newFile)
                            os.rename(origPathFile, newPathFile)
                            print("New File Name : " + newFile)
                        except:
                            pass
                    else:
                        print("Ignore File : " + file)
                else:
                    print("Ignore Folder : " + dirpath)
                
                            #DeleteFile(strFullPathName)

        #command = "/bin/mv ./" + rootFolder + "/* ./"
        #os.system(command)
        #command = "/bin/rm -rf *.py"
        #os.system(command)
    except Exception as ex:
        print("Exception as RenameFilesThread:" + str(ex))
        



rootFolder = "__pycache__"
RenameFilesThread(rootFolder)

