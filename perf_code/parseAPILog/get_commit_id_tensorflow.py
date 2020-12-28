import re
import os
import csv
GIT_LOG = r'git -C {} log -p -u -L {},{}:{}> {}'
GIT_Checkout = r'git -C {} checkout {}'
# GIT_LOG2 = r'git -C {} log -p {}> {}'
# GIT_LOG1=r'git -C {} checkout tags/{}'

version = {'pandas': 'v0.24.2', 'numpy': 'v1.16.4', 'scipy': 'v1.2.1', 'scikit-learn': '0.21.2', 'tensorflow': 'r1.13', 'gensim': '3.7.3'}


def exec_git(line, file_path, repo_path, version='3.7.3'):
    """
    得到line在一特定版本之前的所以commit_id
    :param repo: 库名
    :param line: 行号
    :param path: 存放commit_id的地址
    :param logfile:
    :param version: 版本号
    :return: [commit_id]
    """
    temp_path = os.getcwd() + '\\new' + '.txt'
    temp_file = open(temp_path, 'w')
    temp_file.close()
    git_log_command1 = GIT_Checkout.format(repo_path, version)
    git_log_command = GIT_LOG.format(repo_path, line, line, file_path, temp_path)
    os.system(git_log_command1)
    os.system(git_log_command)
    with open(temp_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    return lines


def read_csv(file_path):
    data = []
    with open(file_path,'r', encoding='utf-8', errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[5] == '1':
                data.append(row)  # [file_path, line_no, kw, url, desc, valid, sig, knowledge]
    return data


def get_commit_id(data, root_path):
    save_data = []
    for d in data:
        line_no = d[1]
        sub_path = d[0].split('/')
        file_path = root_path
        for p in sub_path:
            file_path = file_path + '\\' + p
        git_log = exec_git(line_no, file_path, repo_path=root_path)
        commit_id = parse_log(git_log)
        if len(commit_id) == 0:
            t = []
            t.extend(d)
            save_data.append('not find')
            save_data.append(t)
        for i in range(len(commit_id) - 1, -1, -1):
            t = []
            t.extend(d)
            t.append(commit_id[i])
            save_data.append(t)
    return save_data


def parse_log(git_log):
    commit_id = []
    for log in git_log:
        if re.match(r'commit', log):  # lines[i].startswith('commit'):
            commit_id.append(log.split(' ')[-1].strip())
    return commit_id


def save_csv(save_path, save_data):
    with open(save_path, 'a+', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        for data in save_data:
            writer.writerow(data)


def main():
    data_path = 'D:\\MyDocument\\performance\\user_guide\\guide_desc\\desc_ipynb\\20.02.29\\gensim.csv'
    save_path = 'D:\\MyDocument\\performance\\git_log\\20.03.03\\gensim_ipynb_log2.csv'
    repo_path = 'D:\\MyDocument\\performance\\clone\\gensim'
    data = read_csv(data_path)
    save_data = get_commit_id(data, repo_path)
    save_csv(save_path, save_data)


if __name__ == '__main__':
    main()
