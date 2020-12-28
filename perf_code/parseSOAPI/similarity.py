import ast
import csv
import operator
import re

import nltk
from gensim import matutils
from gensim.models import KeyedVectors
from numpy import dot, array
from tqdm import tqdm



class Embedding():

    def build_vocab(self,sentences, verbose=True):
        """
        :param sentences: list of list of words 输入是训练集与测试集的数据
        :return: dictionary of words and their count
        追踪训练词汇表，遍历所有文本对单词进行计数
        """
        vocab = {}
        for sentence in tqdm(sentences, disable=(not verbose)):
            for word in sentence:
                try:
                    vocab[word] += 1
                except KeyError:
                    vocab[word] = 1
        return vocab

    def load_embed(self,file):
        '''
        加载预训练的embedding
        :param file: 预训embedding的路径
        :return: {word : vec,...}
        '''
        model = KeyedVectors.load_word2vec_format(file, binary=True)
        embeddings_google = {}
        for word, vector in zip(model.vocab, model.vectors):
            embeddings_google[word] = vector
        return embeddings_google

    def check_coverage(self,vocab, embeddings_google):
        known_words = {}  # 两者都有的单词
        unknown_words = {}  # embeddings不能覆盖的单词
        nb_known_words = 0  # 对应的数量
        nb_unknown_words = 0
        for word in vocab.keys():
        #for word in tqdm(vocab):
            try:
                known_words[word] = embeddings_google[word]
                nb_known_words += vocab[word]
            except:
                unknown_words[word] = vocab[word]
                nb_unknown_words += vocab[word]
                pass

        print('Found embeddings for {:.2%} of vocab'.format(len(known_words) / len(vocab)))  # 覆盖单词的百分比
        print('Found embeddings for  {:.2%} of all text'.format(
            nb_known_words / (nb_known_words + nb_unknown_words)))  # 覆盖文本的百分比，与上一个指标的区别的原因在于单词在文本中是重复出现的。
        unknown_words = sorted(unknown_words.items(), key=operator.itemgetter(1))[::-1]
        print("unknown words : ", unknown_words[:30])
        return unknown_words

class ClearnData():

    # def __init__(self):
    #     self.api = []
    #     self.guid = []
    #     self.apiSO = []
    #     self.guidSO = []



    def guid_match(self,packgeName):
        guids=[]
        with open('G:\Performance\SO_Guid_Api\guid\guidDesc\guidDesc_0830\projects-doc-9.2\\' + packgeName + '.csv',
                  'r', encoding='gb18030') as f:
            reader = csv.reader(f)
            # 处理guid表中的一行desc
            for row in reader:
                if row[6] != '':
                    try:
                        API_apilist = (ast.literal_eval(row[6]))  # guid所包含的api
                        descs = self.matchAPI(API_apilist)
                        if len(descs) != 0:
                            guid=[]
                            guid.append(row[1])
                            guid.extend(descs)
                            #self.guidSO.append(descs)
                            guids.append(guid)
                    except:
                        print('***********************AST ERROR!***************************')
                        print(row[6])
                    # 按行传入一个api数列，返回SO中所有匹配到的desc

                        #save_to_csv(apilist, row, 'guid_SO')
            return(guids)

    def api_match(self,packageName):
        '''
        处理api本身的desc
        :param packageName: 包名
        :return:
        '''
        apis=[]
        with open('G:\\Performance\\SO_Guid_Api\\API\\apiDesc\\0919\\' + packageName + '_api_doc_caveats.csv', 'r',
                  encoding='gb18030') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[7] == '0':
                    continue
                API_apilist = (ast.literal_eval(row[5]))  # api本身的desc所包含的api
                descs = self.matchAPI(API_apilist)
                descs=self.cleanData(descs)
                for desc in descs:
                    desc=desc[1]


                if len(descs) != 0:
                    api = []
                    api.append(row[1])
                    api.extend(descs)
                    apis.append(api)
                    #save_to_csv(apilist, row, 'api_SO')
        return apis

    def matchAPI(self,API_apilist):
        '''
        匹配StackOverflow的desc中是否包含了API_apilist中的api
        :param API_apilist:
        :return:[[(apilist,solist),so_row,type],...]
        '''
        # apiList = []
        descs = []
        types = ['answer', 'question', 'comment']
        for type in types:
            f = open(
                'G:\\Performance\\SO_Guid_Api\\stackoverflow\\fullName\\fullname_1011\\stackoverflow_latest_' + type + '.csv',
                'r', encoding='gb18030')
            reader = csv.reader(f)
            # 一行一行处理SO，如果有匹配则添加到apiList
            for row in reader:
                SO_apilist = ast.literal_eval(row[3])
                if len(SO_apilist) != 0:
                    matchList = self.match(API_apilist, SO_apilist)
                    if len(matchList) != 0:
                        descs.append([matchList, row, type])
                        #apiList.append([matchList, row, type])
                        #print(matchList)
            f.close()
        return descs

    def match(self,API_apilist, SO_apilist):
        '''
        比较API_apilist,SO_apilist两个list中是否包含同一个api
        :param API_apilist: api里面的desc所包含的api
        :param SO_apilist:  stackoverflow 里面所包含的api
        :return:  返回API_apilist 和SO_apilist 的交集
        '''
        apiList = []
        for API in API_apilist:
            for SO in SO_apilist:
                if SO == API:
                    apiList.append(API)

        return apiList

    # def get_sentences(self,sentences):
    #     sentences_list = []
    #     preprocess = PreProcess()
    #     preprocess.stopwordslist()
    #     for sentence in sentences:
    #         word_list = preprocess.extact_Stopwords(sentence)
    #         sentences_list.append(word_list)
    #     return sentences_list

    def cleanData(self,descs_list):
        preprocess = PreProcess()
        preprocess.stopwordslist()
        for i in range(len(descs_list)):
            for j in range(len(descs_list[i])):
                descs_list[i][j]=preprocess.extact_Stopwords(descs_list[i][j])
        return descs_list

        # for i in range(len(apis)):
        #     apis[i]=preprocess.extact_Stopwords(apis[i])
        # for i in range(len(self.guid)):
        #     self.guid[i] = preprocess.extact_Stopwords(self.guid[i])
        # for i in range(len(self.apiSO)):
        #     for j in range(len(self.apiSO[i])):
        #         self.apiSO[i][j]=preprocess.extact_Stopwords(self.apiSO[i][j])
        # for i in range(len(self.guidSO)):
        #     for j in range(len(self.guidSO[i])):
        #         self.guidSO[i][j]=preprocess.extact_Stopwords(self.guidSO[i][j])

    def save_to_csv(apiList, rows, filename):
        '''
        将匹配到的结果保存到csv中
        :param apiList: [[(apilist,solist),so_row,type],...]
        :param row: api的desc等信息
        '''
        with open('G:\\Performance\\SO_Guid_Api\\matchResult\\matchResult-1016\\' + filename + '3.csv', 'a',
                  encoding='gb18030', newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

class PreProcess():
    '''
    去停用词表
    '''
    def __init__(self):
        self.stopwords=[]

    def extact_Stopwords(self,sentence):
        word_list = self.textSeg(sentence)
        # stopwords = self.stopwords
        words = [word for word in word_list if word.lower() not in self.stopwords]
        return words

    def textSeg(self,text):
        word_list = nltk.word_tokenize(text)
        return word_list

    def stopwordslist(self):
        stopwords = []
        f = open('G:\Performance\SO_Guid_Api\matchResult\matchResult-1012\\stopwords_en.txt', 'r', encoding='gb18030')
        reader = f.readlines()
        for word in reader:
            stopwords.append(word.strip())
        self.stopwords = stopwords

def sentences_list():
    embedding = Embedding()
    embeddings_google = embedding.load_embed('GoogleNews-vectors-negative300.bin')
    packgenames = ['gensim','numpy','pandas','scipy','sklearn','tensorflow']
    for packgename in packgenames:
        guid_match(packgename,embeddings_google)
        api_match(packgename,embeddings_google)
        # apis = cleanData(apis)
        # guids = cleanData(guids)
        # apis.insert(0,[packgename])
        # guids.insert(0,[packgename])
        # save_to_csv(apis,"desc_api")
        # save_to_csv(guids,'desc_guid')
    # sentences.extend(self.api)
    # sentences.extend(self.guid)
    # for desc in self.apiSO:
    #     sentences.extend(desc)
    # for desc in self.guidSO:
    #     sentences.extend(desc)
    # sentences.extend(self.get_sentences(self.api))
    # sentences.extend(self.get_sentences(self.guid))
    # for descs in self.apiSO:
    #     sentences.extend(self.get_sentences(descs))
    # for descs in self.guidSO:
    #     sentences.extend(self.get_sentences(descs))

    #return sentences

def guid_match(packgeName,embeddings_google):

    f = open('G:\Performance\SO_Guid_Api\guid\guidDesc\guidDesc_0830\projects-doc-9.2\\' + packgeName + '.csv','r', encoding='gb18030')
    reader = csv.reader(f)
    # 处理guid表中的一行desc
    for row in reader:
        guids = []
        if row[6] != '':
            API_apilist = (ast.literal_eval(row[6]))  # guid所包含的api
            # guid desc 单词的列表（已去停用词）,解析驼峰命名格式代码元素
            guid_desc = parse_sentences(cleanData(row[1]))
            SOs = matchAPI(API_apilist)  # 已匹配到的SO中的信息:[matchList, row, type]

            if len(SOs) != 0:
                similaritys = []
                # SO desc去停用词，解析驼峰命名格式的代码元素,得到SO 和guid 的相似度
                for SO in SOs:
                    SO_desc = parse_sentences(cleanData(SO[1][1]))
                    if len(SO_desc)!=0 and len(guid_desc)!=0:
                        similaritys.append(get_similarity(SO_desc,guid_desc, embeddings_google))
                    else:
                        similaritys.append(0)
                # 选择两个相似度最高的index保存

                if len(SOs) > 2:
                    maxindex = []
                    max = 0
                    for i in range(len(similaritys)):
                        if similaritys[i] > max:
                            max = similaritys[i]
                            index = i
                        if i == len(similaritys) - 1:
                            maxindex.append(index)
                    max = 0
                    for i in range(len(similaritys)):
                        if i == maxindex[0]:
                            continue
                        if similaritys[i] > max:
                            max = similaritys[i]
                            index = i
                        if i == len(similaritys) - 1:
                            maxindex.append(index)
                        # 保存信息

                    for i in range(len(SOs)):
                        if i in maxindex:
                            guids.append([SOs[i], similaritys[i], row])
                else:
                    for i in range(len(SOs)):
                        guids.append([SOs[i], similaritys[i], row])
                save_to_csv(guids, 'guid_SO')
    f.close()


def api_match(packageName,embeddings_google):
    '''
    处理api本身的desc
    :param packageName: 包名
    :return:
    '''
    f = open('G:\\Performance\\SO_Guid_Api\\API\\apiDesc\\0919\\' + packageName + '_api_doc_caveats.csv', 'r',encoding='gb18030')
    reader = csv.reader(f)
    for row in reader:
        apis = []
        if row[7] == '0':
            continue
        API_apilist = (ast.literal_eval(row[5]))  # api本身的desc所包含的api
        # api desc 单词的列表（已去停用词）,解析驼峰命名格式代码元素
        API_desc = parse_sentences(cleanData(row[1]))
        SOs = matchAPI(API_apilist) # 已匹配到的SO中的信息:[matchList, row, type]

        if len(SOs) != 0:
            similaritys = []
            # SO desc去停用词，解析驼峰命名格式的代码元素,得到相似度
            for SO in SOs:
                SO_desc = parse_sentences(cleanData(SO[1][1]))
                if len(SO_desc) != 0 and len(API_desc) != 0:
                    similaritys.append(get_similarity(SO_desc, API_desc, embeddings_google))
                else:
                    similaritys.append(0)
            if len(SOs)>2:
                # 选择两个相似度最高的index保存
                maxindex = [] # 两个相似度最高的index
                max=0
                for i in range(len(similaritys)):
                    if similaritys[i]>max:
                        max=similaritys[i]
                        index=i
                    if i==len(similaritys)-1:
                        maxindex.append(index)
                max=0
                for i in range(len(similaritys)):
                    if i==maxindex[0]:
                        continue
                    if similaritys[i] > max:
                        max = similaritys[i]
                        index=i
                    if i == len(similaritys) - 1:
                        maxindex.append(index)

                for i in range(len(SOs)):
                    if i in maxindex:
                        apis.append([SOs[i],similaritys[i],row])
            else:
                for i in range(len(SOs)):
                    apis.append([SOs[i],similaritys[i],row])
            save_to_csv(apis,'api_SO')

    f.close()

def matchAPI(API_apilist):
    '''
    匹配StackOverflow的desc中是否包含了API_apilist中的api
    :param API_apilist:
    :return:[[apilist,row,type],...]
    '''
    # apiList = []
    descs = []
    types = ['answer', 'question', 'comment']
    for type in types:
        f = open(
            'G:\\Performance\\SO_Guid_Api\\stackoverflow\\fullName\\fullname_1011\\stackoverflow_latest_' + type + '.csv',
            'r', encoding='gb18030')
        reader = csv.reader(f)
        # 一行一行处理SO，如果有匹配则添加到apiList
        for row in reader:
            SO_apilist = ast.literal_eval(row[3])
            if len(SO_apilist) != 0:
                matchList = match(API_apilist, SO_apilist)
                if len(matchList) != 0:
                    descs.append([matchList, row, type])
                    # apiList.append([matchList, row, type])
                    # print(matchList)
        f.close()
    return descs

def match(API_apilist, SO_apilist):
    '''
    比较API_apilist,SO_apilist两个list中是否包含同一个api
    :param API_apilist: api里面的desc所包含的api
    :param SO_apilist:  stackoverflow 里面所包含的api
    :return:  返回API_apilist 和SO_apilist 的交集
    '''
    apiList = []
    for API in API_apilist:
        for SO in SO_apilist:
            if SO == API:
                apiList.append(API)

    return apiList

    # def get_sentences(self,sentences):
    #     sentences_list = []
    #     preprocess = PreProcess()
    #     preprocess.stopwordslist()
    #     for sentence in sentences:
    #         word_list = preprocess.extact_Stopwords(sentence)
    #         sentences_list.append(word_list)
    #     return sentences_list

def cleanData(sentence):
    '''
    输入一个句子，去掉句子中包含的停用词，返回单词列表
    :param sentence:
    :return: 返回一个列表的列表：word_list,已经去了停用词的单词列表
    '''
    preprocess = PreProcess()
    preprocess.stopwordslist()
    # for i in range(len(desc_list)):
    #     #for j in range(len(descs_list[i])):
    word_list = preprocess.extact_Stopwords(sentence)
    return word_list

def save_to_csv(apis, filename):
    '''
    将匹配到的结果保存到csv中
    :param apis: [[SO,similarity,row],...],SO=[apilist,row,type]
    :param row: api的desc等信息
    '''
    f = open('G:\\Performance\\SO_Guid_Api\\matchResult\\matchResult-1016\\' + filename + '2.csv', 'a',encoding='gb18030', newline='')
    writer = csv.writer(f)
    for api in apis:
        row=[]
        row.extend(api[2]) # api/guid 的row
        row.append(api[0][0])# match 的api
        row.append(api[1]) # 相似度
        row.append(api[0][2]) # SO_type
        row.extend(api[0][1]) # SO的row
        writer.writerow(row)
    f.close()

def get_sentences(filepath):
    sentences=[] # list of list of word
    with open(filepath,'r',encoding='gb18030') as f:
        reader=csv.reader(f)
        for row in reader:
            for desc in row:
                print(desc)
                if desc == '':
                    break
                elif len(desc)!=0:
                    sentences.append(ast.literal_eval(desc))
    return sentences

def parse_sentences(sentence_list):
    sentence=[]
    l = len(sentence)
    for j in range(len(sentence_list)):
        # 以'.'分割句子
        word = sentence_list[j]
        if str(sentence_list[j]).find('.')!=-1:
            sentence.extend(str(sentence_list[j]).split('.') )
        if len(sentence)== l:
            sentence.append(sentence_list[j])
        l = len(sentence)

    sentence2 = []
    l = len(sentence2)
    for i in range(len(sentence)):
        word = sentence[i]
        # 以'_'分割句子
        if str(sentence[i]).find('_')!=-1:
            sentence2.extend(str(sentence[i]).split('_'))
        if len(sentence2) == l:
            sentence2.append(sentence[i])
        l = len(sentence2)
    sentence3 = []
    # 处理驼峰命名的代码元素
    for word in sentence2:
        sentence3.extend(hump(word))
    return sentence3

def sup(word):
  result=[]
  upperIndex = 0
  for i in range(len(word)):
    if word[i].isupper():
      upperIndex += 1
      continue
    else:
      break
  if upperIndex > 1 and len(word)==upperIndex:
    result.append(word)
    word=''
  elif upperIndex > 1:
    result.append(word[0:upperIndex-1])
    word = word[upperIndex-1:]
  return word,result

def hump(word):
    result = []
    word,r=sup(word)
    if len(r)!=0:
      result.extend(r)

    if len(word)==0:
      return result

    s = len(result)
    for i in range(1,len(word)):
      if word[i].isupper():
          result.append(word[:i])
          result.extend(hump(word[i:]))
          break

    if s == len(result):
      result.append(word)

    return result

def get_similarity(sentence1,sentence2,embeddings_google):
    sentence1_vec_list=[]
    sentence2_vec_list = []
    for word in sentence1:
        try:
            sentence1_vec_list.append(embeddings_google[word])
        except KeyError:
            print('can not find the word: '+word)
    for word in sentence2:
        try:
            sentence2_vec_list.append(embeddings_google[word])
        except KeyError:
            print('can not find the word: '+word)
    similarity=dot(matutils.unitvec(array(sentence1_vec_list).mean(axis=0)), matutils.unitvec(array( sentence2_vec_list).mean(axis=0)))
    return similarity

if __name__=="__main__":
    # data = ClearnData()
    # data.sentences_list()
    # embedding = Embedding()
    # vocab = embedding.build_vocab(sentences)
    # embeddings_google = embedding.load_embed('GoogleNews-vectors-negative300.bin')
    # embedding.check_coverage(vocab, embeddings_google)


    # sentences = []
    # sentences.extend(get_sentences('G:\Performance\SO_Guid_Api\matchResult\matchResult-1016\\desc_api3.csv'))
    # sentences.extend(get_sentences('G:\Performance\SO_Guid_Api\matchResult\matchResult-1016\\desc_guid3.csv'))
    #
    # sentences=parse_sentences(sentences)
    #
    # embedding = Embedding()
    # vocab = embedding.build_vocab(sentences)
    # embeddings_google = embedding.load_embed('GoogleNews-vectors-negative300.bin')
    # unknown_words =  embedding.check_coverage(vocab,embeddings_google)
    # s1=['TensorFlow', '39', 'tf.data.Dataset.shuffle', 'so', 'slow']
    # s2=['shuffle', 'step', 'in', 'code', 'works', 'slow', 'moderate', 'buffer_size', '1000']
    # # embedding = Embedding()
    # # embeddings_google = embedding.load_embed('GoogleNews-vectors-negative300.bin')
    # # print(get_similarity(s1,s2,embeddings_google))
    # print(parse_sentences([s1,s2]))

    embedding = Embedding()
    embeddings_google = embedding.load_embed('GoogleNews-vectors-negative300.bin')
    packgenames = ['gensim', 'numpy', 'pandas', 'scipy', 'sklearn', 'tensorflow']
    for packgename in packgenames:
        guid_match(packgename, embeddings_google)
        api_match(packgename, embeddings_google)

