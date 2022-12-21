import numpy as np
import arcpy
import os
import glob
import re
import time

arcpy.env.overwriteOutput = True

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

