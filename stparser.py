import re
from util import GetFirstResult

# Sql Table Parser (stparser)
# SQL表定义解析器
# @update : 2021.3.6
# @author : 张铭(560365)


# SQL语句分割
# 将原始的SQL语句分割成单个Create的数据
# Param  : (string)   原始的SQL字符串
# Return : (string[]) 根据原始的SQL字符串分割好的单个表的SQL
def SqlCut ( sqlInput ) :

    # 去除各种注释
    sqlStr = re.sub('--.*', "" , sqlInput , flags=re.IGNORECASE)

    # 寻找 "CREATE TABLE" 关键词，并统计共几个表
    tableCount =  len(re.findall('CREATE\s+TABLE', sqlStr , flags=re.IGNORECASE))
    print("共查找到" + str(tableCount) + "张表")

    # 使用正则表达式对表进行分割
    tables = re.findall('CREATE\s+TABLE\s+[^;]*', sqlStr, flags=re.IGNORECASE)

    # 进行分割
    return tables

# SQL表语句解析
# 解析单个表的SQl语句，将其做成一个map存放
# Param  : (string)
# Return : ({})
def ParseTable (tableSql) :

    # 获取表名
    tableName = GetFirstResult(re.findall('CREATE\s+TABLE\s+`(.*)`',tableSql,flags=re.IGNORECASE))

    # 获取注释
    tableComment = GetFirstResult(re.findall('COMMENT\s*=\s*\'(.*)\'[^/)]*$',tableSql,flags=re.IGNORECASE))

    # 获取所有字段主体
    context = re.findall('CREATE\s+TABLE\s+[^\(]+\((.*)\)[^/)]*$',tableSql,flags=re.IGNORECASE|re.DOTALL)[0]

    # 根据逗号分隔字段
    # 直接用用split会有一个在括号中无法进行分割的BUG
    fieldDefines = re.split(',(?!.*\\))',context,0,flags=re.IGNORECASE)

    # 对字段进行解析
    fieldInfos = {}
    primaryFields = set()
    otherCommands = []
    for fieldDefine in fieldDefines :
        # 获取字段名
        fieldName = GetFirstResult(re.findall('^[\s]*`(.*)`',fieldDefine,flags=re.IGNORECASE))
        # 如果不存在字段名，则认为其不是用于定义字段的命令
        # 将其归为其他命令（otherCommands），并跳过执行
        if fieldName == "" :
           otherCommands += [fieldDefine]
           continue
        # 获取字段类型
        fieldType = GetFirstResult(re.findall('^[\s]*`.*`\s+([^\s]*)',fieldDefine,flags=re.IGNORECASE))
        fieldTypeSize = GetFirstResult(re.findall('^.*\s*\\((.*)\\)',fieldType.strip(),flags=re.IGNORECASE))
        # 查找是否含有UNSIGNED
        fieldTypeFormat = fieldType.replace('(', '\\(').replace(')','\\)')
        temp = GetFirstResult(re.findall(fieldTypeFormat + '\s+([^\s]*)',fieldDefine,flags=re.IGNORECASE)).lower()
        unsignedFlag = temp == 'unsigned'
        # 检查否可以为null
        notnull = len(re.findall('\s+not\s+null\s+',fieldDefine,flags=re.IGNORECASE)) > 0
        # 获取注释
        fieldComment = GetFirstResult(re.findall('COMMENT\s+\'(.*)\'',fieldDefine,flags=re.IGNORECASE|re.DOTALL))
        # 检查是否是主键
        primary = len(re.findall('PRIMARY\s+KEY\s+',fieldDefine,flags=re.IGNORECASE)) > 0
        if primary :
            primaryFields += {fieldName}
        # 检查是否有外键
        foreign = None
        # 构造一个字典
        fieldInfo = {
        'name'   : fieldName,
        'type'   : {'name': fieldType,'size':fieldTypeSize,'unsigned':unsignedFlag},
        'notnull': notnull,
        'comment': fieldComment,
        'primary': primary,
        'foreign': foreign,
        }
        # 加入字段信息数组
        fieldInfos[fieldName] = fieldInfo

    # 对其他命令进行解析
    # 这里主要是检查主键和外键
    for command in otherCommands :
        # 对主键进行检查
        # PRIMARY KEY (`?`)
        # TODO BUG
        primaryKeyCheckResult = GetFirstResult(re.findall('PRIMARY\s+KEY\s*\(\s*(.*)\s*\)',command,flags=re.IGNORECASE))
        primaryKeyExtract = re.findall('`([^`^,]*)`',primaryKeyCheckResult)

        # 如果出现检测结果，就合并二者
        # 并将与之对应的字段的信息设置为主键
        if len(primaryKeyExtract) > 0 :
            primaryFields = primaryFields | set(primaryKeyExtract)
            for key in primaryFields :
                fieldInfos[key]['primary'] = True
            continue

        # 对外键进行检查
        # FOREIGN KEY (`?`) REFERENCES table_name(`?`)
        foreignKeyCheckResult = re.findall('FOREIGN\s+KEY\s*\(\s*`(.*)`\s*\)\s*REFERENCES\s+([^\s]*)\s*\(\s*`(.*)`\s*\)',command,flags=re.IGNORECASE)
        if len(foreignKeyCheckResult) > 0 :
            foreign = foreignKeyCheckResult[0]
            fieldInfos[foreign[0]]['foreign'] = {
                'table' : foreign[1] ,
                'key'   : foreign[2]  ,
            }
            continue

    # 返回解析信息
    return {
    'name'      : tableName     ,  # 表名
    'comment'   : tableComment  ,  # 表注释
    'primary'   : primaryFields ,  # 主键表
    'fields'    : fieldInfos    ,  # 字段信息
    }
