import os
import re

import nltk
import pandas as pd

version = {'pandas': 'v0.24.2', 'numpy': 'v1.16.4', 'scipy': 'v1.2.1', 'scikit-learn': '0.21.2', 'tensorflow': 'r1.13', 'gensim': '3.7.3', 'docs': 'r1.13'}


def exec_git(line_start, line_end, file_path, version, repo_path):
    """
    得到line在一特定版本之前的所有commit_id log 存放在临时文件temp_log.txt 中
    :param repo: 库名
    :param line: 行号
    :param path: 存放commit_id的地址
    :param logfile:
    :param version: 版本号
    """
    GIT_LINE_LOG = r'git -C {} log -p -u -L {},{}:{}> {}'
    GIT_Checkout = r'git -C {} checkout {}'
    temp_path = os.getcwd() + '\\tem_log' + '.txt'
    temp_file = open(temp_path, 'w')
    temp_file.close()
    git_log_command1 = GIT_Checkout.format(repo_path, version)
    git_log_command = GIT_LINE_LOG.format(repo_path, line_start, line_end, file_path, temp_path)
    os.system(git_log_command1)
    os.system(git_log_command)


def get_line_diff(repo_path, line_start, line_end, file_path):

    GIT_LINE_LOG = r'git -C {} log -p -u -L {},{}:{}> {}'
    GIT_FILE_LOG = r'git -C {} log -p -u {}> {}'
    GIT_ID_LOG = r'git -C {} log -p -u -1 {} {}> {}'

    def exec_comm(comm, temp_path):
        os.system(comm)
        commit_id = []
        with open(temp_path, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
        for log in lines:
            if re.match(r'commit', log):  # lines[i].startswith('commit'):
                commit_id.append(log.split(' ')[-1].strip())
        return commit_id

    def levenshtein(first, second):
        ''' 编辑距离算法（LevD）
            Args: 两个字符串
            returns: 两个字符串的编辑距离 int
        '''
        if len(first) > len(second):
            first, second = second, first
        if len(first) == 0:
            return len(second)
        if len(second) == 0:
            return len(first)
        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [list(range(second_length)) for x in range(first_length)]

        for i in range(1, first_length):
            for j in range(1, second_length):
                deletion = distance_matrix[i - 1][j] + 1
                insertion = distance_matrix[i][j - 1] + 1
                substitution = distance_matrix[i - 1][j - 1]
                if first[i - 1] != second[j - 1]:
                    substitution += 1
                distance_matrix[i][j] = min(insertion, deletion, substitution)
                # print distance_matrix
        return distance_matrix[first_length - 1][second_length - 1]

    def get_new_filename(ids, repo_path, file_path):
        new_files = []
        new_file = ''
        new_path = repo_path
        temp_path = os.getcwd() + '\\' + 'newfile.txt'
        files_list = []
        for id in ids:
            comm = 'git -C ' + repo_path + ' log -1 --name-only ' + id + ' > ' + temp_path
            os.system(comm)
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            for i in range(len(lines) - 1, -1, -1):
                if len(lines[i].strip()) == 0:
                    break
                files_list.append(lines[i].strip())

        files_set = set(files_list)
        for file in files_set:
            if files_list.count(file) == len(ids):
                new_files.append(file)

        if len(new_files) == 1:
            new_file = new_files[0]
        elif len(new_files) == 0:
            return new_file

        else:
            ls = []
            for file in new_files:
                new_file_name = file.split('/')[-1]
                old_file_name = file_path.split('/')[-1]
                ls.append(levenshtein(new_file_name, old_file_name))
            new_file = new_files[ls.index(min(ls))]

        for p in new_file.split('/'):
            new_path = new_path + '\\' + p
        return new_path

    line_diff = pd.DataFrame()
    git_line_log = GIT_LINE_LOG.format(repo_path, line_start, line_end, file_path, os.getcwd() + '\\tem_log2' + '.txt')
    git_file_log = GIT_FILE_LOG.format(repo_path, file_path, os.getcwd() + '\\tem_log2' + '.txt')
    line_ids = exec_comm(git_line_log, os.getcwd() + '\\tem_log2' + '.txt')
    file_ids = exec_comm(git_file_log, os.getcwd() + '\\tem_log2' + '.txt')
    deficiency_id = [id for id in line_ids if id not in file_ids]
    new_path = get_new_filename(deficiency_id, repo_path, file_path)
    for id in deficiency_id:
        comm = GIT_ID_LOG.format(repo_path, id, new_path, os.getcwd() + '\\tem_log2' + '.txt')
        os.system(comm)
        with open(os.getcwd() + '\\tem_log2' + '.txt', 'r', encoding='UTF-8') as f:
            lines = f.readlines()
        df = split_log(lines)
        line_diff = line_diff.append(df, ignore_index=True)
    return line_diff


def get_commit_id(caveat, root_path, kws):

    save_data = pd.DataFrame()
    for row in range(len(caveat)):
        # if row != 320:
        #     continue
        commit_data = {'line_no': '', 'path': '', 'project': '', 'desc': '', 'id': '', 'type': ''}
        line_no = caveat['lineno'][row]
        sub_path = caveat['path'][row].split('/')
        repo = caveat['project'][row]
        desc = caveat['format_desc'][row]
        line_start = caveat['line_start'][row]
        line_end = caveat['line_end'][row]
        if repo =='sklearn':
            repo = 'scikit-learn'
        repo_path = root_path + '\\' + repo
        file_path = repo_path

        v = version[repo]
        for p in sub_path:
            file_path = file_path + '\\' + p
        exec_git(line_start, line_end, file_path, version=v, repo_path=repo_path)
        log = read_txt(os.getcwd() + '\\tem_log' + '.txt')
        commit = split_log(log)
        # line_diff = get_line_diff(repo_path, line_no, caveat['path'][row])
        len_save_data = len(save_data)
        # tag_extral = False
        index = 0
        while index < len(commit):
            commit_id = commit.loc[index]['id']
            diff = commit.loc[index]['diff']
            commit_type, delete_sent = get_commit_type(diff, desc, file_path)
            if len(commit_type) != 0:
                commit_data['id'] = commit_id
                commit_data['type'] = commit_type
                commit_data['desc'] = desc
                commit_data['path'] = caveat['path'][row]
                commit_data['project'] = repo
                commit_data['line_no'] = line_no
                print(commit_data)
                save_data = save_data.append(commit_data, ignore_index=True)
                if commit_type == 'alter' and is_contain_kw(kws, desc, delete_sent):
                    desc = delete_sent
                    # if tag_extral and save_data.loc[len(save_data) - 2]['type'] == 'add':
                    #     save_data.loc[len(save_data) - 2, 'type'] = 'alter file renamed'
                    #
                    # # save_data = save_data.append(commit_data, ignore_index=True)
                    # # print(commit_data)
                # elif len(line_diff) != 0 and not tag_extral and commit_type == 'add':
                #     commit = line_diff
                #     index = -1
                #     tag_extral = True
                #     # commit_data['type'] = 'alter file renamed'
                #     # save_data = save_data.append(commit_data, ignore_index=True)
                #     # print(commit_data)
                #     # if delete_sent is not None:
                #     #     desc = delete_sent
                else:
                    # if tag_extral and save_data.loc[len(save_data)-2]['type'] == 'add':
                    #     save_data.loc[len(save_data)-2, 'type'] = 'alter file renamed'
                    # save_data = save_data.append(commit_data, ignore_index=True)
                    # print(commit_data)
                    break

            index = index + 1

        if len(save_data) == len_save_data:
            commit_data['id'] = ''
            commit_data['type'] = ''
            commit_data['desc'] = desc
            commit_data['path'] = caveat['path'][row]
            commit_data['project'] = repo
            commit_data['line_no'] = line_no
            save_data = save_data.append(commit_data, ignore_index=True)

    return save_data


def is_contain_kw(kws, desc, delete_sent):
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


def get_commit_type(diff, desc, path):
    commit_type = ''
    delete_sent = ''

    diff_snippets = split_diff(diff)
    for diff_snippet in diff_snippets:
        diff_dic = classify_sens(diff_snippet)
        add = diff_dic['add']
        delete = diff_dic['delete']
        add_space = diff_dic['add_space']
        delete_space = diff_dic['delete_space']

        # ' +/- '行中，含有的desc公共子序列
        add_common_sent = get_common_sent(add, desc, add_space)
        delete_common_sent = get_common_sent(delete, desc, delete_space)

        if add_common_sent == delete_common_sent:
            continue

        if len(add_common_sent) != 0:
            # 求删除的句子和其索引位置
            delete_sent, delete_line_index = find_delete_sent(desc, delete, delete_space)
            if not path.endswith('.ipynb') and delete_line_index is not None:
                lines = []
                for line in delete_space:
                    lines.append(line[1:])
                delete_sent = get_format_desc(delete_sent, delete_line_index, lines)

            # # delete sent的条件
            # if delete_sent is not None and longest_common_sequence(delete_sent, desc)/len(desc) < 0.5:
            #     delete_sent = None

            # 判断commit type, 并返回
            # if delete_sent is None:
            if desc == add_common_sent and delete_sent is None:

                commit_type = 'add'
                return commit_type, delete_sent
            else:
                commit_type = 'alter'
                return commit_type, delete_sent
        else:
            return commit_type, delete_sent

    return commit_type, delete_sent


def find_delete_sent(desc, delete, delete_space):
    """
    在一个字符串列表中，求其与desc的最长公共子序列
    :param desc:
    :param delete_blank: 字符串列表
    :return: delete_string： 与desc具有最长公共子序列的字符串， 最长公共子序列的大小
    """

    delete_string = ''  # 最长公共子序列
    max_res = 0
    delete_line_index = None   # 最长公共子序列在delete中行的索引
    delete_space_line_index = None  # 最长公共子序列在delete_space中行的索引
    for index in range(len(delete)):
        res = []
        if len(delete[index]) > 10000:
            continue
        delete_sents = nltk.sent_tokenize(delete[index][1:])

        # 计算每个句子与desc的最长公共子序列
        for sent in delete_sents:
            res.append(len(find_lcsubstr(sent, desc)))

        # 求最长公共子序列最大的句子及最长公共子序列大小
        max_res_line = 0
        max_res_index = -1
        for i in range(len(res)):
            if res[i] > max_res_line:
                max_res_line = res[i]
                max_res_index = i

        if max_res_line > max_res:
            max_res = max_res_line
            delete_string = delete_sents[max_res_index]
            delete_line_index = index

    # 在delete_space中的索引
    for index in range(len(delete_space)):
        if delete_line_index is None:
            break
        if delete_space[index] == delete[delete_line_index]:
            delete_space_line_index = index
            break

    # 最长公共子序列返回的条件
    if len(delete_string) > 0:  # and max_res/len(delete_string) >= 0.5:
        return delete_string, delete_space_line_index
    else:
        return None, None


def get_common_sent(alter_string, desc, blank_string):

    # 去行前面的"+/-"
    blank_lines = []
    for line in blank_string:
        blank_lines.append(line[1:])

    contained_sen = ""
    for alter_index in range(len(alter_string)):
        line = alter_string[alter_index][1:]
        # print(line)
        if line.strip().startswith('\"image/png\"'):
            continue
        if len(line) > 10000:
            continue

        sens = nltk.sent_tokenize(line)
        for sen in sens:
            if re.search(r'[a-zA-Z]', sen.replace('\\n', '')) is None:
                continue
            # if re.search(str(sen), str(desc)):
            if str(desc).find(sen) != -1:

                for blank_index in range(len(blank_string)):
                    if blank_string[blank_index] == alter_string[alter_index]:
                        complete_sen = get_format_desc(sen, blank_index, blank_lines)
                        if complete_sen.find(desc) != -1:
                            contained_sen = contained_sen + ' ' + sen
    return contained_sen[1:]


def classify_sens(diff):
    """
    split diff: lines：改动的行号; add: 添加的行; delete： 删除的行; add_space: 添加的行和未改动过的行; delete_space: 删除的行和未改动过的行
    :param diff: 字符串列表
    :return: 字典
    """

    diff_dic = {'lines': '', 'add': '', 'delete': '', 'add_space': '', 'delete_space': ''}
    if len(diff) == 0:
        return diff_dic
    lines = diff[0]   # 存放这种形式的内容"@@ -738,20 +738,19 @@"
    add = []          # 存放以"+"开头的行
    add_space = []    # 存放以"+"开头的行，和以空格开头的行
    delete = []          # 存放以"-"开头的行
    delete_space = []    # 存放以"-"开头的行，和以空格开头的行

    for i in range(len(diff)):

        if i == 0:
            continue

        elif re.match('\+', diff[i]):
            add.append(diff[i])
            add_space.append(diff[i])

        elif re.match('-', diff[i]):
            delete.append(diff[i])
            delete_space.append(diff[i])

        else:
            add_space.append(diff[i])
            delete_space.append(diff[i])

    diff_dic['lines'] = lines
    diff_dic['add'] = add
    diff_dic['delete'] = delete
    diff_dic['add_space'] = add_space
    diff_dic['delete_space'] = delete_space

    return diff_dic


def read_txt(file_path):
    """
    读txt文件
    :param file_path: str, txt文件路径
    :return: list, 返回txt所有行
    """
    file = open(file_path, 'r', encoding='UTF-8')
    list = file.readlines()
    file.close()
    return list


def split_log(git_log):
    """
    分割一个commit命令返回的日志
    :param git_log: 待分割的日志
    :return: pd.dataframe 3列['id', 'diff', 'other']   id: commitID; diff: difference;
    """

    diff = list()
    other = list()
    commit = {'id': '', 'diff': '', 'other': ''}
    df_log = pd.DataFrame()
    diff_tag = False
    for line in git_log:
        if re.match(r'@@ ', line):
            diff_tag = True
        if re.match(r'commit', line):  # lines[i].startswith('commit'):

            if len(diff) != 0 and len(other) != 0:
                diff_tag = False
                commit['diff'] = diff
                commit['other'] = other
                df_log = df_log.append(commit, ignore_index=True)

            commit['id'] = (line.split(' ')[-1].strip())
            diff = list()
            other = list()
        elif not diff_tag:
            other.append(line)

        else:
            diff.append(line)


    commit['other'] = other
    commit['diff'] = diff
    df_log = df_log.append(commit, ignore_index=True)
    return df_log


def split_diff(diff):
    """
    以@@ -70,7 +70,7 @@ ... 形式分割diff
    :param diff: list, 改动的日志
    :return: list[list[],] 双重列表，
    """
    diff_list = []
    temp_diff = list()
    for line in diff:
        if str(line).startswith("@@ "):
            if len(temp_diff) != 0:
                diff_list.append(temp_diff)
                temp_diff = list()
            temp_diff.append(line)
        else:
            temp_diff.append(line)
    diff_list.append(temp_diff)
    return diff_list


def reade_csv(file_path):
    """
    读取csv文件
    :param file_path: str
    :return:
    """
    df = pd.read_csv(file_path, encoding='utf_8_sig')
    return df


def get_format_desc(line_desc, line_index, lines):
    """
    根据line_desc的值，在lines中找到它的上下文，使其变成一个完整的句子
    :param line_desc: 字符串
    :param line_index: 整型
    :param lines: 字符串列表
    :return: 字符串 含有line_desc上下文的完整句子
    """
    format_desc = line_desc
    line = lines[line_index]

    sens = nltk.sent_tokenize(line)
    sent_count = len(sens)  # line中含有句子的数量
    order_line_desc = -1   # line_desc 在line子句中的定位

    for sen in sens:
        order_line_desc = order_line_desc + 1
        if sen == line_desc:
            break

    # line_desc 在line的头部， line中含有大于1句子数量，则只需要添加line_desc的上文
    if order_line_desc == 0 and sent_count > 1:
        fw = forward(line_index, lines, line_desc)
        if len(fw) > 0:
            format_desc = fw + format_desc
            format_desc = nltk.sent_tokenize(format_desc)[-1]

    # line_desc 在line的头部， line中只有1个句子，则需要添加line_desc的上文和下文
    elif order_line_desc == 0 and sent_count == 1:
        fw = forward(line_index, lines, line_desc)
        bk = back(line_index, lines, line_desc)
        if len(fw) > 0:
            format_desc = fw + format_desc
            format_desc = nltk.sent_tokenize(format_desc)[-1]
        if len(bk) > 0:
            format_desc = format_desc + bk
            format_desc = nltk.sent_tokenize(format_desc)[0]

    # line_desc 在line的尾部， line中含有大于1句子数量，则只需要添加line_desc的下文
    elif order_line_desc == sent_count - 1:
        bk = back(line_index, lines, line_desc)
        if len(bk) > 0:
            format_desc = format_desc + bk
            format_desc = nltk.sent_tokenize(format_desc)[0]

    # line_desc 在line的中间，无需添加line_desc的下文
    else:
        format_desc = format_desc

    return format_desc


def back(line_index, lines, line_desc):
    """
    向后遍历，补充line_desc,使其变成一个完整的句子
    :param line_index: line_desc 在lines的定位
    :param lines:
    :param line_desc: 不完整的句子
    :return: 让line_desc变成一个完整的句子所缺的后面一部分字符串
    """

    format_desc = ''  # 返回用来填补的字符串
    line_desc = line_desc.strip()

    # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
    if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$', str(line_desc).strip()):
        return format_desc

    while line_index < len(lines) - 1:

        # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
        if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$', str(format_desc).strip()):
            return format_desc

        line_index = line_index + 1  # 下一行
        line = lines[line_index]

        if len(line.strip()) == 0:
            break

        # 如果下一行是以'大写字母','*',"'''",'#','-','"""'开始的，则表明该行是一个新句子的开头，直接返回
        if re.match(r'^[A-Z]|^\* |^- |^#|^\'\'\'|^\"\"\"', str(line).strip()):
            break

        # 加上所有的子句，返回
        sens = nltk.sent_tokenize(line)
        format_desc = format_desc + ' ' + sens[0]
        if len(sens) > 1:
            break
        else:
            continue

    if len(format_desc.strip()) > 0:
        format_desc = format_desc  # [1:]  # 去掉头部空格

    return format_desc


def forward(line_index, lines, line_desc):
    """
    向前遍历，补充line_desc,使其变成一个完整的句子
    :param line_index: line_desc 在lines的定位
    :param lines:
    :param line_desc: 不完整的句子
    :return: 让line_desc变成一个完整的句子所缺的前面一部分字符串
    """
    format_desc = ''  # 返回用来填补的字符串

    # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回
    if re.match(r'^[A-Z]|^\* |^- |^#|^\'\'\'|^\"\"\"', str(line_desc).strip()):
        return format_desc

    while line_index > 0:

        # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回
        if re.match(r'^[A-Z]|^\* |^- |^#|^\'\'\'|^\"\"\"', str(format_desc).strip()):
            return format_desc

        # 上一行
        line_index = line_index - 1
        line = lines[line_index]

        if len(line.strip()) == 0:
            break

        # 如果上一行是以'.',':',"'''",'!','?','"""'结尾的，则表明行是一个新句子的尾部，直接返回
        if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$', str(line).strip()):
            return format_desc

        # 加上所有的子句，返回
        sens = nltk.sent_tokenize(line)
        format_desc = sens[-1] + ' ' + format_desc
        if len(sens) > 1:
            break
        else:
            continue

    if len(format_desc.strip()) > 0:
        format_desc = format_desc  # [:-1]  # 去掉尾部空格
    return format_desc


def find_lcsubstr(s1, s2, case_sensitive=True):
    """
    str_one 和 str_two 的最长公共子序列
    :param str_one: 字符串1
    :param str_two: 字符串2（正确结果）
    :param case_sensitive: 比较时是否区分大小写，默认区分大小写
    :return: 最长公共子串的长度, 及子串
    """
    if not case_sensitive:
        s1 = s1.lower()
        s2 = s2.lower()

    m=[[0 for i in range(len(s2)+1)]  for j in range(len(s1)+1)]  #生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax=0   #最长匹配的长度
    p=0  #最长匹配对应在s1中的最后一位
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i]==s2[j]:
                m[i+1][j+1]=m[i][j]+1
                if m[i+1][j+1]>mmax:
                    mmax=m[i+1][j+1]
                    p=i+1

    return s1[p-mmax:p]  # ,mmax   #返回最长子串及其长度


if __name__ == '__main__':
    path = 'D:\\MyDocument\\performance\\git_log\\auto_evol\\format_desc\\desc_blank_line_unique.csv.csv'
    clone_path = 'D:\\MyDocument\\performance\\clone'
    save_path = 'D:\\MyDocument\\performance\\git_log\\auto_evol\\auto_evol\\auto_evlo16_add_blank.csv'
    # caveat = reade_csv(path)
    # kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    # pf = get_commit_id(caveat, clone_path, kws)
    # pf.to_csv(save_path, encoding='utf_8_sig')