import re
import pandas as pd


class SplitLog:

    @staticmethod
    def classify_sens(diff):
        """
        split diff: lines：改动的行号; add: 添加的行; delete： 删除的行; add_space: 添加的行和未改动过的行; delete_space: 删除的行和未改动过的行
        :param diff: 字符串列表
        :return: 字典
        """

        diff_dic = {'lines': '', 'add': '', 'delete': '', 'add_space': '', 'delete_space': ''}
        if len(diff) == 0:
            return diff_dic
        lines = diff[0]  # 存放这种形式的内容"@@ -738,20 +738,19 @@"
        add = []  # 存放以"+"开头的行
        add_space = []  # 存放以"+"开头的行，和以空格开头的行
        delete = []  # 存放以"-"开头的行
        delete_space = []  # 存放以"-"开头的行，和以空格开头的行

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

    @staticmethod
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

    @staticmethod
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
