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
GIT_FILE_LOG = r'git -C {} log -p -u --no-merges{}> {}'
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
        if index < 298:
             continue

        travel_file_list = []  # 已经遍历过的file
        travel_ids = []  # 已经遍历过的id
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
        travel_file_list.append(commit_data.file_path)

        # 通过GIT_FILE_LOG命令获取一个文件的commit 日志
        commit = get_file_diff(absolute_path, version=version[commit_data.project_name], repo_path=repo_path)

        # 通过GIT_LINE_LOG命令获取一个文件中的一行所有的commit_id
        line_ids = get_line_id(repo_path, line_start, line_end, row['filepath'])

        # 通过GIT_LINE_LOG命令获取一个文件中的一行所有的commit日志
        line_commit = get_line_diff(repo_path, line_start, line_end, absolute_path, version[commit_data.project_name])

        tag_line_id = False  # 标记是否已经遍历过一次所有的line id，防止死循环
        len_save_data = len(save_data)  # 记录一行还没开始处理之前，save_data的大小
        index = 0
        commit_id = ''
        while index < len(commit):
            # print(commit['id'])
            temp_index = index  # 保存过滤id之前的index

            # 过滤id，取出添加/修改的desc的commit_id,evol_type,delete_sent
            evol_type, delete_sent, index = filter_id(commit,  commit_data.desc, absolute_path,  commit_data.sig, index, line_ids)

            commit_id = commit.loc[index]['id']
            travel_ids.extend(commit['id'][temp_index:index+1])  # 加入已经遍历过的id

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
                    commit_data.commit_id = ''
                    commit_data.evol_type = ''
                    commit_data.desc = delete_sent
                    save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                    commit_data.print_data()
                    break

            elif evol_type == 'add':
                commit_data.commit_id = commit_id

                # 检查文件是否重命名，没有重命名则退出循环
                new_file = get_new_file(commit_id, repo_path, absolute_path)
                if new_file != '':
                    # 文件重命名
                    commit_data.file_path = new_file

                    # 检查该文件是否已经遍历过, 遍历过则退出，防止死循环
                    if new_file in travel_file_list:
                        commit_data.evol_type = 'file renamed infinite loop'
                        index = index + 1
                        save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                        commit_data.print_data()
                        continue

                    # 文件重命名，更改文件路径, 保存数据
                    absolute_path = repo_path + '\\' + new_file.replace('/', '\\')
                    commit_data.evol_type = 'file renamed'
                    travel_file_list.append(new_file)
                    save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                    commit_data.print_data()

                    # 获取新文件的commit日志
                    commit = get_file_diff(absolute_path, version[commit_data.project_name], repo_path)

                    # 新文件的日志为空则，使用通过：GIT_LINE_LOG命令获取指定行的commit 日志
                    if commit is None and not tag_line_id:

                        # 过滤已遍历过的commit_id
                        id_list = [commit_id]
                        id_list.extend([id for id in list(line_commit['id']) if id not in travel_ids])
                        commit = line_commit[line_commit['id'].isin(id_list)]

                        # 重置commit索引
                        commit.reset_index(drop=True, inplace=True)
                        tag_line_id = True

                    index = 0
                    continue

                else:
                    commit_data.evol_type = evol_type
                    save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                    commit_data.print_data()
                    break

            # 异常情况 使用 line log再次遍历
            elif not tag_line_id:

                if len(save_data) - len_save_data > 0 and commit_data.evol_type not in ['', 'add']:
                    # ids = list(save_data["commit_id"][(save_data['id'] == commit_data.id) & (save_data['type']
                    # == 'file renamed')])
                    travel_ids = travel_ids[:travel_ids.index(save_data.loc[len(save_data)-1]['commit_id'])]

                id_list = [id for id in list(line_commit['id']) if id not in travel_ids]
                commit = line_commit[line_commit['id'].isin(id_list)]
                commit.reset_index(drop=True, inplace=True)
                tag_line_id = True
                index = 0
                continue

            # 保存最后一个记录
            else:
                commit_data.commit_id = commit_id
                commit_data.evol_type = 'add'
                save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
                commit_data.print_data()
            index = index + 1

        if len(save_data) == len_save_data:
            commit_data.commit_id = commit_id
            commit_data.evol_type = 'add'
            save_data = save_data.append(commit_data.get_dic(), ignore_index=True)
            commit_data.print_data()

    return save_data


def get_file_diff(file_path, version, repo_path):
    """
    得到line在一特定版本之前的所有commit_id log 存放在临时文件temp_log.txt 中
    :param repo: 库名
    :param line: 行号
    :param path: 存放commit_id的地址
    :param logfile:
    :param version: 版本号
    """

    GIT_LOG = r'git -C {} log -p -u {}> {}'
    GIT_Checkout = r'git -C {} checkout {}'
    temp_path = os.path.abspath(os.path.join(os.getcwd(), "..\\TempFile\\tem_log.txt"))
    temp_file = open(temp_path, 'w', encoding='utf-8', errors='ignore')
    temp_file.close()
    git_log_command1 = GIT_Checkout.format(repo_path, version)
    git_log_command = GIT_LOG.format(repo_path, file_path, temp_path)
    os.system(git_log_command1)
    os.system(git_log_command)
    lines = read_txt(temp_path)
    if len(lines) == 0:
        return None
    commit = SplitLog.split_log(lines)
    return commit


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


def get_new_file(id, repo_path, file_path):
    old_file_name = file_path.replace(repo_path, '')[1:].replace('\\', '/')
    temp_path = os.path.abspath(os.path.join(os.getcwd(), "..\\TempFile\\name_status.txt"))
    comm_name_status = GIT_NAME_STATUS.format(repo_path, id, temp_path)
    os.system(comm_name_status)
    lines = read_txt(temp_path)
    new_file_name = ''

    for line in lines:

        if re.search(old_file_name + '$', line.strip()):
            line = line.strip()[::-1].replace(old_file_name[::-1], '', 1)[::-1].strip()  # 从右往左替换第一次出现的字符串
            # line = line.strip().replace(old_file_name, '').strip()
            if re.search(r'\S+$', line):
                new_file_name = re.search(r'\S+$', line).group()
                break

    if not new_file_name.endswith(old_file_name.split('/')[-1].split('.')[-1]):
        new_file_name = ''

    return new_file_name


def filter_id(commit, desc, file_path, sig, commit_id_start, line_ids):
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
    evol_data_dic1 = {}  # 所有增加了desc的commit信息 ： {commit_id_start:CommitType}
    evol_data_dic2 = {}  # 根据api名筛选
    evol_data_dic3 = {}  # 根据line_id 筛选

    # 遍历所有的id，把添加了desc的id都加入evol_data_dic1
    for index in range(commit_id_start, len(commit)):
        commit_id = commit.loc[index]['id']
        # if commit_id != '1d5155c0c786ab29e26df8409757ee4b6bc102e9':
        #     continue
        diff = commit.loc[index]['diff']
        evol_data = EvolutionData()
        evol_data.pase_evol(sig, desc, file_path, diff)
        if evol_data.evol_type != "":
            evol_data_dic1[index] = evol_data

    # 没有找到，返回
    if len(evol_data_dic1) == 0:
        return '', '', len(commit) - 1

    # 只找到一个，返回第一个
    elif len(evol_data_dic1) == 1:
        key = list(evol_data_dic1.keys())[0]
        return evol_data_dic1[key].evol_type, evol_data_dic1[key].delete_sent, key

    # 有两个id及以上都增加了desc，则筛选出一个  ###以下都是找到两个以上id的情况

    # 根据line_ids，存放在evol_data_dic2
    for key in evol_data_dic1.keys():
        for line_id in line_ids:
            if commit.loc[key]['id'] == line_id:
                evol_data_dic2[key] = evol_data_dic1[key]
                break

    # 根据line_ids只找到一个id，直接返回第一个
    if len(evol_data_dic2) == 1:
        key = list(evol_data_dic2.keys())[0]
        return evol_data_dic2[key].evol_type, evol_data_dic2[key].delete_sent, key

    # 根据line_ids找到两个以上的id，从evol_data_dic2中，根据sig重新选择, 存放在evol_data_dic3
    elif len(evol_data_dic2) > 1:
        snippets = [value.evol_snippet for value in evol_data_dic2.values()]
        snippets_index = EvolutionData.get_api_snippet_index(snippets, sig)
        for index in snippets_index:
            evol_data_dic_key = list(evol_data_dic2.keys())[index]
            evol_data_dic3[evol_data_dic_key] = evol_data_dic2[evol_data_dic_key]

    # 根据line_ids一个都没有找到，从evol_data_dic1中，根据sig重新选择, 存放在evol_data_dic3
    else:
        snippets = [value.evol_snippet for value in evol_data_dic1.values()]
        snippets_index = EvolutionData.get_api_snippet_index(snippets, sig)
        for index in snippets_index:
            evol_data_dic_key = list(evol_data_dic1.keys())[index]
            evol_data_dic3[evol_data_dic_key] = evol_data_dic1[evol_data_dic_key]

    # 按顺序从evol_data_dic3，evol_data_dic2，evol_data_dic1中选择第一个返回
    if len(evol_data_dic3) > 0:
        key = list(evol_data_dic3.keys())[0]
        return evol_data_dic3[key].evol_type, evol_data_dic3[key].delete_sent, key
    elif len(evol_data_dic2) > 0:
        key = list(evol_data_dic2.keys())[0]
        return evol_data_dic2[key].evol_type, evol_data_dic2[key].delete_sent, key
    else:
        key = list(evol_data_dic1.keys())[0]
        return evol_data_dic1[key].evol_type, evol_data_dic1[key].delete_sent, key


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
    save_path = 'D:\\MyDocument\\performance\\git_log\\EvolutionLog\\20.05.28\\userguide_evol.csv'
    caveat = reade_csv(path)
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    pf = main(caveat, clone_path, kws)
    pf.to_csv(save_path, encoding='utf_8_sig')
    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds)
