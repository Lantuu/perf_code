# def get_commit_type(diff, desc, file_path, sigs):
#     commit_types = []
#     delete_sents = []
#     diff_contain_desc = []
#
#     diff_snippets = split_diff(diff)
#
#     for diff_snippet in diff_snippets:
#         diff_dic = classify_sens(diff_snippet)
#         add = diff_dic['add']
#         delete = diff_dic['delete']
#         add_space = diff_dic['add_space']
#         delete_space = diff_dic['delete_space']
#
#         # ' +/- '行中，含有的desc公共子序列
#         add_common_sent = get_common_sent(add, desc, add_space)
#         delete_common_sent = get_common_sent(delete, desc, delete_space)
#
#         if add_common_sent.strip() == delete_common_sent.strip():
#             continue
#
#         elif len(add_common_sent) != 0:
#             delete_sent, lc_substr = find_delete_sent(desc, delete, delete_space, file_path)
#             if desc.lstrip() != add_common_sent.lstrip():
#                 commit_type = 'alter'
#             elif len(delete_sent) != 0:
#                 lc_substr = re.sub(r'\W[0-9]', ' ', lc_substr)
#                 lc_subword = nltk.word_tokenize(lc_substr)
#                 # # 最长公共子序列返回的条件
#                 # if len(delete_sent) > 0:
#                 ls = levenshtein(delete_sent.encode('utf-8').decode('unicode-escape'), desc.encode('utf-8').decode('unicode-escape'))
#                 if ls/len(desc) <= 0.58 or len(lc_subword) >= 4:
#                     commit_type = 'alter'
#                 else:
#                     delete_sent = ''
#                     commit_type = 'add'
#             else:
#                 commit_type = 'add'
#
#             if commit_type == 'alter' and delete_sent == '':
#                 delete_sent = desc.replace(add_common_sent + ' ', '')
#
#             commit_types.append(commit_type)
#             delete_sents.append(delete_sent)
#             diff_contain_desc.append(diff_snippet)
#
#     if len(commit_types) == 0:
#         return '', ''
#     elif len(commit_types) == 1:
#         return commit_types[0], delete_sents[0]
#
#     # 有大于1个diff snippet 添加了desc， 则选出一个 优先选择改动的函数为sig中的
#     def_snippets = get_def_snippets(diff_snippets, sigs)
#     for i in range(len(diff_contain_desc)):
#         for snippet in def_snippets:
#             if diff_contain_desc == snippet:
#                 return commit_types[i], delete_sents[i]
#
#     return commit_types[0], delete_sents[0]
#
#
# def find_delete_sent(desc, delete, delete_space, file_path):
#     """
#     在一个字符串列表中，求其与desc的最长公共子序列
#     :param desc:
#     :param delete_blank: 字符串列表
#     :return: delete_string： 与desc具有最长公共子序列的字符串， 最长公共子序列的大小
#     """
#     lines = []
#     for line in delete_space:
#         lines.append(line[1:])
#     delete_string = ''  # 最长公共子序列
#     max_res = 0
#     delete_line_index = None   # 最长公共子序列在delete中行的索引
#     delete_space_line_index = None  # 最长公共子序列在delete_space中行的索引
#     lc_substring = ''
#     for index in range(len(delete)):
#         lc = []
#         substring = []
#         if len(delete[index]) > 10000:
#             continue
#
#         blank_index = get_blank_index(index, delete_space, '-')
#         delete_sents = tokenizer.tokenize(delete[index][1:])
#
#         # 计算每个句子与desc的最长公共子序列
#         for sent in delete_sents:
#             format_sent = get_format_desc(sent, blank_index, lines)
#             format_sent_ = ' '.join([i for i in format_sent.strip().split(' ') if i != ''])
#             desc_ = ' '.join([i for i in desc.strip().split(' ') if i != ''])
#             s = find_lcsubstr(format_sent_, desc_)
#             lc.append(len(s.strip()))
#             substring.append(s.strip())
#
#         # 求最长公共子序列最大的句子及最长公共子序列大小
#         max_lc_line = 0
#         max_lc_index = -1
#         for i in range(len(lc)):
#             if lc[i] > max_lc_line:
#                 max_lc_line = lc[i]
#                 max_lc_index = i
#
#         if max_lc_line > max_res:
#             max_res = max_lc_line
#             delete_string = delete_sents[max_lc_index]
#             delete_line_index = index
#             lc_substring = substring[max_lc_index]
#
#     # 在delete_space中的索引
#     for index in range(len(delete_space)):
#         if delete_line_index is None:
#             break
#         if delete_space[index] == delete[delete_line_index]:
#             delete_space_line_index = index
#             break
#
#     if not file_path.endswith('.ipynb') and len(delete_string) > 0:
#         delete_string = get_format_desc(delete_string, delete_space_line_index, lines)
#
#     return delete_string, lc_substring
#
#
# def get_blank_index(alter_index, blank_list, alter_tag):
#     # 找到在blank中的索引下标
#     blank_index = -1
#     add_or_delete = -1
#     for index in range(len(blank_list)):
#         if blank_list[index].startswith(alter_tag):
#             add_or_delete = add_or_delete + 1
#
#         if add_or_delete == alter_index:
#             blank_index = index
#             break
#     return blank_index
#
#
# def get_common_sent(alter_list, desc, blank_list):
#
#     common_sen = ''
#     # 去每一行前面的"+/-"
#     blank_lines = [line[1:] for line in blank_list]
#     alter_lines = [line[1:] for line in alter_list]
#
#     line_sen_index = 0
#     line_sen = ''
#     alter_index = 0
#     while alter_index < len(alter_lines):
#         line = alter_lines[alter_index]
#         if line.strip().startswith('\"image/png\"'):
#             continue
#         if len(line) > 10000:
#             continue
#
#         # line_sents = nltk.sent_tokenize(line)
#         line_sents = tokenizer.tokenize(line)
#         for sen_index in range(len(line_sents)):
#             if re.search(r'[a-zA-Z]', line_sents[sen_index].replace('\\n', '')) is None:
#                 continue
#
#             if line_sents[sen_index].strip() in desc:
#
#                 # 找到在blank中的索引下标
#                 blank_index = get_blank_index(alter_index, blank_list, alter_list[alter_index].strip()[0])
#                 # blank_index = -1
#                 # add_or_delete = -1
#                 # for index in range(len(blank_list)):
#                 #     if blank_list[index].startswith(alter_list[alter_index].strip()[0]):
#                 #         add_or_delete = add_or_delete + 1
#                 #
#                 #     if add_or_delete == alter_index:
#                 #         blank_index = index
#                 #         break
#                 complete_sen = get_format_desc(line_sents[sen_index], blank_index, blank_lines)
#
#                 if desc in complete_sen:
#                     line_sen_index = sen_index
#                     line_sen = line_sents[sen_index]
#                     break
#
#         if line_sen != '':
#             common_sen = line_sen
#             desc2 = desc.replace(line_sen, '')
#             if line_sen_index < len(line_sents)-1:
#                 break
#
#             for i in range(alter_index + 1, len(alter_lines)):
#                 line = alter_lines[i]
#                 # line_sens = nltk.sent_tokenize(line)
#                 line_sens = tokenizer.tokenize(line)
#                 tag = True
#                 for sen in line_sens:
#                     if sen in desc2:
#                         common_sen = common_sen + ' ' + sen
#                         desc2 = desc2.replace(sen, '')
#                     else:
#                         tag = False
#                         break
#                 if not tag:
#                     break
#             break
#         else:
#             alter_index = alter_index + 1
#     return common_sen


# def get_format_desc(line_desc, line_index, lines):
#     """
#     根据line_desc的值，在lines中找到它的上下文，使其变成一个完整的句子
#     :param line_desc: 字符串
#     :param line_index: 整型
#     :param lines: 字符串列表
#     :return: 字符串 含有line_desc上下文的完整句子
#     """
#     format_desc = line_desc
#     line = lines[line_index]
#     line = line.replace('O(n!)', 'O(n\\\\)')  # .replace('\n', '\\n').replace('"""', '')
#     sens = tokenizer.tokenize(line)
#     sent_count = len(sens)  # line中含有句子的数量
#     order_line_desc = -1   # line_desc 在line子句中的定位
#
#     for sen in sens:
#         order_line_desc = order_line_desc + 1
#         sen = sen.replace('O(n\\\\)', 'O(n!)')  # .replace('\\n', '\n')
#         if sen == line_desc:
#             break
#
#     # line_desc 在line的头部， line中含有大于1句子数量，则只需要添加line_desc的上文
#     if order_line_desc == 0 and sent_count > 1:
#         fw = forward(line_index, lines, line_desc)
#         if len(fw) > 0:
#             format_desc = fw + format_desc
#             format_desc = tokenizer.tokenize(format_desc)[-1]
#
#     # line_desc 在line的头部， line中只有1个句子，则需要添加line_desc的上文和下文
#     elif order_line_desc == 0 and sent_count == 1:
#         fw = forward(line_index, lines, line_desc)
#         bk = back(line_index, lines, line_desc)
#         if len(fw) > 0:
#             format_desc = fw + format_desc
#             format_desc = tokenizer.tokenize(format_desc)[-1]
#
#         if len(bk) > 0:
#             format_desc = format_desc + bk
#             format_desc = tokenizer.tokenize(format_desc)[0]
#
#     # line_desc 在line的尾部， line中含有大于1句子数量，则只需要添加line_desc的下文
#     elif order_line_desc == sent_count - 1:
#         bk = back(line_index, lines, line_desc)
#         if len(bk) > 0:
#             format_desc = format_desc + bk
#             format_desc = tokenizer.tokenize(format_desc)[0]
#
#     # line_desc 在line的中间，无需添加line_desc的下文
#     else:
#         format_desc = format_desc
#
#     return format_desc
#
#
# def back(line_index, lines, line_desc):
#     """
#     向后遍历，补充line_desc,使其变成一个完整的句子
#     :param line_index: line_desc 在lines的定位
#     :param lines:
#     :param line_desc: 不完整的句子
#     :return: 让line_desc变成一个完整的句子所缺的后面一部分字符串
#     """
#
#     format_desc = ''  # 返回用来填补的字符串
#     line_desc = line_desc.strip()
#
#     # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
#     if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===', str(line_desc).strip()):
#         return format_desc
#
#     while line_index < len(lines) - 1:
#
#         # 如果desc是以'.',':',"'''",'!','?','"""'结尾的，则表明该句子已经结束，直接返回
#         if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===', str(format_desc).strip()):
#             return format_desc
#
#         line_index = line_index + 1  # 下一行
#         line = lines[line_index]
#
#         if len(line.strip()) == 0:
#             break
#
#         # 如果下一行是以'大写字母','*',"'''",'#','-','"""'开始的，则表明该行是一个新句子的开头，直接返回  ^[A-Z]|
#         if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\S+ :', str(line).strip()):  # |\S+:^[A-Z]|
#             break
#
#         # 加上所有的子句，返回
#
#         line = line.replace('O(n!)', 'O(n\\\\)')  # .replace('"""', '').replace('\n', '\\n')
#         sens = tokenizer.tokenize(line)
#         format_desc = format_desc + ' ' + sens[0].replace('O(n\\\\)', 'O(n!)')  # .replace('\\n', '\n')
#         # back_line = back_line + 1
#         if len(sens) > 1:
#             break
#         else:
#             continue
#
#     return format_desc
#
#
# def forward(line_index, lines, line_desc):
#     """
#     向前遍历，补充line_desc,使其变成一个完整的句子
#     :param line_index: line_desc 在lines的定位
#     :param lines:
#     :param line_desc: 不完整的句子
#     :return: 让line_desc变成一个完整的句子所缺的前面一部分字符串
#     """
#     format_desc = ''  # 返回用来填补的字符串
#
#     # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回   ^[A-Z]|
#     if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\S+ :', str(line_desc).strip()):  # |\S+:^[A-Z]|
#         return format_desc
#
#     while line_index > 0:
#
#         # 如果desc以'大写字母','*',"'''",'#','-','"""'开始的，则表明该desc头部已经结束，直接返回    ^[A-Z]|
#         if re.match(r'^\* |^- |^#|^\'\'\'|^\"\"\"|>>>|---|===|\S+ :', str(format_desc).strip()):  # |\S+: ^[A-Z]|
#             break
#
#         # 上一行
#         line_index = line_index - 1
#         line = lines[line_index]
#
#         if len(line.strip()) == 0:
#             break
#
#         # 如果上一行是以'.',':',"'''",'!','?','"""'结尾的，则表明行是一个新句子的尾部，直接返回
#         if re.match(r'.*\.$|.*:$|.*\"\"\"$|.*\'\'\'$|.*!$|.*\?$|---|===', str(line).strip()):
#             break
#
#         # 加上所有的子句，返回
#         line = line.replace('O(n!)', 'O(n\\\\)')  # .replace('"""', '').replace('\n', '\\n')
#         sens = tokenizer.tokenize(line)
#         format_desc = sens[-1].replace('O(n\\\\)', 'O(n!)') + ' ' + format_desc   # .replace('\\n', '\n')
#         # forward_line = forward_line + 1
#         if len(sens) > 1:
#             break
#         else:
#             continue
#
#     return format_desc