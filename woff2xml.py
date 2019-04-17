from fontTools.ttLib import TTFont

font = TTFont('./deca.woff')
font.saveXML('./deca.xml')

font = TTFont('./deca.woff')   # 打开文件
gly_list = font.getGlyphOrder()     # 获取 GlyphOrder 字段的值
for gly in gly_list[2:]:    # 前两个值不是我们要的，切片去掉
    print(gly)                 # 打印

