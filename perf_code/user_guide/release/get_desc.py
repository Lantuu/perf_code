import csv
import os
import re
import nltk


def get_file_path(repo_name, root_path):
    """
    得到repo_name中所有release文件的路径
    :param repo_name: str, 库名
    :param root_path: str, 库的根目录
    :return files_path: list, 该库的所有release文件的路径
    """
    files_path = []  # 存放该库的所有release文件的路径
    repo_path = os.path.join(root_path, repo_name)
    list_dir = os.listdir(repo_path)
    for f in list_dir:
        files_path.append(os.path.join(repo_path, f))
    return files_path


def get_desc(files_path, key_words, repo, url_root):
    """
    根据关键词匹配，含有关键词的句子
    :param files_path: list, 该库所有release文件的路径
    :param key_words: list, 匹配的关键次
    :param repo: str, 库名
    :param url_root: list, 所有库存放release文件在GitHub上的根路径
    :return repo_descs: list, [file_path, desc, line_no, kw, url, project] 返回含有关键词的句子
    """
    repo_descs = []  # repo中所有文件的数据
    for path in files_path:
        url = get_url(url_root, path, repo)
        file_path = get_path(url, repo)
        descs = []  # repo中一个文件的数据
        version = []

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(len(lines)):
            version = get_version(lines[i], path, version)
            sentences = nltk.sent_tokenize(lines[i])
            for sentence in sentences:
                kws = match_key_words(key_words, sentence)
                if len(kws) != 0:
                   descs.append([file_path, sentence, i + 1, kws, url+'#'+str(i+1), repo, version])
        repo_descs.extend(complete_desc(lines, descs))
    return repo_descs


def get_version(line, filepath, version):
    v = []
    if filepath.endswith('rst'):
        v = get_rst_version(filepath)

    elif filepath.endswith('CHANGELOG.md'):
        if re.match(r'## \d+\.\d+\.', line) is not None:
            v = get_md_version(line)

    elif filepath.endswith('RELEASE.md'):
        if line.startswith('# Release'):
            v = get_md_version(line)

    if len(v) != 0:
        return v
    else:
        return version


def get_md_version(line):
    version_list = re.findall(r'\d+\.\d+\.\d+\S*', line)
    for i in range(len(version_list)):
        if version_list[i].endswith(','):
            version_list[i] = version_list[i][:-1]
    return version_list


def get_rst_version(filename):
    version = re.findall(r'\d+.\d+\.\w*', filename)
    for i in range(len(version)):
        if version[i].endswith('.rst'):
            version[i] = version[i][:-4]
    return version


def get_url(url_root, file_path, repo):
    """
    得到文件在GitHub的链接
    :param url_root: list, 所有库存放release文件在GitHub上的根路径
    :param file_path: str, 该release文件的路径
    :param repo: str, 库名
    :return url: str, 返回该库的链接
    """
    filename = file_path.split('\\')[-1]
    url = ''
    if repo == 'sklearn':
        repo = 'scikit-learn'
    for root in url_root:
        if root.find(repo) != -1:
            url = root + '/' + filename
            break
    return url


def get_path(url, repo):
    """
    得到文件的路径
    :param url: str, 该库的链接
    :param repo: str, 库名
    :return path: str, release文件的路径
    """
    if repo == 'sklearn':
        repo = 'scikit-learn'
    path = str(repo) + str(url).split(repo)[-1]
    return path


def match_key_words(key_words, sentence):
    """
    匹配是否句子含有key_words的部分单词
    :param key_words: list, 关键词
    :param sentence: str, 句子
    :return kws: list, sentence包含的关键词
    """
    kws = []
    for kw in key_words:
        match_obj = re.search(r"(.*)" + kw + r"(.*)", sentence, re.I)
        if match_obj is not None:
            # 句子含有kw
            kws.append(kw)
    return kws


def complete_desc(lines, descs):
    """
    根据一行填充完整的句子
    :param lines: list, 读取一个release文件的所有行
    :param descs: str,
    :return descs:  list, [file_path, desc, line_no, kw, url, project] 含有关键词的完整句子
    """

    sentence_list = []  # 存放划分好的句子
    segment_list = get_segment_split(lines)  # 存放划分的段

    # 划分每一段里所包含的句子
    for segment in segment_list:
        sentence_list.extend(split_sentence(segment))

    # 遍历每一个含有关键词的desc, 填充句子
    for i in range(len(descs)):
        sentence_kw = []
        for sentence in sentence_list:  # 遍历每一个句子，含有desc则插入sentence_list
            if descs[i][1].strip() in sentence:
                sentence_kw.append(sentence)
        if len(sentence_kw) == 1:
            descs[i][1] = sentence_kw[0]
        elif len(sentence_kw) == 0:
            print('########################### ERROR 0! ##################################################')
            print(descs[i])
        else:
            print('>1  ', descs[i][1], sentence_kw)

        # 去掉以'-','*'开头的字符，防止乱码
        if descs[i][1].strip().startswith('- ') or descs[i][1].strip().startswith('* '):
            descs[i][1] = descs[i][1].strip()[1:]

        # 去掉前后空格和换行符
        descs[i][1] = descs[i][1].strip()

    return descs


def get_segment_split(data):
    """
    把data根据标签分成段
    :param data: list, 待分段的数据
    :return tem_segment_list_j:  list,  分好的段
    """
    tem_segment_list_sub = []  # 存放用 '---' 分的段
    tem_segment_list_j = []  # 存放用 '#' 分的段
    tem_segment_list_code = []  # 存放用 '```' 分的段

    #  用 '===' 分段
    tem_segment_list_equal = tag_segment_split('===', data, False)

    #  用 '---' 分段
    for segment in tem_segment_list_equal:
        tem_segment_list_sub.extend(tag_segment_split('---', segment, False))

    #  用 '```' 分段
    for segment in tem_segment_list_sub:
        tem_segment_list_code.extend(tag_segment_split('```', segment, False))

    #  用 '#' 分段
    for segment in tem_segment_list_code:
        tem_segment_list_j.extend(tag_segment_split('#', segment, True))

    return tem_segment_list_j


def tag_segment_split(tag, data, add):
    """
    根据不用的标签把data分成多个segment
    :param tag: str, 标签 '----' or '====' or '#' or '```'
    :param data: list, 待分段的数据
    :param add: boolean, 是否把带标签的那一行数据加入分段
    :return segment_list:  list,  分好的段
    """
    segment_list = []  # 存放分好的段
    tem_segment = []  # 暂时存放中间产生的段
    if not add:
        for line in data:
            if line.strip().startswith(tag) and len(tem_segment) != 0:
                segment_list.append(tem_segment)
                tem_segment = []
            elif line.strip().startswith(tag) and len(tem_segment) == 0:
                continue
            elif line.strip() == '':
                continue
            else:
                tem_segment.append(line)
        segment_list.append(tem_segment)
    if add:
        for line in data:
            if line.strip().startswith(tag) and len(tem_segment) != 0:
                segment_list.append(tem_segment)
                tem_segment = []
                tem_segment.append(line)
            elif line.strip().startswith(tag) and len(tem_segment) == 0:
                tem_segment.append(line)
            elif line.strip() == '':
                continue
            else:
                tem_segment.append(line)
        segment_list.append(tem_segment)
    return segment_list


def split_sentence(segment):
    """
    把一段数据分成一个个句子
    :param segment: list, 待分句子的段
    :return sentence_list:  list,  分好的句子
    """
    sentence_list = []  # 存放句子
    temp_sentence_sub = ''  # 存放 '- '开头的行
    temp_sentence_j = ''    # 存放 '#'开头的行
    temp_sentence_star = ''  # 存放 '*'开头的行
    text = ''  # 存放普通的行

    for line in segment:

        # 行以'- '开头，保存其他temp的句子， 更新temp变量
        if line.strip().startswith('- '):
            sentence_list.extend(save_memo(temp_sentence_j, temp_sentence_star, text, temp_sentence_sub))
            temp_sentence_j = temp_sentence_star = text = temp_sentence_sub = ''
            temp_sentence_sub = line

        # 行以'* '开头，保存其他temp的句子， 更新temp变量
        elif line.strip().startswith('* '):
            sentence_list.extend(save_memo(temp_sentence_j, temp_sentence_star, text, temp_sentence_sub))
            temp_sentence_j = temp_sentence_star = text = temp_sentence_sub = ''
            temp_sentence_star = line

        # 行以'#'开头，保存其他temp的句子， 更新temp变量
        elif line.strip().startswith('#'):
            sentence_list.extend(save_memo(temp_sentence_j, temp_sentence_star, text, temp_sentence_sub))
            temp_sentence_j = temp_sentence_star = text = temp_sentence_sub = ''
            temp_sentence_star = line

        # 行以空格开头，则如果有中间变量不为''的，则认为它们是同一段
        elif line.startswith(' '):
            if temp_sentence_j != '':
                temp_sentence_j += line
            elif temp_sentence_sub != '':
                temp_sentence_sub += line
            elif temp_sentence_star != '':
                temp_sentence_star += line
            else:
                text += line

        else:
            text += line

    # 保存最后一段的数据
    sentence_list.extend(save_memo(temp_sentence_j, temp_sentence_star, text, temp_sentence_sub))

    return sentence_list


def save_memo(tex1, tex2, tex3, tex4):
    """
    检查四个str是否有数据，有则划分为句子并保存
    :param tex1: str,  待保存的数据
    :param tex2: str,  待保存的数据
    :param tex3: str,  待保存的数据
    :param tex4: str,  待保存的数据
    :return sentence_list:  list,  分好的句子
    """
    sentence_list = []

    if tex1 != '':
        sentence_list.extend(nltk.sent_tokenize(tex1))

    if tex2 != '':
        sentence_list.extend(nltk.sent_tokenize(tex2))

    if tex3 != '':
        sentence_list.extend(nltk.sent_tokenize(tex3))

    if tex4 != '':
        sentence_list.extend(nltk.sent_tokenize(tex4))

    return sentence_list


def save_csv(csv_path, desc_list):
    """
    保存数据到.csv文件
    :param csv_path: str, 保存文件的路径
    :param desc_list: str,  待保存的数据 [file_path, desc, line_no, kw, url, project]
    """
    file = open(csv_path, 'a+', encoding='utf-8', newline='')
    writer = csv.writer(file)
    print(len(desc_list))
    for desc in desc_list:
        writer.writerow(desc)  # [file_path, desc, line_no, kw, url, project, version]
    file.close()


def main():
    """
    主函数
    """
    key_words = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']
    root_path = 'D:\\work\\performance\\release'
    save_path = 'D:\\work\\performance\\user_guide\\desc\\desc_1220.csv'
    url_root = ['https://github.com/pandas-dev/pandas/tree/v0.24.2/doc/source/whatsnew',
                'https://github.com/numpy/numpy/tree/master/doc/source/release',
                'https://github.com/scipy/scipy/tree/master/doc/release',
                'https://github.com/scikit-learn/scikit-learn/tree/master/doc/whats_new',
                'https://github.com/tensorflow/tensorflow/blob/master',
                'https://github.com/RaRe-Technologies/gensim/blob/develop/']

    repos = os.listdir(root_path)
    for repo in repos:
        files_path = get_file_path(repo, root_path)
        repo_desc_list = get_desc(files_path, key_words, repo, url_root)
        save_csv(save_path, repo_desc_list)


if __name__ == '__main__':
    main()
