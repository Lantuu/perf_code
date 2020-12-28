import re

import spacy
from nltk.tree import Tree
import pandas as pd
import ast


spacy_nlp = spacy.load('en_core_web_sm')

noun_tag = ["PROPN", "PROPN", "NOUN", "NN", "NNP", "NNS"]
noun_dep = ["nsubj", "nsubjpass", "dobj", "iobj", "pobj"]
negative_perf = ['slow', 'expensive', 'computation']
positive_perf = ['fast', 'cheap', 'perform', 'speed', 'accelerate', 'intensive', 'scalab', 'efficien']
negative_prep = ["less", "little", "low", "implication", "cost", "suboptimal", "penalty"]
perf_words = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation',
                  'accelerate', 'intensive', 'scalab', 'efficien']


def format_tuple(dic):
    neg_count = 0
    neg = 1
    for word in negative_perf:
        if word in dic['perf']:
            neg_count += 1
            break

    if 'neg' in dic.keys():
        neg_count += 1
    if 'prep' in dic.keys():
        neg_count += 1

    if 'than_api_name' in dic.keys() and dic['than_api_name'] in api_names:
        neg_count += 1

    if neg_count % 2 != 0:
        neg = -1

    api_name = None
    if 'api_name' in dic.keys() and dic["api_name"] in api_names:
        api_name = dic["api_name"]
    if 'than_api_name' in dic.keys() and dic["than_api_name"] in api_names:
        api_name = dic["than_api_name"]
    return [api_name, neg]


def perf_tuple(sent, api_names):
    doc = spacy_nlp(sent)

    per_node = []
    for token in doc:
        if match_kws(token.orth_, perf_words):
            per_node.append(token)
    res = []
    res_dic = {}

    for node in per_node:
        # 性能词
        res_dic['perf'] = node.orth_

        # 搜索名词
        res_dic["nn"] = search_nn(doc)

        # 搜索API NAME
        res_dic['api_name'] = search_api(doc, api_names)

        # 搜索than_api
        than_api_name = search_than_api(api_names, doc)
        if than_api_name:
            res_dic['than_api_name'] = than_api_name

        # 搜索否定词
        if search_neg(node):
            res_dic["neg"] = True

        # 搜索介词
        if search_prep(node):
            res_dic["prep"] = search_prep(node)

        print(res_dic)
        # res.append(format_tuple(res_dic))
        res.append(res_dic)
        res_dic.clear()
    print(res)
    return res


def search_nn(doc):
    nn = []
    for n in doc:
        if n.dep_ in noun_dep or n.tag_ in noun_tag:
            nn.append(n.orth_)
    return nn


def search_api(doc, api_names):
    apis = []
    for n in doc:
        if n.dep_ in noun_dep or n.tag_ in noun_tag:
            if match_api(n.orth_, api_names):
                apis.append(match_api(n.orth_, api_names))
    return apis


def search_than_api(api_names, doc):
    apis = []
    after_tag = False
    for n in doc:
        if n.orth_ == "than":
            after_tag = True
        if after_tag:
            if match_api(n.orth_, api_names):
                apis.append(match_api(n.orth_, api_names))
    return apis


def search_neg(node):
    # 否定词
    neg_count = 0
    neg_node = node
    while neg_node.dep_ != "ROOT":
        neg_node = neg_node.head
        for child in neg_node.children:
            if child.dep_ == "neg":
                neg_count += 1
    if neg_count % 2 != 0:
        return True
    return False


def search_prep(node):

    if node.tag_ in noun_tag and match_kws(node.orth_, positive_perf):
        if node.head != node and match_kws(node.head.orth_, negative_prep):
            return node.head.orth_

        for child in node.children:
            if match_kws(child.orth_, negative_prep):
                return child.orth_
    return None


def match_kws(word, kws):
    for kw in kws:
        if word.lower().find(kw) != -1:
            return True
    return False


def match_api(non_word, api_names):
    if re.search(r"\w+", non_word.split('.')[-1]):
        word = re.search(r"\w+", non_word.split('.')[-1]).group()
    else:
        return None

    format_api_name = [word.split(".")[-1] for word in api_names]

    for i in range(len(format_api_name)):
        if format_api_name[i] == word:
            return api_names[i]
    return None


def nltk_spacy_tree(sent):
    """
    Visualize the SpaCy dependency tree with nltk.tree
    """
    doc = spacy_nlp(sent)

    def token_format(token):
        return " ".join([token.orth_, token.tag_, token.dep_])

    def to_nltk_tree(node):
        if node.n_lefts + node.n_rights > 0:
            return Tree(token_format(node), [to_nltk_tree(child) for child in node.children])
        else:
            return token_format(node)

    tree = [to_nltk_tree(sent.root) for sent in doc.sents]
    # The first item in the list is the full tree
    tree[0].draw()


if __name__ == "__main__":
    text = "A cleaner and faster way is to load the model directly from S3 through smart_open which is used by gensim.models.KeyedVectors.load() as well as gensim.models.KeyedVectors.load_word2vec_format()."
    api_names = ['gensim.corpora.BleiCorpus.load', 'gensim.models.KeyedVectors.load_word2vec_format']
    res = perf_tuple(text, api_names)
    nltk_spacy_tree(text)