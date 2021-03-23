# PO对象文件命名规范
1. PO对象文件命名与表名相同,且以".po.go"为后缀，例如:"user.po.go"
2. PO对象的结构体创建，需要使用驼峰命名法，使结构体命名与表名相同（或者能够直接对其进行识别），且需要在末尾添加PO作为标识
3. 每个PO对象都需要使用type重新命名一次，将"PO"替换为"Table"，以该方式命名的结构体仅在 4 中描述的情况下，即作为外键的情况下进行使用
4. 结构体内部的字段命名，外键需要使用"表名 + Ref"作为后缀，如果本身引用的表名就是以"Ref"作为结尾的，那么使用"Reference"进行代替，如果该字段作为外键，那么使用"RefForeign"进行命名。同时在表内需要添加外键对应的表的结构体(使用以 3 中描述的Table为结尾命名的结构体)。
5. 字段名可以根据需要进行创建字符串常量，且用"大写字母 + 下划线"的方式进行命名，命名规则为"表名+字段名"
6. 结构体出主键外的每个字段强制使用 gorm 的 column 进行表名配置 
7. 无论结构名与表名是否相同，都强制使用TableName()返回表名

---
# PO file naming specification
1. The go file name is the same as the table name, and is marked with ".po.go" Is a suffix, for example: "user.po.go "
2. To create the structure of Po object, we need to use hump naming method to make the structure name the same as the table name (or be able to identify it directly), and we need to add Po at the end as the identifier
3. Each Po object needs to be renamed with type, and "PO" is replaced with "Table". The structure named in this way can only be used as a foreign key in the case described in 4
4. For field naming inside structure, foreign key needs to use "table name + Ref" as suffix. If the referenced table name ends with "Ref", then use "Reference" instead. If the field is used as foreign key, then use "RefForeign" for naming. At the same time, you need to add the structure of the table corresponding to the foreign key in the table (use the structure named after the table described in 3).
5. The field name can be created as a string constant according to the needs, and named in the way of "capital letter + underline". The naming rule is "table name + field name"
6. Each field outside the primary key of the structure is forced to use the column of Gorm for table name configuration
7. Force TableName() to return the table name regardless of whether the structure name is the same as the table name