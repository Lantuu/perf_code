import csv

import numpy

import nltk
from gensim import matutils
from gensim.models import KeyedVectors
from numpy import dot, array
import pandas


def main():

    csv_data=get_sentences('G:\Performance\SO_Guid_Api\matchResult\matchResult-1011\\guid_SO.csv')
    csv_data['guid_cleanData'] = csv_data['guid_desc'].apply(lambda sentence: cleanData(sentence))
    csv_data['so_cleanData'] = csv_data['so_desc'].apply(lambda sentence: cleanData(sentence))

    model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
    embeddings_google = {}
    for word, vector in zip(model.vocab, model.vectors):
        embeddings_google[word] = vector

    csv_data['similarity'] = csv_data.apply(
        lambda row: get_similarity(row['guid_cleanData'],row['so_cleanData'],embeddings_google), axis=1)

    print(csv_data['similarity'])

    csv_data.to_csv('G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_SO2.csv',mode='a',encoding='gb18030')
    # sort_similarity()

def get_sentences(filepath):
    # f = open(filepath,'r',encoding='gb18030')
    # api_desc=[]
    # so_desc=[]
    # reader = csv.reader(f)
    # for row in reader:
    #     api_desc.append(row[1])
    #     so_desc.append(row[12])
    # desc=pandas.DataFrame()
    # desc['api'] = api_desc
    # desc['so'] = so_desc
    csv_data=pandas.read_csv(filepath,encoding='gb18030')
    return csv_data

def get_similarity(sentence1,sentence2,embeddings_google):
    '''

    :param sentence1: list of word
    :param sentence2: list of word
    :param embeddings_google:
    :return:
    '''
    sentence1_vec_list=[]
    sentence2_vec_list = []

    for word in sentence1:
        try:
            sentence1_vec_list.append(embeddings_google[word])
            #print(embeddings_google[word])
        except KeyError:
            sentence1_vec_list.append(numpy.zeros(300))
            print('can not find the word: '+word)
    for word in sentence2:
        try:
            sentence2_vec_list.append(embeddings_google[word])
        except KeyError:
            sentence2_vec_list.append(numpy.zeros(300,dtype='float32'))
            print('can not find the word: '+word)
    similarity=dot(matutils.unitvec(array(sentence1_vec_list).mean(axis=0)), matutils.unitvec(array( sentence2_vec_list).mean(axis=0)))
    # print(sentence1_vec_list)
    #     # print(sentence2_vec_list)
    print(sentence1,sentence2,': ',similarity)
    return similarity

def cleanData(sentence):
    '''
    输入一个句子，取词干，去掉句子中包含的停用词，解析驼峰命名格式代码返回单词列表
    :param sentence:
    :return: 返回一个列表的列表：word_list,已经去了停用词的单词列表
    '''

    # 取词干
    word_list = nltk.word_tokenize(sentence)
    stemmer = nltk.stem.SnowballStemmer('english')
    stemm_words = [stemmer.stem(word) for word in word_list]

    # 去停用词
    stopwords = []
    f = open('G:\Performance\SO_Guid_Api\matchResult\matchResult-1012\\stopwords_en.txt', 'r', encoding='gb18030')
    reader = f.readlines()
    for word in reader:
        stopwords.append(word.strip())
        stopwords = stopwords
    extract_stop_words = [word for word in stemm_words if word.lower() not in stopwords]

    # 解析驼峰命名格式代码元素
    words = parse_sentences(extract_stop_words)

    return words

    #return word_list
    # preprocess = PreProcess()
    # preprocess.stopwordslist()
    # # for i in range(len(desc_list)):
    # #     #for j in range(len(descs_list[i])):
    # word_list = preprocess.extact_Stopwords(sentence)
    # return word_list

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

def get_id(similarityPath):
    f=open(similarityPath,'r',encoding='gb18030')
    reader=csv.reader(f)
    api_desc = ''
    ids =[]
    index=0
    for row in reader:
        if api_desc==row[2]:
            ids.append(str(index))
        else:
            api_desc = row[2]
            index=index+1
            ids.append(str(index))
    f.close()
    return ids
    # f = open('G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_SO_id.csv', 'a',encoding='gb18030', newline='')
    # writer = csv.writer(f)
    # for id in ids:
    #     writer.writerow([id])
    # f.close()

def sort_similarity(SortPath,SimilarityPath,resultPath):

    csv_data = pandas.read_csv(SimilarityPath,encoding='gb18030')
    # csv_data['id']=get_id(SimilarityPath)
    # print(csv_data['id'])
    df_sort = csv_data.groupby('id')['similarity'].nlargest(2)
    df_sort.to_csv(fileSortPath,mode='a',encoding='gb18030')

    index = []
    results=[]

    with open(SortPath,'r',encoding='gb18030') as f:
        rows=csv.reader(f)
        for row in rows:
            index.append(row[1])

    with open(SimilarityPath,'r',encoding='gb18030') as f:
        rows = csv.reader(f)
        i=0
        for row in rows:
            if row[0] == index[i]:
                results.append(row)
                i+=1

    with open(resultPath,'a',encoding='gb18030',newline='') as f:
        writer=csv.writer(f)
        for result in results:
            writer.writerow(result)



if __name__=='__main__':
    fileSortPath = 'G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_SO_similarity_sort2.csv'
    fileSimilarityPath = 'G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_SO_similarity.csv'
    resultPath = 'G:\Performance\SO_Guid_Api\matchResult\matchResult-10-22\\guid_SO_result.csv'
    #main()
    # sort_similarity()
    #get_id()
    sort_similarity(fileSortPath,fileSimilarityPath,resultPath)