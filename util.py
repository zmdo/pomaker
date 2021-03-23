# 一个小的工具函数
# 主要是获取正则表达式的第一个结果
# 如果结果为空，则返回 ""
# Param  : (string[]) 正则表达式的匹配结果
# Return : (string)   获取正则表达式的第一个结果,如果结果为空，则返回 ""
def GetFirstResult(result) :
    if len(result) > 0 :
        return result[0]
    else :
        return ""

# 驼峰命名法转换器
# 该函数能够将下滑线命名的形式转换为驼峰命名的形式
# 该函数默认首字母大写，可将defaultFlag设为False即
# 为首字母为小写
def Hump(name , defaultFlag = True) :
    flag = defaultFlag
    humpName = ""
    for ch in name :
        if ch == "_" :
            flag = True
            continue
        if flag :
            humpName += ch.upper()
            flag = False
        else :
            humpName += ch
    return humpName