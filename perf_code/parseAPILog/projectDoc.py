import csv
import os
import re
import nltk
import nbformat


KWs = ['fast','slow','efficient','scalable','expensive','intensive','quick','rapid','performant','faster','slower','better','worse','worst','fastest','slowest',
    'performance','efficiency','speed ups','improve','slowdown','speedup', 'speed up','increase','accelerate', 'computationally']

new_kws = ['inefficient', 'inefficiency']

kw_not_complete = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive', 'scalab', 'efficien']



def get_ipynb_file_path(repoPath):
    '''得到.ipynb文件的路径'''
    ipynb_file = []
    repoPathList = os.listdir(repoPath)
    for file in repoPathList:
        newdir = os.path.join(repoPath, file)  # 将文件名加入到当前文件路径后面
        if os.path.isfile(newdir):  # 如果是文件
            if os.path.splitext(newdir)[1] == ".ipynb":  # 如果文件是".rst"后缀的
                ipynb_file.append(newdir)
        elif os.path.isdir(newdir):  # 如果是文件夹，递归其子文件夹
            subAPIfile = get_ipynb_file_path(newdir)
            for subfile in subAPIfile:
                ipynb_file.append(subfile)
    return ipynb_file


def get_rst_file_path(repoPath):
   '''得到.rst文件的路径'''
   rst_file = []
   repoPathList = os.listdir(repoPath)
   for file in repoPathList:
      newdir = os.path.join(repoPath, file)  # 将文件名加入到当前文件路径后面
      if os.path.isfile(newdir):  # 如果是文件
         if os.path.splitext(newdir)[1] == ".rst":  # 如果文件是".rst"后缀的
            rst_file.append(newdir)
      elif os.path.isdir(newdir):  # 如果是文件夹，递归其子文件夹
         subAPIfile=get_rst_file_path(newdir)
         for subfile in subAPIfile:
            rst_file.append(subfile)
   return rst_file


def get_md_file_path(repoPath):
   '''得到.md文件的路径'''
   md_file = []
   repoPathList = os.listdir(repoPath)
   for file in repoPathList:
      newdir = os.path.join(repoPath, file)  # 将文件名加入到当前文件路径后面
      if os.path.isfile(newdir):  # 如果是文件
         if os.path.splitext(newdir)[1] == ".md":  # 如果文件是".md"后缀的
            md_file.append(newdir)
      elif os.path.isdir(newdir):  # 如果是文件夹，递归其子文件夹
         subAPIfile=get_md_file_path(newdir)
         for subfile in subAPIfile:
            md_file.append(subfile)
   return md_file


def get_desc_list(pathList, KW):
    '''得到一个库中所有.rst文件的desc'''
    repo_descs_list = []  # 存储一个库中所有.rst文件的desc,all_descs_list中的每一个元素为：[desc完整的句子，desc行号，关键字，路径，desc本身]
    for path in pathList:
        one_file_descs = []  # 存储一个.rst文件的desc
        # 读取文件的内容，存放于lines中
        with open(path, 'r', encoding='UTF-8') as logfilehandler:
            lines = logfilehandler.readlines()

        # 按行遍历文件，找到含有关键字的行，存储于one_file_descs:[行,行号，关键字,路径]
        for i in range(len(lines)):
            sens = nltk.sent_tokenize(lines[i])
            for sentence in sens:
                kwList = []
                for kw in KW:
                    matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", sentence, re.I)
                    if matchobj is not None:
                        kwList.append(kw)
                if len(kwList) != 0:
                    one_file_descs.append([sentence, i+1, kwList, path, sentence])
        # 得到完整的desc句子
        # one_file_descs = get_complete_desc(lines, one_file_descs)
        one_file_descs = complete_desc(lines, one_file_descs)

        for desc in one_file_descs:
            repo_descs_list.append(desc)

    return repo_descs_list


def get_desc_from_ipynb(path_list, kw_list):
    repo_descs_list = []  # 存储一个库中所有.pynb文件的desc,all_descs_list中的每一个元素为：[desc完整的句子，关键字，路径]
    for path in path_list:
        print(path)
        # one_file_descs = []  # 存储一个.rst文件的desc
        try:
            nb = nbformat.read(path, nbformat.NO_CONVERT)
        except:
            print('\033[1;35;0m ERROR: ', path, '\033[0m')
            continue

        for cell in nb.cells:
            if cell.cell_type == 'markdown':

                str = cell.source
                str_list = nltk.sent_tokenize(str)
                kw_sentence = extract_kw_sentence_not_complete(str_list, kw_list)

            for i in range(len(kw_sentence)):
                kw_sentence[i].append(path)

            repo_descs_list.extend(kw_sentence)
            kw_sentence = []

    return repo_descs_list


def extract_kw_sentence(sentence_list, kw_list):
    kw_sentence = []
    for sentence in sentence_list:
        kwList = []
        for kw in kw_list:
            matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", sentence, re.I)
            if matchobj is not None:
                kwList.append(kw)
        if len(kwList) != 0:
            kw_sentence.append([sentence, kwList])
    return kw_sentence


def extract_kw_sentence_not_complete(sentence_list, kw_list):
    kw_sentence = []
    for sentence in sentence_list:
        kwList = []
        for kw in kw_list:
            if sentence.lower().find(kw) != -1:
                kwList.append(kw)
        if len(kwList) != 0:
            kw_sentence.append([sentence, kwList])
    return kw_sentence


def extract_new_kw_desc(desc_list, older_kw_list):
    new_desc = list()
    new_desc.extend(desc_list)
    for desc in desc_list:
        for kw in older_kw_list:
            matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", str(desc[0]), re.I)
            if matchobj is not None:
                new_desc.remove(desc)
                break
    return new_desc


def get_complete_desc(lines,desc_list):
   '''得到desc的完整句子'''
   str=''
   for line in lines:
      str=str+line+' '  # 一个文件的所有行变成字符串
   sens=nltk.sent_tokenize(str)  # 把文件分成句子列表

   for i in range(len(desc_list)):  # 遍历每一个含有关键词的desc
      sentence_list = []  # 存放所有含有关键词desc的句子
      for sen in sens:  # 遍历每一个句子，含有desc则插入sentence_list
         #if sen.find(desc_list[i][0].strip())!=-1:
         if desc_list[i][0].strip() in sen:
            sentence_list.append(sen)
      # sentence_list只有一个元素，则直接更改desc_list[i][0],即插入完整的desc句子
      if len(sentence_list)==1:
         desc_list[i][0] = sentence_list[0]
      # if len(sentence_list)>1:  # 如果有多个句子含有关键词desc
      #    print('>1')
      #    complete_desc= desc_list[i][0]  # 含有关键字的desc
      #    desc_lines=''
      #    lineno = desc_list[i][1]-1  # desc的行号-1 = 下标
      #    tag=0  # 更改行的标签
      #    sens2=[]
      #    while len(sens2)>=3 and tag==len(lines): # 可以分割成3个句子,防止死循环
      #       if lineno-tag>=0:
      #          desc_lines=insertStr(desc_lines,lines[lineno-tag])
      #       #if tag>0 and lineno+tag<len(lines):
      #       if lineno + tag < len(lines):
      #          desc_lines=desc_lines+' '+lines[lineno+tag]
      #       tag=tag+1
      #       sens2.clear()
      #       sens2 = nltk.sent_tokenize(desc_lines)
      #    p=1
      #    t=False
      #    for s in sens2:
      #       if s.find(desc_list[i][0].strip())!=-1:
      #          p=p+1
      #          for i in sentence_list:
      #             if i==s:
      #                t=True
      #          complete_desc=s
      #          break
      #    print(t)
      #    if p>1:
      #       print('########################## p! #################################################')
      #       print(p)
      #          #break
      #    if tag==len(lines):
      #       print('########################## ERROR code! #################################################')
      #    else:
      #       desc_list[i][0] = complete_desc
      if len(sentence_list)==0:
         print('########################### ERROR 0! ##################################################')
         print(desc_list[i])
      sentence_list.clear()

   return desc_list


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
         if descs[i][0].strip() in sentence:
            sentence_kw.append(sentence)
      if len(sentence_kw) == 1:
         descs[i][0] = sentence_kw[0]
      elif len(sentence_kw) == 0:
         print('########################### ERROR 0! ##################################################')
         print(descs[i])
      else:
         print('>1  ', descs[i][0], sentence_kw)

      # 去掉以'-','*'开头的字符，防止乱码
      if descs[i][0].strip().startswith('- ') or descs[i][0].strip().startswith('* '):
         descs[i][0] = descs[i][0].strip()[1:]

      # 去掉前后空格和换行符
      descs[i][0] = descs[i][0].strip()

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
   temp_sentence_j = ''  # 存放 '#'开头的行
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


def insertStr(str1, str2):
   str1_list = list(str1)
   str2 = str2 + " "
   str1_list.insert(0, str2)
   str = "".join(str1_list)
   return str


def repo_ipynb_process(repo_path, repo_url, doc_csv_root):
    ipnb_path_list = get_ipynb_file_path(repo_path)
    doc_csv = doc_csv_root + '\\' + repo_path.split('\\')[4] + '.csv'
    # kw_list = []
    # kw_list.extend(KWs)
    # kw_list.extend(new_kws)
    repo_desc_list = get_desc_from_ipynb(ipnb_path_list, kw_not_complete)  # [desc完整的句子，关键字，路径]
    file = open(doc_csv, 'w', encoding="utf-8", newline='')
    writer = csv.writer(file)
    print(len(repo_desc_list))
    for desc in repo_desc_list:
        # =get_desc_url(repo_url,desc[3])  # 不带行号的URL
        desc_url = get_desc_url(repo_url, desc[2])   # 不带行号的URL
        path = get_desc_path(desc_url)

        writer.writerow([path, desc[0], desc[1], desc[2], desc_url,])  # [dec,commitID,type,url]
    file.close()


def repo_rst_process(repo_path, repo_url, doc_csv_root):
    rst_path_list = get_rst_file_path(repo_path)
    doc_csv = doc_csv_root + '\\' + repo_path.split('\\')[4] + '.csv'
    # repo_descs_list = get_desc_list(rst_path_list, KWs)  # [desc完整的句子，desc行号，关键字，路径，desc本身]
    repo_descs_list = get_desc_list(rst_path_list, new_kws)  # [desc完整的句子，desc行号，关键字，路径，desc本身]
    repo_descs_list = extract_new_kw_desc(repo_descs_list, KWs)
    file = open(doc_csv, 'w', encoding="utf-8", newline='')
    writer = csv.writer(file)
    print(len(repo_descs_list))
    for desc in repo_descs_list:
        # =get_desc_url(repo_url,desc[3])  # 不带行号的URL
        desc_url = get_desc_url(repo_url,desc[3])+'#L'+str(desc[1])  # 代行号的URL
        path=get_desc_path(desc_url)
        # path = url.split(re.match(r'(.*)/(.*)\d(.*)\.(.*)\d/', url).group(0))[1]  # 句子在repo中的路径
        writer.writerow([path,desc[0], desc[1], desc[2],desc_url,desc[4]])  # [dec,commitID,type,url]
    file.close()


def repo_md_process(repo_path, repo_url, doc_csv_root):
    md_path_list = get_md_file_path(repo_path)
    doc_csv = doc_csv_root + '\\' + repo_path.split('\\')[3] + '.csv'
    # repo_descs_list = get_desc_list(md_path_list, KWs)  # [desc完整的句子，desc行号，关键字，路径，desc本身]
    repo_desc_list = get_desc_list(md_path_list, new_kws)  # [desc完整的句子，desc行号，关键字，路径，desc本身]
    repo_desc_list = extract_new_kw_desc(repo_desc_list, KWs)
    file = open(doc_csv, 'w', encoding="utf-8", newline='')
    writer = csv.writer(file)
    print(len(repo_desc_list))
    for desc in repo_desc_list:
        # url=get_desc_url(repo_url,desc[3])  # 不带行号的URL
        desc_url=get_desc_url(repo_url,desc[3])+'#L'+str(desc[1])  # 代行号的URL
        path = get_desc_path(desc_url)  # 句子在repo中的路径
        writer.writerow([path,desc[0], desc[1], desc[2],desc_url,desc[4]])  # [dec,desc完整的句子,行号,关键字，url]
    file.close()


def get_desc_path(desc_url):
   desc_url_list=desc_url.split('/')
   path=''
   tag=False
   for i in desc_url_list:
      s = re.search(r'\d+\.\d+', i)
      if tag:
         path = path + '/' + i
      if s is not None:
         tag =True
   path=path[1:]
   path = path.split('#')[0]
   return path


def get_desc_url(repo_url,desc_path):
    '''得到desc的url'''
    url = repo_url
    root_name = repo_url.split('/')[-1]
    desc_path_list = desc_path.split('\\')
    for i in range(len(desc_path_list)):
        if desc_path_list[i] == root_name:
            for j in range(i+1, len(desc_path_list)):
                url = url + '/' + desc_path_list[j]
            break
    return url


def all_repo_process():
    rst_repo_path_list = ['D:\\MyDocument\\performance\\download\\pandas-0.24.2\\doc\\source',
                          'D:\\MyDocument\\performance\\download\\numpy-1.16.4\\doc\\source',
                          'D:\\MyDocument\\performance\\download\\scipy-1.2.1\\doc\\source',
                          'D:\\MyDocument\\performance\\download\\scikit-learn-0.21.2\\doc',
                          'D:\\MyDocument\\performance\\download\\gensim-3.7.3\\docs\\src']
    md_repo_path_list = ['D:\\MyDocument\\performance\\download\\docs-r1.13\\site\\en']
    rst_repo_url_list = ['https://github.com/pandas-dev/pandas/tree/v0.24.2/doc/source',
                         'https://github.com/numpy/numpy/tree/v1.16.4/doc/source',
                         'https://github.com/scipy/scipy/tree/v1.2.1/doc/source',
                         'https://github.com/scikit-learn/scikit-learn/tree/0.21.2/doc',
                         'https://github.com/RaRe-Technologies/gensim/tree/3.7.3/docs/src']
    doc_csv_root = 'D:\\MyDocument\\performance\\user_guide\\guide_desc\\desc_0130'
    md_repo_url_list = ['https://github.com/tensorflow/docs/tree/r1.13/site/en']
    for i in range(len(rst_repo_path_list)):
        repo_rst_process(rst_repo_path_list[i], rst_repo_url_list[i], doc_csv_root)
    for i in range(len(md_repo_path_list)):
        repo_md_process(md_repo_path_list[i], md_repo_url_list[i], doc_csv_root)


if __name__ == '__main__':
    # repo_path = 'D:\\MyDocument\\performance\\download\\docs-r1.13\\site\\en'
    # repo_url = 'https://github.com/tensorflow/docs/tree/r1.13/site/en'


    repo_path = 'D:\\MyDocument\\performance\\download\\gensim-3.7.3\\docs'
    repo_url = 'https://github.com/RaRe-Technologies/gensim/tree/3.7.3/docs'
    doc_csv_root = 'D:\\MyDocument\\performance\\user_guide\\guide_desc\\desc_ipynb'
    repo_ipynb_process(repo_path, repo_url, doc_csv_root)



    # all_repo_process()