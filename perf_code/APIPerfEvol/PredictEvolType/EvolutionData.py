import re

import nltk

from APIPerfEvol.PredictEvolType.SplitLog import SplitLog
from APIPerfEvol.PredictEvolType.FormatDesc import FormatDesc


class EvolutionData:

    def __init__(self):
        self.evol_type = ''  # 变更的类型
        self.delete_sent = ''  # 变更之前的句子
        self.evol_snippet = []  # 变更所处的代码片段  @@...@@

    def pase_evol(self, sig, desc, file_path, diff):
        """
        :param sig:  list, api
        :param desc:
        :param file_path:
        :param diff: 一个commit_id 对应一个diff
        :return:
        """
        evol_type_list = []
        delete_sent_list = []
        evol_snippet_list = []

        # 分段，并遍历所有的 @@...@@
        evol_snippets = SplitLog.split_diff(diff)
        for evol_snippet in evol_snippets:
            diff_dic = SplitLog.classify_sens(evol_snippet)
            add = diff_dic['add']  # 所有 "+" 行
            delete = diff_dic['delete']  # 所有 "-" 行
            add_space = diff_dic['add_space']   # 所有 "+" 行 和 “+” 行的上下行
            delete_space = diff_dic['delete_space']

            # ' +/- '行中，含有的desc公共子序列
            add_common_sent = self.get_common_sent(add, desc, add_space)
            delete_common_sent = self.get_common_sent(delete, desc, delete_space)

            if add_common_sent == delete_common_sent:
                continue

            elif len(add_common_sent) != 0:

                # 修改之前的句子，和最长公共字串
                delete_sent, lc_substr = self.get_delete_sent(desc, delete, delete_space, file_path)

                if desc.lstrip() != add_common_sent.lstrip():
                    evol_type = 'alter'

                elif len(delete_sent) != 0:

                    # 最长公共字串含有的word 数量
                    lc_subword = nltk.word_tokenize(lc_substr)
                    lc_subword2 = []
                    for i in range(len(lc_subword)):
                        if len(re.sub(r'[\W0-9]', '', lc_subword[i])) != 0:
                            lc_subword2.append(lc_subword[i])

                    # 编辑距离
                    ls = EvolutionData.levenshtein(delete_sent.encode('utf-8').decode('unicode-escape'),
                                     desc.encode('utf-8').decode('unicode-escape'))

                    # 相似条件 编辑距离<=0.58 最长公共字串含有的word 数量>=4
                    lenven = ls/len(desc)
                    if ls/len(desc) <= 0.58 or len(lc_subword2) >= 4:
                        evol_type = 'alter'

                    else:
                        delete_sent = ''
                        evol_type = 'add'
                else:
                    evol_type = 'add'

                # 没有删除句子，只是在句子原来的基础上，添加了一些，Example:
                #    A is a API
                # +  ,and it is very fast.
                if evol_type == 'alter' and delete_sent == '':
                    if add_common_sent + ' ' in desc:
                        delete_sent = desc.replace(add_common_sent + ' ', '')
                    elif ' ' + add_common_sent in desc:
                        delete_sent = desc.replace(' ' + add_common_sent, '')
                    else:
                        delete_sent = desc.replace(add_common_sent, '')

                # 把所有满足条件的都加入列表
                evol_type_list.append(evol_type)
                delete_sent_list.append(delete_sent)
                evol_snippet_list.append(evol_snippet)

        if len(evol_type_list) == 1:
            self.evol_type = evol_type_list[0]
            self.delete_sent = delete_sent_list[0]
            self.evol_snippet = evol_snippet_list[0]

        # 有大于1个diff snippet 添加了desc， 则选出一个 优先选择改动的函数为sig中的
        elif len(evol_type_list) > 1:
            api_snippets_index = self.get_api_snippet_index(evol_snippet_list, sig)
            if len(api_snippets_index) != 0:
                api_snippet_index = api_snippets_index[0]
                self.evol_type = evol_type_list[api_snippet_index]
                self.delete_sent = delete_sent_list[api_snippet_index]
                self.evol_snippet = evol_snippet_list[api_snippet_index]
            else:
                self.evol_type = evol_type_list[0]
                self.delete_sent = delete_sent_list[0]
                self.evol_snippet = evol_snippet_list[0]

    @staticmethod
    def get_common_sent(alter_list, desc, blank_list):

        # 去每一行前面的"+/-"
        blank_lines = [line[1:].strip() for line in blank_list]
        alter_lines = [line[1:].strip() for line in alter_list]

        common_sen = ''  # 添加/删除的 desc公共子串
        alter_index = -1  # 行在alter_lines的索引

        # 找到开始添加desc的行号，从desc的头部开始找
        while alter_index < len(alter_lines) - 1 and common_sen == "":
            alter_index = alter_index + 1
            line = alter_lines[alter_index]

            # 过滤一些特殊字符
            if line.strip().startswith('\"image/png\"'):
                alter_index = alter_index + 1
                continue
            if len(line) > 10000:
                alter_index = alter_index + 1
                continue

            # 分句
            line_sents = FormatDesc.token_sent(line)

            #  遍历一行中包含的所有句子
            for line_sen_index in range(len(line_sents)):
                line_sen = line_sents[line_sen_index]

                # 过滤没有单词的子句
                if re.search(r'[a-zA-Z]', line_sen.replace('\\n', '')) is None:
                    continue

                if line_sen.strip() in desc:

                    # 找到在blank中的索引下标
                    blank_index = EvolutionData.get_blank_index(alter_index, blank_list, alter_list[alter_index].strip()[0])

                    # 补全句子上下文，变成一个完整的句子
                    formatDesc = FormatDesc()
                    formatDesc.format_desc(line_sen, blank_index, blank_lines)
                    complete_sen = formatDesc.desc
                    # complete_sen = FormatDesc.format_desc(line_sen, blank_index, blank_lines)

                    # 只有当其上下文包含完整的desc时，才结束
                    if desc in complete_sen:
                        common_sen = line_sen
                        desc = desc.replace(line_sen, '')

                        # line_sen 不是此行的结尾可以直接退出
                        if line_sen_index < len(line_sents) - 1:
                            return common_sen
                        break

        # 找到添加进去的字符串， 以“+/-”开头的句子 , Example:  找到下面句子的“ + ,and B is faster.”
        #   A is a API
        # + ,and B is faster.
        # 向后匹配， 遍历alter_lines中alter_line_index后面的行，找到剩余的添加的字符串，从alter_line_index+1开始
        while alter_index < len(alter_lines) - 1:
            alter_index = alter_index + 1

            line_sens = FormatDesc.token_sent(alter_lines[alter_index])
            for sen in line_sens:
                if sen in desc:
                    common_sen = common_sen + ' ' + sen
                    desc = desc.replace(sen, '')
                else:
                    alter_index = len(alter_lines)
                    break

        return common_sen

    @staticmethod
    def get_delete_sent(desc, delete_lines, delete_space, file_path):
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
        for delete_index in range(len(delete_lines)):
            if len(delete_lines[delete_index]) > 10000:
                continue

            blank_index = EvolutionData.get_blank_index(delete_index, delete_space, '-')
            delete_sents = FormatDesc.token_sent(delete_lines[delete_index][1:])

            # 计算每个句子与desc的最长公共子序列
            for sent in delete_sents:
                if not file_path.endswith('.ipynb') and len(sent) > 0:
                    formatDesc = FormatDesc()
                    formatDesc.format_desc(sent, blank_index, lines)
                    # format_delete_sent = FormatDesc.format_desc(sent, blank_index, lines)
                    format_delete_sent = formatDesc.desc
                else:
                    format_delete_sent = sent

                format_delete_sent_ = ' '.join([i for i in format_delete_sent.strip().split(' ') if i != ''])
                desc_ = ' '.join([i for i in desc.strip().split(' ') if i != ''])
                leven = EvolutionData.levenshtein(format_delete_sent_, desc_)
                lc = len(EvolutionData.find_lcsubstr(format_delete_sent_, desc_))
                if lc > max_lc or (lc == max_lc and leven < min_leven):
                    max_lc = len(EvolutionData.find_lcsubstr(format_delete_sent_, desc_))
                    min_leven = EvolutionData.levenshtein(format_delete_sent_, desc_)
                    lc_substring = EvolutionData.find_lcsubstr(format_delete_sent_, desc_)
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
    def get_api_snippet_index(evol_snippets, sig):
        """
        :param evol_snippets: @@...@@ 片段
        :param sig:  # api
        :return: list, 含有api的snippet在evol_snippets的index
        """

        # diff_lines = []  # 所有 @@ ...@@
        api_snippets_index = []  # @@ ...@@  中含有的函数名 in sigs 则插入
        apis_name = []

        for api in sig:
            if api.split('.')[-1].strip() == '__init__':
                apis_name.append(api.split('.')[-2].strip())
            else:
                apis_name.append(api.split('.')[-1].strip())

        # 检查snippet diff中是否包含sig中的api
        for index in range(len(evol_snippets)):
            for line in evol_snippets[index]:
                if EvolutionData.re_search(apis_name, line) is not None:
                    api_snippets_index.append(index)
                    break

        return api_snippets_index

    @staticmethod
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

    @staticmethod
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

        m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
        mmax = 0  # 最长匹配的长度
        p = 0  # 最长匹配对应在s1中的最后一位
        for i in range(len(s1)):
            for j in range(len(s2)):
                if s1[i] == s2[j]:
                    m[i + 1][j + 1] = m[i][j] + 1
                    if m[i + 1][j + 1] > mmax:
                        mmax = m[i + 1][j + 1]
                        p = i + 1

        return s1[p - mmax:p]  # ,mmax   #返回最长子串及其长度

    @staticmethod
    def re_search(apis_name,str):
        for api in apis_name:
            if re.search('def ' + api + '\(|class ' + api + '\(', str):
                return True
