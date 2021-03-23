import re
from util import GetFirstResult

# 这里定义了Sql类型转换为go类型的基本函数
# @update : 2021.3.6
# @author : 张铭(560365)

SQL_TO_GO_TYPE = {
# 整型
'tinyint'   : 'int8'      ,
'smallint'  : 'int16'     ,
'int'       : 'int32'     ,
'bigint'    : 'int64'     ,
# 浮点型
'float'     : 'float32'   ,
'double'    : 'float64'   ,
# Text 类型
'text'      : 'string'    ,
'varchar'   : 'string'    ,
# 日期类型
'date'      : 'time.Time' ,
'datetime'  : 'time.Time' ,
'timestamp' : 'time.Time' ,
}

SQL_TO_GO_UNSIGNED_TYPE = {
# 整型
'tinyint'   : 'uint8'    ,
'smallint'  : 'uint16'   ,
'int'       : 'uint32'   ,
'bigint'    : 'uint64'   ,
}

# 将SQL的类型转换成Go的类型
def SqlTypeToGoType (sqlType,unsignedFlag) :
    # 分离类型与括号
    sqlBaseType =  GetFirstResult(re.findall('([^\(]*)',sqlType,flags=re.IGNORECASE)).lower()
    # 匹配go的类型
    if unsignedFlag :
        return SQL_TO_GO_UNSIGNED_TYPE[sqlBaseType]
    else :
        return SQL_TO_GO_TYPE[sqlBaseType]
