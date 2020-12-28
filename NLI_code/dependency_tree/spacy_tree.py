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


def main(input_path, save_path):
    df = pd.read_csv(input_path, encoding='utf-8', header=0)
    crowded_sentence_list = df['crowded_desc']
    official_sentence_list = df['official_desc']
    info_type_list = df['info_type']
    api_name_list = df['api']

    res = []
    crowded_tuple = []
    official_tuple = []

    for i in range(len(crowded_sentence_list)):
        print("###################################################################################")
        api_name = ast.literal_eval(api_name_list[i])

        crowded_sentence = " ".join(crowded_sentence_list[i].replace(":meth:", " ").replace("`", ' ').replace("~", ' ').split())
        crowded = perf_tuple(crowded_sentence, api_names)
        crowded_tuple.append(crowded)

        official_sentence = " ".join(official_sentence_list[i].replace(":meth:", " ").replace("`", ' ').replace("~", ' ').split())
        official = perf_tuple(official_sentence, api_names)
        official_tuple.append(official)

        print(api_name)
        print("crowded:", crowded_sentence[i])
        print("crowded:", crowded)

        print("official:", official_sentence[i])
        print("official:", official)
        print(info_type_list[i])

        temp_res = ""
        for c in crowded:
            if not c[0]:
                continue
            for o in official:
                if c[0] == o[0]:
                    if c[1] == o[1]:
                        temp_res = "entailment"
                    elif int(c[1]) == -int(o[1]):
                        temp_res = "contradiction"
                if c[0] != o[0]:
                    if c[1] == o[1]:
                        temp_res = "contradiction"
                    elif int(c[1]) == -int(o[1]):
                        temp_res = "entailment"
                if temp_res != "":
                    break
            if temp_res != "":
                break

        if temp_res != "":
            res.append(temp_res)
        else:
            res.append("neutral")
        print(res[-1])

    eval = []
    for i in range(len(res)):
        if res[i] == info_type_list[i]:
            eval.append(1)
        else:
            eval.append(-1)

    print(len(res))
    df['rule'] = res
    df['eval'] = eval
    df['crowded_tuple'] = crowded_tuple
    df['official_tuple'] = official_tuple
    df.to_csv(save_path, mode="w", encoding='utf-8')


def perf_tuple(sent, api_names):

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

        # 搜索API NAME
        res_dic['api_name'] = search_api(node, api_names)

        # 搜索than_api
        than_api_name = search_than_api(node, api_names)
        if than_api_name:
            res_dic['than_api_name'] = than_api_name

        # 搜索否定词
        if search_neg(node):
            res_dic["neg"] = True

        # 搜索介词
        if search_prep(node):
            res_dic["prep"] = search_prep(node)

        print(res_dic)
        res.append(format_tuple(res_dic))
        res_dic.clear()
    return res


def search_api(node, api_names):

    def post_order(n):
        nonlocal nn_tag

        for child in n.lefts:
            post_order(child)

        for child in n.rights:
            post_order(child)

        if n.dep_ in noun_dep or n.tag_ in noun_dep:
            nn_tag = True
            if match_api(n.orth_, api_names):
                res.append(match_api(n.orth_, api_names))

        if n.tag_ in ["PN", "PRP", "WP"]:
            pronouns.append(n.orth_)

    nn_tag = False
    pronouns = []  # 保存后序遍历检索到的代词
    res = []  # 保存后序遍历检索到的api

    # 找到非名词根节点
    root = node
    while root.head != root and root.tag_ in noun_tag:
        root = root.head

    # 后序遍历树 检索api
    post_order(root)

    if len(res) != 0:
        return res[0]
    # elif len(pronouns) != 0 or not nn_tag:  # 检索到代词，或是没有检索到名词
    #     return api_names[0]
    else:
        return None


def search_than_api(node, api_names):

    def pre_order(n):
        if n.dep_ in noun_dep or n.tag_ in noun_tag:
            if match_api(n.orth_, api_names):
                res.append(match_api(n.orth_, api_names))

        for child in n.lefts:
            pre_order(child)

        for child in n.rights:
            pre_order(child)

    res = []
    pre_order(node)

    if len(res) > 0:
        return res[0]
    else:
        return None


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


def mid_travel(node):
    for child in node.lefts:
        mid_travel(child)
    print(node.orth_)
    for child in node.rights:
        mid_travel(child)


if __name__ == "__main__":
    text = "you may use this argument instead of `documents` to get performance boost"
    kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation',
           'accelerate', 'intensive', 'scalab', 'efficien']
    api_names = ['pandas.DataFrame.iterrows']
    res = perf_tuple(text, api_names)
    # print(res)
    # nltk_spacy_tree(text)
    # save_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\dependency_data\\res4.csv"
    # # csv_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\dependency_data\\test.csv"
    # csv_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\test_data\\test_matched7.csv"
    # main(csv_path, save_path)
