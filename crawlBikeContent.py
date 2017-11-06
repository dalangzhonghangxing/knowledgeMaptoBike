import 组卷网映射到百度词条.bike as bike
import 组卷网映射到百度词条.getBikeContent as gbc
import Utils

file = open("F:\学习\一课一练\实验结果\映射的叶子知识点.txt", "r", encoding="utf-8")
# file = ["数据分析:数据分析", "多项式:多项式"]
i = 1
for line in file:
    knowledge = line.split(":")[0]
    bikeWords = line.split(":")[1].replace("\n", "").split(" ")
    content = ""
    for bikeWord in bikeWords:
        if bikeWord == "":
            continue
        if bikeWord.find(">") != -1:
            bw = bikeWord.split(">")[0]
            kw = bikeWord.split(">")[1]
            content += "mainContent\n"
            content += bike.getContentByTitle(bw, kw)
        elif bikeWord.find("#") != -1:
            bw = bikeWord.split("#")[0]
            kw = bikeWord.split("#")[1]
            content += "mainContent\n" + bike.getSentence(bw, kw)
        else:
            content += gbc.getContentOfBikeWord(bikeWord)
    Utils.writeFile("F:\学习\一课一练\实验结果\知识点内容\\" + knowledge + ".txt", content)
    print(i, knowledge)
    i += 1
