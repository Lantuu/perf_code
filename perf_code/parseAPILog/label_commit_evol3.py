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
pd.set_option('max_colwidth', 10000)
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
        # if index < 582:
        #     continue
        travel_file_list = []
        travel_ids = []
        commit_data = {'path': '', 'project': '', 'line_no': '', 'id': '', 'type': '', 'desc': ''}
        line_no = row['lineno']
        sub_path = row['filepath']
        repo = row['project']
        desc = row['format_desc'].strip()
        sigs = ast.literal_eval(row['sig'])

        if desc == 'no':
            commit_data['id'] = 'no'
            commit_data['type'] = 'no'
            commit_data['desc'] = desc
            commit_data['path'] = sub_path
            commit_data['project'] = repo
            commit_data['line_no'] = line_no
            commit_data['sigs'] = sigs
            save_data = save_data.append(commit_data, ignore_index=True)
            print(commit_data)
            continue
        line_start = row['line_start']
        line_end = row['line_end']

        repo_path = root_path + '\\' + repo
        file_path = repo_path
        v = version[repo]
        file_path = file_path + '\\' + sub_path.replace('/', '\\')
        travel_file_list.append(sub_path)
        commit = get_file_diff(file_path, version=v, repo_path=repo_path)
        line_ids = get_line_id(repo_path, line_start, line_end, row['filepath'])
        line_commit = get_line_diff(repo_path, line_start, line_end, file_path, v)

        tag_rename = False
        tag_line_id = False
        len_save_data = len(save_data)
        index = 0
        commit_id = ''
        while index < len(commit):
            # print(commit['id'])
            temp_index = index
            commit_type, delete_sent, index = filter_id(commit, desc, file_path, sigs, index, line_ids)
            commit_id = commit.loc[index]['id']
            travel_ids.extend(commit['id'][temp_index:index+1])

            if len(commit_type) != 0:
                commit_data['id'] = commit_id
                commit_data['type'] = commit_type
                if desc.startswith('-'):
                    commit_data['desc'] = ' ' + desc
                else:
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
                if new_file != '' and not tag_line_id:
                    if new_file in travel_file_list:
                        save_data.loc[len(save_data) - 1, 'type'] = 'file renamed infinite loop'
                        index = index + 1
                        continue
                    file_path = repo_path + '\\' + new_file.replace('/', '\\')
                    sub_path = new_file
                    commit = get_file_diff(file_path, v, repo_path)
                    save_data.loc[len(save_data) - 1, 'type'] = 'file renamed'
                    travel_file_list.append(new_file)
                    if commit is None:
                        # print(line_ids)
                        id_list = [commit_id]
                        id_list.extend([id for id in list(line_commit['id']) if id not in travel_ids])
                        commit = line_commit[line_commit['id'].isin(id_list)]
                        commit.reset_index(drop=True, inplace=True)
                        tag_line_id = True
                        index = 0
                        continue
                    index = -1
                else:
                    break

            if index == len(commit) - 1:
                # print(line_ids)
                type = ''
                if len(save_data) - len_save_data > 0:
                    type = save_data.loc[len(save_data)-1]['type']
                is_contained = is_contain_kw(kws, desc, desc)
                if (len(save_data) == len_save_data or (type != 'add' and is_contained)) and not tag_line_id:  # or (type != 'add' and is_contained))
                    travel_ids_temp = travel_ids
                    if type == 'file renamed' and not tag_rename:
                        tag_rename = True
                        renamed_ids = []
                        for id in save_data['id'][save_data['type'] == 'file renamed']:
                            renamed_ids.append(id)
                        for renamed_ids_index in range(len(renamed_ids)-1, -1, -1):
                            if renamed_ids[renamed_ids_index] in travel_ids_temp:
                                travel_ids_index = travel_ids_temp.index(renamed_ids[renamed_ids_index])
                                travel_ids_temp = travel_ids_temp[:travel_ids_index]
                                break

                        travel_ids_temp = [id for id in travel_ids_temp if id not in renamed_ids]
                    id_list = [id for id in list(line_commit['id']) if id not in travel_ids_temp]
                    commit = line_commit[line_commit['id'].isin(id_list)]
                    commit.reset_index(drop=True, inplace=True)
                    tag_line_id = True
                    index = 0
                    continue

            index = index + 1

        # Moved numpy-docs under doc/ in the main Numpy trunk.
        if len(save_data) == len_save_data:
            commit_data['id'] = commit_id
            commit_data['type'] = 'add'
            if desc.startswith('-'):
                commit_data['desc'] = ' ' + desc
            else:
                commit_data['desc'] = desc
            commit_data['path'] = sub_path
            commit_data['project'] = repo
            commit_data['line_no'] = line_no
            commit_data['sigs'] = sigs
            commit.reset_index(drop=True, inplace=True)
            save_data = save_data.append(commit_data, ignore_index=True)
            print(commit_data)

        if index == len(commit) and save_data.loc[len(save_data)-1]['type'] == 'alter':
            commit_data['id'] = ''
            commit_data['type'] = ''
            commit_data['desc'] = desc
            save_data = save_data.append(commit_data, ignore_index=True)
            print(commit_data)

    return save_data


class CommitType:
    def __init__(self, diff):
        self.diff = diff
        self.commit_type = ''
        self.delete_sent = ''
        self.diff_snippet = []

    def set_commit_type(self, sig, desc, file_path):
        commit_type_list = []
        delete_sent_list = []
        snippet_list = []
        diff_snippets = split_diff(self.diff)

        for diff_snippet in diff_snippets:
            diff_dic = classify_sens(diff_snippet)
            add = diff_dic['add']
            delete = diff_dic['delete']
            add_space = diff_dic['add_space']
            delete_space = diff_dic['delete_space']

            # ' +/- '行中，含有的desc公共子序列
            add_common_sent = self.get_common_sent(add, desc, add_space)
            delete_common_sent = self.get_common_sent(delete, desc, delete_space)

            if add_common_sent == delete_common_sent:
                continue

            elif len(add_common_sent) != 0:
                delete_sent, lc_substr = self.get_delete_sent(desc, delete, delete_space, file_path)
                if desc.lstrip() != add_common_sent.lstrip():
                    commit_type = 'alter'
                elif len(delete_sent) != 0:
                    lc_subword = nltk.word_tokenize(lc_substr)
                    lc_subword2 = []
                    for i in range(len(lc_subword)):
                        if len(re.sub(r'[\W0-9]', '', lc_subword[i])) != 0:
                            lc_subword2.append(lc_subword[i])
                    # lc_substr = re.sub(r'[\W0-9]', ' ', lc_substr)
                    # # 最长公共子序列返回的条件
                    ls = levenshtein(delete_sent.encode('utf-8').decode('unicode-escape'),
                                     desc.encode('utf-8').decode('unicode-escape'))
                    if ls/len(desc) <= 0.58 or len(lc_subword2) >= 4:
                        commit_type = 'alter'
                    else:
                        delete_sent = ''
                        commit_type = 'add'
                else:
                    commit_type = 'add'

                if commit_type == 'alter' and delete_sent == '':
                    if add_common_sent + ' ' in desc:
                        delete_sent = desc.replace(add_common_sent + ' ', '')
                    elif ' ' + add_common_sent in desc:
                        delete_sent = desc.replace(' ' + add_common_sent, '')
                    else:
                        delete_sent = desc.replace(add_common_sent, '')

                commit_type_list.append(commit_type)
                delete_sent_list.append(delete_sent)
                snippet_list.append(diff_snippet)

        if len(commit_type_list) == 1:
            self.commit_type = commit_type_list[0]
            self.delete_sent = delete_sent_list[0]
            self.diff_snippet = snippet_list[0]
            # return commit_types[0], delete_sents[0]

        # 有大于1个diff snippet 添加了desc， 则选出一个 优先选择改动的函数为sig中的
        elif len(commit_type_list) > 1:
            api_snippet_dic = self.get_api_snippets(snippet_list, sig)
            if len(api_snippet_dic) != 0:
                api_snippet_index = list(api_snippet_dic.keys())[0]
                self.commit_type = commit_type_list[api_snippet_index]
                self.delete_sent = delete_sent_list[api_snippet_index]
                self.diff_snippet = snippet_list[api_snippet_index]
            else:
                self.commit_type = commit_type_list[0]
                self.delete_sent = delete_sent_list[0]
                self.diff_snippet = snippet_list[0]

    @staticmethod
    def get_common_sent(alter_list, desc, blank_list):

        common_sen = ''
        # 去每一行前面的"+/-"
        blank_lines = [line[1:].strip() for line in blank_list]
        alter_lines = [line[1:].strip() for line in alter_list]

        line_sen_index = 0
        line_sen = ''
        alter_index = 0
        while alter_index < len(alter_lines):
            line = alter_lines[alter_index]
            if line.strip().startswith('\"image/png\"'):
                alter_index = alter_index + 1
                continue
            if len(line) > 10000:
                alter_index = alter_index + 1
                continue

            line_sents = token_sent(line)
            for sen_index in range(len(line_sents)):
                if re.search(r'[a-zA-Z]', line_sents[sen_index].replace('\\n', '')) is None:
                    continue

                if line_sents[sen_index].strip() in desc:
                    # 找到在blank中的索引下标
                    blank_index = CommitType.get_blank_index(alter_index, blank_list, alter_list[alter_index].strip()[0])
                    format_desc = FormatDesc(line_sents[sen_index], blank_index, blank_lines)
                    format_desc.set_format_desc()
                    complete_sen = format_desc.format_desc

                    if desc in complete_sen:
                        line_sen_index = sen_index
                        line_sen = line_sents[sen_index]
                        break

            if line_sen != '':
                common_sen = line_sen
                desc2 = desc.replace(line_sen, '')
                if line_sen_index < len(line_sents) - 1:
                    break

                for i in range(alter_index + 1, len(alter_lines)):
                    line_sens = token_sent(alter_lines[i])
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

    @staticmethod
    def get_delete_sent(desc, delete, delete_space, file_path):
        """
        在一个字符串列表中，求其与desc的最长公共子序列
        :param desc:
        :param delete_blank: 字符串列表
        :return: delete_string： 与desc具有最长公共子序列的字符串， 最长公共子序列的大小
        """
        lines = [line[1:].strip() for line in delete_space]
        delete_sent = ''  # 最长公共子序列
        max_lc = 0
        min_leven = 0
        lc_substring = ''
        for index in range(len(delete)):
            if len(delete[index]) > 10000:
                continue

            blank_index = CommitType.get_blank_index(index, delete_space, '-')
            delete_sents = token_sent(delete[index][1:])

            # 计算每个句子与desc的最长公共子序列
            for sent in delete_sents:
                if not file_path.endswith('.ipynb') and len(sent) > 0:
                    formatDesc = FormatDesc(sent, blank_index, lines)
                    formatDesc.set_format_desc()
                    format_delete_sent = formatDesc.format_desc
                else:
                    format_delete_sent = sent

                format_delete_sent_ = ' '.join([i for i in format_delete_sent.strip().split(' ') if i != ''])
                desc_ = ' '.join([i for i in desc.strip().split(' ') if i != ''])
                leven = levenshtein(format_delete_sent_, desc_)
                lc = len(find_lcsubstr(format_delete_sent_, desc_))
                if lc > max_lc or (lc == max_lc and leven < min_leven):
                    max_lc = len(find_lcsubstr(format_delete_sent_, desc_))
                    min_leven = levenshtein(format_delete_sent_, desc_)
                    lc_substring = find_lcsubstr(format_delete_sent_, desc_)
                    delete_sent = format_delete_sent

        return delete_sent, lc_substring

    @staticmethod
    def get_blank_index(alter_index, blank_list, alter_tag):
        # 找到在blank中的索引下标
        blank_index = -1
        add_or_delete = -1
        for index in range(len(blank_list)):
            if blank_list[index].startswith(alter_tag):
                add_or_delete = add_or_delete + 1

            if add_or_delete == alter_index:
                blank_index = index
                break
        return blank_index

    @staticmethod
    def get_api_snippets(diff_snippets, sig):
        """
        找到sigs 中 包含 @@ ...@@  中含有的函数名的 diff_snippets
        :param diff_snippets: @@...@@ 片段
        :param sigs: APIs
        :return:  APIs 中 包含 @@ ...@@  中含有的函数名的diff_snippets
        """

        # diff_lines = []  # 所有 @@ ...@@
        api_snippets_dic = {}  # @@ ...@@  中含有的函数名 in sigs 则插入
        apis_name = []

        for api in sig:
            if api.split('.')[-1].strip() == '__init__':
                apis_name.append(api.split('.')[-2].strip())
            else:
                apis_name.append(api.split('.')[-1].strip())

        # 检查snippet diff中是否包含sig中的api
        for index in range(len(diff_snippets)):
            api_line = []
            for line in diff_snippets[index]:
                for api in apis_name:
                    if re.search('def '+api+'\(|class '+api+'\(', line):
                        api_line.append(line)
                        break

                if len(api_line) != 0:
                    api_snippets_dic[index] = diff_snippets[index]
                    break
        # if len(api_snippets_dic) > 0:
        #     return api_snippets_dic
        #
        # # 检查snippet line中是否包含sig中的api
        # for index in range(len(diff_snippets)):
        #     for api in apis_name:
        #         if re.search(api, diff_snippets[index][0]):
        #             api_snippets_dic[index] = diff_snippets[index]
        #             break
        return api_snippets_dic


class FormatDesc:
    def __init__(self, line_desc, line_desc_index, lines):
        self.line_desc = line_desc.strip()
        self.lines = lines
        self.line_desc_index = line_desc_index
        self.format_desc = ''

    def set_format_desc(self):
        """
        根据line_desc的值，在lines中找到它的上下文，使其变成一个完整的句子
        :param line_desc: 字符串
        :param line_index: 整型
        :param lines: 字符串列表
        :return: 字符串 含有line_desc上下文的完整句子
        """
        format_desc = self.line_desc.strip()
        line = self.lines[self.line_desc_index]
        line = line.replace('O(n!)', 'O(n\\\\)').strip()  # .replace('\n', '\\n').replace('"""', '')
        sens = token_sent(line)
        sent_count = len(sens)  # line中含有句子的数量
        order_line_desc = -1  # line_desc 在line子句中的定位

        for sen in sens:
            order_line_desc = order_line_desc + 1
            if sen == self.line_desc:
                break

        # line_desc 在line的头部， line中含有大于1句子数量，则只需要添加line_desc的上文
        if order_line_desc == 0 and sent_count > 1:
            fw = self.forward(self.line_desc_index, self.lines, self.line_desc)
            if len(fw) > 0:
                format_desc = fw + format_desc
                format_desc = token_sent(format_desc)[-1]

        # line_desc 在line的头部， line中只有1个句子，则需要添加line_desc的上文和下文
        elif order_line_desc == 0 and sent_count == 1:
            fw = self.forward(self.line_desc_index, self.lines, self.line_desc)
            bk = self.back(self.line_desc_index, self.lines, self.line_desc)
            if len(fw) > 0:
                format_desc = fw + format_desc
                format_desc = token_sent(format_desc)[-1]

            if len(bk) > 0:
                format_desc = format_desc + bk
                format_desc = token_sent(format_desc)[0]

        # line_desc 在line的尾部， line中含有大于1句子数量，则只需要添加line_desc的下文
        elif order_line_desc == sent_count - 1:
            bk = self.back(self.line_desc_index, self.lines, self.line_desc)
            if len(bk) > 0:
                format_desc = format_desc + bk
                format_desc = token_sent(format_desc)[0]

        self.format_desc = format_desc

    @staticmethod
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
        if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(line_desc).strip()):
            return format_desc

        while line_index < len(lines) - 1:

            # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
            if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(format_desc).strip()):
                return format_desc

            line_index = line_index + 1  # 下一行
            line = lines[line_index]

            if len(line.strip()) == 0:
                break

            # 如果下一行是以'大写字母','*',"'''",'#','-','"""'开始的，则表明该行是一个新句子的开头，直接返回  ^[A-Z]|
            if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(line).strip()):  # |\S+:^[A-Z]|
                break

            # 加上所有的子句，返回
            sens = token_sent(line)
            format_desc = format_desc + ' ' + sens[0].strip()  # .replace('\\n', '\n')
            if len(sens) > 1:
                break
            else:
                continue

        return format_desc

    @staticmethod
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
        if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(line_desc).strip()):  # |\S+:^[A-Z]|
            return format_desc

        while line_index > 0:

            # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回    ^[A-Z]|
            if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(format_desc).strip()):  # |\S+: ^[A-Z]|
                break

            # 上一行
            line_index = line_index - 1
            line = lines[line_index]

            if len(line.strip()) == 0:
                break

            # 如果上一行是以'.',':',"'''",'!','?','"""'结尾的，则表明行是一个新句子的尾部，直接返回
            if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(line).strip()):
                break

            # 加上所有的子句，返回
            sens = token_sent(line)
            format_desc = sens[-1].strip() + ' ' + format_desc  # .replace('\\n', '\n')
            # forward_line = forward_line + 1
            if len(sens) > 1:
                break
            else:
                continue

        return format_desc


def token_sent(str):
    str = str.replace('O(n!)', 'O(n\\\\)').strip()  # .replace('\n', '\\n').replace('"""', '')
    sens = []
    for sen in tokenizer.tokenize(str):
        sen_list = sen.split('_. ')
        for i in range(0, len(sen_list) - 1):
            sens.append(sen_list[i].strip() + '_.')
        if (len(sen_list)) > 0:
            sens.append(sen_list[-1].strip())
    for i in range(len(sens)):
        if 'O(n\\\\)' in sens[i]:
            sens[i] = sens[i].replace('O(n\\\\)', 'O(n!)')
    return sens


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
    if len(lines) == 0:
        return None
    commit = split_log(lines)
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
    temp_path = os.getcwd() + '\\tem_log' + '.txt'
    temp_file = open(temp_path, 'w', encoding='utf-8', errors='ignore')
    temp_file.close()
    git_log_command1 = GIT_Checkout.format(repo_path, version)
    git_line_log = GIT_LINE_LOG.format(repo_path, str(int(line_start)), str(int(line_end)), file_path, temp_path)
    os.system(git_log_command1)
    os.system(git_line_log)
    lines = read_txt(temp_path)
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


def filter_id(commit, desc, file_path, sig, commit_index, line_ids):
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
    commit_ids = {}  # 所有增加了desc的commit信息 ： {commit_index:CommitType}
    commit_ids_2 = {}  # 根据api名筛选
    commit_ids_3 = {}  # 根据line_id 筛选

    for index in range(commit_index, len(commit)):
        commit_id = commit.loc[index]['id']
        # if commit_id != '7b80bb7b793a70676f2a232ec484ea618fc8ad78':
        #     continue
        diff = commit.loc[index]['diff']
        commitType = CommitType(diff)
        commitType.set_commit_type(sig, desc, file_path)
        if len(commitType.commit_type) != 0:
            commit_ids[index] = commitType

    if len(commit_ids) == 0:
        return '', '', len(commit) - 1

    elif len(commit_ids) == 1:
        key = list(commit_ids.keys())[0]
        return commit_ids[key].commit_type, commit_ids[key].delete_sent, key

    # 有两个id及以上都增加了desc，则筛选出一个
    else:
        for key in commit_ids.keys():
            for line_id in line_ids:
                if commit.loc[key]['id'] == line_id:
                    commit_ids_2[key] = commit_ids[key]
                    break

        if len(commit_ids_2) == 1:
            key = list(commit_ids_2.keys())[0]
            return commit_ids_2[key].commit_type, commit_ids_2[key].delete_sent, key

        # 根据line_ids
        elif len(commit_ids_2) > 1:
            snippets = [value.diff_snippet for value in commit_ids_2.values()]
            snippets_dic = CommitType.get_api_snippets(snippets, sig)
            for key in snippets_dic:
                commit_ids_key = list(commit_ids_2.keys())[key]
                commit_ids_3[commit_ids_key] = commit_ids_2[commit_ids_key]
        else:
            snippets = [value.diff_snippet for value in commit_ids.values()]
            snippets_dic = CommitType.get_api_snippets(snippets, sig)
            for key in snippets_dic:
                commit_ids_key = list(commit_ids.keys())[key]
                commit_ids_3[commit_ids_key] = commit_ids[commit_ids_key]
        # snippets = [value.diff_snippet for value in commit_ids.values()]
        #
        # # 根据api名
        # snippets_dic = CommitType.get_api_snippets(snippets, sig)
        # for key in snippets_dic:
        #     commit_ids_key = list(commit_ids.keys())[key]
        #     commit_ids_2[commit_ids_key] = commit_ids[commit_ids_key]
        #
        # if len(commit_ids_2) == 1:
        #     key = list(commit_ids_2.keys())[0]
        #     return commit_ids_2[key].commit_type, commit_ids_2[key].delete_sent, key
        #
        # # 根据line_ids
        # elif len(commit_ids_2) > 1:
        #     for key in commit_ids_2.keys():
        #         for line_id in line_ids:
        #             if commit.loc[key]['id'] == line_id:
        #                 commit_ids_3[key] = commit_ids_2[key]
        #                 break
        # else:
        #     for key in commit_ids.keys():
        #         for line_id in line_ids:
        #             if commit.loc[key]['id'] == line_id:
        #                 commit_ids_3[key] = commit_ids[key]
        #                 break
        if len(commit_ids_3) > 0:
            key = list(commit_ids_3.keys())[0]
            return commit_ids_3[key].commit_type, commit_ids_3[key].delete_sent, key
        elif len(commit_ids_2) > 0:
            key = list(commit_ids_2.keys())[0]
            return commit_ids_2[key].commit_type, commit_ids_2[key].delete_sent, key
        else:
            key = list(commit_ids.keys())[0]
            return commit_ids[key].commit_type, commit_ids[key].delete_sent, key


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
    df = pd.read_csv(file_path, encoding='utf-8', dtype={'format_desc': str, 'line_no': int, 'line_star': int, 'line_end': int})  # ISO-8859-1
    return df


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
    path = 'D:\\MyDocument\\performance\\git_log\\commit\\docstring_commits_unique2.csv'
    clone_path = 'D:\\MyDocument\\performance\\clone'
    save_path = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\doctring_evol\\docstring_evol3.csv'
    caveat = reade_csv(path)
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    pf = main(caveat, clone_path, kws)
    pf.to_csv(save_path, encoding='utf_8_sig')
