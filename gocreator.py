# 创建Go结构体字段标签
def CreateGoStructFieldTarget (target , limit = None ) :
    targetCode = ""
    if limit != None and len(limit) > 0:
        for i in range (len(target)) :
            targetCode += ('{0:' + str(limit[i]) + 's} ').format(target[i])
    else :
        for item in target :
            targetCode += item + " "
        targetCode = targetCode.strip()
    return targetCode

# 创建Go结构体字段
def CreateGoStructField ( filedName , typeName , tag , comment = '' ,limit = [1,1] ) :
    code = ('\t{0:' + str(limit[0]) +  's} {1:' + str(limit[1]) +  's}').format(filedName,typeName)
    if tag != '' :
        code = code + ' `{0}`'.format(tag)

    if comment != '' :
        code += ' // ' + comment
    return code

# 创建Go结构体
def CreateGoStruct( structName , structFields , formatFlag = True , Notes = True) :
    contentCode = ""
    if formatFlag :
        # 寻找每个部分最长的字符串长度
        maxLen = [0,0]
        maxLen[0] = max([len(fieldDefine['name']) for fieldDefine in structFields])
        maxLen[1] = max([len(fieldDefine['type']) for fieldDefine in structFields])
        # 同理，寻找target的字段的最长长度
        targetNum = max([len(fieldDefine['target']) for fieldDefine in structFields])
        targetMaxlen = []
        for i in range (targetNum) :
            targetMaxlen += [max([len(fieldDefine['target'][i]) for fieldDefine in structFields])]

        for fieldDefine in structFields :
            targetCode = CreateGoStructFieldTarget ( fieldDefine['target'] , targetMaxlen)
            contentCode += CreateGoStructField( fieldDefine['name'] , fieldDefine['type'] , targetCode , fieldDefine['comment'] , maxLen ) + "\n"
    else :
        for fieldDefine in structFields :
            targetCode = CreateGoStructFieldTarget ( fieldDefine['target'])
            contentCode += CreateGoStructField( fieldDefine['name'] , fieldDefine['type'] , fieldDefine['comment'] , targetCode ) + "\n"
    code = 'type {0} struct {{\n{1}}}\n'.format(structName,contentCode)
    return code

# 创建结构体方法/函数
def CreateGoStructMethod ( structName , structType ,  methodName , methodParams , returnTypes, content ) :
    belong = "{0} {1}".format(structName,structType).strip()
    paramsCode = ""
    for param in methodParams :
        paramsCode += param['name'] + ' ' + param['type'] + ','
    paramsCode = paramsCode[:-1]
    returnsCode = " "
    if len(returnTypes) > 1 :
        returnsCode += "("
        for type in returnTypes :
            returnsCode += type + ','
        returnsCode = returnsCode[:-1] + ") "
    elif len(returnTypes) == 1:
        returnsCode += returnTypes[0] + " "
    code = 'func ({0}) {1}({2}){3}{{\n{4}\n}}\n'.format(belong,methodName,paramsCode,returnsCode,content)
    return code

def AssembleCode (*code) :
    res = ""
    for block in code :
        if block != '':
            res += block + "\n"
    return res
