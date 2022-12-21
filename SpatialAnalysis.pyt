
import arcpy
import glob
import os
import sys


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "空间分析赋值"
        self.alias = "空间分析赋值"

        # List of tool classes associated with this toolbox
        self.tools = [AddFieldByIntersection,LabelPatchByPercentage]


class AddFieldByIntersection(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "按面积占优赋值"
        self.description = "通过相交方式添加字段"
        self.canRunInBackground = False


    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入要素",
            name=" base_fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="唯一标识码",
            name="unique_bsm",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param1.parameterDependencies = [param0.name]
        param2 = arcpy.Parameter(
            displayName="挂接属性要素",
            name="add_fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        param3 = arcpy.Parameter(
            displayName="挂接属性字段",
            name="add_fc_attribute",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param3.parameterDependencies = [param2.name]

        param4 = arcpy.Parameter(
            displayName="是否显示最优属性占比",
            name="in_dir4",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        param4.filter.list = ['Yes','No']  

        params = [param0,param1,param2,param3,param4] 
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
        base_fc = parameters[0].valueAsText
        unique_bsm = parameters[1].valueAsText
        add_fc = parameters[2].valueAsText
        add_fc_attribute = parameters[3].valueAsText
        show_percentage = parameters[4].valueAsText

        add_field_by_intersection(base_fc,unique_bsm,add_fc,add_fc_attribute,show_percentage)
        return


class LabelPatchByPercentage(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "按指定比例标记图斑（按比例相交）"
        self.description = "根据相交比例占原图斑比例的大小标记原图斑，用于多源数据融合"
        self.canRunInBackground = False


    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入要素",
            name="in_dir0",
            datatype=["DEFeatureClass","GPFeatureLayer"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="标记要素",
            name="in_dir1",
            datatype=["DEFeatureClass","GPFeatureLayer"],
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="输出临时文件夹",
            name="in_dir2",
            datatype=["DEFolder","DECatalogRoot","DEWorkspace"],
            parameterType="Required",
            direction="Input")  

        param3 = arcpy.Parameter(
            displayName="输入要素唯一标识码",
            name="in_dir3",
            datatype="Field",
            parameterType="Optional",
            direction="Input")
        param3.parameterDependencies = [param0.name]

        param4 = arcpy.Parameter(
            displayName="指定阈值",
            name="in_dir4",
            datatype="GPString",
            parameterType="Required",
            direction="Input")  

        params = [param0,param1,param2,param3,param4]     
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
        label_fc = parameters[1].valueAsText
        temp_gdb = parameters[2].valueAsText
        unique_bsm = parameters[3].valueAsText
        threshold = parameters[4].valueAsText

        # 执行函数
        label_patch_by_percentage(in_fc,label_fc,temp_gdb,unique_bsm,threshold)
        arcpy.AddMessage("处理完成")
        return


def add_field_by_value(fc,new_field,value,field_length=30,value_quotation=True):
    """
    通过值添加字段
    仅通过添加字段并统一赋值的方式给数据库新增一个字段（这里的字段都是文本形式）
    fc: 输入要素
    new_field: 新建字段名称
    value: 新建字段的值
    field_length: 新建字段的长度
    value_quotation: 字段值外面是否要包引号，默认是包一对引号，组成双重引号
    """
    try:
        arcpy.AddField_management(fc,new_field,"Text",field_length=field_length)
    except:
        pass
    if value_quotation:
        arcpy.CalculateField_management(fc,new_field,"'"+value+"'","PYTHON3")
    else:
        arcpy.CalculateField_management(fc,new_field,value,"PYTHON3")


def add_field_by_intersection(base_fc,unique_bsm,add_fc,add_fc_attribute,show_percentage):
    """
    通过相交方式给图斑添加属性（字段），此方式不用破图斑，按照50%比例添加字段
    base_fc: 原图层
    unique_bsm:原图层的唯一标识码
    add_fc: 添加图层（一定要覆盖全域的图层）
    add_fc_attribute: 添加要素属性
    """

    # 定义中间数据输出位置
    # 基于磁盘文件的中间文件存储方式
    # Step1_TabulateIntersection = "TabulateIntersection"
    # Step2_Sort = "Sort"
    # Step3_Statistics = "Statistics"

    # 基于内存的中间文件存储方式
    Step1_TabulateIntersection = "memory/TabulateIntersection"
    Step2_Sort = "memory/Sort"
    Step3_Statistics = "memory/Statistics"
    

    # 1.Process: 交集制表 (交集制表) 
    arcpy.TabulateIntersection_analysis(in_zone_features=base_fc
    , zone_fields=[unique_bsm]
    , in_class_features=add_fc
    , out_table=Step1_TabulateIntersection
    , class_fields=[add_fc_attribute]   
    , sum_fields=[]
    , xy_tolerance="")

    # 2.Process: 排序 (排序) 
    arcpy.Sort_management(in_dataset=Step1_TabulateIntersection
    , out_dataset=Step2_Sort
    , sort_field=[["PERCENTAGE", "DESCENDING"]])

    # TODO 筛选百分比小于指定比例的记录，用于去除因容差问题而导致的相邻斑块会

    # 3.Process: 汇总统计数据 (汇总统计数据) 
    arcpy.Statistics_analysis(in_table=Step2_Sort
    , out_table=Step3_Statistics
    , statistics_fields=[[add_fc_attribute,"FIRST"],["PERCENTAGE","FIRST"]] 
    , case_field=[unique_bsm])

    # 连接前先删除base_fc中与连接字段名称相同的字段
    try:
        arcpy.management.DeleteField(base_fc,"FIRST_"+add_fc_attribute)
    except:
        pass

    # 4.Process: 连接字段 (连接字段) 
    arcpy.JoinField_management(in_data=base_fc
    , in_field=unique_bsm
    , join_table=Step3_Statistics
    , join_field=unique_bsm
    , fields=["FIRST_"+add_fc_attribute,"FIRST_PERCENTAGE"])

    # 5.重命名新添加的字段（添加新字段，删除老字段）
    # 添加新字段
    add_field_by_value(base_fc,add_fc_attribute,"!FIRST_"+add_fc_attribute+"!",value_quotation=False)
    add_field_by_value(base_fc,add_fc_attribute+"_PERCENTAGE","!FIRST_PERCENTAGE!",value_quotation=False)
    # 删除带FIRST的老字段
    arcpy.DeleteField_management(base_fc,["FIRST_"+add_fc_attribute])
    arcpy.DeleteField_management(base_fc,["FIRST_PERCENTAGE"])

    if show_percentage == 'false':
        arcpy.DeleteField_management(base_fc,[add_fc_attribute+"_PERCENTAGE"])

    arcpy.AddMessage("处理完成")


def label_patch_by_percentage(in_fc,label_fc,temp_gdb,unique_bsm,threshold):
    intersect_fc = os.path.join(temp_gdb,"intersect_fc")
    intersect_fc_sta = os.path.join(temp_gdb,"intersect_fc_sta")
    # 1. 相交
    arcpy.Intersect_analysis([in_fc, label_fc], intersect_fc)
    # 2. 计算相交前后几何属性
    in_fc_area_field = "图斑面积"
    expression = "round(!shape.geodesicArea!,2)"
    try:
        arcpy.AddField_management(in_fc,in_fc_area_field,"DOUBLE")
    except:
        print("[图斑面积]字段已存在，已覆盖原来字段的值！！！")
    arcpy.CalculateField_management(in_fc,in_fc_area_field,expression,"PYTHON")

    identify_area_field = "标记面积"
    try:
        arcpy.AddField_management(intersect_fc,identify_area_field,"DOUBLE")
    except:
        print("[标记面积]字段已存在，已覆盖原来字段的值！！！")
    arcpy.CalculateField_management(intersect_fc,identify_area_field,expression,"PYTHON")
    # 3. 汇总统计
    arcpy.Statistics_analysis(intersect_fc,intersect_fc_sta, [[identify_area_field, "SUM"]],unique_bsm)

    # 4. 字段连接
    arcpy.JoinField_management(in_data=in_fc
    , in_field=unique_bsm
    , join_table=intersect_fc_sta
    , join_field=unique_bsm)

    # 5. 后处理字段
    # 5.1 计算标记面积占比
    try:
        arcpy.AddField_management(in_fc,"标记图层占比","DOUBLE")
    except:
        print("[标记图层占比]字段已存在，已覆盖原来字段的值！！！")
    
    expression_get_percentage = "get_code(!图斑面积!,!SUM_标记面积!)"
    codeblock_get_percentage = """def get_code(sum_area,identify_area):
        if identify_area is None:
            return 0
        else:
            return identify_area/sum_area"""
    arcpy.CalculateField_management(in_fc,"标记图层占比",expression_get_percentage,"PYTHON",codeblock_get_percentage)
    
    # 5.2 按指定比例标记输入图斑
    try:
        arcpy.AddField_management(in_fc,"是否标记","Text",field_length=5)
    except:
        print("[是否标记]字段已存在，已覆盖原来字段的值！！！")
    threshold = str(threshold)
    expression_get_label = "get_code(!标记图层占比!)"
    codeblock_get_label = """def get_code(x):
        if x is None:
            return '不标记'
        elif x > 0.5:
            return '标记'
        else:
            return '不标记'"""
    codeblock_get_label = codeblock_get_label.replace("0.5",threshold)
    arcpy.CalculateField_management(in_fc,"是否标记",expression_get_label,"PYTHON",codeblock_get_label)


