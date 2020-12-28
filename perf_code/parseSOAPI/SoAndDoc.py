import ast
import csv
# import numpy
# import gensim

def match_guid(packgeName):
    with open('G:\Performance\SO_Guid_Api\guid\guidDesc\guidDesc_0830\projects-doc-9.2\\' + packgeName + '.csv', 'r',encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[6]!='':
                try:
                    API_apilist = (ast.literal_eval(row[6]))  # guid所包含的api
                except:
                    print('***********************AST ERROR!***************************')
                    print(row[6])
                # 按行传入一个api数列
                apilist = matchAPI(API_apilist)
                if len(apilist) != 0:
                    save_to_csv(apilist, row,'guid_SO')

def match_api(packageName):
    '''
    处理api本身的desc
    :param packageName: 包名
    :return:
    '''
    with open('G:\\Performance\\SO_Guid_Api\\API\\apiDesc\\0919\\'+packageName+'_api_doc_caveats.csv','r',encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[7]=='0':
                continue
            API_apilist = (ast.literal_eval(row[5]))  # api本身的desc所包含的api
            apilist = matchAPI(API_apilist)
            if len(apilist)!=0:
                save_to_csv(apilist,row,'api_SO')

def matchAPI(API_apilist):
    '''
    匹配StackOverflow的desc中是否包含了API_apilist中的api
    :param API_apilist:
    :return:[[(apilist,solist),so_row,type],...]
    '''
    apiList=[]
    types = ['answer','question','comment']
    for type in types:
        f = open('G:\\Performance\\SO_Guid_Api\\stackoverflow\\fullName\\fullname_1011\\stackoverflow_latest_' + type + '.csv', 'r',encoding='gb18030')
        reader = csv.reader(f)
        # 一行一行处理SO，如果有匹配则添加到apiList
        for row in reader:
            SO_apilist = ast.literal_eval(row[3])
            if len(SO_apilist)!=0:
                matchList = match(API_apilist, SO_apilist)
                if len(matchList)!=0:
                    apiList.append([matchList,row,type])
                    print(matchList)
        f.close()
    return apiList

def match(API_apilist,SO_apilist):
    '''
    比较API_apilist,SO_apilist两个list中是否包含同一个api
    :param API_apilist: api里面的desc所包含的api
    :param SO_apilist:  stackoverflow 里面所包含的api
    :return:  返回API_apilist 和SO_apilist 的交集
    '''
    apiList = []
    tag = False
    for API in API_apilist:
        for SO in SO_apilist:
            if SO==API:
                tag=True
                apiList.append((API,SO))
    # if tag is False:
    #     for API in API_apilist:
    #         APIlist = API.split('.')
    #         for SO in SO_apilist:
    #             SOlist = SO.split('.')
    #             if len(SOlist)>len(APIlist) and compare(SOlist,APIlist):
    #                 apiList.append((API,SO))
    #             elif len(SOlist)<len(APIlist) and compare(APIlist,SOlist):
    #                 apiList.append((API,SO))
    return apiList

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

def save_to_csv(apiList,row,filename):
    '''
    将匹配到的结果保存到csv中
    :param apiList: [[(apilist,solist),so_row,type],...]
    :param row: api的desc等信息
    '''
    with open('G:\\Performance\\SO_Guid_Api\\matchResult\\matchResult-1012\\'+filename+'2.csv', 'a', encoding='gb18030', newline='') as f:
        writer = csv.writer(f)
        for i in range(len(apiList)):
            r = []
            r.extend(row)
            r.append(apiList[i][0])
            r.append(apiList[i][2])
            r.extend(apiList[i][1])
            writer.writerow(r)

if __name__=="__main__":
    #match_api('gensim')
    # match_api('numpy')
    # match_api('pandas')
    # match_api('scipy')
    # match_api('sklearn')
    # match_api('tensorflow')
    #
    match_guid('gensim')
    # match_guid('numpy')
    # match_guid('pandas')
    # match_guid('scipy')
    # match_guid('scikit-learn')
    # match_guid('tensorflow')