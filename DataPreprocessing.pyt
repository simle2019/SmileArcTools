import arcpy
import glob
import os
import sys
import string


# 重要:可以走多进程的程序应该给一个接口，让其分开计算

# 数据输入输出接口
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "数据预处理"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [BatchMerge,SelectXian,ClipXian,RemoveNullValue,DeleteNullFC,BatchDeleteFC,BatchMergeByAppend]


class BatchMerge(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "专题要素合并（批量合并）"
        self.description = "批量合并输入文件夹内指定图层到同一个图层"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入根目录",
            name="in_dir",
            datatype=["DEFolder","DECatalogRoot"],
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="搜索图层名字",
            name="layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="输出要素图层位置",
            name="out_path",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")

        param3 = arcpy.Parameter(
            displayName="图层搜索类型",
            name="layer_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")  

        param3.filter.type = "ValueList"
        param3.filter.list = ["FeatureClass","Shapefile","Table","Datasets-FeatureClass","Datasets-Table"]
        param3.value = "FeatureClass"                 

        params = [param0,param1,param2,param3]
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
        in_dir = parameters[0].valueAsText
        layer_name = parameters[1].valueAsText
        out_path = parameters[2].valueAsText
        layer_type = parameters[3].valueAsText
        # 执行函数
        batch_merge(in_dir,layer_name,out_path,layer_type)
        return


class BatchMergeByAppend(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "专题要素合并（以追加方式批量合并）"
        self.description = "批量合并输入文件夹内指定图层到同一个图层"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入根目录",
            name="in_dir",
            datatype=["DEFolder","DECatalogRoot"],
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="模板GDB文件（追加合并结果）",
            name="layer_name",
            datatype=["DECatalogRoot","DEWorkspace"],
            parameterType="Required",
            direction="Input")

        params = [param0,param1]
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
        workspace = parameters[0].valueAsText
        outdb = parameters[1].valueAsText

        # 执行函数
        batch_merge_by_append(workspace,outdb)
        return


class DeleteNullFC(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "批量删除空图层"
        self.description = "批量删除要素数量为0的图层"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入根目录",
            name="in_dir",
            datatype=["DEFolder","DECatalogRoot"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="图层搜索类型",
            name="layer_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")  

        param1.filter.type = "ValueList"
        param1.filter.list = ["FeatureClass","Shapefile","Table","Datasets-FeatureClass","Datasets-Table"]
        param1.value = "FeatureClass"                 

        params = [param0,param1]
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
        in_dir = parameters[0].valueAsText
        layer_type = parameters[1].valueAsText
        # 执行函数
        delete_null_fc(in_dir,layer_type)
        return


class BatchDeleteFC(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "批量删除指定名称图层"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入根目录",
            name="in_dir",
            datatype=["DEFolder","DECatalogRoot"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="删除图层名字",
            name="layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="图层搜索类型",
            name="layer_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")  

        param2.filter.type = "ValueList"
        param2.filter.list = ["FeatureClass","Shapefile","Table","Datasets-FeatureClass","Datasets-Table"]
        param2.value = "FeatureClass"                 

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
        in_dir = parameters[0].valueAsText
        layer_name = parameters[1].valueAsText
        layer_type = parameters[2].valueAsText
        # 执行函数
        batch_delete_fc(in_dir,layer_name,layer_type)
        return


class SelectXian(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "专题要素分县（选择:按字段名称)"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="专题要素数据（全省,选要素图层）",
            name="in_dir0",
            datatype=["DEFeatureClass"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="分县字段(请选县代码)",
            name="in_dir1",
            datatype="Field",
            parameterType="Optional",
            direction="Input")
        param1.parameterDependencies = [param0.name]

        param2 = arcpy.Parameter(
            displayName="县级行政区字典表（选表格）",
            name="in_dir2",
            datatype=["DETable"],
            parameterType="Required",
            direction="Input")  


        param3 = arcpy.Parameter(
            displayName="分县专题要素输出目录（选文件夹）",
            name="in_dir3",
            datatype=["DEFolder","DECatalogRoot","DEWorkspace"],
            parameterType="Required",
            direction="Input")  


        params = [param0,param1,param2,param3]     
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

        thematic_fc = parameters[0].valueAsText
        xian_code_field = parameters[1].valueAsText
        XZQ_TAB = parameters[2].valueAsText
        out_dir = parameters[3].valueAsText

        # 执行函数
        select_xian(thematic_fc,xian_code_field,XZQ_TAB,out_dir)
        arcpy.AddMessage("处理完成")
        return


class ClipXian(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "专题要素分县（裁剪:按行政边界）"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="专题要素数据（全省,选要素图层）",
            name="in_dir0",
            datatype=["DEFeatureClass"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="县级行政区目录（选文件夹）",
            name="in_dir1",
            datatype=["DEFolder","DECatalogRoot","DEWorkspace"],
            parameterType="Required",
            direction="Input")  

        param2 = arcpy.Parameter(
            displayName="县级行政区要素名称（输入图层名字）",
            name="in_dir2",
            datatype="GPString",
            parameterType="Required",
            direction="Input")  

        param3 = arcpy.Parameter(
            displayName="分县专题要素输出目录（选文件夹）",
            name="in_dir3",
            datatype=["DEFolder","DECatalogRoot","DEWorkspace"],
            parameterType="Required",
            direction="Input")  


        params = [param0,param1,param2,param3]     
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
        arcpy.AddMessage("1111")
        thematic_fc = parameters[0].valueAsText
        in_dir = parameters[1].valueAsText
        layer_name = parameters[2].valueAsText
        out_dir = parameters[3].valueAsText

        # 执行函数
        # arcpy.AddMessage(xian_code_field)
        frame = XianFrame(clip_xian,thematic_fc,in_dir,layer_name,out_dir)
        frame.run()
        arcpy.AddMessage("处理完成")
        return


class RemoveNullValue(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "移除NULL值（数据库标准化）"
        self.description = "移除数据库中存在的NULL值，并将其替换为0或者空字符串"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="输入数据库",
            name="in_database",
            datatype=["DEWorkspace"],
            parameterType="Required",
            direction="Input")  

        params = [param0]
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
        database = parameters[0].valueAsText

        # 执行函数
        remove_null_value(database)
        return



# 工具函数
def batch_merge(in_dir,layer_name,out_path,layer_type="FeatureClass"):
    """
    批量合并数据（合并多个数据图层），该工具会自动查找某个目录下所有符合条件的图层，并将其合并
    in_dir: 合并数据的目录
    layer_name: 合并数据所需要的图层
    layer_type: 图层类型，可选1【FeatureClass】、2【Shapefile】、3【Table】、4【Datasets-FeatureClass】、5【Datasets-Table】
    out_path: 合并后要素图层存放的位置
    """
    feat_paths = get_paths(in_dir,layer_name,layer_type)
    arcpy.AddMessage(feat_paths)
    arcpy.Merge_management(feat_paths,out_path)
    print(len(feat_paths))
    arcpy.AddMessage("本次执行工具共合并【{}】个图层".format(str(len(feat_paths))))


def remove_null_value(database,*fc_list):
    """
    
    对接收的数据进行标准化处理,去除Null值，替换NULL值为空字符串或者是0
    database: 需要标准化的数据库路径
    fc_list: 需要标准化的数据库图层列表

    后续可能会增加的参数
    replace_value: 需要替换的值

    """
    # 遍历数据集
    # 遍历图层
    # 遍历字段
    # 通过基于图层的方法查询数据值为NULL的记录，并将其计算为字符串空值

    # 第一部分：遍历数据集
    arcpy.env.workspace = database 
    dataset_list = arcpy.ListDatasets()
    for dataset in dataset_list:
        arcpy.env.workspace = os.path.join(database,dataset)
        fc_list = arcpy.ListFeatureClasses()
        for fc in fc_list:
            fc_lyr = os.path.join("\memory",fc)
            arcpy.MakeFeatureLayer_management(fc, fc_lyr)
            field_obj_list = [f for f in arcpy.ListFields(fc)]
            for field_obj in field_obj_list:
                arcpy.SelectLayerByAttribute_management(fc_lyr, selection_type="NEW_SELECTION",where_clause=field_obj.name + " IS NULL")
                try:
                    if field_obj.type == "String":
                        arcpy.CalculateField_management(fc_lyr,field_obj.name,"''","PYTHON3")
                    elif field_obj.type == "Double":
                        arcpy.CalculateField_management(fc_lyr,field_obj.name,"0","PYTHON3")
                    elif field_obj.type == "Integer":
                         arcpy.CalculateField_management(fc_lyr,field_obj.name,"0","PYTHON3")
                    arcpy.AddMessage("数据集{}图层{}更改成功：{}".format(dataset,fc,field_obj.name))
                except:
                    arcpy.AddMessage(field_obj.name)

    # 第二部分：直接遍历图层要素
    arcpy.env.workspace = database
    fc_list = arcpy.ListFeatureClasses()
    for fc in fc_list:
        fc_lyr = os.path.join("\memory",fc)
        arcpy.MakeFeatureLayer_management(fc, fc_lyr)
        field_obj_list = [f for f in arcpy.ListFields(fc)]
        for field_obj in field_obj_list:
            arcpy.SelectLayerByAttribute_management(fc_lyr, selection_type="NEW_SELECTION",where_clause=field_obj.name + " IS NULL")
            try:
                if field_obj.type == "String":
                    arcpy.CalculateField_management(fc_lyr,field_obj.name,"''","PYTHON3")
                elif field_obj.type == "Double":
                    arcpy.CalculateField_management(fc_lyr,field_obj.name,"0","PYTHON3")
                elif field_obj.type == "Integer":
                        arcpy.CalculateField_management(fc_lyr,field_obj.name,"0","PYTHON3")
                arcpy.AddMessage("图层{}更改成功：{}".format(fc,field_obj.name))
            except:
                arcpy.AddMessage(field_obj.name)


def get_paths(in_dir,layer_name,layer_type="FeatureClass"):
    """
    get paths from input directory
    获取根目录下所有符合条件图层的路径
    此工具可复用
    in_dir: 输入根目录
    layer_name: 图层名字
    layer_type: 图层类型，可选1【FeatureClass】、2【Shapefile】、3【Table】、4【Datasets-FeatureClass】、5【Datasets-Table】
    """
    if not layer_name:
        layer_name = "*"
    # 遍历根目录下所有符合条件图层，返回路径列表
    feat_paths = []
    for root,dirs,files in os.walk(in_dir):
        arcpy.env.workspace = root
        if root.endswith(".gdb") and layer_type == "FeatureClass":
            gdb_feats = arcpy.ListFeatureClasses(layer_name)
            gdb_feats = list(map(lambda x: os.path.join(root,x),gdb_feats))
            feat_paths = feat_paths+gdb_feats
        elif root.endswith(".gdb") and layer_type == "Table":
            gdb_feats = arcpy.ListTables(layer_name)
            gdb_feats = list(map(lambda x: os.path.join(root,x),gdb_feats))
            feat_paths = feat_paths+gdb_feats
        elif root.endswith(".gdb") and layer_type == "Datasets-FeatureClass":
            dataset = arcpy.ListDatasets("*")[0]
            arcpy.env.workspace = os.path.join(root,dataset)
            gdb_feats = arcpy.ListFeatureClasses(layer_name)
            gdb_feats = list(map(lambda x: os.path.join(root,x),gdb_feats))
            feat_paths = feat_paths+gdb_feats
        elif root.endswith(".gdb") and layer_type == "Datasets-Table":
            dataset = arcpy.ListDatasets("*")[0]
            arcpy.env.workspace = os.path.join(root,dataset)
            gdb_feats = arcpy.ListTables(layer_name)
            gdb_feats = list(map(lambda x: os.path.join(root,x),gdb_feats))
            feat_paths = feat_paths+gdb_feats
        elif layer_type == "Shapefile":
            shp_feats = glob.glob(os.path.join(root,layer_name+".shp"))
            feat_paths = feat_paths+shp_feats

    return feat_paths


class XianFrame(object):
    """
    func: 需要批量处理的函数，此函数为不带参数的函数，需要进行参数定义请在func函数内进行定义
    thematic_fc: 全省
    in_dir: 输入文件根目录
    layer_name： 需要查找的图层
    out_dir： 输出文件根目录，默认为None,表示不需要输出目录
    split_dir: 分区县GDB文件夹
    
    """
    def __init__(self,func,thematic_fc,in_dir=None,layer_name=None,out_dir=None):
        self.func = func
        self.thematic_fc = thematic_fc
        self.in_dir = in_dir
        self.layer_name = layer_name
        self.out_dir = out_dir



    def test(self):
        self.set_in_path()
        self.set_out_path()


        for out_gdb in self.out_gdb_list:
            print(out_gdb)

    
    def run(self):
        self.set_in_path() # 初始化输入路径
        self.set_out_path() # 初始化输出路径
        self.scheduler() # 执行调度


    def set_in_path(self):
        """
        此方法应该生成栈
        此函数主要用来处理输入目录，通过这个方法，初始化【输入要素】目录列表
        """
        # 直接通过给定文件夹根目录获取
        self.in_fc_list = get_paths(self.in_dir,self.layer_name)


    def set_refence_path(self):
        if self.refence_dir:
            self.refence_gdb_list_loop = list(map(lambda x: os.path.dirname(x.replace(self.in_dir,self.refence_dir)),self.in_fc_list))
            self.refence_gdb_list = []
            for refence_gdb in self.refence_gdb_list_loop:
                refence_gdb_name = os.path.basename(os.path.dirname(refence_gdb))+".gdb"
                refence_gdb_dirname = os.path.dirname(os.path.dirname(refence_gdb))
                refence_gdb_new = os.path.join(refence_gdb_dirname,refence_gdb_name)
                self.refence_gdb_list.append(refence_gdb_new)


    def set_ref_add_path(self):
        if self.ref_add_dir:
            self.ref_add_gdb_list = list(map(lambda x: x.replace(self.refence_dir,self.ref_add_dir),self.refence_gdb_list))


    def set_out_path(self):
        """
        注意：此方法应该生成栈
        此函数主要用来处理输出目录，通过这个方法，初始化【输出GDB】目录列表
        """        
        if self.out_dir:
            self.out_gdb_list = list(map(lambda x: os.path.dirname(x.replace(self.in_dir,self.out_dir)),self.in_fc_list))
        # 批量新建gdb
            for out_gdb in self.out_gdb_list:
                out_folder_path = os.path.dirname(out_gdb)
                if not os.path.exists(out_folder_path):
                    os.mkdir(out_folder_path)
                out_name = os.path.basename(out_gdb)
                try:
                    arcpy.CreateFileGDB_management(out_folder_path, out_name)
                except:
                    print("已存在GDB:{}".format(out_name))
        else:
            self.out_gdb_list = None


    def set_temp_path(self):
        """
        注意：此方法应该生成栈
        此函数主要用来处理输出目录，通过这个方法，初始化【输出GDB】目录列表
        """        
        if self.temp_dir:
            self.temp_gdb_list_loop = list(map(lambda x: os.path.dirname(x.replace(self.in_dir,self.temp_dir)),self.in_fc_list))
        # 批量新建gdb
            self.temp_gdb_list = []
            for temp_gdb in self.temp_gdb_list_loop:
                temp_folder_path = os.path.dirname(temp_gdb)
                if not os.path.exists(temp_folder_path):
                    try:
                        os.mkdir(temp_folder_path)
                    except:
                        os.mkdir(os.path.dirname(temp_folder_path))
                        os.mkdir(temp_folder_path)
                temp_name = os.path.basename(os.path.dirname(temp_gdb))+"_过程数据.gdb"
                try:
                    arcpy.CreateFileGDB_management(temp_folder_path, temp_name)
                except:
                    print("已存在GDB:{}".format(temp_name))
                self.temp_gdb_list.append(os.path.join(temp_folder_path, temp_name))
        else:
            self.temp_gdb_list = None


    def scheduler(self):
        """
        调度器，用来对多个区县处理任务进行多进程任务分配
        """
        for in_fc,out_gdb in zip(self.in_fc_list,self.out_gdb_list):
            try:
                self.func(self.thematic_fc,in_fc,out_gdb) 
                arcpy.AddMessage("处理完成：{}".format(os.path.basename(out_gdb)))
                # print(out_gdb)     
            except:
                arcpy.AddMessage("{}未处理".format(out_gdb))


def clip_xian(thematic_fc,XZQ_X1,out_gdb):
    fc_name = os.path.basename(thematic_fc)
    out_fc = os.path.join(out_gdb,fc_name)
    arcpy.Clip_analysis(thematic_fc, XZQ_X1,out_fc)


def select_xian(thematic_fc,xian_code_field,XZQ_TAB,out_dir):
    xzq_dict_list = arcpy.da.TableToNumPyArray(XZQ_TAB,["XZQDM","XZQMC"])
    for xian_code,xian_name in xzq_dict_list:
        xian_code = str(xian_code)
        thematic_fc_name = os.path.basename(thematic_fc)
        gdb_name = xian_code+xian_name+".gdb"
        out_gdb = os.path.join(out_dir,gdb_name)
        try:
            arcpy.CreateFileGDB_management(out_dir, gdb_name)
        except:
            arcpy.AddMessage("{}GDB已存在".format(gdb_name))
        try:
            arcpy.FeatureClassToFeatureClass_conversion(thematic_fc,out_gdb,thematic_fc_name,where_clause= xian_code_field+"= '"+xian_code+"'")
            arcpy.AddMessage("{}处理成功".format(gdb_name))
        except:
            arcpy.AddMessage("{}要素查找失败".format(gdb_name))


def delete_null_fc(in_dir,layer_type):
    """
    批量删除空图层
    in_dir: 需要删除空图层的目录
    layer_type: 空图层所在的图层类型
    可选1【FeatureClass】、2【Shapefile】、3【Table】、4【Datasets-FeatureClass】、5【Datasets-Table】
    """
    fc_list = get_paths(in_dir,"*",layer_type=layer_type)
    arcpy.AddMessage("开始")
    for fc in fc_list:
        num = int(arcpy.GetCount_management(fc)[0])
        if num == 0:
            arcpy.AddMessage("{}:{}".format(fc,num))
            arcpy.Delete_management(fc)
    arcpy.AddMessage("完成")


def batch_delete_fc(in_dir,layer_name,layer_type):
    """
    批量删除指定名称图层
    in_dir: 需要删除空图层的目录
    layer_type: 空图层所在的图层类型
    可选1【FeatureClass】、2【Shapefile】、3【Table】、4【Datasets-FeatureClass】、5【Datasets-Table】
    """
    fc_list = get_paths(in_dir,layer_name,layer_type=layer_type)
    arcpy.AddMessage("开始")
    for fc in fc_list:
        arcpy.Delete_management(fc)
        arcpy.AddMessage("删除图层{}".format(fc))
    arcpy.AddMessage("完成")

# TODO 下面的代码来自于网络博主：gisoracle

def isGDB(yldir):
    "判断是否为GDB或者MDB格式"
    if (yldir.lower().endswith(".gdb")):
        return True
    elif (yldir.lower().endswith(".mdb")):
        return True
    else:
        return False


def CopyDir(outdb,workspace): #shp
    arcpy.env.workspace = workspace

    files = arcpy.ListWorkspaces("","")
    if files:
        for File in files:
            if (File==outdb):
                continue
            AppendGDB(File,outdb)


def AppendGDB(File,outdb):
    if (File.lower()==outdb.lower()):
        return

    arcpy.AddMessage('File=========:'+File)
    arcpy.env.workspace = outdb
    fcs = arcpy.ListFeatureClasses()
    for fc in fcs:

        try:
            if arcpy.Exists(File + "\\" + fc):
                arcpy.AddMessage("fc:"+File + "\\" + fc)
                arcpy.Append_management([ File + "\\" + fc], outdb + "\\" + fc,"NO_TEST","","")
            elif  arcpy.Exists(File + os.sep + fc + ".shp"):  # 或者shp:
                arcpy.AddMessage("fc:" + File + "\\" + fc+".shp")
                arcpy.Append_management([File + "\\" + fc+".shp"], outdb + "\\" + fc, "NO_TEST", "", "")
            else:
                arcpy.AddMessage("not exists:"+File + "\\" + fc)
        except arcpy.ExecuteError:
            arcpy.AddWarning(arcpy.GetMessages())


    fcs = arcpy.ListTables()
    for fc in fcs:
        arcpy.AddMessage("fc:"+fc)
        try:
            if arcpy.Exists(File + os.sep + fc):#或者dbf
                arcpy.Append_management([File + "\\" + fc], outdb + "\\" + fc,"NO_TEST","","")
            elif arcpy.Exists(File + os.sep + fc+".dbf"):
                arcpy.Append_management([File + "\\" + fc+".dbf"], outdb + "\\" + fc, "NO_TEST", "", "")
            else:
                arcpy.AddMessage("not exists:"+File + "\\" + fc)
        except arcpy.ExecuteError:
             arcpy.AddWarning(arcpy.GetMessages())

    dss = arcpy.ListDatasets()
    for ds in dss:
        arcpy.AddMessage("ds:"+ds)
        arcpy.env.workspace = outdb+"\\"+ds
        fcs1 = arcpy.ListFeatureClasses()
        for fc1 in fcs1:
            arcpy.AddMessage("fc1:"+fc1)
            try:
                if arcpy.Exists(File + "\\" + ds + "\\" + fc1):
                    arcpy.Append_management([File + "\\" + ds + "\\" + fc1], outdb + "\\" + ds + "\\" + fc1,"NO_TEST","","")
                else:
                    arcpy.AddMessage("not exists:"+File + "\\" + ds + "\\" + fc1)

            except arcpy.ExecuteError:
                arcpy.AddWarning(arcpy.GetMessages())


def batch_merge_by_append(workspace,outdb):
    """
    workspace: 工作空间
    outdb: 模板GDB，合并后的结果将保存到模板文件GDB中
    
    """
    # workspace =arcpy.GetParameterAsText(0)  #'C:\Users\Administrator\Desktop\\cc'
    # outdb =arcpy.GetParameterAsText(1)   #'C:\Users\Administrator\Desktop\\lutian.mdb'
    workspace = r"E:\HQS\20221129_新化县地形图合库\01原始数据\新化乡镇数据库1129"
    outdb = r"E:\HQS\20221129_新化县地形图合库\01原始数据\模板\GX21_430-111E.gdb"

    for dirpath, dirnames, filenames in os.walk(workspace):
        arcpy.AddMessage('dirpath=======:'+dirpath)
        if isGDB(dirpath):#是gdb
            arcpy.AddMessage(u'dirpath=======是gdb:'+dirpath)
            AppendGDB(dirpath,outdb)


        for dirname in dirnames:
            arcpy.AddMessage("dirname=="+dirname)

            if isGDB(dirname):
                arcpy.AddMessage(u'dirname=======是gdb:'+dirpath)
                continue
            else:
                filepath= os.path.join(dirpath,dirname)
                AppendGDB(filepath,outdb)
                arcpy.AddMessage(u'dirname不是gdb:'+dirname)
        for filename in filenames:
            if filename.lower().endswith(".mdb"):
                filepath= os.path.join(dirpath,filename)
                arcpy.AddMessage('filepath===:'+filepath)
                AppendGDB(filepath,outdb)

