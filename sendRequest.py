from urllib import request
from urllib import parse
import requests
import Utils
import re
import 组卷网映射到百度词条.bike as bike

zjw_knowledge_path = "F:\学习\一课一练\组卷网平台知识点\初中.csv"

pattern = "(?<=target=\"_blank\"><em>)[^em]*(?=</em>_百度百科</a>)"  # 全红的词条，质量最好


# r = requests.get(bikePageURL)
# print(r.url.find("error"))

def isBikeWords(url, word):
    response = requests.get("https://baike.baidu.com/item/" + parse.quote(word))
    if response.url.find("error") == -1:
        return True
    else:
        return False


# 筛选出所有知识点中能够直接与百度百科词条相匹配的知识点
def findMatchandUnmatch():
    matched = []
    unmatched = []

    i = 1
    file = open(zjw_knowledge_path, "r", encoding="utf-8")
    for line in file:
        knowledge = line.split(",")[1]
        print(i)
        i += 1
        if bike.isBikeWords(knowledge):
            matched.append(knowledge)
        else:
            unmatched.append(knowledge)
    content = ""
    for k in matched:
        content += k + " "
    Utils.writeFile("matched.txt", content)
    content = ""
    for k in unmatched:
        content += k + " "
    Utils.writeFile("unmatched.txt", content)


# 为不能直接匹配的知识点中寻找最近词条
def findCloseBikesForUnmatch():
    subMatch = ""
    empty = ""
    exception = ""

    file = open("unmatched.txt", "r", encoding="utf-8")
    line = file.readline()
    i = 1
    for k in line.split(" "):
        try:
            html = request.urlopen("https://baike.baidu.com/search/none?word=" + parse.quote(k)).read().decode()
            bestResult = re.findall(pattern, html)
            if len(bestResult) == 0:
                empty += k + " "
            else:
                subMatch += k + ":"
                for s in bestResult:
                    subMatch += s + " "
                subMatch += "\n"
        except (Exception) as e:
            exception += k + " "
        print(i)
        i += 1
    Utils.writeFile("subMatch.txt", subMatch)
    Utils.writeFile("empty.txt", empty)
    Utils.writeFile("exception.txt", exception)


findCloseBikesForUnmatch()
