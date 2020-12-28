import pandas as pd
import os
from APIPerfEvol.PredictEvolType.SplitLog import SplitLog


def reade_csv(file_path):
    """
    读取csv文件
    :param file_path: str
    :return:
    """
    df = pd.read_csv(file_path, encoding='utf-8',
                     dtype={'format_desc': str, 'id': int})
    return df


def read_txt(file_path):
    """
    读txt文件
    :param file_path: str, txt文件路径
    :return: list, 返回txt所有行
    """
    f = open(file_path, 'r', encoding='utf-8', errors='ignore')
    lines = f.readlines()
    f.close()
    return lines


def get_change(format_commit_path, correct_commit_path, save_path, repo_root):
    git_command = "git -C {} log -p -u -L {},{}:{}> {}"
    correct_commit = reade_csv(correct_commit_path)
    format_commit = reade_csv(format_commit_path)
    for index, row in format_commit.iterrows():

        commit_ids = correct_commit.loc[(correct_commit['id'] == index) &
                                        (correct_commit['type'] == 'alter')]['commit_id']
        descs = correct_commit.loc[(correct_commit['id'] == index) & (correct_commit['type'] == 'alter')]['desc']

        if len(commit_ids) == 0:
            continue

        repo_path = repo_root + "\\" + row['project']
        file_path = repo_path + "\\" + row['filepath'].replace('/', '\\')
        line_start = int(row['line_start'])
        line_end = int(row['line_end'])
        temp_path = os.path.abspath(os.path.join(os.getcwd(), "..\\TempFile\\tem_log.txt"))
        git_command = git_command.format(repo_path, line_start, line_end, file_path, temp_path)
        os.system(git_command)
        lines_txt = read_txt(temp_path)
        commit_log = SplitLog.split_log(lines_txt)

        for i, commit_id in commit_ids.items():
            print(commit_id, " : ", descs.loc[i])


if __name__ == '__main__':
    format_commit_path = "D:\\MyDocument\\performance\\git_log\\commit\\format_commit\\docstring_commits.csv"
    correct_commit_path = "D:\\MyDocument\\performance\\git_log\\commit\\correct_commit\\docstring_correct.csv"
    save_path = "D:\\MyDocument\\performance\\git_log\\EvolutionNote\\preproccess\\docstring_commits.csv"
    repo_root = "D:\\MyDocument\\performance\\clone"
    get_change(format_commit_path, correct_commit_path, save_path, repo_root)
