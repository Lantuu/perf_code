import ast
import csv
# import numpy
# import gensim


def match_guid(package_name):
    with open('D:\\work\\performance\\user_guide\\guide_desc\\desc_0107\\' + package_name + '.csv', 'r', encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[6] != '' and row[5] == '1':
                try:
                    doc_apis = (ast.literal_eval(row[6]))  # guid所包含的api
                    issues_list = matchAPI(doc_apis)
                    if len(issues_list) != 0:
                        save_to_csv(issues_list, row, "issues_guide")
                except:
                    print('***********************AST ERROR!***************************')
                    print(row[6])

                # 按行传入一个api数列


def match_api(packageName):
    '''
    处理api本身的desc
    :param packageName: 包名
    :return:
    '''
    with open('D:\\work\\performance\\comments\\0919\\'+packageName+'_api_doc_caveats.csv', 'r', encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[7]=='0':
                continue
            doc_apis = (ast.literal_eval(row[5]))  # api本身的desc所包含的api
            issues_list = matchAPI(doc_apis)
            if len(issues_list)!=0:
                save_to_csv(issues_list, row, 'issues_api')


def matchAPI(doc_apis):
    '''
    匹配StackOverflow的desc中是否包含了API_apilist中的api
    :param API_apilist:
    :return:[[(apilist,solist),so_row,type],...]
    '''
    issues_list = []
    types = ['issues','comments']
    for type in types:
        f = open('D:\\work\\performance\\github_issues\\issues_desc\\desc_19_1112\\' + type + '.csv', 'r', encoding='gb18030')
        reader = csv.reader(f)
        # 一行一行处理SO，如果有匹配则添加到apiList
        for row in reader:
            issues_apis = ast.literal_eval(row[4])
            if len(issues_apis) != 0:
                match_apis = match(doc_apis, issues_apis)
                if len(match_apis) != 0:
                    issues_list.append([match_apis, row, type])
                    print(match_apis)
        f.close()
    return issues_list


def match(doc_apis, issues_apis):
    '''
    比较API_apilist,SO_apilist两个list中是否包含同一个api
    :param API_apilist: api里面的desc所包含的api
    :param SO_apilist:  stackoverflow 里面所包含的api
    :return:  返回API_apilist 和SO_apilist 的交集
    '''
    match_apis = []
    tag = False
    for doc_api in doc_apis:
        for issues_api in issues_apis:
            if doc_api == issues_api:
                tag = True
                match_apis.append(issues_api)
    # if tag is False:
    #     for API in API_apilist:
    #         APIlist = API.split('.')
    #         for SO in SO_apilist:
    #             SOlist = SO.split('.')
    #             if len(SOlist)>len(APIlist) and compare(SOlist,APIlist):
    #                 apiList.append((API,SO))
    #             elif len(SOlist)<len(APIlist) and compare(APIlist,SOlist):
    #                 apiList.append((API,SO))
    return match_apis


def compare(lenger,shorter):
    '''
    比较名字较短的api是否包含于名字较长的api中
    :param lenger: 名字较长的api
    :param shorter: 名字较短的api
    :return:bool类型，包含返回True，否则返回False
    '''
    if lenger[0] != shorter[0] or lenger[-1] != shorter[-1]:
        return False
    else:
        for s in range(len(shorter)):
            for l in range(len(lenger)):
                if shorter[s] == lenger[l]:
                    break
                elif l == len(lenger)-1:
                    return False
            if s == len(shorter)-1:
                return True


def save_to_csv(apiList, row, filename):
    '''
    将匹配到的结果保存到csv中
    :param apiList: [[(apilist,solist),so_row,type],...]
    :param row: api的desc等信息
    '''
    with open('D:\\work\\performance\\github_issues\\issues_doc\\issues_doc_kw_incomplete\\'+filename+'.csv', 'a', encoding='gb18030', newline='') as f:
        writer = csv.writer(f)
        for i in range(len(apiList)):
            r = []
            r.extend(row)
            r.append(apiList[i][0])
            r.append(apiList[i][2])
            r.extend(apiList[i][1])
            writer.writerow(r)


if __name__=="__main__":
    # match_api('gensim')
    # match_api('numpy')
    # match_api('pandas')
    # match_api('scipy')
    # match_api('sklearn')
    # match_api('tensorflow')

    match_guid('gensim')
    match_guid('numpy')
    match_guid('pandas')
    match_guid('scipy')
    match_guid('sklearn')
    match_guid('tensorflow')