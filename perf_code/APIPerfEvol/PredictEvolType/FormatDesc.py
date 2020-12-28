import re

from nltk.tokenize.punkt import PunktParameters, PunktSentenceTokenizer

punkt_param = PunktParameters()
abbreviation = ['i.e', 'e.g']
punkt_param.abbrev_types = set(abbreviation)
tokenizer = PunktSentenceTokenizer(punkt_param)


class FormatDesc:

    def __init__(self):
        self.line_forward = 0  # 向前的行数
        self.line_back = 0  # 向后的行数
        self.desc = ""  # 完整的句子
        self.back_desc = ""  # 向后的填补的字符串
        self.forward_desc = ""  # 向前的填补的字符串

    def format_desc(self, line_desc, line_desc_index, lines):
        """
        根据line_desc的值，在lines中找到它的上下文，使其变成一个完整的句子
        :param line_desc: 字符串
        :param line_desc_index: 整型
        :param lines: 字符串列表
        :return: 字符串 含有line_desc上下文的完整句子
        """
        line_desc = line_desc.strip()
        self.desc = line_desc.strip()
        line = lines[line_desc_index]
        sens = FormatDesc.token_sent(line)
        sent_count = len(sens)  # line中含有句子的数量
        order_line_desc = -1  # line_desc 在line子句中的定位

        for sen in sens:
            order_line_desc = order_line_desc + 1
            if sen == line_desc:
                break

        # line_desc 在line的头部， line中含有大于1句子数量，则只需要添加line_desc的上文
        if order_line_desc == 0 and sent_count > 1:
            self.forward(line_desc_index, lines, line_desc)

        # line_desc 在line的头部， line中只有1个句子，则需要添加line_desc的上文和下文
        elif order_line_desc == 0 and sent_count == 1:
            self.forward(line_desc_index, lines, line_desc)
            self.back(line_desc_index, lines, line_desc)

        # line_desc 在line的尾部， line中含有大于1句子数量，则只需要添加line_desc的下文
        elif order_line_desc == sent_count - 1:
            self.back(line_desc_index, lines, line_desc)

        self.desc = self.forward_desc + self.desc
        self.desc = FormatDesc.token_sent(self.desc)[-1]
        self.desc = self.desc + self.back_desc
        self.desc = FormatDesc.token_sent(self.desc)[0]

    def back(self, line_index, lines, line_desc):
        """
        向后遍历，补充line_desc,使其变成一个完整的句子
        :param line_index: line_desc 在lines的定位
        :param lines:
        :param line_desc: 不完整的句子
        :return: 让line_desc变成一个完整的句子所缺的后面一部分字符串
        """

        line_desc = line_desc.strip()

        # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
        if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(line_desc).strip()):
            return

        while line_index < len(lines) - 1:

            # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
            if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(self.back_desc).strip()):
                break

            line_index = line_index + 1  # 下一行
            line = lines[line_index]

            if len(line.strip()) == 0:
                break

            # 如果下一行是以'大写字母','*',"'''",'#','-','"""'开始的，则表明该行是一个新句子的开头，直接返回  ^[A-Z]|
            if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(line).strip()):  # |\S+:^[A-Z]|
                break

            # 加上所有的子句，返回
            sens = FormatDesc.token_sent(line)
            self.back_desc = self.back_desc + ' ' + sens[0].strip()  # .replace('\\n', '\n')
            self.line_back = self.line_back + 1
            if len(sens) > 1:
                break
            else:
                continue

    def forward(self, line_index, lines, line_desc):
        """
        向前遍历，补充line_desc,使其变成一个完整的句子
        :param line_index: line_desc 在lines的定位
        :param lines:
        :param line_desc: 不完整的句子
        :return: 让line_desc变成一个完整的句子所缺的前面一部分字符串
        """

        # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回   ^[A-Z]|
        if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(line_desc).strip()):  # |\S+:^[A-Z]|
            return

        first_word = str(line_desc).strip().split(" ")[0]
        if re.match("[A-Z][a-z]{" + str(len(first_word)-1) + "}", first_word):
            return

        while line_index > 0:

            # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回    ^[A-Z]|
            if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(self.forward_desc).strip()):  # |\S+: ^[A-Z]|
                break

            first_word = str(self.forward_desc).strip().split(" ")[0]
            if re.match("[A-Z][a-z]{" + str(len(first_word) - 1) + "}", first_word):
                return
            # 上一行
            line_index = line_index - 1
            line = lines[line_index]

            if len(line.strip()) == 0:
                break

            # 如果上一行是以'.',':',"'''",'!','?','"""'结尾的，则表明行是一个新句子的尾部，直接返回
            if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(line).strip()):
                break

            # 加上所有的子句，返回
            sens = FormatDesc.token_sent(line)
            self.forward_desc = sens[-1].strip() + ' ' + self.forward_desc  # .replace('\\n', '\n')
            self.line_forward = self.line_forward + 1
            if len(sens) > 1:
                break
            else:
                continue

    @staticmethod
    def token_sent(str):
        """
        分句
        :param str:
        :return:
        """
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
