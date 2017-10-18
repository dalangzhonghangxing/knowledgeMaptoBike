from urllib import parse
import requests
from bs4 import BeautifulSoup
from urllib import request
import re

resultPath = "../result/"

# pattern = "(?<=target=\"_blank\"><em>)[^em]*(?=</em>_百度百科</a>)"  # 全红的词条，质量最好
pattern_bikeword = r"(?<= target=\"_blank\">).*(?=_百度百科</a>)"
pattren_bikeword_summary = r"(?<=<p class=\"result-summary\">).*(?=</p>)"
pattern_red = r"(?<=<em>)[^em]*(?=</em>)"


# 判断某个词语是否是百度词条
def isBikeWords(word):
    response = requests.get("https://baike.baidu.com/item/" + parse.quote(word))
    if response.url.find("error") == -1:
        return True
    else:
        return False


# 获取百度百科页面
def getBikePage(word):
    res = requests.Session().get("https://baike.baidu.com/item/" + parse.quote(word))
    res.encoding = "utf-8"
    return res.text


# 解析html中class="para"的内容
def parsePara(node):
    paras = node.find_all(class_="para")
    content = ""
    for p in paras:
        content += p.text
    return content


# 解析百度百科中对词条的定义
def parseLemmaSummary(html):
    soup = BeautifulSoup(html, "lxml")
    ls = soup.find_all(class_="lemma-summary")
    if len(ls) > 0:
        text = parsePara(ls[0])
    else:
        text = ""
    return text


# 找到正文开始的节点
def MainContentBegin(soup):
    catalog = soup.find(class_=u"lemmaWgt-lemmaCatalog")
    if catalog == None:
        catalog = soup.find(class_=u"basic-info cmn-clearfix")
    if catalog == None:
        catalog = soup.find(class_=u"edit-prompt")
    return catalog


def parseMainContent(html, title):
    soup = BeautifulSoup(html, "lxml")
    catalog = MainContentBegin(soup)
    # title = soup.find(attrs={"class": re.compile(r"lemmaWgt-lemma ?Title-title")}).find("h1").text
    node = catalog.find_next_sibling()
    content = ""
    flag = False
    tag = ""
    while (node != None):
        if 'class' in node.attrs and "anchor-list" not in node.attrs['class']:
            if ('para-title' in node.attrs['class']):
                content += node.text.replace(title, "").replace("\n", "")
            elif node.text.find("词条图册") == -1 and node.text.find("参考资料") == -1 and node.text.find("词条标签") == -1:
                c = node.text.strip().replace("\n", "")
                if c != "":
                    content += c + "\n"
        if node.text.find("词条标签") != -1:
            tag = node.text.strip().replace("词条标签：", "").replace("\n", "")
            flag = True
        node = node.find_next_sibling()
    if flag != True:
        tag = "None"
    return content, tag


def getContentByTitle(bikeWord, word):
    html = getBikePage(bikeWord)
    soup = BeautifulSoup(html, "lxml")
    catalog = MainContentBegin(soup)
    node = catalog.find_next_sibling()
    content = ""
    while node != None:
        if 'class' in node.attrs and "para-title" in node.attrs['class'] and node.text.find(word) != -1:
            NodeClass = node.attrs['class'][1]
            node = node.find_next_sibling()
            while "para-title" not in node.attrs['class'] or node.attrs['class'][1] != NodeClass:
                if "anchor-list" not in node.attrs["class"]:
                    if "para-title" in node.attrs['class']:
                        content += node.text.strip().replace("\n", "").replace(bikeWord, "") + "\n"
                    else:
                        c = node.text.strip().replace("\n", "")
                        if c != "":
                            content += c + "\n"
                node = node.find_next_sibling()
        if node != None:
            node = node.find_next_sibling()
    return content


# 为一个知识点寻找最近词条
def findClosedBikeWord(word):
    try:
        html = request.urlopen("https://baike.baidu.com/search/none?word=" + parse.quote(word)).read().decode()
        bikewords = re.findall(pattern_bikeword, html)
        summarys = re.findall(pattren_bikeword_summary, html)
        bestResult = []
        for i in range(0, len(bikewords)):
            redBikeWords = re.findall(pattern_red, bikewords[i])
            rbw = ""  # 将红色关键词整理出来
            for redBikeWord in redBikeWords:
                rbw += redBikeWord
            bw = bikewords[i].replace("<em>", "").replace("</em>", "")  # 将爬下来的百科词条中的em去掉
            radioBK = len(rbw) / len(bw)  # 红色关键词在词条中所占比例
            radioW = len(rbw) / len(word)  # 红色关键词在查询单词中所占的比例
            # redSummary = re.findall(pattern_red, summarys[i])
            if radioW > 0.9:  # 基本上能确定就是这个
                bestResult.clear()
                bestResult.append(bw)
                break
            if radioBK > 0.3 and radioW > 0.2:
                bestResult.append(bw)
        # 为了找到尽可能相近的百度词条，如果A词条是B词条的子串，则去除。例如“有理数”与“有理数加法”，去除“有理数”
        finalResult = []
        for br1 in bestResult:
            flag = True
            for br2 in bestResult:
                if br1 == br2: continue
                if br2.find(br1) != -1:
                    flag = False
            if flag == True:
                finalResult.append(br1)
        return finalResult
    except (Exception) as e:
        return []


def getSentence(bikeWord, keyWord):
    html = getBikePage(bikeWord)
    soup = BeautifulSoup(html, "lxml")
    catalog = MainContentBegin(soup)
    node = catalog.find_next_sibling()
    content = ""
    while node != None:
        if 'class' in node.attrs and "para" in node.attrs['class'] and node.text.find(keyWord) != -1:
            content += node.text.strip().replace("\n", "") + "\n"
        node = node.find_next_sibling()
    return content


# parseLemmaSummary(getBikePage("有理数"))
# parseMainContent(getBikePage("有理数乘法法则"))
# parseMainContent(getBikePage("有理数"))
# print(parseMainContent(getBikePage("一元二次方程")))
# getSentence("绝对值", "非负性")
# print(getContentByTitle("一元一次方程", "应用"))
# print(findClosedBikeWord("总体、个体、样本、样本容量"))

# file = open(resultPath = "../result/"+"unmatched.txt", "r", encoding="utf-8")
# line = file.readline()
# knowledges = line.split(" ")
# for k in knowledges:
#     print(k + "->",findClosedBikeWord(k))
