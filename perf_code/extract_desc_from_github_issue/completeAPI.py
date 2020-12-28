# import ast
import ast
import csv
import pandas
import re


def get_data(csv_path):
    f = open(csv_path, 'r', encoding='gb18030')
    reader = csv.reader(f)
    repolist = []
    sen_apis = []
    comment_apis = []
    data = []  # [repolist, sen_apis, comment_apis]
    for row in reader:
        repolist.append(row[1])
        sen_apis.append(ast.literal_eval(row[5]))
        comment_apis.append(ast.literal_eval(row[6]))
    f.close()
    data.append(repolist)
    data.append(sen_apis)
    data.append(comment_apis)
    return data


def completeApi(data):
    repolist = data[0]
    sen_apis = data[1]
    comment_apis = data[2]
    fullName = []
    desc_apis=[]
    context_apis=[] # 根据上下文填充的api

    for index in range(len(sen_apis)):  # 每一个desc句子所包含的apis
        for sen_api in sen_apis[index]:  # apis中的一个api

            if sen_api is None:
                continue

            if re.match(r'^numpy\.|^scipy\.|^pandas\.|^tensorflow\.|^sklearn\.|^gensim\.',str(sen_api)) is not None:
                desc_apis.append(str(sen_api))

            # 根据上下文填充api
            else:
                for comment_api in comment_apis[index]: # 该desc句子所在comment 所包含的所有apis 中的一个api
                    # print('comment_api:',comment_api)
                    if comment_api is None:
                        continue

                    if str(comment_api).endswith('.'+sen_api):
                        context_apis.append(comment_api)

                if len(context_apis)!=0:
                    desc_apis.extend(context_apis)
                    context_apis = []

            # 上下文没有找到则根据文档填充api
            if len(context_apis) == 0 :
                if repolist[index].find('scipy') != -1:
                    repo = 'scipy'
                elif repolist[index].find('numpy') != -1:
                    repo = 'numpy'
                elif repolist[index].find('pandas') != -1:
                    repo = 'pandas'
                elif repolist[index].find('tensorflow') != -1:
                    repo = 'tensorflow'
                elif repolist[index].find('gensim') != -1:
                    repo = 'gensim'
                else:
                    repo = 'sklearn'
                # repo = re.match(r'[a-z-]+',repolist[index]).group()
                doc_apis = matchAPI(repo, str(sen_api))
                if len(doc_apis) == 0:
                    if repo != 'scipy':
                        doc_apis.extend(matchAPI('scipy', str(sen_api)))
                    if repo != 'numpy':
                        doc_apis.extend(matchAPI('numpy', str(sen_api)))
                    if repo != 'pandas':
                        doc_apis.extend(matchAPI('pandas', str(sen_api)))
                    if repo != 'tensorflow':
                        doc_apis.extend(matchAPI('tensorflow', str(sen_api)))
                    if repo != 'gensim':
                        doc_apis.extend(matchAPI('gensim', str(sen_api)))
                    if repo != 'sklearn':
                        doc_apis.extend(matchAPI('sklearn', str(sen_api)))
                    desc_apis.extend(get_shorter_api(doc_apis))
                else:
                    desc_apis.extend(doc_apis)

                if len(desc_apis) == 0:
                    print('cna not complete: ', sen_api)

        desc_apis=list(set(desc_apis))
        fullName.append(desc_apis)
        desc_apis=[]

    print(fullName)
    return fullName


def matchAPI(packgeName, code):
    fullname_list = []

    with open('D:\\work\\performance\\fullname\\0103\\'+packgeName+'.csv', 'r', encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0 and str(row[0]).endswith('.'+code):
                fullname_list.append(row[0])
    fullname_list = get_shorter_api(fullname_list)
    return fullname_list


def get_shorter_api(api_list):
    fullname_len1 = []
    fullname_len2 = []
    fullname_len3 = []
    fullname_len4 = []
    fullname_lenother = []
    for api in api_list:
        api_len = len(str(api)) - len(str(api).replace('.', ''))
        if api_len == 1:
            fullname_len1.append(api)
        elif api_len == 2:
            fullname_len2.append(api)
        elif api_len == 3:
            fullname_len3.append(api)
        elif api_len == 4:
            fullname_len4.append(api)
        else:
            fullname_lenother.append(api)
    if len(fullname_len1) != 0:
        return fullname_len1
    elif len(fullname_len2) != 0:
        return fullname_len2
    elif len(fullname_len3) != 0:
        return fullname_len3
    elif len(fullname_len4) != 0:
        return fullname_len4
    else:
        return fullname_lenother


def save_to_csv(csv_path,data):

    with open(csv_path, 'a', newline="",encoding='gb18030') as f:
        writer = csv.writer(f)
        for d in data:
            writer.writerow([d])


if __name__=="__main__":
    save_csv_path = 'D:\\work\\performance\\github_issues\\issues_desc\\complete_api\\comments_complete3.csv'
    data_csv_path = 'D:\\work\\performance\\github_issues\\issues_desc\\desc_20_0102\\comments.csv'
    data = get_data(data_csv_path)
    full_name = completeApi(data)
    save_to_csv(save_csv_path, full_name)
