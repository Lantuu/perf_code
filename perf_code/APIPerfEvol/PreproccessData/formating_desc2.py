import csv

import pandas
import pandas as pd
import nltk
import re
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

punkt_param = PunktParameters()
abbreviation = ['i.e', 'e.g']
punkt_param.abbrev_types = set(abbreviation)
tokenizer = PunktSentenceTokenizer(punkt_param)


def reade_csv(file_path):
    """
    读取csv文件
    :param file_path: str
    :return:
    """
    df = pd.read_csv(file_path, encoding='utf-8', dtype={'lineno': int})
    return df


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


def main(caveat, root_path):

    df = pandas.DataFrame()
    one_line_desc_list = []
    format_desc_list = []
    line_start_list = []
    line_end_list = []
    data = {'one_line_desc': '', 'format_desc': '', 'line_start': '', 'line_end': ''}
    for row in range(len(caveat)):
        # if row != 126:
        #     continue
        project = caveat['project'][row]
        sub_path = caveat['filepath'][row]
        line_no = caveat['lineno'][row]
        desc = get_sen_desc(caveat['docstring'][row])

        project_path = root_path + '\\' + project
        file_path = project_path + '\\' + sub_path.replace('/', '\\')

        if caveat['commit'][row] == 'no':
            one_line_desc_list.append('no')
            format_desc_list.append('no')
            line_start_list.append('no')
            line_end_list.append('no')
            df = df.append(data, ignore_index=True)
            continue

        if file_path.endswith('ipynb'):
            one_line_desc = desc
            format_desc = get_ipynb_desc(desc, line_no, file_path)
            line_start = line_end = line_no
        else:
            one_line_desc = get_one_line_desc(desc, line_no, file_path)
            print("###################################################")
            print(one_line_desc)

            format_desc, line_start, line_end = get_format_desc(one_line_desc, line_no, file_path)
            print('')
            print(format_desc)
        one_line_desc_list.append(one_line_desc)
        if format_desc.startswith('-') or format_desc.startswith('+'):
            format_desc_list.append(' ' + format_desc)
        else:
            format_desc_list.append(format_desc)
        line_start_list.append(line_start)
        line_end_list.append(line_end)
        # data['one_line_desc'] = one_line_desc
        # data['format_desc'] = format_desc
        # data['line_start'] = str(line_start)
        # data['line_end'] = str(line_end)
        # df = df.append(data, ignore_index=True)

    caveat['one_line_desc'] = one_line_desc_list
    caveat['format_desc'] = format_desc_list
    caveat['line_start'] = line_start_list
    caveat['line_end'] = line_end_list
    return caveat


def get_ipynb_desc(desc, line_no, file_path):
    lines = read_txt(file_path)
    line = lines[line_no - 1]
    sens = token_sent(line)
    lines_desc = desc.split('\n')

    format_desc = ""
    for sen in sens:
        for d in lines_desc:
            if sen.find(d) != -1:
                format_desc = sen
                break
        if len(format_desc) != 0:
            break
    return format_desc


def get_sen_desc(desc):
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    sens = token_sent(desc)

    if len(sens) == 1:
        return desc

    for sen in sens:
        sen = sen
        for kw in kws:
            if sen.lower().find(kw) != -1:
                desc = sen
    return desc


def get_format_desc(line_desc, line_no, file_path):
    # line_no = int(line_no)
    format_desc = line_desc.strip()
    lines = read_txt(file_path)
    line = lines[line_no - 1]
    line_desc = line_desc.strip()
    sens = token_sent(line.strip())
    sent_count = len(sens)
    order_line_desc = -1
    line_start = line_no
    line_end = line_no

    for sen in sens:
        order_line_desc = order_line_desc + 1
        sen = sen.strip()
        if sen == line_desc:
            break

    if order_line_desc == 0 and sent_count > 1:
        fw, forward_line = forward(line_no, file_path, line_desc)
        if len(fw) > 0:
            format_desc = fw + format_desc
            format_desc = token_sent(format_desc)[-1]
            line_start = line_start - forward_line

    elif order_line_desc == 0 and sent_count == 1:
        fw, forward_line = forward(line_no, file_path, line_desc)
        bk, back_line = back(line_no, file_path, line_desc)
        if len(fw) > 0:
            format_desc = fw + format_desc
            format_desc = token_sent(format_desc)[-1]
            line_start = line_start - forward_line
        if len(bk) > 0:
            format_desc = format_desc + bk
            format_desc = token_sent(format_desc)[0]
            line_end = line_end + back_line

    elif order_line_desc == sent_count - 1:
        bk, back_line = back(line_no, file_path, line_desc)
        if len(bk) > 0:
            format_desc = format_desc + bk
            format_desc = token_sent(format_desc)[0]
            line_end = line_end + back_line

    return format_desc, line_start, line_end


def back(line_no, file_path, line_desc):

    format_desc = ''
    lines = read_txt(file_path)
    line_desc = line_desc.strip()
    back_line = 0

    if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(line_desc).strip()):
        return format_desc, back_line

    while line_no < len(lines):

        line_no = line_no + 1
        if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(format_desc).strip()):
            return format_desc, back_line

        line = lines[line_no - 1]

        if line == '\n':
            break

        if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(line).strip()):  # |\S+:^[A-Z]|
            break

        else:
            sens = token_sent(line)
            format_desc = format_desc + ' ' + sens[0].strip()  # .replace('\\n', '\n')
            back_line = back_line + 1
            if len(sens) > 1:
                break
            else:
                continue

    if len(format_desc.strip()) > 0:
        format_desc = format_desc  # [1:]  # 去掉头部的换行符

    return format_desc, back_line


def forward(line_no, file_path, line_desc):

    format_desc = ''
    lines = read_txt(file_path)
    forward_line = 0

    if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(line_desc).strip()):  # |\S+:^[A-Z]|
        return format_desc, forward_line

    while line_no > 0:

        line_no = line_no - 1
        if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\w+ *:|/\*', str(format_desc).strip()):  # |\S+:^[A-Z]|
            return format_desc, forward_line

        line = lines[line_no - 1]
        if line == '\n':
            break

        if re.match(r'.*\.$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===|.*\*/$', str(line).strip()):
            return format_desc, forward_line
        sens = token_sent(line)
        format_desc = sens[-1].strip() + ' ' + format_desc  # .replace('\\n', '\n')
        forward_line = forward_line + 1
        if len(sens) > 1:
            break
        else:
            continue
    return format_desc, forward_line


def get_one_line_desc(desc, line_no, file_path):
    one_line_desc = ''
    lines = read_txt(file_path)

    line = lines[line_no - 1]
    descs = desc.strip().split('\n')
    line_sens = token_sent(line.strip())
    for line_sen in line_sens:
        line_sen = line_sen
        for desc_line in descs:
            if line_sen.lower().find(desc_line.lower().strip()) != -1:
                one_line_desc = line_sen
                break
        if len(one_line_desc) != 0:
            break

    if len(one_line_desc) == 0:
        raise SystemExit('ERROR GET ONE LINE DESC! ', file_path, line_no)
        # print("\033[0;32;40mERROR GET ONE LINE DESC!\033[0m")

    return one_line_desc


def get_sub_desc(line, sub_desc):
    result = ''
    sens = token_sent(line)
    for sen in sens:
        if sen.lower().find(sub_desc.lower()) != -1:
            result = sen
    return result


def save_csv(save_path, save_data1, save_data2):
    with open(save_path, 'a+', encoding='utf_8_sig', newline="") as f:
        writer = csv.writer(f)
        for i in range(len(save_data1)):
            writer.writerow([save_data1[i], save_data2[i]])


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


if __name__ == "__main__":
    file_path = 'D:\\MyDocument\\performance\\git_log\\commit\\docstring_commits_desc.csv'
    save_path = 'D:\\MyDocument\\performance\\git_log\\commit\\docstring_commits_unique2.csv'
    root_path = 'D:\\MyDocument\\performance\\download'
    caveat = reade_csv(file_path)
    data = main(caveat, root_path)
    pandas.DataFrame.to_csv(data, save_path, encoding='utf_8_sig')
