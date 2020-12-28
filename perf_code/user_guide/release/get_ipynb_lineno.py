import ast
import csv
import re
import nltk


def reader_csv(path):
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for line in reader:
            data.append(line)
    return data


def get_lineno(data):
    lineno_list = []
    kw_list = []
    path_list = []
    desc_list = []
    markdown_tag = False

    for d in data:
        desc_list.append(d[1])
        kw_list.append(ast.literal_eval(d[2]))
        path_list.append(d[3])

    for path_tag in range(len(path_list)):
        print(path_list[path_tag])


        # 和上一行是同一文件(.ipnyb)
        if path_tag > 0 and path_list[path_tag] == path_list[path_tag-1]:
            # #  删除上一行的数据
            # file_data[lineno_list[path_tag-1]] = file_data[lineno_list[path_tag-1]].replace()

            # 继续上一行之后的lineno开始遍历
            for ipnyb_tag in range(lineno_list[path_tag - 1]-1, len(file_data)):  # (上一行的行号， 文件的长度)
                if file_data[ipnyb_tag].strip() == '"cell_type": "markdown",':
                    markdown_tag = True
                elif file_data[ipnyb_tag].strip() == '"cell_type": "code",':
                    markdown_tag = False
                lineno = -1
                if is_kw_list_desc(kw_list[path_tag], file_data[ipnyb_tag]) and markdown_tag:
                    lineno = ipnyb_tag + 1
                    print(lineno)
                    file_data[ipnyb_tag] = delete_kw_in_line(file_data[ipnyb_tag], kw_list[path_tag])
                    break
                else:
                    continue
            lineno_list.append(lineno)
        else:
            file_data = get_ipnyb_data(path_list[path_tag])
            markdown_tag = False

            for ipnyb_tag in range(len(file_data)):
                if file_data[ipnyb_tag].strip() == '"cell_type": "markdown",':
                    markdown_tag = True
                elif file_data[ipnyb_tag].strip() == '"cell_type": "code",':
                    markdown_tag = False
                lineno = -1
                if is_kw_list_desc(kw_list[path_tag], file_data[ipnyb_tag]) and markdown_tag:
                    lineno = ipnyb_tag + 1
                    print(lineno)
                    file_data[ipnyb_tag] = delete_kw_in_line(file_data[ipnyb_tag], kw_list[path_tag])
                    break
                else:
                    continue
            lineno_list.append(lineno)
    return lineno_list


def get_ipnyb_data(path):
     f = open(path, 'r', encoding='utf-8')
     data = f.readlines()
     f.close()
     return data


def is_kw_list_desc(kw_list, line):
    for kw in kw_list:
        if is_kw_desc(kw, line):
            continue
        else:
            return False
    return True


def is_kw_desc(kw, line):
    # matchobj = re.search(r"(.*)" + r"\b" + kw + r"\b" + r"(.*)", line, re.I)
    # if matchobj is not None:
    #     return True
    if line.lower().find(kw) != -1:
        return True
    else:
        return False


def delete_kw_in_line(line, kw_list):
    result = ''
    sentences = nltk.sent_tokenize(line)
    for i in range(len(sentences)):
        if is_kw_list_desc(kw_list, sentences[i]):
            for kw in kw_list:
                sentences[i] = sentences[i].lower().replace(kw, '')
            break
    for sentence in sentences:
        result = result + ' ' + sentence
    return result.strip()


def save_csv(path, data):
    with open(path,'a+',encoding='utf-8',newline='') as f:
        writer = csv.writer(f)
        for d in data:
            writer.writerow([d])

def main():
    path = 'D:\\MyDocument\\performance\\user_guide\\guide_desc\\desc_ipynb\\gensim-3.7.3.csv'
    save_path = 'D:\\MyDocument\\performance\\user_guide\\guide_desc\\desc_ipynb\\gensim-lineno.csv'
    data = reader_csv(path)  # [path,desc,kw,full_path,url]
    lino_list = get_lineno(data)
    print(lino_list)
    save_csv(save_path, lino_list)
    print(lino_list)


if __name__ == '__main__':
    main()
    # str = '"Note: In real applications batching is essential for performance. The best code to convert to AutoGraph is code where the control flow is decided at the _batch_ level. If making decisions at the individual _example_ level, you must index and batch the examples to maintain performance while applying the control flow logic.\n",'
    # result = delete_part_line(str, ['performance'])
    # print(result)
