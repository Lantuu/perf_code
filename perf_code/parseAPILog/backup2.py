import ast
import os
import re
import pandas as pd
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters


# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)
version = {'pandas': 'v0.24.2', 'numpy': 'v1.16.4', 'scipy': 'v1.2.1', 'sklearn': '0.21.2', 'tensorflow': 'r1.13', 'gensim': '3.7.3', 'docs': 'r1.13'}
GIT_LINE_LOG = r'git -C {} log -p -u -L {},{}:{}> {}'
GIT_FILE_LOG = r'git -C {} log -p -u {}> {}'
GIT_ID_LOG = r'git -C {} log -p -u -1 {} {}> {}'
GIT_FIlE_CHANGE_LOG = r'git -C {} log --stat {} {}> {}'
GIT_Checkout = r'git -C {} checkout {}'
GIT_NAME_STATUS = r'git -C {} log --name-status -1 {} > {}'

punkt_param = PunktParameters()
abbreviation = ['i.e', 'e.g']
punkt_param.abbrev_types = set(abbreviation)
tokenizer = PunktSentenceTokenizer(punkt_param)


def main(caveat, root_path, kws):

    save_data = pd.DataFrame()
    for index, row in caveat.iterrows():
        if index < 65:
            continue
        path_list = []
        commit_data = {'path': '', 'project': '', 'line_no': '', 'id': '', 'type': '', 'desc': ''}
        line_no = row['lineno']
        sub_path = row['filepath']
        repo = row['project']
        desc = row['format_desc']
        if desc == 'no':
            continue
        line_start = row['line_start']
        line_end = row['line_end']
        sigs = ast.literal_eval(row['sig'])
        repo_path = root_path + '\\' + repo
        file_path = repo_path
        v = version[repo]
        file_path = file_path + '\\' + sub_path.replace('/', '\\')
        path_list.append(file_path)
        commit = get_file_diff(file_path, version=v, repo_path=repo_path)
        line_ids = get_line_id(repo_path, line_start, line_end, row['filepath'])

        len_save_data = len(save_data)
        travel_ids = []
        new_file_list = []
        index = 0
        while index < len(commit):
            # i = commit.loc[len(commit)-1]['id']
            commit_id = commit.loc[index]['id']
            diff = commit.loc[index]['diff']
            commit_type, delete_sent, index = filter_id(commit, desc, file_path, sigs, index, line_ids)
            commit_id = commit.loc[index]['id']
            travel_ids.append(commit_id)

            if len(commit_type) != 0:
                commit_data['id'] = commit_id
                commit_data['type'] = commit_type
                commit_data['desc'] = desc
                commit_data['path'] = sub_path
                commit_data['project'] = repo
                commit_data['line_no'] = line_no
                commit_data['sigs'] = sigs

                save_data = save_data.append(commit_data, ignore_index=True)
                print(commit_data)

            if commit_type == 'alter':
                if is_contain_kw(kws, desc, delete_sent):
                    desc = delete_sent
                else:
                    commit_data['id'] = ''
                    commit_data['type'] = ''
                    commit_data['desc'] = delete_sent
                    save_data = save_data.append(commit_data, ignore_index=True)
                    print(commit_data)
                    break

            elif commit_type == 'add':
                new_file = get_new_file(commit_id, repo_path, file_path)
                if new_file != '':
                    if new_file in new_file_list:
                        save_data.drop([len(save_data) - 1], inplace=True)
                        save_data.loc[len(save_data) - 1, 'type'] = 'file renamed infinite loop'
                        index = len(commit)
                        break
                    file_path = repo_path + '\\' + new_file.replace('/', '\\')
                    sub_path = new_file
                    commit = get_file_diff(file_path, v, repo_path)
                    save_data.loc[len(save_data) - 1, 'type'] = 'file renamed'
                    index = -1
                    new_file_list.append(new_file)
                else:
                    break

                # #  commit_type = 'add' or ''
                # # if commit_type == 'add':
                # deficiency_ids = [id for id in line_ids if id not in travel_ids]
                # new_path_list = get_new_path(commit_id, repo_path, file_path, deficiency_ids)
                #
                #
                # for p in new_path_list:
                #     if p in path_list:
                #         new_path_list = []
                #         break
                #
                # if len(new_path_list) == 0:
                #     break
                #
                # path_list.extend(new_path_list)
                # for i in range(len(new_path_list)):
                #
                #     if get_file_diff(new_path_list[i], v, repo_path) is not None:
                #         len_new_data = len(save_data)
                #         file_path = new_path_list[i]
                #         commit = get_file_diff(file_path, v, repo_path)
                #         save_data.loc[len(save_data) - 1, 'type'] = 'alter file renamed'
                #         save_data.loc[len(save_data) - 1, 'path'] = file_path
                #         new_path_index = i
                #         index = -1
                #         break
            # else:
            #     if index == len(commit) - 1 and len_new_data == len(save_data) and new_path_index < len(new_path_list)-1:
            #         for i in range(new_path_index + 1, len(new_path_list)):
            #             if get_file_diff(new_path_list[i], v, repo_path) is not None:
            #                 len_new_data = len(save_data)
            #                 new_path_index = i + 1
            #                 file_path = new_path_list[i]
            #                 commit = get_file_diff(file_path, v, repo_path)
            #                 save_data.loc[len(save_data) - 1, 'type'] = 'alter file renamed'
            #                 save_data.loc[len(save_data) - 1, 'path'] = file_path
            #                 index = -1

            index = index + 1

        if len(save_data) == len_save_data:
            commit_data['id'] = ''
            commit_data['type'] = ''
            commit_data['desc'] = desc
            commit_data['path'] = row['filepath']
            commit_data['project'] = repo
            commit_data['line_no'] = line_no
            save_data = save_data.append(commit_data, ignore_index=True)

        if index == len(commit) and save_data.loc[len(save_data)-1]['type'] == 'alter':
            commit_data['id'] = ''
            commit_data['type'] = ''
            commit_data['desc'] = desc
            save_data = save_data.append(commit_data, ignore_index=True)
            print(commit_data)

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
    temp_path = os.getcwd() + '\\tem_log' + '.txt'
    temp_file = open(temp_path, 'w', encoding='utf-8', errors='ignore')
    temp_file.close()
    git_log_command1 = GIT_Checkout.format(repo_path, version)
    git_log_command = GIT_LOG.format(repo_path, file_path, temp_path)
    os.system(git_log_command1)
    os.system(git_log_command)
    # with open(temp_path, 'r', encoding='utf-8'):
    lines = read_txt(temp_path)
    # if len(lines) == 0:
    #     return None
    commit = split_log(lines)
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

    temp_path = os.getcwd() + '\\tem_log2' + '.txt'
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
    temp_path = os.getcwd() + '\\' + 'name_status.txt'
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


def get_new_path(id, repo_path, file_path, ids):
    sub_path = file_path.replace(repo_path, '').replace('\\', '/')[1:]
    temp_path = os.getcwd() + '\\' + 'newfile.txt'
    comm_file_change = GIT_FIlE_CHANGE_LOG.format(repo_path, id, file_path, temp_path)
    os.system(comm_file_change)
    sub_path2 = sub_path.replace('/', '.')
    sub_path2 = sub_path2.replace('.' + sub_path.split('.')[-1], '')
    new_path_list = []

    file = []
    move_file = {}
    lines = read_txt(temp_path)
    for line in lines:
        line = line.strip()
        if line.find(' -> ') != -1:
            if re.search('^\S+', line.split(' -> ')[-1]):
                to_file = re.search('^\S+', line.split(' -> ')[-1]).group()
            else:
                break
            from_file = line.split(' -> ')[0].split('move ')[-1].split(', ')
            # from_file = re.search('\S+$', line.split(' -> ')[0]).group()
            for f in from_file:
                f = f.split(' ')[-1]
                move_file[f] = to_file

        elif re.search('move .* to .*', line):
            if re.search('^\S+', line.split(' to ')[-1]):
                to_file = re.search('^\S+', line.split(' to ')[-1]).group()
            else:
                break
            from_file = line.split(' to ')[0].split('move ')[-1].split(', ')
            for f in from_file:
                f = f.split(' ')[-1]
                move_file[f] = to_file

        elif re.search('rename .* to .*', line, re.I):
            if re.search('^\S+', line.split(' to ')[-1]):
                to_file = re.search('^\S+', line.split(' to ')[-1]).group()
            else:
                break

            if to_file.endswith('.'):
                to_file = to_file[:-1]

            from_file = line.split(' to ')[0].split('ename ')[-1].split(', ')
            for f in from_file:
                f = f.split(' ')[-1]
                move_file[f] = to_file

    for to in move_file.values():
        # file.extend([k for k,v in move_file.items() if v == value])
        if sub_path.find(to) != -1:
            # move_file[key] + sub_path.replace(key, ''))

            file.extend([sub_path.replace(to, k) for k, v in move_file.items() if v == to])
            file.extend([k for k, v in move_file.items() if v == to])
            break

        elif sub_path2.find(to) != -1:
            file.extend([sub_path2.replace(to, k).replace('.', '/') + '.' + sub_path.split('.')[-1] for k, v in move_file.items() if v == to])
            file.extend([k.replace('.', '/') + '.' + sub_path.split('.')[-1] for k, v in move_file.items() if v == to])
            break

    for f in file:
        if not f.endswith('.'+sub_path.split('.')[-1]):
            continue
        new_path = repo_path + '\\' + f.replace('/', '\\')
        new_path_list.append(new_path)

    if len(new_path_list) == 0 and len(ids) > 0:
        new_files = []

        new_path = repo_path
        temp_path = os.getcwd() + '\\' + 'newfile.txt'
        files_list = []
        for id in ids:
            comm = 'git -C ' + repo_path + ' log -1 --name-only ' + id + ' > ' + temp_path
            os.system(comm)
            files = []
            lines = read_txt(temp_path)
            for i in range(len(lines) - 1, -1, -1):
                if len(lines[i].strip()) == 0:
                    break
                files.append(lines[i].strip())
            if len(files) == 1:
                new_file = files[0]
                for p in new_file.split('/'):
                    new_path = new_path + '\\' + p
                    new_path_list.append(new_path)
                return new_path_list
            else:
                files_list.extend(files)

        files_set = set(files_list)
        for file in files_set:
            if files_list.count(file) == len(ids):
                new_files.append(file)

        if len(new_files) == 1:
            new_file = new_files[0]
        elif len(new_files) == 0:
            return new_path_list

        else:
            ls = []
            for file in new_files:
                new_file_name = file.split('/')[-1]
                old_file_name = file_path.split('/')[-1]
                ls.append(levenshtein(new_file_name, old_file_name))
            new_file = new_files[ls.index(min(ls))]

        for p in new_file.split('/'):
            new_path = new_path + '\\' + p

        new_path_list.append(new_path)

    return new_path_list


def filter_id(commit, desc, file_path, sigs, commit_index, lines_ids):
    """
    找到所有增加了desc的commit
    :param commit: 所有id的commit内容
    :param desc:  performance sentence
    :param file_path: performance sentence 所在的文件
    :param sigs: performance sentence 描述的APIs
    :param commit_index: 接着上文，从这个index开始遍历commit
    :param lines_ids: performance sentence所在行的diff ids
    :return: commit_type： 改动类型add or alter, delete_sent 改动之前的句子, index 该commit的索引
    """
    commit_ids = []  # 所有增加了desc的commit信息 commit_type, delete_sent, index

    for index in range(commit_index, len(commit)):
        commit_id = commit.loc[index]['id']
        if commit_id != '8ddb0ce0acafe75d78df528b4d2540dfbf4b364d':
            continue
        diff = commit.loc[index]['diff']
        commit_type, delete_sent = get_commit_type(diff, desc, file_path, sigs)
        if len(commit_type) != 0:
            commit_ids.append((commit_type, delete_sent, index))

    if len(commit_ids) == 0:
        return '', '', len(commit) - 1

    elif len(commit_ids) == 1:
        return commit_ids[0][0], commit_ids[0][1], commit_ids[0][2]

    # 有两个id及以上都增加了desc，则筛选出一个
    # 根据line_ids
    for index in range(len(commit_ids)):
        id = commit.loc[commit_ids[index][2]]['id']
        for line_id in lines_ids:
            if id == line_id:
                return commit_ids[index][0], commit_ids[index][1], commit_ids[index][2]

    # 根据diff的函数名
    for index in range(len(commit_ids)):
        diff = commit.loc[commit_ids[index][2]]['diff']
        diff_snippets = split_diff(diff)
        # 优先选择改动的函数为sig中的
        if len(get_def_snippets(diff_snippets, sigs)) > 0:
            return commit_ids[index][0], commit_ids[index][1], commit_ids[index][2]

    # line_ids 和函数名都没找到则返回第一个
    return commit_ids[0][0], commit_ids[0][1], commit_ids[0][2]


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


def get_def_snippets(diff_snippets, sigs):
    """
    找到sigs 中 包含 @@ ...@@  中含有的函数名的 diff_snippets
    :param diff_snippets: @@...@@ 片段
    :param sigs: APIs
    :return:  APIs 中 包含 @@ ...@@  中含有的函数名的diff_snippets
    """
    diff_lines = []  # 所有 @@ ...@@
    def_snippets = []  # @@ ...@@  中含有的函数名 in sigs 则插入

    for diff_snippet in diff_snippets:
        diff_dic = classify_sens(diff_snippet)
        diff_lines.append(diff_dic['lines'])

    for diff_index in range(len(diff_lines)):
        if re.search(r' \w+\(', diff_lines[diff_index]):
            # 匹配函数名
            def_name = re.search(r' \w+\(', diff_lines[diff_index]).group()[1:-1]

            # 遍历sigs, sigs 含有 def_name 则插入
            for sig in sigs:
                field_name = sig.split('.')
                if def_name in field_name:
                    def_snippets.append(diff_snippets[diff_index])
    return def_snippets


def get_commit_type(diff, desc, file_path, sigs):
    commit_types = []
    delete_sents = []
    diff_contain_desc = []

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

        if add_common_sent.strip() == delete_common_sent.strip():
            continue

        elif len(add_common_sent) != 0:
            delete_sent, lc_substr = find_delete_sent(desc, delete, delete_space, file_path)
            if desc.lstrip() != add_common_sent.lstrip():
                commit_type = 'alter'
            elif len(delete_sent) != 0:
                lc_substr = re.sub(r'\W', ' ', lc_substr)
                # lc_subword = nltk.word_tokenize(lc_substr)
                lc_subword = nltk.word_tokenize(lc_substr)
                # # 最长公共子序列返回的条件
                # if len(delete_sent) > 0:
                ls = levenshtein(delete_sent.encode('utf-8').decode('unicode-escape'), desc.encode('utf-8').decode('unicode-escape'))
                if ls/len(desc) <= 0.58 or len(lc_subword) >= 4:
                    commit_type = 'alter'
                else:
                    delete_sent = ''
                    commit_type = 'add'
            else:
                commit_type = 'add'

            if commit_type == 'alter' and delete_sent == '':
                delete_sent = desc.replace(add_common_sent + ' ', '')

            commit_types.append(commit_type)
            delete_sents.append(delete_sent)
            diff_contain_desc.append(diff_snippet)

    if len(commit_types) == 0:
        return '', ''
    elif len(commit_types) == 1:
        return commit_types[0], delete_sents[0]

    # 有大于1个diff snippet 添加了desc， 则选出一个 优先选择改动的函数为sig中的
    def_snippets = get_def_snippets(diff_snippets, sigs)
    for i in range(len(diff_contain_desc)):
        for snippet in def_snippets:
            if diff_contain_desc == snippet:
                return commit_types[i], delete_sents[i]

    return commit_types[0], delete_sents[0]


def find_delete_sent(desc, delete, delete_space, file_path):
    """
    在一个字符串列表中，求其与desc的最长公共子序列
    :param desc:
    :param delete_blank: 字符串列表
    :return: delete_string： 与desc具有最长公共子序列的字符串， 最长公共子序列的大小
    """
    lines = []
    for line in delete_space:
        lines.append(line[1:])
    delete_string = ''  # 最长公共子序列
    max_res = 0
    delete_line_index = None   # 最长公共子序列在delete中行的索引
    delete_space_line_index = None  # 最长公共子序列在delete_space中行的索引
    lc_substring = ''
    for index in range(len(delete)):
        lc = []
        substring = []
        if len(delete[index]) > 10000:
            continue
        # delete_sents = nltk.sent_tokenize(delete[index][1:])
        delete_sents = tokenizer.tokenize(delete[index][1:])

        # 计算每个句子与desc的最长公共子序列
        for sent in delete_sents:
            s = find_lcsubstr(sent.strip(), desc.strip())
            lc.append(len(s.strip()))
            substring.append(s.strip())

        # 求最长公共子序列最大的句子及最长公共子序列大小
        max_lc_line = 0
        max_lc_index = -1
        for i in range(len(lc)):
            if lc[i] > max_lc_line:
                max_lc_line = lc[i]
                max_lc_index = i
        # max_lc_line = max(lc)
        # max_lc_index = lc.index(max_lc_line)

        if max_lc_line > max_res:
            max_res = max_lc_line
            delete_string = delete_sents[max_lc_index]
            delete_line_index = index
            lc_substring = substring[max_lc_index]

    # 在delete_space中的索引
    for index in range(len(delete_space)):
        if delete_line_index is None:
            break
        if delete_space[index] == delete[delete_line_index]:
            delete_space_line_index = index
            break

    if not file_path.endswith('.ipynb') and len(delete_string) > 0:
        delete_string = get_format_desc(delete_string, delete_space_line_index, lines)

    # # lc_substring = re.sub(r'[\[\]()`~·、\\{}\-_+=?.,<>:;\"\'@#$%^&*!]*', '', lc_substring)
    # lc_substring = re.sub(r'\W', ' ', lc_substring)
    # lc_subword = nltk.word_tokenize(lc_substring)
    #
    # # 最长公共子序列返回的条件
    # if len(delete_string) > 0:
    #     ls = levenshtein(delete_string.encode('utf-8').decode('unicode-escape'), desc.encode('utf-8').decode('unicode-escape'))
    #     if ls/len(desc) <= 0.58 or len(lc_subword) >= 4:
    #         return delete_string
    #
    # else:
    #     return None

    return delete_string, lc_substring


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
    # print(distance_matrix)
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


def get_common_sent(alter_list, desc, blank_list):

    common_sen = ''
    # 去每一行前面的"+/-"
    blank_lines = [line[1:] for line in blank_list]
    alter_lines = [line[1:] for line in alter_list]

    line_sen_index = 0
    line_sen = ''
    alter_index = 0
    while alter_index < len(alter_lines):
        line = alter_lines[alter_index]
        if line.strip().startswith('\"image/png\"'):
            continue
        if len(line) > 10000:
            continue

        # line_sents = nltk.sent_tokenize(line)
        line_sents = tokenizer.tokenize(line)
        for sen_index in range(len(line_sents)):
            if re.search(r'[a-zA-Z]', line_sents[sen_index].replace('\\n', '')) is None:
                continue

            if line_sents[sen_index].strip() in desc:

                # 找到在blank中的索引下标
                blank_index = -1
                add_or_delete = -1
                for index in range(len(blank_list)):
                    if blank_list[index].startswith(alter_list[alter_index].strip()[0]):
                        add_or_delete = add_or_delete + 1

                    if add_or_delete == alter_index:
                        blank_index = index
                        break
                complete_sen = get_format_desc(line_sents[sen_index], blank_index, blank_lines)

                if desc in complete_sen:
                    line_sen_index = sen_index
                    line_sen = line_sents[sen_index]
                    break

        if line_sen != '':
            common_sen = line_sen
            desc2 = desc.replace(line_sen, '')
            if line_sen_index < len(line_sents)-1:
                break

            for i in range(alter_index + 1, len(alter_lines)):
                line = alter_lines[i]
                # line_sens = nltk.sent_tokenize(line)
                line_sens = tokenizer.tokenize(line)
                tag = True
                for sen in line_sens:
                    if sen in desc2:
                        common_sen = common_sen + ' ' + sen
                        desc2 = desc2.replace(sen, '')
                    else:
                        tag = False
                        break
                if not tag:
                    break
            break
        else:
            alter_index = alter_index + 1
    return common_sen


def get_conained_sen(index, string_list, desc):
    contained_sen = ''
    tag = True
    for i in range(index, len(string_list)):
        # for s in nltk.sent_tokenize(string_list[i]):
        for s in tokenizer.tokenize(string_list[i]):
            if str(desc).find(s) != -1:
                contained_sen = contained_sen + ' ' + s
            else:
                tag = False
                break
        if not tag:
            break
    if len(contained_sen) > 0:
        contained_sen = contained_sen[1:]
    return contained_sen


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
    f = open(file_path, 'r', encoding='utf-8', errors='ignore')
    # data = f.read()
    # print(chardet.detect(data))
    lines = f.readlines()
    f.close()
    return lines


def split_log(git_log):
    """
    分割一个commit命令返回的日志
    :param git_log: 待分割的日志
    :return: pd.dataframe 3列['id', 'diff', 'other']   id: commitID; diff: difference;
    """

    diff = []
    other = []
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

    # sens = nltk.sent_tokenize(line)
    line = line.replace('\n', '\\n')
    sens = tokenizer.tokenize(line)
    sent_count = len(sens)  # line中含有句子的数量
    order_line_desc = -1   # line_desc 在line子句中的定位

    for sen in sens:
        sen = sen.replace('\\n', '\n')
        order_line_desc = order_line_desc + 1
        if sen == line_desc:
            break

    # line_desc 在line的头部， line中含有大于1句子数量，则只需要添加line_desc的上文
    if order_line_desc == 0 and sent_count > 1:
        fw = forward(line_index, lines, line_desc)
        if len(fw) > 0:
            format_desc = fw + format_desc
            format_desc = tokenizer.tokenize(format_desc)[-1]
            # format_desc = nltk.sent_tokenize(format_desc)[-1]

    # line_desc 在line的头部， line中只有1个句子，则需要添加line_desc的上文和下文
    elif order_line_desc == 0 and sent_count == 1:
        fw = forward(line_index, lines, line_desc)
        bk = back(line_index, lines, line_desc)
        if len(fw) > 0:
            format_desc = fw + format_desc
            format_desc = tokenizer.tokenize(format_desc)[-1]
           # format_desc = nltk.sent_tokenize(format_desc)[-1]
        if len(bk) > 0:
            format_desc = format_desc + bk
            format_desc = tokenizer.tokenize(format_desc)[0]
            # format_desc = nltk.sent_tokenize(format_desc)[0]

    # line_desc 在line的尾部， line中含有大于1句子数量，则只需要添加line_desc的下文
    elif order_line_desc == sent_count - 1:
        bk = back(line_index, lines, line_desc)
        if len(bk) > 0:
            format_desc = format_desc + bk
            format_desc = tokenizer.tokenize(format_desc)[0]
            # format_desc = nltk.sent_tokenize(format_desc)[0]

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
    if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===', str(line_desc).strip()):
        return format_desc

    while line_index < len(lines) - 1:

        # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
        if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===', str(format_desc).strip()):
            return format_desc

        line_index = line_index + 1  # 下一行
        line = lines[line_index]

        if len(line.strip()) == 0:
            break

        # 如果下一行是以'大写字母','*',"'''",'#','-','"""'开始的，则表明该行是一个新句子的开头，直接返回  ^[A-Z]|
        if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\S+ :', str(line).strip()):  # |\S+:^[A-Z]|
            break

        # 加上所有的子句，返回
        sens = tokenizer.tokenize(line)
        # sens = nltk.sent_tokenize(line)
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

    # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回   ^[A-Z]|
    if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\S+ :', str(line_desc).strip()):  # |\S+:^[A-Z]|
        return format_desc

    while line_index > 0:

        # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回    ^[A-Z]|
        if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\S+ :', str(format_desc).strip()):  # |\S+: ^[A-Z]|
            break

        # 上一行
        line_index = line_index - 1
        line = lines[line_index]

        if len(line.strip()) == 0:
            break

        # 如果上一行是以'.',':',"'''",'!','?','"""'结尾的，则表明行是一个新句子的尾部，直接返回
        if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===', str(line).strip()):
            break

        # 加上所有的子句，返回
        sens = tokenizer.tokenize(line)
        # sens = nltk.sent_tokenize(line)
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

    m = [[0 for i in range(len(s2)+1)] for j in range(len(s1)+1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax = 0   # 最长匹配的长度
    p = 0  # 最长匹配对应在s1中的最后一位
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i+1][j+1] = m[i][j]+1
                if m[i+1][j+1] > mmax:
                    mmax = m[i+1][j+1]
                    p = i+1

    return s1[p-mmax:p]  # ,mmax   #返回最长子串及其长度


if __name__ == '__main__':
    path = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\docstring_unique4.csv'
    clone_path = 'D:\\MyDocument\\performance\\clone'
    save_path = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\auto_evol\\docstring_evol8.csv'
    caveat = reade_csv(path)
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    pf = main(caveat, clone_path, kws)
    pf.to_csv(save_path, encoding='utf_8_sig')