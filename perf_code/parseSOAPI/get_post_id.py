import csv

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
    f = open('G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_SO_result.csv', 'r', encoding='gb18030')
    reader = csv.reader(f)
    post_id=[]
    for row in reader:
        type = row[11]
        comment_id = row[12]
        if type == 'comment':
            post_id.append(executeSelect(cursor,comment_id)[0][0])
        else:
            post_id.append('0')

    savecsv(post_id,'G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_post_id.csv')
    f.close()
    db.close()  # 关闭数据库连接
    print('Close the database connection......')

def executeSelect(cursor,comment_id):
    '''
      执行Select操作，返回SELECT的结果(body)
    '''
    print('Execute sql SELECT......')
    sql = "SELECT post_id FROM comments where comment_id="+comment_id  # SQL 查询语句
    try:
        cursor.execute(sql)
        questions = cursor.fetchall()
    except:
        print("Error: unable to fecth data")
    print('Sql SELECT execution is complete')
    return questions

def savecsv(post_id,csv_Path):
    '''
    save desc data to csv file.
    :param descs: kw_and_code_descs:['sen:含关键字和代码的句子','kw:sen包含的关键字','codelist:sen包含的代码']
    :param question_id:
    :param csv_Path: 保存csv的路径
    '''
    with open(csv_Path, 'a+', encoding='gb18030',newline="") as f:
        writer = csv.writer(f)
        for id in post_id:
            writer.writerow([id])

connectMySQL()
