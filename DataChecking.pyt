# -*- coding: utf-8 -*-
import arcpy
import glob
import os
import sys


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""
        # List of tool classes associated with this toolbox        
        self.tools = [CheckFieldExists,CheckFieldAttribution,CheckFieldContent,CheckAngle]


class CheckFieldExists(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "字段存在性检查"
        self.description = "用来检查数据库中的给定字段是否存在"
        self.canRunInBackground = False
    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None        
        return params
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""
        return
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""
        return
    def execute(self, parameters, messages):
        """The source code of the tool."""
        return


class CheckFieldAttribution(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "字段属性结构核查"
        self.description = "用来核查数据库中字段的名称、类型、字段长度等属性字段是否符合规范"
        self.canRunInBackground = False
    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None        
        return params
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""
        return
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""
        return
    def execute(self, parameters, messages):
        """The source code of the tool."""
        return


class CheckFieldContent(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "字段内容检查（值域检查）"
        self.description = "用来检查数据库中各字段的值域是否在给定范围内"
        self.canRunInBackground = False
    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None        
        return params
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""
        return
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""
        return
    def execute(self, parameters, messages):
        """The source code of the tool."""
        return


class CheckAngle(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "锐角检查"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入要素",
            name="in_dir1",
            datatype=["DEFeatureClass","GPFeatureLayer"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="最小角度",
            name="in_dir2",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param1.filter.type = "Range"
        param1.filter.list = [0,30]

        param2 = arcpy.Parameter(
            displayName="输出要素",
            name="in_dir3",
            datatype=["DEFeatureClass","GPFeatureLayer"],
            parameterType="Required",
            direction="Output")
        params = [param0,param1,param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        in_fc = parameters[0].valueAsText
        angle = parameters[1].valueAsText
        out_fc = parameters[2].valueAsText
        check_angle(in_fc,float(angle),out_fc)
        return


# 下面是具体的工具

def check_field_exists():
    pass


class Point:
    X=0
    Y=0

    
def caculate_angle(pointArray,angle,sr):
    pt_geom_list = []
    FLAG = False
    if len(pointArray)<3:
        return False
    for i in range(0, len(pointArray)):
        ptL=Point()
        ptM=Point()
        ptR=Point()     
        if i<len(pointArray)-2:
            ptL=pointArray[i]
            ptM=pointArray[i+1]
            ptR=pointArray[i+2]
        elif i==len(pointArray)-2:
            ptL = pointArray[i]
            ptM = pointArray[i + 1]
            ptR = pointArray[0]
        elif i == len(pointArray) - 1:
            ptL = pointArray[i]
            ptM = pointArray[0]
            ptR = pointArray[1]
        AML=Point()
        AML.X=ptL.X-ptM.X
        AML.Y=ptL.Y-ptM.Y
 
        AMR=Point()
        AMR.X=ptR.X-ptM.X
        AMR.Y = ptR.Y - ptM.Y
 
        ab=(AML.X*AMR.X+AML.Y*AMR.Y)
        M=(math.sqrt(AML.X*AML.X+AML.Y*AML.Y)*math.sqrt(AMR.X*AMR.X+AMR.Y*AMR.Y))
        cosA=ab/M
        # print(i,ptL.X,ptL.Y,ptR.X,ptR.Y,cosA)
 
        #向量乘积小于0，说明是大于90度，不用判断
        if ab<0:
            continue
        #因为0到π/2是递减,所以小于cos给定角度值，那么角度比给定角度值大,就返回了
        elif cosA<=math.cos(angle/180*math.pi):
            continue
        elif cosA>math.cos(angle/180*math.pi):
            # 建立一个点文件
            print(ptM.X,ptM.Y)
            pt = arcpy.Point(ptM.X,ptM.Y)
            pt_geom = arcpy.PointGeometry(pt,spatial_reference=sr)
            pt_geom_list.append(pt_geom)
            FLAG = True
    # 遍历所有的顶点了，说明满足要求
    return pt_geom_list
 
 
def check_angle(in_fc,angle,out_fc):
    pt_geom_lists = []
    sr = arcpy.Describe(in_fc).spatialReference
    for row in arcpy.da.SearchCursor(in_fc, ["OBJECTID", "SHAPE@"]):
        ID = row[0]
        tempPart = []
        partnum = 0
        for part in row[1]:
            print("Part {0}:".format(partnum))
            tempPart = []
            ptnum=0
            pointArray=[]
            for pnt in part:
                if pnt:
                    print("点 {0}:{1},{2}".format(ptnum,pnt.X,pnt.Y))
                    point = Point()
                    point.X = pnt.X
                    point.Y = pnt.Y
                    pointArray.append(point)
                    ptnum+=1
                else:
                    print("内环:")
            pointArray.pop(len(pointArray)-1) # 为什么要使用这行，因为起点与终点相同

            #将不符合要求的写入到要素文件中
            pt_geom_list = caculate_angle(pointArray, angle,sr)
            pt_geom_lists = pt_geom_lists+pt_geom_list
    arcpy.CopyFeatures_management(pt_geom_lists, out_fc)

