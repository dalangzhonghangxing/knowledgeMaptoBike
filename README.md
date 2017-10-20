# mapping_3

+ 分支做了如下改进
  1. 构建词库，避免“数与式”等短语被拆开
  2. 组合的时候不去掉“的”
  3. 在分词过程中，生成组合短语的时候，主语使用原来的主语，不使用百度百科最接近的主语

+ 结果
  + 准确率 211/256 = 0.824
  + 召回率 303/442 = 0.68

+ 还存在的问题
  9. 包含“混合运算”、“乘除法”、“加减法”、“XX法则”、“运用公式法”等还可再分词的结果不好
  10. “一元一次不等式的应用:一元一次方程 ”存在这种映射
  11. “点的坐标:地面点坐标 ”
  12. “坐标确定位置:光学坐标定位仪 坐标系”存在没有“的”主从关系
  13. 红色字体可能会被百度做转义，不能直接使用，要逐字计算
  14. 考虑用summary中的红色字体+推荐词条与Knowledge的相似度来衡量Knowledge与bikeword的相似性
  15. “与”和“的”划分的先后关系要做实验考虑