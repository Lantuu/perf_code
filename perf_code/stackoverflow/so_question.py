import csv
import math
from datetime import datetime

import pymysql as pymysql


def connect_mysql(host='localhost', username='root', password='123456', database='stackoverflow'):
    """
    连接数据库
    :param host:
    :param username:
    :param password:
    :param database:
    :return:
    """
    print('Open the database connection......')    # 打开数据库连接
    db = pymysql.connect(host, username, password, database, charset='utf8')    # 使用 cursor() 方法创建一个游标对象 cursor
    return db


def execute_select(cursor, select_sql):
    """
    执行Select操作，返回SELECT的结果(body)
    :param cursor:
    :param select_sql: 查询语句
    :return:
    """
    print('Execute sql SELECT......')
    cursor.execute(select_sql)
    columns = cursor.fetchall()
    return columns


def get_perf_question(question_columns, kws):
    """
    搜索含有关键词的问题
    :param question_columns: 待处理的问题
    :param kws: 关键词
    :return: 所有含关键词问题的question_id
    """
    perf_question = []
    for column in question_columns:
        question_id = column[0]
        body = column[1]
        title = column[2]
        tags = column[3]
        if is_kw_str(kws, body + title ) or is_perf_tag(tags):
            perf_question.append(question_id)
    return perf_question


def is_kw_str(kws, str):
    for kw in kws:
        if str.find(kw) != -1:
           return True
    return False


def is_perf_tag(tags):
    for tag in tags:
        if tag.lower() == 'performance':
            return True
    return False


def get_data(perf_question_ids, cursor):
    save_data = []  # [['question_id','up_vote_count','view_count','interval_seconds','format_time'
    for question_id in perf_question_ids:
        one_data = []
        select_question_sql = 'SELECT creation_date,up_vote_count,view_count FROM questions WHERE question_id=' + str(question_id)
        select_answer_sql = 'SELECT creation_date FROM answers WHERE question_id=' + str(question_id) + ' AND is_accepted=1'
        question_data = execute_select(cursor, select_question_sql)
        question_creation_date = question_data[0][0]
        answer_creation_date = execute_select(cursor, select_answer_sql)
        one_data.extend([question_id, question_data[0][1], question_data[0][2]])
        if len(answer_creation_date) != 0:
            answer_creation_date = answer_creation_date[0][0]
            secs = (answer_creation_date-question_creation_date).seconds
            time_interval = change_time(secs)
            one_data.append(secs)
            one_data.append(time_interval)
        else:
            one_data.append(-1)
            one_data.append(-1)
        print(one_data)
        save_data.append(one_data)
    return save_data


def change_time(all_time):
    day = 24 * 60 * 60
    hour = 60 * 60
    min = 60
    if all_time < 60:
        return "%d sec" % math.ceil(all_time)
    elif all_time > day:
        days = divmod(all_time, day)
        return "%d days,%s" % (int(days[0]), change_time(days[1]))
    elif all_time > hour:
        hours = divmod(all_time, hour)
        return '%d hours,%s' % (int(hours[0]), change_time(hours[1]))
    else:
        mins = divmod(all_time, min)
        return "%d mins,%d sec" % (int(mins[0]), math.ceil(mins[1]))


def save_csv(path, data):
    with open(path, 'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def save_to_mysql(cursor, data):
    insert_table_sql = "INSERT INTO 'perf_question'" \
                       "('question_id','up_vote_count','view_count','interval_seconds','format_time')"
    drop_table_sql = "DROP TABLE IF EXISTS 'perf_question'"
    create_table_sql = "CREATE TABLE 'perf_question' (" \
                       "'question_id' int(11) NOT NULL," \
                       "'up_vote_count' int(11) DEFAULT NULL, " \
                       "'view_count' int(11) DEFAULT NULL," \
                       "'interval_seconds' int(11) DEFAULT NULL,"\
                       "'format_time' varchar(150) DEFAULT NULL," \
                       "PRIMARY KEY ('question_id')" \
                       ");"
    for d in data:
        insert_table_sql = insert_table_sql + \
                           "values(" + str(d[0]) + str(d[1]) + str(d[2]) + str(d[3]) + str(d[4]) + "),"
    insert_table_sql[-1] = ";"
    cursor.execute(drop_table_sql)
    cursor.execute(create_table_sql)


def main():
    save_path = 'D:\\MyDocument\\performance\\stackoverflow\\perf_question\\perf_question.csv'
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive',
                 'scalab', 'efficien']
    db = connect_mysql()  # 打开数据库
    cursor = db.cursor()
    question_sql = "SELECT question_id,body,title,tags FROM questions"  # SQL 查询语句
    question_columns = execute_select(cursor, question_sql)
    perf_question_ids = get_perf_question(question_columns, kws)
    print(perf_question_ids)
    print(len(perf_question_ids))
    save_data = get_data(perf_question_ids, cursor)
    save_csv(save_path, save_data)
    db.close()  # 关闭数据库连接


if __name__ == "__main__":
    main()
    # print(change_time(123))
