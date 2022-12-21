
import arcpy
import os
import glob

arcpy.env.overwriteOutput = True  
# 框架工具
# 1. 相交求椭球面积算子（单边版、双边版）
# 2. 汇总统计算子
# 3. 后续再补充其他算子


class XianFrame(object):
    """
    县级处理框架(此框架暂时忽略过程数据的存储)
    func: 需要批量处理的函数，此函数为不带参数的函数，需要进行参数定义请在func函数内进行定义
    in_dir: 输入文件根目录
    layer_name： 需要查找的图层
    out_dir： 输出文件根目录，默认为None,表示不需要输出目录
    out_name: 输出图层名称（可选）
    refence_dict: 参考数据的字段，可选多个县级参考数据，多个省级参考数据（可选)
    
    """
    def __init__(self,func,in_dir=None,layer_name=None,out_dir=None,out_name=None,**refence_dict):
        self.func = func
        self.in_dir = in_dir
        self.layer_name = layer_name
        self.out_dir = out_dir
        self.out_name = out_name
        self.refence_dict = refence_dict
        
        # 处理输出路径文件
        if self.out_dir and not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

    @staticmethod
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
        self.in_fc_list = self.get_paths(self.in_dir,self.layer_name)


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


    def scheduler(self):
        """
        调度器，用来对多个区县处理任务进行多进程任务分配
        """
        if  self.out_dir:
            for xian_loop_fc,out_gdb in zip(self.in_fc_list,self.out_gdb_list):
                try:
                    self.func(xian_loop_fc,out_gdb,self.out_name,**self.refence_dict) 
                    print(xian_loop_fc)     
                except:
                    print("{}未处理,错误原因：{}".format(xian_loop_fc,e))
        else:
            for xian_loop_fc in self.in_fc_list:
                try:
                    self.func(xian_loop_fc,**self.refence_dict) 
                    print(xian_loop_fc)     
                except Exception as e:
                    print("{}未处理,错误原因：{}".format(xian_loop_fc,e))


class MultiprocessXianFrame(XianFrame):
    """
    此为多进程版，后续再补充吧
    """
    def __init__(self):
        pass


def demo_func(xian_loop_fc,out_gdb=None,out_name=None,**refence_dict):
    """
    此为分县处理算子demo函数
    """
    print("县循环变量：{}".format(xian_loop_fc))
    # print("县输出变量：{}".format(os.path.join(out_gdb,out_name)))
    # 全省参考数据
    print("省参考变量1：{}".format(refence_dict['province_ref_fcs'][0]))
    print("省参考变量2：{}".format(refence_dict['province_ref_fcs'][1]))
    # 分县参数数据
    xian_code = os.path.basename(os.path.dirname(xian_loop_fc))
    BGGB2020_fc = os.path.join(refence_dict['xian_ref_dir']['BG2020'][0],xian_code,refence_dict['xian_ref_dir']['BG2020'][1])
    SDGB2020_fc = os.path.join(refence_dict['xian_ref_dir']['SD2019'][0],xian_code,refence_dict['xian_ref_dir']['SD2019'][1])
    print("县参考变量1：{}".format(BGGB2020_fc))
    print("县参考变量2：{}".format(BGGB2020_fc))


def intersect_add_geoarea_1(xian_loop_fc,out_gdb=None,out_name=None,**refence_dict):
    """
    相交求面积算子（单边版）
    xian_loop_fc: 县级循环要素（此部分为分县的数据）
    out_gdb: 最终的输出结果，此部分输出为分县GDB
    refence_dict：省参考数据、县参考数据
    """
    # 处理省参考数据
    province_fc = refence_dict['province_ref_fcs'][0]
    # 输入输出数据
    intersect_result_path = os.path.join(out_gdb,out_name)
    # 1. 求相交
    arcpy.Intersect_analysis([xian_loop_fc,province_fc],intersect_result_path)
    # 2. 添加几何属性
    sr = arcpy.Describe(xian_loop_fc).spatialReference
    arcpy.AddGeometryAttributes_management(Input_Features=intersect_result_path
    , Geometry_Properties=["AREA_GEODESIC"]
    , Length_Unit=""
    , Area_Unit="SQUARE_METERS"
    , Coordinate_System=sr) 


def intersect_add_geoarea_2(xian_loop_fc,out_gdb=None,out_name=None,**refence_dict):
    """
    相交求面积算子（双边版）
    xian_loop_fc: 县级循环要素（此部分为分县的数据）
    out_gdb: 最终的输出结果，此部分输出为分县GDB
    """
    # 处理参考数据路径（此部分人工处理）
    xian_code = os.path.basename(os.path.dirname(xian_loop_fc))[:6]
    ref_fc = os.path.join(refence_dict['xian_ref_dir']["YN2020"][0],"T"+xian_code+".gdb",refence_dict['xian_ref_dir']["YN2020"][1])

    # 输入输出数据
    intersect_result_path = os.path.join(out_gdb,out_name)
    # 1. 求相交
    arcpy.Intersect_analysis([xian_loop_fc,ref_fc],intersect_result_path)
    # 2. 添加几何属性
    sr = arcpy.Describe(xian_loop_fc).spatialReference
    arcpy.AddGeometryAttributes_management(Input_Features=intersect_result_path
    , Geometry_Properties=["AREA_GEODESIC"]
    , Length_Unit=""
    , Area_Unit="SQUARE_METERS"
    , Coordinate_System=sr) 


def repair_geom_dissolve(xian_loop_fc,**ref):
    """
    分县修复几何融合算子
    xian_loop_fc: 县级循环要素（此部分为分县的数据）
    """
    # 修复几何
    print("{}开始修复几何".format(xian_loop_fc))  
    arcpy.RepairGeometry_management(xian_loop_fc)
    # 融合
    print("{}开始融合".format(xian_loop_fc)) 
    out_gdb = os.path.dirname(xian_loop_fc)
    dissolved_fc = os.path.join(out_gdb,"上图数据_修复后融合")
    arcpy.Dissolve_management(xian_loop_fc, dissolved_fc,multi_part="SINGLE_PART")


def summary_statistic(xian_loop_fc,**ref):
    pass


def main():
    in_dir = r"D:\Data\06工具测试数据\01分县处理框架\02相交重算椭球（双边版）\2020年变更公报分县"
    layer_name = "GBDLTB"
    out_dir = r"D:\Data\06工具测试数据\01分县处理框架\02相交重算椭球（双边版）\输出"
    out_name = "输出文件"
    

    refence_dict = {
        "province_ref_fcs":["STTJ","GGTJ"],
        "xian_ref_dir": {"YN2020":[r"D:\Data\06工具测试数据\01分县处理框架\02相交重算椭球（双边版）\永久基本农田上图4950分县","上图数据_修复后融合"]}
    }

    frame = XianFrame(intersect_add_geoarea_2,in_dir,layer_name,out_dir,out_name,**refence_dict)
    frame.run()


if __name__ == '__main__':
    main()