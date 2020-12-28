import csv
import numpy
import re

import nltk
import pandas
import pymysql
from py.parseSOAPI import extractAPI
host = 'localhost'
username = 'root'
password = '123456'
database = 'github_issues'

# 关键词
KWs = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien','scalable', 'scalability', 'efficiency', 'efficient']
Kws2 = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']


def connect_mysql():
    '''连接数据库'''
    print('Open the database connection......')    # 打开数据库连接
    db = pymysql.connect(host, username, password, database, charset='utf8')    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    issues = execute_select(cursor)
    parse_body(issues)
    db.close()  # 关闭数据库连接
    print('Close the database connection......')


def execute_select(cursor):
    '''
      执行Select操作，返回SELECT的结果(body)
    '''
    print('Execute sql SELECT......')
    sql = "SELECT issue_number,repo,comment_id,body FROM comments"  # SQL 查询语句
    try:
        cursor.execute(sql)
        issues = cursor.fetchall()
        print('Sql SELECT execution is complete')
    except:
        print("Error: unable to fecth data")
    return issues


def execute_alter(cursor):
    print('Execute sql Alter......')
    sql = 'alter table questions add question varchar(5000)'
    try:
        cursor.execute(sql)
    except:
        print("Error: unable to fecth data")


def parse_body(columns):
    '''
    解析html代码（body,title)
    :param columns:title,body列
    :return: 包含关键词和code的句子
    '''
    len_kw_sen = 0  # 含有kw的句子数量

    for column in columns:
        issues_number = column[0]
        repo = column[1]
        comment_id = column[2]
        body = column[3]

        # if issues_number!=38:
        #     continue
        #  如果含有代码片段，则删除
        body = delete_code(body)

        # 得到一个issues下描述的所有api
        codes = get_all_code(body)
        apis = []
        for code in codes:
            apis.extend(extractAPI.get_apis(code))
        apis = list(set(apis))  # 去重

        l, kw_and_code_descs = get_kw_code_desc(body)
        len_kw_sen += l

        if len(kw_and_code_descs) != 0:
            save_csv(kw_and_code_descs, issues_number, repo, 'D:\\work\\performance\\github_issues\\issues_desc\\desc_20_0102\\comments.csv',apis,comment_id)
            for i in kw_and_code_descs:
                print(issues_number, " : ", i)
    print('len_kw_sen: ',len_kw_sen)


def delete_code(text):
    '''
    删除代码片段(含有pre标志的代码）
    :param body:
    :return:返回删除代码片段的body
    '''
    text_list = text.split('\n')
    text = ''
    tag_start = -1
    for i in range(len(text_list)):
        if text_list[i].strip().startswith('```') and tag_start == -1:
            tag_start = i
            continue

        elif text_list[i].strip().startswith('```') and tag_start != -1:
            tag_start = -1
            continue

        elif tag_start != -1:
            continue

        elif text_list[i]=='':
            continue

        elif text_list[i].strip().startswith('> > '):
            continue

        else:
            text = text + text_list[i] + '\n'

    return text


def get_all_code(body):
    codes = []
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
    # 提取代码

    code_list = re.findall('`{1,2}[^`]*`{1,2}', sentence)

    for i in range(len(code_list)):
        sentence = sentence.replace(code_list[i],'')
        code_list[i] = code_list[i].replace('`','')

    # 去掉句子的链接(链接会影响正则表达式的匹配)
    pattern = re.compile(r'\S*http\S*|\S+\.com\S*|\S+\.htm\S*|\S+\.org\S*|\S+\.io\S*|\S+\.edu\S*|\S+\.shtml\S*|\S*/\w+/\w+/\w+\S*')
    linkList = pattern.findall(sentence)
    for link in linkList:
        sentence = sentence.replace(link, '')

    # 用正则表达式匹配出code element
    pattern = re.compile(
        r'[a-zA-Z_]\w*\(*\)*\[*\]*\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|\s\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|^\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|[a-zA-Z]\w*\([a-zA-Z0-9,=\.\(\)\[\]]*\)|[a-zA-Z]\w*\[[a-zA-Z0-9,=\.\(\)\[\]]*\]')
    re_code_list = pattern.findall(sentence)

    for code in re_code_list:
        sentence = sentence.replace(code,'')

    for i in range(len(re_code_list)):
        # 去点以",", "." 结尾的符号
        if re_code_list[i][-1] == ',' or re_code_list[i][-1] == '.':
            re_code_list[i] = re_code_list[i][:-1]

        if re_code_list[i] == 'i.e' or re_code_list[i] == 'e.g' or re_code_list[i] == 'i.e.' or re_code_list[i] == 'e.g.':
            continue
        else:
            code_list.append(re_code_list[i])

    code_list=list(set(code_list))  # 去重
    sen_codelist.append(sentence)
    sen_codelist.append(code_list)
    return sen_codelist


def get_kw_list(sentence):
    # kwList = []
    # for kw in KWs:
    #     matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", sentence, re.I)
    #     if matchobj is not None:
    #         kwList.append(kw)
    # return kwList
    re_kw = []
    for kw in KWs:
        matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", sentence, re.I)
        if matchobj is not None:
            re_kw.append(kw)

    kw_list = []

    if len(re_kw) != 0:
        return kw_list

    for kw in Kws2:
        if sentence.find(kw) != -1:
            kw_list.append(kw)

    return kw_list


def get_kw_code_desc(body):
    '''
    提取含关键字和代码的句子
    :param body:主体
    :param title:标题
    :return:kw_and_code_descs:['sen:含关键字和代码的句子','kw:sen包含的关键字','codelist:sen包含的代码']
    '''
    len_kw_sen = 0
    kw_and_code_descs = []  # 存放含有关键词也含有代码的句子

    # 提取含关键字的body
    sentencesList = body.split('\n')  # 以\n划分
    for sentences in sentencesList:
        sentenceList = nltk.sent_tokenize(sentences)  # 划分句子
        for sentence in sentenceList:
            code_sen_list = get_code_list(sentence)
            code_list = code_sen_list[1]  # 句子含有的所有代码元素
            sen = code_sen_list[0]  # 除去代码元素后的句子
            kwList = get_kw_list(sen)  # 句子含有的所有关键词

            if len(kwList) != 0:
                len_kw_sen += 1

            if len(code_list) != 0 and len(kwList) != 0:
                kw_and_code_descs.append([sentence,kwList,code_list])

    return (len_kw_sen,kw_and_code_descs)


def save_csv(kw_and_code_descs, issues_number, repo, csv_Path, apis, comment_id):
    """
     save desc data to csv file.
    """
    with open(csv_Path, 'a+', encoding='gb18030', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        for desc in kw_and_code_descs:
            writer.writerow([issues_number,repo,desc[0],desc[1],desc[2],apis,comment_id])  # [question_id,desc,kw[],codelist]


if __name__ == "__main__":
    connect_mysql()
