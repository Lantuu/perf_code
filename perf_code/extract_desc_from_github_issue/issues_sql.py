import csv
import numpy
import re

import nltk
import pandas
import pymysql
from parseSOAPI import extractAPI
from bs4 import BeautifulSoup

host = 'localhost'
username = 'root'
password = '123456'
database='github_issues'

#关键词
KWs=['fast','slow','efficient','scalable','expensive','intensive','quick','rapid','performant','faster','slower','better','worse','worst','fastest','slowest',
    'performance','efficiency','speed ups','improve','slowdown','speedup', 'speed up','increase','accelerate','computationally']

def connectMySQL():
    '''连接数据库'''
    print('Open the database connection......')    # 打开数据库连接
    db = pymysql.connect(host,username,password,database,charset='utf8')    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    issues = executeSelect(cursor)
    parseBody(issues)
    db.close()  # 关闭数据库连接
    print('Close the database connection......')

def executeSelect(cursor):
    '''
      执行Select操作，返回SELECT的结果(body)
    '''
    print('Execute sql SELECT......')
    sql = "SELECT issues_number,repo,title,body,labels,link FROM issues"  # SQL 查询语句
    try:
        cursor.execute(sql)
        issues = cursor.fetchall()
        print('Sql SELECT execution is complete')
    except:
        print("Error: unable to fecth data")
    return issues

def executeAlter(cursor):
    print('Execute sql Alter......')
    sql = 'alter table questions add question varchar(5000)'
    try:
        cursor.execute(sql)
    except:
        print("Error: unable to fecth data")

def parseBody(columns):
    '''
    解析html代码（body,title)
    :param columns:title,body列
    :return: 包含关键词和code的句子
    '''
    for column in columns:
        issues_number = column[0]
        # if issues_number!=276:
        #     continue
        repo = column[1]
        title = column[2]
        body = column[3]
        label = column[4]
        link = column[5]


        #  如果含有代码片段，则删除
        if body.find('<pre')!=-1:
            body = deleteCode(body)
        if title.find('<pre')!=-1:
            title = deleteCode(title)

        codes = get_all_code(body, title)
        apis = []
        for code in codes:
            apis.extend(extractAPI.get_calls(code))
        apis = list(set(apis))  # 去重
        # print(codes)
        # print(apis)

        kw_and_code_descs = getKWDesc(body,title)
        savecsv(kw_and_code_descs,issues_number,repo,label,link,'G:\Performance\SO_Guid_Api\github_issues\desc\\issues3.csv',apis)
        for i in kw_and_code_descs:
            print(issues_number," : ",i)

def deleteCode(body):
    '''
    删除代码片段(含有pre标志的代码）
    :param body:
    :return:返回删除代码片段的body
    '''
    body_list = body.split('<pre')
    body = body_list[0]
    for i in range(len(body_list)):
        if body_list[i].find('</pre>') != -1:
            body_list[i] = body_list[i].split('</pre>')
            body = body + body_list[i][1]
    return body

def get_all_code(body,title):
    codes = []
    codes.extend(get_code_list(title)[1])
    codes.extend(get_code_list(body)[1])
    return codes

def get_code_list(sentence):
    '''
    提取出sentence含有<code>标志的代码：例如<code>tf.py_func()</code>
    :param sentence:待处理字符串
    :return:sen_codelist:[sen,code_list] code_list:sentence含有的所有代码,sen:sentence去除code_list之后的句子
    '''
    code_list = []  # 句子含有的代码
    sen_codelist = [] # ['sen','codelist']
    #提取出含有<code>的代码
    sen=''
    if sentence.find('<code>') != -1:
        for i in range(len(sentence.split('<code>'))):
            if i == 0:
                sen = sen + sentence.split('<code>')[0]
            if sentence.split('<code>')[i].find('</code>') != -1:
                code_list.append(sentence.split('<code>')[i].split('</code>')[0])
                sen = sen + sentence.split('<code>')[i].split('</code>')[1]
    else:
        sen = sentence

    # 去掉代码的标签(<code>)
    for i in range(len(code_list)):
        soup = BeautifulSoup(code_list[i],'html.parser')
        code_list[i] = ''
        for c in soup.find_all(text=True):
            code_list[i] = code_list[i] + c

    # 去掉句子的标签(<p>,</p>)
    soup = BeautifulSoup(sen, 'html.parser')
    sen = ''
    for q in soup.find_all(text=True):
        sen = sen + q

    # 去掉句子的链接(链接会影响正则表达式的匹配)
    pattern = re.compile(r'\S*http\S*|\S+\.com\S*|\S+\.htm\S*|\S+\.org\S*|\S+\.io\S*|\S+\.edu\S*|\S+\.shtml\S*|\S*/\w+/\w+/\w+\S*')
    linkList = pattern.findall(sen)
    for link in linkList:
        sen = sen.replace(link, '')

    # 用正则表达式匹配出code element
    pattern = re.compile(
        r'[a-zA-Z]\w*\(*\)*\[*\]*\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|\s\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|^\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|[a-zA-Z]\w*\([a-zA-Z0-9,=\.\(\)\[\]]*\)|[a-zA-Z]\w*\[[a-zA-Z0-9,=\.\(\)\[\]]*\]')
    re_code_list = pattern.findall(sen)

    for code in re_code_list:
        sen = sen.replace(code,'')

    for i in range(len(re_code_list)):
        # 去点以",", "." 结尾的符号
        if re_code_list[i][-1] == ',' or re_code_list[i][-1] == '.':
            re_code_list[i] = re_code_list[i][:-1]

        if re_code_list[i] == 'i.e' or re_code_list[i] == 'e.g' or re_code_list[i] == 'i.e.' or re_code_list[i] == 'e.g.':
            continue
        else:
            code_list.append(re_code_list[i])

    code_list=list(set(code_list))  # 去重
    sen_codelist.append(sen)
    sen_codelist.append(code_list)
    return sen_codelist

def getKWDesc(body,title):
    '''
    提取含关键字和代码的句子
    :param body:主体
    :param title:标题
    :return:kw_and_code_descs:['sen:含关键字和代码的句子','kw:sen包含的关键字','codelist:sen包含的代码']
    '''
    kw_and_code_descs = []  # 存放含有关键词也含有代码的句子
    # 提取含关键字的body
    sentencesList = body.split('<p>')  # 以<p>划分
    for sentences in sentencesList:
        sentenceList = nltk.sent_tokenize(sentences)  # 划分句子
        for sentence in sentenceList:
            code_sen_list = get_code_list(sentence)
            code_list = code_sen_list[1]
            sen = code_sen_list[0]
            #code_list= get_code_list(sentence)
            if len(code_list)!=0:
                kwList = []
                for kw in KWs:
                    matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", sen, re.I)
                    if matchobj is not None:
                        kwList.append(kw)
                if len(kwList) != 0:
                    soup = BeautifulSoup(sentence, 'html.parser')
                    sen = ''
                    for q in soup.find_all(text=True):
                        sen = sen + q
                    kw_and_code_descs.append([sen,kwList,code_list])

    # 提取含关键字的title
    titles = nltk.sent_tokenize(title)
    for t in titles:
        code_sen_list = get_code_list(t)
        code_list = code_sen_list[1]
        sen = code_sen_list[0]
        if len(code_list)!=0:
            kwList = []
            for kw in KWs:
                matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", str(sen), re.I)
                if matchobj is not None:
                    kwList.append(kw)
            if len(kwList) != 0:
                kw_and_code_descs.append([t, kwList,code_list])

    return kw_and_code_descs

def savecsv(kw_and_code_descs,issues_number,repo,label,link,csv_Path,apis):
    '''
    save desc data to csv file.
    :param descs: kw_and_code_descs:['sen:含关键字和代码的句子','kw:sen包含的关键字','codelist:sen包含的代码']
    :param question_id:
    :param csv_Path: 保存csv的路径
    '''
    with open(csv_Path, 'a+', encoding='gb18030',newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        for desc in kw_and_code_descs:
            writer.writerow([issues_number,repo,label,link,desc[0],desc[1],desc[2],apis])  # [question_id,desc,kw[],codelist]

if __name__ == "__main__":
    connectMySQL()