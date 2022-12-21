# -*- coding: utf-8 -*-

import arcpy
import re
import os

arcpy.env.overwriteOutput = True

# 工具箱入口
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [TXT2SHP]


class TXT2SHP(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "TXT文件转shapefile文件"
        self.description = "xxx"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="txt文件夹",
            name="txt_dir",
            datatype=["DEFolder","DECatalogRoot"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="shapefile输出文件夹",
            name="out_dir",
            datatype=["DEFolder","DECatalogRoot"],
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
        infos = []
        txt_dir = parameters[0].valueAsText
        output_dir = parameters[1].valueAsText

        # 执行函数
        txt2shp(info, txt_dir, output_dir)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are outputs are processed and
        added to the display."""
        return



# 工具函数
def points_genarator(txt_file):
	"""
	points_genarator(txt_file)   return list
	txt_file：文本文件地址
	将txt转换为可以使用的点集列表
	"""
	try:
	
		fffs = open(txt_file, "r")
		input_data = fffs.readlines()
		# input_data.remove("\n")
		# 去除换行符
		# input_data = [x.strip() for x in input_data]
		# input_data = input_data[2:]  # 去除前13行
		#▶注释1◀ 去除带@的行
		input_data = [x.strip() for x in input_data if "@" not in x]
		# 去除非J行
		while True:  # 去除前13行
			# 如果首行字符不在下列元组中
			first = ("J", "1", "0", "2", "3", "4", "5", "6", "7", "8", "9")
			if input_data[0][0] not in first:
				del input_data[0]
			# elif :
			#  del input_data[0]
			else:
				break
		# input_data = input_data[12:]  # 去除前13行
		fffs.close()
		# 每一根闭合线单独组成一个列表
		line_closed = []
		# 多根线条组成面
		polygon_list = []
		#▶注释2◀
		while input_data:
			row = input_data.pop(0)
			# ['J1', '1', '3405133.8969', '35353662.0113']
			row1 = row.split(",")
			# 去除字母和数字组合中的字母 如 "J1" 只保留 "1"
			row_num = re.findall(r'[0-9]+|[a-z]+', row1[0])  # ['1']
			# 解决了文本最后有空行会报错的问题
			if row1 == [""] or row1 == [" "]:
				# print u"&<{}> 存在空行 \n 已解决\n&".format(txt_file)
				continue
			row_num2 = row1[1]
			if not line_closed:  # 为空时
				line_closed.append(row1)
				flag1 = int(row_num[0])  # 1 第一列数字
				# 第二列数字
				flag2 = row1[1]  # '1'
			elif int(row_num[0]) > flag1:
				if row_num2 != flag2:  # 第二列出现不一样的，新一轮开始
					flag2 = row_num2
					polygon_list.append(line_closed)
					line_closed = []
				# 未开始新一轮就接着上一个，如果开始新一轮那么这里就是第一个起始点
				line_closed.append(row1)
			elif int(row_num[0]) == flag1:  # 新一轮开始
				polygon_list.append(line_closed)
				line_closed = []
				line_closed.append(row1)
		if line_closed:
			polygon_list.append(line_closed)
		return polygon_list
	
	except Exception as e:
		# 这样报错就能知道是遍历的那个文件出错了
		raise IndexError(e.message,"Error File: {}".format(txt_file))
		

def draw_poly(coord_list, sr, y, x):
	"""
	创建多边形
	coord_list(List)：多个点组成的坐标
	sr: 投影系
	y(Int): y坐标列
	x(Int): x坐标列
	"""
	parts = arcpy.Array()
	yuans = arcpy.Array()
	yuan = arcpy.Array()
	for part in coord_list:
		for pnt in part:
			if pnt:
				yuan.add(arcpy.Point(pnt[y], pnt[x]))
			else:
				# null point - we are at the start of a new ring
				yuans.add(yuan)
				yuan.removeAll()
		# we have our last ring, add it
		yuans.add(yuan)
		yuan.removeAll()
		# if we only have one ring: remove nesting
		if len(yuans) == 1:
			yuans = yuans.getObject(0)
		parts.add(yuans)
		yuans.removeAll()
	# 只有一个，单个图形
	if len(parts) == 1:
		parts = parts.getObject(0)
	return arcpy.Polygon(parts, sr)


def txt2shp(info, txt_folder, output_folder):
	"""
	功能实现的主函数
	info(List): 存放信息的列表，作为独立脚本使用时没啥用
	txt_folder(Unicode/String): 包含txt文件的文件夹
	output_folder(Unicode/String): 导出文件夹
	"""
	arcpy.env.overwriteOutput = True
	txts = os.listdir(txt_folder)
	for txt in txts:
		if txt[-3:].lower() == "txt":
			txt_p = os.path.join(txt_folder, txt)
			f = points_genarator(txt_p)
			name = os.path.splitext(os.path.basename(txt_p))[0]
			# 创建空白shp
			blank_shp = arcpy.CreateFeatureclass_management(
				output_folder,name, "Polygon",
				spatial_reference=None)
			# create the polygons and write them
			Rows = arcpy.da.InsertCursor(blank_shp, "SHAPE@")
			#▶注释3◀
			p = draw_poly(f, sr=None, y=3, x=2)
			
			Rows.insertRow([p])
			del Rows
			output_info = "--Export succeed: " + os.path.join(
				output_folder, name).encode("utf8")
			print(output_info)
			info.append(output_info)
			
			# 给新建的shp文件添加 MC 字段和值
			shp_name = name + ".shp"
			newfield_name = "MC"
			fresh_layer = arcpy.mapping.Layer(
				os.path.join(output_folder, shp_name))
			arcpy.AddField_management(
				fresh_layer, newfield_name, "TEXT", field_length=100)
			cursor2 = arcpy.da.UpdateCursor(fresh_layer, newfield_name)
			for roww in cursor2:
				roww[0] = name
				cursor2.updateRow(roww)
			del cursor2



