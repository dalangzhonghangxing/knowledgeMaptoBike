import os

import Utils
import 组卷网映射到百度词条.bike as bike

resultPath = "../result/"

words = ["数与式", "点、线、面、体"]


# 根据百科词语去爬取百科页面
def getContentOfBikeWord(bikeWord):
    content = ""
    html = bike.getBikePage(bikeWord)
    defination = bike.parseLemmaSummary(html)
    content += "LemmaSummary" + "\n"
    content += defination + "\n"
    content += "mainContent" + "\n"
    mainContent = bike.parseMainContent(html, bikeWord)
    content += mainContent[0] + "\n"
    if mainContent[1].find("书籍") != -1 or mainContent[1].find("出版物") != -1 or mainContent[1].find("游戏") != -1:
        return ""
    else:
        return content


def getMatchedContent():
    fileMatched = open(resultPath + "matched.txt", "r", encoding="utf-8")
    line = fileMatched.readline()
    error = ""
    book = ""
    knowledges = line.split(" ")
    length = len(knowledges)
    i = 0
    for knowledge in knowledges:
        i += 1
        print(i / length)
        try:
            content = getContentOfBikeWord(knowledge)
            if content != "":
                Utils.writeFile("../KnowledgeContent/" + knowledge + ".txt", content)
            else:
                book += knowledge + " "
        except Exception:
            error += knowledge + " "
    fileMatched.close()
    Utils.writeFile("error.txt", error)
    Utils.writeFile("book.txt", book)


def getSimilarity(a, b):
    # zma = set()
    # zmb = set()
    # for _, z in enumerate(a):
    #     zma.add(z)
    # for _, z in enumerate(b):
    #     zmb.add(z)
    #
    # for z in zmb:
    s = [x for x in a if x in b]
    print(len(s) / len(a) + len(b))


def divideKnowledge(knowledge):
    # 如果该知识点处于词库中，则不进行分词
    if knowledge in words:
        return [], [knowledge], []

    # 首先按照并列词划分
    partition = []
    he = knowledge.split(u"和")
    for h in he:
        yu = h.split(u"与")
        for y in yu:
            dh = y.split(u"、")
            for d in dh:
                ji = d.split(u"及")
                for j in ji:
                    partition.append(j)

    # 从划分的短语中划分出主要概念以及子概念
    subjects = []
    combination = []
    newPartition = []
    for p in partition:
        subject = ""
        left = ""
        if p.find(u"-") != -1:
            subject = p.split(u"-")[0]
            left = p.split(u"-")[1]
        elif p.find(u"—") != -1:
            subject = p.split(u"—")[0]
            left = p.split(u"—")[1]
        elif p.find(u"的") != -1:
            subject = p.split(u"的")[0]
            if len(p.split(u"的")) > 2:
                res = p.split(u"的")
                left = res[1] + "的" + res[2]
            else:
                left = p.split(u"的")[1]

        if left == "":
            newPartition.append(p)
        else:
            newPartition.append(left)

        if subject != "":
            subjects.append(subject)
            combination.append(p)


            # 如果有主概念，则对这个短语进行主从的一个组合
            # if subject != "":
            #
            #     if bike.isBikeWords(subject):
            #         subjects.append(subject)
            #         combination.append(subject + u"的" + left)
            #         newPartition.append(left)
            #     else:
            #         candinates = bike.findClosedBikeWord(subject)
            #         if len(candinates) > 0:
            #             newPartition.append(left)
            #             for candinate in candinates:
            #                 combination.append(candinate + u"的" + left)
            #                 subjects.append(candinate)
            #
            # else:
            #      newPartition.append(p)

    # 如果只有一个主概念，那么将这个主概念与所有子概念进行组合
    if len(subjects) == 1:
        combination.clear()
        for p in newPartition:
            combination.append(subjects[0] + u"的" + p)

    return subjects, newPartition, combination


def getUnmatchedKnowledgeContent(knowledge):
    divisionResult = divideKnowledge(knowledge)
    subjects = divisionResult[0]  # 主概念
    partitions = divisionResult[1]  # 子概念
    combinations = divisionResult[2]  # 组合

    addedBikeWords = set()  # 已经爬过的百度词条
    # 如果有subjects
    if len(subjects) > 0:
        content = "mainContent" + "\n"
        specificKowledge = ""
        for partition in partitions:
            flag = False
            for subject in subjects:
                titleContent = bike.getContentByTitle(subject, partition)
                if titleContent != "":  # 从subject的百科页面中找到partition的子模块
                    content += titleContent
                    flag = True
                    specificKowledge += subject + ">" + partition + " "
                    addedBikeWords.add(subject)
            if flag == False:  # 没有子模块，尝试找句子
                s = ""
                for subject in subjects:
                    sentence = bike.getSentence(subject, partition)
                    if sentence != "":
                        s += sentence + "\n"
                        addedBikeWords.add(subject)
                        specificKowledge += subject + "#" + partition + " "
                if s != "":  # 从subject的百科页面中找到有关partition的句子
                    content += s
                if s == "":  # 没找到句子，尝试找组合
                    for combination in combinations:
                        isbike = bike.isBikeWords(combination)
                        if isbike:  # 组合是百科词条，直接把这个词条抓过来
                            s += getContentOfBikeWord(combination) + "\n"
                            addedBikeWords.add(combination)
                            specificKowledge += combination + " "
                        else:  # 寻找组合的相近词条
                            candinates = bike.findClosedBikeWord(combination)
                            for candinate in candinates:
                                if candinate not in addedBikeWords:
                                    s += getContentOfBikeWord(candinate) + "\n"
                                    addedBikeWords.add(candinate)
                                    specificKowledge += candinate + " "
                    content += s
                if s == "":  # 如果没还找到对应的内容，那就把subject的内容作为该知识点的内容
                    for subject in subjects:
                        content += getContentOfBikeWord(subject).replace("LemmaSummary\n", "").replace(
                            "mainContent\n", "") + "\n"
                        specificKowledge += subject + " "
        return content, specificKowledge
    else:
        content = ""
        specificKowledge = ""
        for partition in partitions:
            if partition in addedBikeWords:
                continue
            isBike = bike.isBikeWords(partition)
            if isBike == True:
                c = getContentOfBikeWord(partition)
                if c != "":
                    content += c + "\n"
                    specificKowledge += partition + " "
                    addedBikeWords.add(partition)
                else:
                    specificKowledge += "?" + partition + " "
            else:
                candinates = bike.findClosedBikeWord(partition)
                for candinate in candinates:
                    c = getContentOfBikeWord(candinate)
                    if c != "":
                        content += c + "\n"
                        specificKowledge += candinate + " "
                        addedBikeWords.add(candinate)
        return content, specificKowledge


def getUnmatchedContent():
    file = open(resultPath + "unmatched.txt", "r", encoding="utf-8")
    line = file.readline()
    knowledges = line.split(" ")
    length = len(knowledges)
    i = 0;
    error = ""
    empty = ""
    mapping = ""
    for k in knowledges:
        i += 1
        try:
            t = getUnmatchedKnowledgeContent(k)
            content = t[0]
            m = k + ":" + t[1]
            if content != "":
                Utils.writeFile("../unMatchedKnowledgeContent/" + k + ".txt", content)
                mapping += m + "\n"
                print(i / length, k, "\t", m)
            else:
                empty += k + " "
                print("empty:" + k)
        except Exception:
            error += k + " "
            print("error:" + k)
    Utils.writeFile(resultPath + "error.txt", error)
    Utils.writeFile(resultPath + "empty.txt", empty)
    Utils.writeFile(resultPath + "mapping.txt", mapping)


# clearEmptyFile("../unMatchedKnowledgeContent/")
def clearEmptyFile(path):
    pathDir = os.listdir(path)
    for filename in pathDir:
        fopen = open(os.path.join('%s%s' % (path, filename)), 'r', encoding="utf-8")
        line = fopen.readline()
        fopen.close()
        if line == "":
            print(filename)
            os.remove(os.path.join('%s%s' % (path, filename)))


getUnmatchedContent()
# print(getUnmatchedKnowledgeContent("幂的乘方与积的乘方"))
# print(getContentOfBikeWord("样本"))
# print(divideKnowledge("总体、个体、样本、样本容量"))
# "../unMatchedKnowledgeContent/"
