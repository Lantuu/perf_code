import csv
import re

import nltk
import pymysql
from parseSOAPI import extractAPI
from bs4 import BeautifulSoup



host = 'localhost'
username = 'root'
password = '123456'
database='so'

#关键词
KWs=['fast','slow','efficient','scalable','expensive','intensive','quick','rapid','performant','faster','slower','better','worse','worst','fastest','slowest',
    'performance','efficiency','speed ups','improve','slowdown','speedup', 'speed up','increase','accelerate','computationally']

def connectMySQL():
    '''连接数据库'''
    print('Open the database connection......')    # 打开数据库连接
    db = pymysql.connect(host,username,password,database,charset='utf8')    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    parseBody(executeSelect(cursor))
    db.close()  # 关闭数据库连接
    print('Close the database connection......')

def executeSelect(cursor):
    '''
      执行Select操作，返回SELECT的结果(body)
    '''
    print('Execute sql SELECT......')
    sql = "SELECT answer_id,question_id,body FROM answers"  # SQL 查询语句
    try:
        cursor.execute(sql)
        answers = cursor.fetchall()
    except:
        print("Error: unable to fecth data")
    print('Sql SELECT execution is complete')
    return answers

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
    len_kw_sen = 0

    for column in columns:
        answer_id = column[0]
        question_id = column[1]
        body = column[2]

        #  如果含有代码片段，则删除
        if body.find('<pre')!=-1:
            body = deleteCode(body)

        kw_desc, len_kw = getKWDesc(body)
        len_kw_sen = len_kw_sen + len_kw

        # apis = get_all_code(body)
        # savecsv(kw_desc,answer_id,question_id,'G:\\Performance\\SO_Guid_Api\\stackoverflow\\SO_desc\\SO_1011\\stackoverflow_latest_answer.csv',apis)
        # for i in kw_desc:
        #     print(answer_id," : ",i)
    print(len_kw_sen)

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

def getKWDesc(body):
    '''
    提取含关键字和代码的句子
    :param body:主体
    :return:kw_and_code_descs:['sen:含关键字和代码的句子','kw:sen包含的关键字','codelist:sen包含的代码']
    '''
    kw_and_code_descs = []  # 存放含有关键词也含有代码的句子
    # 提取含关键字的body
    len_kw_sen = 0

    sentencesList = body.split('<p>')  # 以<p>划分句子
    for sentences in sentencesList:
        sentenceList=nltk.sent_tokenize(sentences)

        for sentence in sentenceList:
            code_sen_list = get_code_list(sentence)
            code_list = code_sen_list[0]
            sen = code_sen_list[1]
            kws = get_kw_list(sen)
            if len(kws)!=0:
                len_kw_sen +=1

            # if len(codes) != 0 and len(kws) != 0:
            #     soup = BeautifulSoup(sentence, 'html.parser')
            #     sen = ''
            #     for q in soup.find_all(text=True):
            #         sen = sen + q
            #     kw_and_code_descs.append([sen, kws, codes])

    return (kw_and_code_descs,len_kw_sen)

def get_kw_list(sentence):
    kwList = []
    for kw in KWs:
        matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", sentence, re.I)
        if matchobj is not None:
            kwList.append(kw)
    return kwList

def get_code_list(sentence):
    '''
    提取出sentence含有<code>标志的代码：例如<code>tf.py_func()</code>
    :param sentence:待处理字符串
    :return:code_sen_list:[code_list,sen] code_list:sentence含有的所有代码,sen:sentence去除code_list之后的句子
    '''
    code_list=[]
    code_sen_list=[]
    #提取出含有<code>的代码
    sen=''
    if sentence.find('<code>') != -1:
        for i in range(len(sentence.split('<code>'))):
            if i==0:
                sen=sen+sentence.split('<code>')[0]
            if sentence.split('<code>')[i].find('</code>') != -1:
                code_list.append(sentence.split('<code>')[i].split('</code>')[0])
                sen=sen+sentence.split('<code>')[i].split('</code>')[1]
    else:
        sen=sentence

    for i in range(len(code_list)):
        soup=BeautifulSoup(code_list[i],'html.parser')
        code_list[i]=''
        for c in soup.find_all(text=True):
            code_list[i]=code_list[i]+c

    soup = BeautifulSoup(sen, 'html.parser')
    sen = ''
    for q in soup.find_all(text=True):
        sen = sen + q

    pattern = re.compile(r'\S*http\S*|\S+\.com\S*|\S+\.htm\S*|\S+\.org\S*|\S+\.io\S*|\S+\.edu\S*|\S+\.shtml\S*|\S*/\w+/\w+/\w+\S*')
    linkList = pattern.findall(sen)

    for link in linkList:
        sen = sen.replace(link, '')

    pattern = re.compile(
        r'[a-zA-Z]\w*\(*\)*\[*\]*\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|\s\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|^\.[a-zA-Z]\w*\(*\)*\[*\]*[a-zA-Z0-9,=\.\(\)\[\]]*|[a-zA-Z]\w*\([a-zA-Z0-9,=\.\(\)\[\]]*\)|[a-zA-Z]\w*\[[a-zA-Z0-9,=\.\(\)\[\]]*\]')
    code_list2 = pattern.findall(sen)

    for code in code_list2:
        sen=sen.replace(code,'')

    for i in range(len(code_list2)):
        if code_list2[i][-1] == ',' or code_list2[i][-1] == '.':
            code_list2[i] = code_list2[i][:-1]
        if code_list2[i] == 'i.e' or code_list2[i] == 'e.g' or code_list2[i] == 'i.e.' or code_list2[i] == 'e.g.':
            continue
        else:
            code_list.append(code_list2[i])
    code_list=list(set(code_list))
    code_sen_list.append(code_list)
    code_sen_list.append(sen)
    return code_sen_list

def savecsv(descs, answer_id, question_id, csv_Path,apis):
    '''
    save desc data to csv file.
    :param descs: kw_and_code_descs:['sen:含关键字和代码的句子','kw:sen包含的关键字','codelist:sen包含的代码']
    :param question_id:
    :param csv_Path: 保存csv的路径
    '''
    with open(csv_Path, 'a+', encoding='gb18030',newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        for desc in descs:
            writer.writerow([answer_id,question_id,desc[0],desc[1],desc[2],apis])  # [question_id,desc,kw[],codelist]

def get_all_code(body):
    # codes = []
    #codes.extend(get_code_list(title)[0])
    codes = get_code_list(body)[0]
    #codes = get_all_code(body)[0]
    apis = []
    for code in codes:
        apis.extend(extractAPI.get_apis(code))
    apis = list(set(apis))  # 去重
    print(codes)
    return apis

if __name__ == "__main__":
    connectMySQL()