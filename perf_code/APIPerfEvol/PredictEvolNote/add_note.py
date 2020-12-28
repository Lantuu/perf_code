import os
import re

import pandas as pd
import ast

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)

GIT_LOG_DEF = r'git -C {} log -L:{}:{}> {}'
GIT_FIlE_CHANGE_LOG = r'git -C {} log --stat {} {}> {}'


def get_alter_apiname(add, delete, current_apiname):
    add_apis_name = []
    delete_apis_name = []
    for line in add:
        add_apis_name.extend(re.findall('\'\w+\'', line))
    for line in delete:
        delete_apis_name.extend(re.findall('\'\w+\'', line))
    add_apis_name = [api[1:-1] for api in add_apis_name]
    delete_apis_name = [api[1:-1] for api in delete_apis_name]
    if current_apiname in add_apis_name:
        same_api = [api for api in delete_apis_name if api in add_apis_name]
        if len(same_api) > 0:
            delete_index = delete_apis_name.index(same_api[0]) - add_apis_name.index(same_api[0]) + add_apis_name.index(current_apiname)
            if delete_index < len(delete_apis_name) and delete_apis_name[delete_index] not in same_api:
                current_apiname = delete_apis_name[delete_index]
    return current_apiname


def get_def_evol(repo_path, file_path, api_name):
    df_apiname_evol = pd.DataFrame()
    dic_api_name_evol = {'api_name':api_name, 'id': '', 'name_before': '', 'name_after': ''}
    temp_path = os.getcwd() + '\\def_evol' + '.txt'
    comm = GIT_LOG_DEF.format(repo_path, api_name, file_path, temp_path)
    os.system(comm)
    with open(temp_path, 'r',encoding='utf-8') as f:
        lines = f.readlines()
    log = split_log(lines)
    current_api = api_name
    for index, row in log.iterrows():
        diff = row['diff']
        dic_api_name_evol['id'] = row['id']
        dic_api_name_evol['name_before'] = current_api
        add = []
        delete = []

        for line in diff:
            if line.startswith('+'):
                add.append(line[1:])
            elif line.startswith('-'):
                delete.append(line[1:])

        if len(diff) > 1 and re.match('__all__ = \[', diff[1][1:]):
            current_api = get_alter_apiname(add, delete, current_api)
            dic_api_name_evol['name_after'] = current_api
            df_apiname_evol = df_apiname_evol.append(dic_api_name_evol, ignore_index=True)
            continue

        renamed = False

        for line in add:
            if re.match('[ \t]*(def) '+api_name+'[:\(]', line):
                renamed = True
                api_type = 'def'
                break
            elif re.match('[ \t]*(class) '+api_name+'[:\(]', line):
                renamed = True
                api_type = 'class'
                break

        if renamed:
            for line in delete:
                if re.match('[ \t]*'+api_type+' '+'(\w+)[:\(]', line):
                    current_api = re.match('[ \t]*'+api_type+' '+'(\w+)[:\(]', line).group(1)
                    break

        dic_api_name_evol['name_after'] = current_api
        df_apiname_evol = df_apiname_evol.append(dic_api_name_evol, ignore_index=True)

    return df_apiname_evol


def reade_csv(file_path):
    """
    读取csv文件
    :param file_path: str
    :return:
    """
    df = pd.read_csv(file_path, encoding='utf_8_sig')
    # data = df.loc[df['type'] == 'add', ['commit_id', 'sig', 'path', 'desc', 'line_no', 'project']]
    return df


def get_file_list(repo_path, commit_id, sig):
    temp_path = os.getcwd() + '\\' + 'newfile.txt'
    comm = 'git -C ' + repo_path + ' log -1 --name-only ' + commit_id + ' > ' + temp_path
    os.system(comm)
    files = []
    file_list = []

    with open(temp_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    for i in range(len(lines) - 1, -1, -1):
        if len(lines[i].strip()) == 0:
            break
        elif re.search(r'.*/.*\.', lines[i].strip()):
            files.append(lines[i].strip())

    for file in files:
        # for api in sig:
        #     field_name = file.split('/')[-1].split('.')[0]
        if file.endswith('.py'): # and api.find(field_name) != -1:
            file_list.append(file)
    return file_list


def get_files_diff(repo_path, commit_id, file_list):
    GIT_ID_LOG = r'git -C {} log -p -u -1 {} {}> {}'
    temp_path = os.getcwd() + '\\tem_log2' + '.txt'
    files_diff = pd.DataFrame()
    for file in file_list:
        file_path = repo_path
        for file_name in file.split('/'):
            file_path = file_path + '\\' + file_name
        comm = GIT_ID_LOG.format(repo_path, commit_id, file_path, temp_path)
        os.system(comm)
        with open(temp_path, 'r', encoding='utf_8_sig',  errors='ignore') as f:
            lines = f.readlines()
        df = split_log(lines)
        files_diff = files_diff.append(df, ignore_index=True)
    return files_diff


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


def is_add_api(string_list, apis_name):

    is_contain = False
    for line in string_list:
        for api_name in apis_name:
            if re.match('[ \t]*(def|class) '+api_name+'[:\(]', line):
                is_contain = True
                return is_contain
    return is_contain


def get_commit_note(files_diff, sig, repo_path, file_path, commit_id):
    note = 'later added'
    apis_name = []
    before_name = []
    after_name = []
    for api in sig:
        api_name = re.search('\w+', api.split('.')[-1].strip()).group()
        if api_name == '__init__':
            apis_name.append(api_name)
        else:
            apis_name.append(api_name)
    apis_name = list(set(apis_name))

    for i in range(len(apis_name)):
        after = apis_name[i]
        before = apis_name[i]
        df = get_def_evol(repo_path, file_path, apis_name[i])
        print(df)
        for index, row in df.iterrows():
            if row['id'] == commit_id:
                after = row['name_after']
                before = row['name_before']
                break
        before_name.append(before)
        after_name.append(after)

    for index, row in files_diff.iterrows():
        # print(files_diff)
        diff = row['diff']
        add = []
        delete = []
        for line in diff:
            if line.startswith('+'):
                add.append(line[1:])
            elif line.startswith('-'):
                delete.append(line[1:])
        if is_add_api(add, after_name) and not is_add_api(delete, before_name):
            note = 'added together with def'
            break

    return note


def main(data, root_path):
    # comm = 'git -C ' + repo_path + ' log -1 --name-only ' + id + ' > ' + temp_path
    note_list = []
    for index, row in data.iterrows():
        if index != 923:
            continue
        commit_type = row['type']
        if commit_type != 'add':
            note_list.append('')
            continue
        sig = ast.literal_eval(row['sigs'])
        commit_id = row['id']
        file_path = row['path']
        project = row['project']
        repo_path = root_path + '\\' + project

        file_list = []
        if file_path.endswith('.py'):
            file_list.append(file_path)
        else:
            file_list = get_file_list(repo_path, commit_id, sig)
        files_diff = get_files_diff(repo_path, commit_id, file_list)

        # apis_name = []
        # for api in sig:
        #     api_name = re.search('\w+', api.split('.')[-1].strip()).group()
        #     if api_name == '__init__':
        #         apis_name.append(api_name)
        #     else:
        #         apis_name.append(api_name)
        # apis_name = list(set(apis_name))
        # # apiname_evol = pd.DataFrame()
        # alter_api = []
        # for api in apis_name:
        #     apiname_evol = get_def_evol(repo_path, file_path, api)
        #     alter_api.extend(apiname_evol['api'][apiname_evol['id'] == commit_id])
        note = get_commit_note(files_diff, sig, repo_path, file_path, commit_id)
        print(index, ": ", note)
        note_list.append(note)
    data['note_predict'] = note_list
    return data


if __name__ == '__main__':
    root_path = 'D:\\MyDocument\\performance\\clone'
    file_path = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\doctring_evol\\docstring_commits_correct_note.csv'
    save_path = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\doctring_evol\\docstring_commits_correct_note2.csv'
    data = reade_csv(file_path)
    # pd.DataFrame.to_csv(data, save_path)
    save_data = main(data, root_path)
    pd.DataFrame.to_csv(save_data, save_path, encoding='utf_8_sig')

