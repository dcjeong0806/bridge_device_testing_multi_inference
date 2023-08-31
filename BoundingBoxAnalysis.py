# Scenera Bounding Box Analysis Version 1.0
# Andre Jacobs 
# 2020 07 16

import numpy as math
import time


class BoundingBoxClass:
    strType = ""
    xmax = 0
    xmin = 0
    ymax = 0
    ymin = 0 
    iCameraHeight = 0
    iCameraWidth = 0

class ObjectAnalysisClass:
    iArea = 0
    iXCenterPos = 0
    iYCenterPos = 0
    timeDetection = 0
    strType = ""
    xmax = 0
    xmin = 0
    ymax = 0
    ymin = 0
    iCameraHeight = 0
    iCameraWidth = 0

listObjectToAnalyse = []
listObjectToAnalyseFalling = []
prevTimeDoingLoiteringAnalysis = 0
iPrevAreaLargest = 0
iPrevXCenterPointLargest = 0
iPrevYCenterPointLargest = 0


def MovementAnalysis(listBoundingBoxes):
    global iPrevAreaLargest
    global iPrevXCenterPointLargest
    global iPrevYCenterPointLargest
    global listObjectToAnalyse
    global prevTimeDoingLoiteringAnalysis
    fLoiteringDetected = False
    listObjectsLoiteringDetected = []
    fFightDetection = False
    listObjectsFightingDetected = []
    fMovementAnalysed = False
    fFallDetected = False
    listObjectsFallingDetected = []
    strType = ""
    
    iTimePeriodForAnalysis_sec = 10
    floatPrecentageObjectSizeChangeAllowed = 50.0
    floatPrecentageDistanceChangeAllowed = 50.0
    floatPrecentageDistanceForFightingDetection = 5.0
    floatFallAspectRatio = 1.0

    try:
        timeNow = time.time()
        floatSampelPeriod_sec = 1.0
        if (timeNow - prevTimeDoingLoiteringAnalysis >= floatSampelPeriod_sec):    
            fMovementAnalysed = True
            prevTimeDoingLoiteringAnalysis = timeNow
            iAreaLargest = 0
            xCenterPointLargest = 0
            yCenterPointLargest = 0
            fValidPersonDetection = False
            xmin = 0
            xmax = 0
            ymin = 0
            ymax = 0
            iCameraHeight = 0
            iCameraWidth = 0
            #Find the Largest object
            for obj in listBoundingBoxes:
                print(obj.strType,"#####",obj.iCameraHeight, obj.iCameraWidth)
                if (obj.strType == 'person'):
                    # check that person is properly in the the view 
                    iSideTolerance = int(float(obj.iCameraWidth) * 0.01)

                    #print("########iSideTolerance",iSideTolerance)
                    #print("#####",obj.xmin,iSideTolerance,":::",obj.xmax,(obj.iCameraWidth - iSideTolerance),":::",obj.ymin,iSideTolerance,":::",obj.ymax,(obj.iCameraHeight - iSideTolerance))
                    if ((obj.xmin > iSideTolerance) and (obj.xmax < (obj.iCameraWidth - iSideTolerance)) and (obj.ymin > iSideTolerance) and (obj.ymax < (obj.iCameraHeight - iSideTolerance))):
                        #Determine Size of object
                        iHeightPerson = int(obj.ymax - obj.ymin)
                        iWidthPerson = int(obj.xmax - obj.xmin)
                        iArea = iHeightPerson * iWidthPerson
                        if (iArea > iAreaLargest):
                            fValidPersonDetection = True
                            strType = obj.strType
                            iAreaLargest = iArea
                            xCenterPointLargest = int(float(obj.xmax + obj.xmin)/2.0)
                            yCenterPointLargest = int(float(obj.ymax + obj.ymin)/2.0)
                            xmin = obj.xmin
                            xmax = obj.xmax
                            ymin = obj.ymin
                            ymax = obj.ymax
                            iCameraHeight = obj.iCameraHeight
                            iCameraWidth = obj.iCameraWidth

            if (fValidPersonDetection):
                objPerson = ObjectAnalysisClass()
                objPerson.strType = strType
                objPerson.iArea = iAreaLargest
                objPerson.iXCenterPos = xCenterPointLargest
                objPerson.iYCenterPos = yCenterPointLargest
                objPerson.timeDetected = time.time()
                objPerson.xmin = xmin
                objPerson.xmax = xmax
                objPerson.ymin = ymin
                objPerson.ymax = ymax
                objPerson.iCameraHeight = iCameraHeight
                objPerson.iCameraWidth = iCameraWidth
                listObjectToAnalyse.append(objPerson)

            # Only keep objects in time period to analyse
            listObjectToAnalyseFalling = []
            listNewObjectToAnalyse = []
            for objPersonItem in listObjectToAnalyse:
                timeDelta = time.time() - objPersonItem.timeDetected
                if (timeDelta < iTimePeriodForAnalysis_sec):
                    listNewObjectToAnalyse.append(objPersonItem)
                if (timeDelta <= 5):
                    listObjectToAnalyseFalling.append(objPersonItem)
            listObjectToAnalyse = listNewObjectToAnalyse
            
            fFallDetected, listObjectsFallingDetected = CheckForFalling(listObjectToAnalyseFalling, True, floatFallAspectRatio)
            
            print("Person Object in List = " + str(len(listObjectToAnalyse)))
            iRequiredNumberOfObjects = int(float(iTimePeriodForAnalysis_sec)/floatSampelPeriod_sec)/2
            if (len(listObjectToAnalyse) >= iRequiredNumberOfObjects):   # Require at least 50% of Samples
                fLoiteringDetected, listObjectsLoiteringDetected = CheckForLoitering(listObjectToAnalyse, floatPrecentageObjectSizeChangeAllowed, floatPrecentageDistanceChangeAllowed)       
                fFightDetection, listObjectsFightingDetected = CheckForFighting(listObjectsLoiteringDetected, fLoiteringDetected, floatPrecentageDistanceChangeAllowed, floatPrecentageDistanceForFightingDetection)
                
               
    except Exception as ex:
        print("Exception in LoiteringDetection : " + str(ex))
    return(fMovementAnalysed, fLoiteringDetected, listObjectsLoiteringDetected, fFightDetection, listObjectsFightingDetected, fFallDetected, listObjectsFallingDetected ) 


def CheckForLoitering(listObjectToAnalyse, floatPrecentageObjectSizeChangeAllowed, floatPrecentageDistanceChangeAllowed):
    fLoiteringDetected = False
    try:
        iCount = 0
        iTotalArea = 0
        for item in listObjectToAnalyse:
            iTotalArea += item.iArea
            iCount += 1
            #print(str(iCount) + " ) " + str(item.iArea) )
        iAverageSize = int(float(iTotalArea)/float(iCount))
        #print(" Average = " + str(iAverageSize) )

        # Check if all the sizes are more or less the same 
        fAllSizeTestPassed = True
        iHowManyFailedCheck = 0
        listNewObjectToAnalyse = []
        for item in listObjectToAnalyse:
            if IsValueInTolerance(item.iArea, iAverageSize, floatPrecentageObjectSizeChangeAllowed):
                listNewObjectToAnalyse.append(item)
            else:
                iHowManyFailedCheck += 1
                iNumberOfErrorsAllowed = int(float(len(listObjectToAnalyse))*0.2) # Allow for 20% errors
                if (iHowManyFailedCheck >= iNumberOfErrorsAllowed ): 
                    fAllSizeTestPassed = False
                    break
        listObjectToAnalyse = listNewObjectToAnalyse

        if (fAllSizeTestPassed):
            #Check if objects are in the required distance drom each other
            fFirtsObject = True
            fIsObjectsInRequiredDistance = True
            iHowManyFailedCheck = 0
            iNumberOfErrorsAllowed = int(float(len(listObjectToAnalyse))*0.2) # Allow for 20% errors
            listNewObjectToAnalyse = []
            for item in listObjectToAnalyse:
                if fFirtsObject:
                    objFirst = item
                    fFirtsObject = False
                else:
                    iDistanceBetweenObjects = CalculateDistancebetweenTwoObjects(objFirst, item)
                    iRequiredDistance = (item.iCameraWidth * (floatPrecentageDistanceChangeAllowed/100.0))
                    if (iDistanceBetweenObjects > iRequiredDistance):
                        iHowManyFailedCheck += 1
                        if (iHowManyFailedCheck >= iNumberOfErrorsAllowed):
                            fIsObjectsInRequiredDistance = False
                    else:
                        listNewObjectToAnalyse.append(item)
            listObjectToAnalyse = listNewObjectToAnalyse

        fLoiteringDetected = fAllSizeTestPassed and fIsObjectsInRequiredDistance
    except Exception as ex:
        print("Exception in CheckForLoitering : " + str(ex))
            
    return(fLoiteringDetected, listObjectToAnalyse)

def CheckForFighting(listObjectToAnalyse, fLoiteringDetected, floatPrecentageDistanceChangeAllowed, floatPrecentageDistanceForFightingDetection):
    fFightDetected = False
    try:
        if fLoiteringDetected:
            fFirtsObject = True
            iTotalDistanceTravelled = 0
            for item in listObjectToAnalyse:
                if fFirtsObject:
                    objPrev = item
                    iRequiredDistance = (item.iCameraWidth * (floatPrecentageDistanceChangeAllowed/100.0))
                    fFirtsObject = False
                else:
                    iDistanceToNextPosition = CalculateDistancebetweenTwoObjects(objPrev, item)
                    iTotalDistanceTravelled += iDistanceToNextPosition
                    objPrev = item

            iNumberOfObjects = len(listObjectToAnalyse)          
            iMaxPotentialDistance = iRequiredDistance * iNumberOfObjects
            fReqDistanceForFighting = False
            floatPrecentage = ((float(iTotalDistanceTravelled) / float(iMaxPotentialDistance)) * 100.0)
            #print("iTotalDistanceTravelled=" + str(iTotalDistanceTravelled) + " [" + str(floatPrecentage) + " %]")
            if (floatPrecentage > floatPrecentageDistanceForFightingDetection):
                fReqDistanceForFighting = True

            fFightDetected = fReqDistanceForFighting
    except Exception as ex:
        print("Exception in CheckForFightDetection : " + str(ex))      

    return(fFightDetected, listObjectToAnalyse)

def CheckForFalling(listObjectToAnalyse, fLoiteringDetected, floatFallAspectRatio):
    fFallDetected = False
    try:
        if fLoiteringDetected:
            iFallDetectedCount = 0
            listNewObjectToAnalyse = []
            for item in listObjectToAnalyse:
                fFallDetected, floatDetectedRation = FallDetection(item, floatFallAspectRatio)
                if fFallDetected:
                    iFallDetectedCount += 1
                    listNewObjectToAnalyse.append(item)
            if (iFallDetectedCount >= 1):    
                fFallDetected = True

    except Exception as ex:
        print("Exception in CheckForFalling : " + str(ex))      

    return(fFallDetected, listNewObjectToAnalyse)

def IsValueInTolerance(iValue, iRefValue, floatPresTolerance):
    fValueInTolerance = False
    try:
        iMinValue = int(float(iRefValue) * ((100.0 - floatPresTolerance)/100.0))
        iMaxValue = int(float(iRefValue) * ((100.0 + floatPresTolerance)/100.0))
        if ((iValue > iMinValue) and (iValue < iMaxValue)):
            fValueInTolerance = True
    except:
        pass
    return(fValueInTolerance)

def CalculateDistancebetweenTwoObjects(obj1, obj2):
    iDistance = 0
    try:
        # What is the Distance between the object 
        iXDif = abs(obj1.iXCenterPos - obj2.iXCenterPos)
        iYDif = abs(obj1.iYCenterPos - obj2.iYCenterPos)
        iDistance = int(math.sqrt( (iXDif * iXDif) + (iYDif * iYDif)))
    except:
        pass
    return(iDistance)

def FallDetection(obj, floatFallAspectRatio):
    fFallDetected = False
    floatDetectedRation = 0
    try:
        iSideTolerance = int(float(obj.iCameraWidth) * 0.01)
        if (obj.strType == 'person'):
            # check that person is properly in the the view 
            if ((obj.xmin > iSideTolerance) and (obj.xmax < (obj.iCameraWidth - iSideTolerance)) and (obj.ymin > iSideTolerance) and (obj.ymax < (obj.iCameraHeight - iSideTolerance))):
                iHeightPerson = int(obj.ymax - obj.ymin)
                iWidthPerson = int(obj.xmax - obj.xmin)
                floatDetectedRation = float(iHeightPerson) / float(iWidthPerson)
                if(floatDetectedRation <=  floatFallAspectRatio):
                    fFallDetected = True
    except Exception as ex:
        print("Exception in FallDetection : " + str(ex))
    return(fFallDetected, floatDetectedRation) 


