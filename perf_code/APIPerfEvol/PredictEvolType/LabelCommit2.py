import ast
import datetime
import re

import pandas as pd
import os

from APIPerfEvol.PredictEvolType.EvolutionData import EvolutionData
from APIPerfEvol.PredictEvolType.SplitLog import SplitLog
from APIPerfEvol.PredictEvolType.CommitData import CommitData

version = {'pandas': 'v0.24.2', 'numpy': 'v1.16.4', 'scipy': 'v1.2.1', 'sklearn': '0.21.2', 'tensorflow': 'r1.13', 'gensim': '3.7.3', 'docs': 'r1.13'}
GIT_LINE_LOG = r'git -C {} log -p -u -L {},{}:{}> {}'
GIT_FILE_LOG = r'git -C {} log -p -u {}> {}'
GIT_ID_LOG = r'git -C {} log -p -u -1 {} {}> {}'
GIT_FIlE_CHANGE_LOG = r'git -C {} log --stat {} {}> {}'
GIT_Checkout = r'git -C {} checkout {}'
GIT_NAME_STATUS = r'git -C {} log --name-status -1 {} > {}'


def main(caveat, root_path, kws):
    """
    :param caveat: DataFrame, 所有待处理的数据
    :param root_path: str, repo path
    :param kws: list, performance key words
    :return: save_data, DataFrame, 处理好的数据
             columns=[id,file_path,desc,project,line_no,sig,commit_id,evol_type]
             id: 一个id对应一行待处理的数据
             file_path: 文件路径
             desc: performance desc
             project: 库名
             line_no: kw所在的行号
             sig: list, desc描述的api
             evol_type: add or alter

    """

    save_data = pd.DataFrame()  # 存放处理好的数据
    commit_data = CommitData()  # 一行数据对应一个对象

    # 迭代每一行
    for index, row in caveat.iterrows():
        # if index < 405:
        #      continue

        line_start = row['line_start']  # 句子在文档的开始行
        line_end = row['line_end']  # 句子在文档的结束行

        # 取出数据，c初始化，封装对象
        commit_data.project_name = row['project']
        commit_data.line_no = row['lineno']
        commit_data.sig = ast.literal_eval(row['sig'])
        commit_data.id = index
        commit_data.file_path = row['filepath']
        commit_data.desc = row['format_desc'].strip()
        commit_data.commit_id = ''
        commit_data.evol_type = ''

        if commit_data.desc == 'no':
            save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
            commit_data.print_data()
            continue

        repo_path = root_path + '\\' + commit_data.project_name  # 库路径
        absolute_path = repo_path + '\\' + commit_data.file_path.replace('/', '\\')  # 文件绝对路径

        # 通过GIT_LINE_LOG命令获取一个文件中的一行所有的commit_id
        line_ids = get_line_id(repo_path, line_start, line_end, row['filepath'])

        # 通过GIT_LINE_LOG命令获取一个文件中的一行所有的commit日志
        line_commit = get_line_diff(repo_path, line_start, line_end, absolute_path, version[commit_data.project_name])

        len_save_data = len(save_data)  # 记录一行还没开始处理之前，save_data的大小
        index = 0
        while index < len(line_commit):
            # print(commit['id'])
            # 过滤id，取出添加/修改的desc的commit_id,evol_type,delete_sent
            evol_type, delete_sent, index = filter_id(line_commit,  commit_data.desc, absolute_path,  commit_data.sig, index)
            commit_id = line_commit.loc[index]['id']
            if evol_type == 'alter':
                # 保存数据
                commit_data.commit_id = commit_id
                commit_data.evol_type = evol_type
                save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                commit_data.print_data()  # 打印数据

                # 检查delete_sent 是否包含performance kw， 是则继续追踪
                if is_contain_kw(kws, commit_data.desc, delete_sent):
                    commit_data.desc = delete_sent

                # 否则结束循环，保存delete_sent
                else:
                    commit_data.commit_id = ""
                    commit_data.evol_type = ""
                    commit_data.desc = delete_sent
                    save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                    commit_data.print_data()
                    break

            elif evol_type == 'add':
                commit_data.commit_id = commit_id
                commit_data.evol_type = evol_type
                save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                commit_data.print_data()
                break

            # 保存最后一个记录
            else:
                commit_data.commit_id = commit_id
                commit_data.evol_type = 'add'
                save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                commit_data.print_data()
            index = index + 1

        if len(save_data) == len_save_data:
            commit_data.commit_id = ""
            commit_data.evol_type = ""
            save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
            commit_data.print_data()

    return save_data


def get_line_diff(repo_path, line_start, line_end, file_path, version):
    """
    desc根据行号 -L 命令得到commit diff
    :param repo_path:
    :param line_start: desc开始行号
    :param line_end: desc结束行号
    :param file_path: 该desc所在文件的文件路径
    :return:
    """
    temp_path = os.path.abspath(os.path.join(os.getcwd(), "..\\TempFile\\tem_log.txt"))
    temp_file = open(temp_path, 'w', encoding='utf-8', errors='ignore')
    temp_file.close()
    git_log_command1 = GIT_Checkout.format(repo_path, version)
    git_line_log = GIT_LINE_LOG.format(repo_path, str(int(line_start)), str(int(line_end)), file_path, temp_path)
    os.system(git_log_command1)
    os.system(git_line_log)
    lines = read_txt(temp_path)
    commit = SplitLog.split_log(lines)
    return commit


def get_line_id(repo_path, line_start, line_end, file_path):
    """
    desc根据行号 -L 命令得到commit diff
    :param repo_path:
    :param line_start: desc开始行号
    :param line_end: desc结束行号
    :param file_path: 该desc所在文件的文件路径
    :return:
    """
    temp_path = os.path.abspath(os.path.join(os.getcwd(), "..\\TempFile\\tem_log2.txt"))
    git_line_log = GIT_LINE_LOG.format(repo_path, str(int(line_start)), str(int(line_end)), file_path, temp_path)

    git_checkout =GIT_Checkout.format(repo_path, version[repo_path.split('\\')[-1]])
    line_ids = get_commit_id(git_checkout, git_line_log, temp_path)

    return line_ids


def get_commit_id(comm_checkout, comm_log, temp_path):
    """

    :param comm_checkout: 定位到某个具体的版本
    :param comm_log: git log 命令
    :param temp_path: 临时数据存放的路径
    :return: commit_id
    """
    os.system(comm_checkout)
    os.system(comm_log)
    commit_id = []
    lines = read_txt(temp_path)
    for log in lines:
        if re.match(r'commit', log):  # lines[i].startswith('commit'):
            commit_id.append(log.split(' ')[-1].strip())
    return commit_id


def filter_id(commit, desc, file_path, sig, commit_id_start):
    """
    找到所有增加了desc的commit
    :param commit: 所有id的commit内容
    :param desc:  performance sentence
    :param file_path: performance sentence 所在的文件
    :param sigs: performance sentence 描述的APIs
    :param commit_id_start: 接着上文，从这个index开始遍历commit
    :param lines_ids: performance sentence所在行的diff ids
    :return: evol_type： 改动类型add or alter, delete_sent 改动之前的句子, index 该commit的索引
    """

    evol_type = ""
    delete_sent = ""
    id_index = commit_id_start

    # 遍历所有的id，把添加了desc的id都加入evol_data_dic1
    for index in range(commit_id_start, len(commit)):
        commit_id = commit.loc[index]['id']
        # if commit_id != '23418e4317b9e2c4a5148368daec873592a0de9e':
        #     continue
        id_index = index
        diff = commit.loc[index]['diff']
        evol_data = EvolutionData()
        evol_data.pase_evol(sig, desc, file_path, diff)
        if evol_data.evol_type != "":
            evol_type = evol_data.evol_type
            delete_sent = evol_data.delete_sent
            break
    return evol_type, delete_sent, id_index


def is_contain_kw(kws, desc, delete_sent):
    """
    检查delete_sent是否包含kw
    :param kws: performance words
    :param desc: performance sentence
    :param delete_sent:
    :return:
    """
    keyword = []

    # desc中包含的关键词
    for kw in kws:
        if desc.lower().find(kw) != -1:
            keyword.append(kw)

    # 判断delete_sent是否含有关键词
    for kw in keyword:
        if str(delete_sent).lower().find(kw) != -1:
            return True

    return False


def read_txt(file_path):
    """
    读txt文件
    :param file_path: str, txt文件路径
    :return: list, 返回txt所有行
    """
    f = open(file_path, 'r', encoding='utf-8', errors='ignore')
    # data = f.read()
    # print(chardet.detect(data))
    lines = f.readlines()
    f.close()
    return lines


def reade_csv(file_path):
    """
    读取csv文件
    :param file_path: str
    :return:
    """
    df = pd.read_csv(file_path, encoding='utf-8', dtype={'format_desc': str, 'line_no': int, 'line_start': int, 'line_end': int})  # ISO-8859-1
    return df


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    path = 'D:\\MyDocument\\performance\\git_log\\commit\\format_commit\\userguide_commits.csv'
    clone_path = 'D:\\MyDocument\\performance\\clone'
    save_path = 'D:\\MyDocument\\performance\\git_log\\EvolutionLog\\20.05.26\\userguide_evol.csv'
    caveat = reade_csv(path)
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    pf = main(caveat, clone_path, kws)
    pf.to_csv(save_path, encoding='utf_8_sig')
    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds)
