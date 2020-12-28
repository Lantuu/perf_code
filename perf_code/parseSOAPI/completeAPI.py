import ast
import csv
import re

import pymysql


host = 'localhost'
username = 'root'
password = '123456'
database='so'

def connectMySQL():
    '''连接数据库'''
    print('Open the database connection......')    # 打开数据库连接
    db = pymysql.connect(host,username,password,database,charset='utf8')    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    codeLists = get_codeLists()  # [[question_id,codelist,apis],...,...]
    for codeList in codeLists:
        comment_id = codeList[0]
        codelist = codeList[1]
        question_id=executeSelectQuestionId(cursor,comment_id)
        # question_id = codeList[0]
        apis = codeList[2]
        tagList = executeSelect(cursor,question_id)[0][0].split(',')
        save_to_csv(completeApi(codelist,tagList,apis))
    db.close()  # 关闭数据库连接
    print('Close the database connection......')

def executeSelect(cursor,question_id):
    '''
      执行Select操作，返回SELECT的结果(tags)
    '''
    #print('Execute sql SELECT......')
    sql = "SELECT tags FROM questions where question_id = "+ question_id # SQL 查询语句
    try:
        cursor.execute(sql)
        tags = cursor.fetchall()
    except:
        print("Error: unable to fecth data")
    #print('Sql SELECT execution is complete')
    return tags

def executeSelectQuestionId(cursor,comment_id):
    '''
      执行Select操作，返回SELECT的结果(tags)
    '''
    #print('Execute sql SELECT......')
    sql = "SELECT post_id,post_type FROM comments where comment_id = "+ comment_id # SQL 查询语句
    try:
        cursor.execute(sql)
        comments = cursor.fetchall()
        if str(comments[0][1])=='question':
            return str(comments[0][0])
        elif str(comments[0][1])=='answer':
            try:
                cursor.execute("SELECT question_id FROM answers where answer_id = "+ str(comments[0][0]))
                qustion_id=cursor.fetchall()
                return str(qustion_id[0][0])
            except:
                print("Error:select!")
    except:
        print("Error: unable to fecth data")
    #print('Sql SELECT execution is complete')
    #return tags

def get_codeLists():
    f = open('G:\\Performance\\SO_Guid_Api\\stackoverflow\\SO_desc\\SO_1011\\stackoverflow_latest_comment.csv', 'r', encoding='gb18030')
    reader = csv.reader(f)
    codeLists = []  # [question_id , codeList],[commment_id,codelist]
    for row in reader:
        codeLists.append([row[0], ast.literal_eval(row[4]),ast.literal_eval(row[5])])
    f.close()
    return codeLists

def completeApi(codelist,taglist,apis):
    codes = []
    # 根据上下文的代码元素
    for code in codelist:
        for i in range(len(apis)):
            if code is not None and str(code).find('.') == -1 and str(apis[i]).endswith('.'+code):
                codes.append(apis[i])
                break
            elif code is not None and i==len(apis)-1:
                codes.append(code)

    fullName=[]
    for code in codes:
        if re.match(r'^numpy\.|^scipy\.|^pandas\.|^tensorflow\.|^sklearn\.|^gensim\.',str(code)) is not None:
            fullName.append(code)
        else:
            for tag in taglist:
                pattern=re.compile(r'numpy|scipy|pandas|tensorflow|sklearn|gensim')

                if pattern.match(tag) is not None and len(matchAPI(pattern.match(tag).group(),str(code)))!=0:
                    fullName.extend(matchAPI(pattern.match(tag).group(),str(code)))
                # elif re.search(r'.*\..*',code) is not None:
                #     fullName.append(code)
    fullName=list(set(fullName))
    print(fullName)
    return fullName


def matchAPI(packgeName,code):
    fullname=[]
    with open('G:\\Performance\\fullname\\'+packgeName+'.csv','r',encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            # if re.search(r'\.'+ code + '$',row[0]) is not None:
            numP = len(str(row[0]))-len(str(row[0]).replace('.', ''))
            if code.find('.') == -1 and numP>2:
                continue
            elif str(row[0]).endswith('.'+code):
                fullname.append(row[0])
    return fullname

def save_to_csv(fullName):
    with open('G:\\Performance\\stackoverflow\\completeAPI\\completeAPI_1011\\comment.csv', 'a', newline="",encoding='gb18030') as f:
        writer = csv.writer(f)
        writer.writerow([fullName])

if __name__ == "__main__":
    # f = open('G:\\Performance\\stackoverflow\\stackoverflow_latest_question.csv', 'r', encoding='gb18030')
    # reader = csv.reader(f)
    # codeLists = []  # question_id , codeList
    # for row in reader:
    #     codeLists.append([row[0],ast.literal_eval(row[4])])
    # f.close()
    #
    # for codeList in codeLists:
    #     question_id = codeList[0]
    #     codeList = codeList[1]

    connectMySQL()

