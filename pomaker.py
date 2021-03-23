import os
import re

from util import Hump

from stparser import ParseTable
from stparser import SqlCut

from gotype import SqlTypeToGoType
from gocreator import CreateGoStruct
from gocreator import CreateGoStructMethod
from gocreator import AssembleCode
# PO对象代码生成器
# 1.本生成器仅适配于mysql的SQL语句定义格式
# 2.请使用Navicat进行以“仅表结构”的方式进行转储，否则可能识别不出来
# @update : 2021.3.6
# @author : 张铭(560365)

# 项目根目录地址
PROJECT_ROOT_PATH = "E:\\goland workspaces\\apimg"

# PO对象在项目根目录下的输出地址
OUTPUT_PATH = "share\\potest"

# SQL文件名
SQL_FILE = "aam.sql"

# 表前缀
TABLE_PREFIX = "aam_"

# 包名
PACKAGE_NAME = 'po'

# 对输出go文件进行注释，描述PO对象的生成方式
# 且告知生成PO文件的命名规则
GO_FILE_NOTES = \
'// 本代码由pomaker自动生成 ' + "\n" + \
'// PO对象结构体代码命名规则符合 README.md 中描述，具体详情请参考该文件的介绍' + "\n" + \
'// 注意：如果有些注释和代码是手工添加上的，所以在修改表文件后最好连带修改SQL' + "\n" + \
'// 中与之相关的代码，否则如果直接运行pomaker.py可能造成注释损失或者代码报错！'


# 构建PO结构体代码
# 创建PO结构体代码
# Param  : ({})     解析后的单个表信息
# Return : (string) 根据PO对象结构体代码命名规则转换好的go语言的
#          PO对象结构体代码段
def CreatePO ( packageName ,tableInfo ) :

    # 包名
    packageNameCode = 'package {0}\n'.format(packageName)

    # 需要引入的库
    importLib = set()

    # 全部代码
    allCode = ""

    # 结构体组成的部分 字段和方法
    structFields = []
    structMethods = []

    # 表字段名的结构体
    tableFieldNameFields = []

    # 添加表名的注释
    tableNotes = '//【' + tableInfo['comment'] + '】'

    # 获取字段信息
    fieldInfos = tableInfo['fields']
    for fieldName in fieldInfos :

        # 表字段名结构体
        tableFieldNameFields += [{
        'name'    : fieldName.upper() ,
        'type'    : 'string'          ,
        'target'  : []                ,
        'comment' : ''                ,
        }]

        # 获取当前字段详细信息
        fieldInfo = fieldInfos[fieldName]

        # 这里的作用是将SQL的类型转换为Go的类型
        # 这里需要注意UNSIGNED和DATE两种情况：
        #  (1) UNSIGNED 需要设置标识符，将其转化为无整数型
        #  (2) 如果含有DATA需要给PO文件添加go标准库的"time"引用

        # 获取类型
        fieldType = fieldInfo['type']

        # 将SQL的类型转换为Go的类型
        goType = SqlTypeToGoType (fieldType['name'],fieldType['unsigned'])
        # 判断是否是time.Time,如果是那么引入time库
        if goType == 'time.Time' :
            importLib.add("time")

        # 字段命名 、外键 与 target标签 构建
        structFieldName = ""
        foreignFieldDefine = None
        target = []

        # gorm一般性标注
        gormOther = "type:{1}".format(fieldName,fieldType['name'])
        if fieldInfo['notnull']:
            gormOther += ";not null"

        # 检查命名方式
        structFieldName = re.sub('Ref$','Reference',Hump(fieldName))

        # 默认注释
        structFieldComment = fieldInfo['comment']

        # 设置Target及外键
        # 如果是主键
        if fieldInfo['primary'] :
            target += ['gorm:"column:{0};primary_key;{1}"'.format(fieldName,gormOther)]
            structFieldComment = '【主键】 ' + structFieldComment
        elif fieldInfo['foreign'] != None:
            # 注意：这里检测到外键，我们需要创建一个新的字段与外键对应
            # 检查命名方式
            # 检查是否包含ref作为结尾
            if len(re.findall('Ref$',Hump(fieldName))) > 0 :
                structFieldName = re.sub('Ref$','RefForeign',Hump(fieldName))
            else :
                structFieldName = Hump(fieldName) + 'Ref'
            target += ['gorm:"column:{0};{1}"'.format(fieldName,gormOther)]

            # 创建一个新的字段与外键定义
            foreignKey = fieldInfo['foreign']['key']
            foreignTable = fieldInfo['foreign']['table']
            foreignFieldTarget = [
                'gorm:"foreignKey:{0}"'.format(structFieldName),
                'json:"{0}"'.format(foreignTable + '_data')
            ]
            # 修改默认注释
            structFieldComment = '【外键】 指向({0})表.'.format(foreignTable) + structFieldComment

            # 创建外键指向的结构体的字段
            RefTableNameBase = Hump(re.sub('^' + TABLE_PREFIX , '' , foreignTable))
            foreignFieldDefine = {
            'name'    : RefTableNameBase + 'Data'                        ,
            'type'    : RefTableNameBase + 'Table'                       ,
            'target'  : foreignFieldTarget                               ,
            'comment' : '【实体】{0} 指向的实体'.format(structFieldName) ,
            }
        else :
            target += ['gorm:"column:{0};{1}"'.format(fieldName,gormOther)]
        target += ['json:"{0}"'.format(fieldName)]

        # 构建结构体字段
        fieldDefine = {
        'name'    : structFieldName      ,
        'type'    : goType               ,
        'target'  : target               ,
        'comment' : structFieldComment   ,
        }
        structFields += [fieldDefine]
        if foreignFieldDefine != None:
            structFields += [foreignFieldDefine]

    # 去掉前缀且不含后缀的结构名
    structNameBase = Hump(re.sub('^' + TABLE_PREFIX , '' , tableInfo['name']))
    # 含PO后缀的结构体名
    structPOName = structNameBase + 'PO'
    # 构建结构体别名
    structAliasCode = 'type {0}Table {0}PO'.format(structNameBase)
    # 构建结构体
    structCode = CreateGoStruct(structPOName,structFields,True)
    # 构建TableName()方法
    tableNameMethodCode = CreateGoStructMethod ('', structPOName ,'TableName',[],['string'],'\treturn "{0}"'.format(tableInfo['name']))
    # 构建Field结构体
    tableFieldNameStructName = re.sub('^' + TABLE_PREFIX , '' , tableInfo['name']).upper() + '_FIELDS'
    tableFieldNameStructCode = CreateGoStruct(tableFieldNameStructName,tableFieldNameFields,True)
    # 构建实例结构体
    tableFieldNameStructInstanceName = '_' + tableFieldNameStructName
    tableFieldNameStructInstanceContent = ""
    fieldNameMaxLen = max([ len(f['name']) for f in tableFieldNameFields])
    for tableFieldNameField in tableFieldNameFields :
        tableFieldNameStructInstanceContent += ('\t{0:'+ str(fieldNameMaxLen) +'s} : "{1}",\n').format(tableFieldNameField['name'],tableFieldNameField['name'].lower())
    tableFieldNameStructInstanceCode = 'var {0} {1} = {1} {{\n{2}}}'.format(tableFieldNameStructInstanceName,tableFieldNameStructName,tableFieldNameStructInstanceContent)
    # 构建FIELD方法
    tableFieldMethodCode = CreateGoStructMethod ('', structPOName ,'FIELD',[],[tableFieldNameStructName],'\treturn {0}'.format(tableFieldNameStructInstanceName))
    # 构建import
    importHeadCode = ''
    if len(importLib) > 1 :
        importHeadCode = 'import ('
        for lib in importLib :
            importHeadCode += '"{0}"\n'.format(lib)
        importHeadCode += ')'
    elif len(importLib) == 1 :
        importHeadCode = 'import "{0}"\n'.format(list(importLib)[0])

    # 合成代码
    allCode = AssembleCode(
    GO_FILE_NOTES,
    packageNameCode,
    importHeadCode,
    tableNotes,
    structAliasCode,
    structCode,
    tableNameMethodCode,
    # 这里是对SQL表中的字段名称的结构体生成，如果有需要可以自行取消注释
    # tableFieldMethodCode,
    # tableFieldNameStructCode,
    # tableFieldNameStructInstanceCode
    )

    # 返回结果
    return allCode

# 保存go文件
def SaveGoFile (path,fileName,poStr,encoding='utf-8') :
    # 打开一个文件
    fo = open(path + "/" + fileName, "w"  , encoding = encoding )
    fo.write( poStr )
    # 关闭打开的文件
    fo.close()
    return

def main() :
    ##################
    #  读取SQL文件   #
    ##################
    sqlStr = ""
    with open(SQL_FILE, 'r',encoding='UTF-8') as f:
       sqlStr = f.read()

    # 判断是否正确读取到SQL文件数据
    if sqlStr == "" :
        print("为正确读取到SQL文件：" + SQL_FILE)
        return

    ##################
    #   解析与生成   #
    ##################
    # 进行SQL表分割
    tables = SqlCut(sqlStr)

    # 获取包名
    packageName = ''
    if PACKAGE_NAME != '' :
        packageName = PACKAGE_NAME
    else :
        packageName = re.split('\\\\|/',OUTPUT_PATH)[-1]

    savePath = re.sub('\\\\','/',PROJECT_ROOT_PATH + "/" + OUTPUT_PATH)

    # 对每个表进行的数据解析

    for index in range (len(tables)) :
        tableInfo = ParseTable (tables[index])
        fileName = '{0}.po.go'.format(tableInfo['name'])
        print('构建[{0}]:'.format(index+1), fileName)
        code = CreatePO( packageName , tableInfo)
        SaveGoFile (savePath,fileName,code,encoding='UTF-8')

    return

## gogogo
if __name__ == '__main__':
    main()