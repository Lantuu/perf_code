import csv
import os

# GIT_LOG = r'git -C {} log -p -u -L {},{}:{}> {}'
import re

import pandas

GIT_LOG2 = r'git -C {} log -p -u -L {},{}:{}> {}'
GIT_LOG = r'git -C {} log -p -u {}> {}'
GIT_Checkout = r'git -C {} checkout {}'
# GIT_LOG2 = r'git -C {} log -p {}> {}'
# GIT_LOG1=r'git -C {} checkout tags/{}'
GIT_ID_LOG = r'git -C {} log -p -u {} {}> {}'
version = {'pandas': 'v0.24.2', 'numpy': 'v1.16.4', 'scipy': 'v1.2.1', 'scikit-learn': '0.21.2', 'tensorflow': 'r1.13', 'gensim': '3.7.3'}


def exec_comm(commond,temp_path):
    os.system(commond)
    commit_id =[]
    with open(temp_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    for log in lines:
        if re.match(r'commit', log):  # lines[i].startswith('commit'):
            commit_id.append(log.split(' ')[-1].strip())
    return commit_id


def get_commit_id_log(common, id, file_path):
    commit_log = []
    os.system(common)
    with open(file_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    tag = False
    for line in lines:
        if re.match('commit ' + id, line):
            tag = True
        elif re.match('commit ', line) and tag:
            break
        if tag:
            commit_log.append(line)
    return commit_log


def main():
    repo_path = 'D:\\MyDocument\\performance\\clone\\scipy'
    file_path = 'D:\\MyDocument\\performance\\clone\\scipy\\scipy\\sparse\\linalg\\eigen\\arpack\\arpack.py'
    # log = exec_git(file_path, repo_path)
    # commit_id = parse_log(log)
    temp_path = os.getcwd() + '\\new' + '.txt'
    temp_file = open(temp_path, 'w')
    temp_file.close()
    git_log_command = GIT_LOG2.format(repo_path, 1, 1, file_path,  temp_path)
    id = '1d32d4cdb84f6044496b4c1f6f9853da1369a31f'
    git_log_command2 = GIT_ID_LOG.format(repo_path, id, file_path,temp_path)
    # s = ['52263a60f426aab9441243892d8f7fbe9eb1b8cb','e9d6673c6ec10543bf377b9d89ddbf5439907ae0','882c346abd48353c4f8e0929c3687b490f157374','e777fa7b28bef44cb7452056fbebeca78bfd30c0','fb123ed24b15000bbcd703be035c06c7327e07c2']
    # # for i in range(len(commit_id)):
    # #     for id in s:
    # #         if commit_id[i] == id:
    # #             print(id,': ',i)
    # os.system(git_log_command2)
    # commit_id = exec_comm(git_log_command2, temp_path)
    # for id in commit_id:
    #     print(id)
    log = get_commit_id_log(git_log_command2, id, temp_path)
    for i in log:
        print(i)


def rreplace(self, old, new, *max):
    count = len(self)
    if max and str(max[0]).isdigit():
        count = max[0]
    while count:
        index = self.rfind(old)
        if index >= 0:
            chunk = self.rpartition(old)
            self = chunk[0] + new + chunk[2]
        count -= 1
    return self

def right_replace(string, old, new, max=1):
    return string[::-1].replace(old[::-1], '', max)[::-1]

if __name__ == '__main__':
    # main()
    #pandas.select_multiple
    str = '    def select_as_multiple(self, keys, where=None, selector=None, columns=None,'
    if re.match('[ \t]*(def|class) (\w+)\(', str):
        current_api = re.match('[ \t]*(def|class) (\w+)\(', str).group(2)
        print(current_api)


