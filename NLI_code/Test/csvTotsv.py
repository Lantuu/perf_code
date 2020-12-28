import ast
import re

import nltk
import pandas as pd
import numpy


def csv_to_tsv():
    csv_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\oringinal\\stackoverflow_perf_concerns.csv'
    save_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\test_data\\test_matched7.csv'

    pd_data = pd.read_csv(csv_path, encoding='utf-8',
                          dtype={'project': str, 'id': str, 'parent_id': str, 'post_type': str, 'desc': str, 'kw': str,
                                 'api': str, 'docstrings': str, 'docstrings_urls': str, 'userguide': str,
                                 'guide_urls': str, 'info_type': str, 'knowledge': str}
                          )
    df_save = pd.DataFrame(columns=['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                                    'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type'])
    dic_save = {'index': 0}

    for index, row in pd_data.iterrows():
        print(row)
        list_docstring = ast.literal_eval(row['docstrings'])
        list_userguide = ast.literal_eval(row['userguide'])

        if len(list_docstring) == 0 and len(list_userguide) == 0:
            continue

        dic_save['project'] = str(row['project'])
        dic_save['post_id'] = str(row['id'])
        dic_save['parent_id'] = str(row['parent_id'])
        dic_save['post_type'] = str(row['post_type'])
        dic_save['crowded_desc'] = format_desc(str(row['desc']))
        dic_save['kw'] = str(row['kw'])
        dic_save['api'] = str(row['api'])
        dic_save['knowledge'] = row['knowledge']

        if row['info_type'] == 'additional':
            dic_save['info_type'] = 'neutral'
        elif row['info_type'] == 'consistent':
            dic_save['info_type'] = 'entailment'
        else:
            dic_save['info_type'] = 'contradiction'

        list_docstring_url = ast.literal_eval(row['docstrings_urls'])
        list_guide_url = ast.literal_eval(row['guide_urls'])

        print('==================docstring========================')
        for i in range(len(list_docstring)):
            dic_save['official_desc'] = format_desc(str(list_docstring[i]))
            if len(list_docstring_url) > i:
                dic_save['url'] = str(list_docstring_url[i]).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            else:
                dic_save['url'] = ''
            dic_save['official_type'] = 'docstring'
            df_save = df_save.append(dic_save, ignore_index=True)
            dic_save['index'] = dic_save['index'] + 1
            # print(dic_save['official_desc'])

        print('==================userguide========================')
        for i in range(len(list_userguide)):
            dic_save['official_desc'] = format_desc(str(list_userguide[i]))
            if len(list_guide_url) > i:
                dic_save['url'] = str(list_guide_url[i]).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            else:
                dic_save['url'] = ''
            dic_save['official_type'] = 'userguide'
            df_save = df_save.append(dic_save, ignore_index=True)
            dic_save['index'] = dic_save['index'] + 1
            # print(dic_save['official_desc'])

    df_save.to_csv(save_path, index=False, mode="w",
                   header=['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                           'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type'],
                   encoding='utf-8')


def format_desc(desc):
    print("old=======", desc)
    temp_desc = ""
    for word in desc.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').split(' '):
        if word != '':
            temp_desc = temp_desc + ' ' + word
    desc = temp_desc[1:]
    # for word in nltk.word_tokenize(desc):
    #     if word != '':
    #         desc = desc.replace(word, split_word(word))
    print("new=======", desc)
    return ' ' + desc


def split_word(word):
    def _sub_symbol(matched):
        return ' ' + matched.group("symbol")[1:]

    def _sub_camel_case(matched):
        return matched.group("camelCase")[:-1] + ' ' + matched.group("camelCase")[-1]

    def _sub_number(matched):
        return matched.group("number")[:-1] + ' ' + matched.group("number")[-1]

    replaced_str = re.sub("(?P<symbol>(\.[a-zA-Z]+)|(_[a-zA-Z]+))", _sub_symbol, word)
    replaced_str = re.sub("(?P<camelCase>[a-z0-9]+[A-Z])", _sub_camel_case, replaced_str)
    replaced_str = re.sub("(?P<number>[a-zA_Z]+[0-9])", _sub_number, replaced_str)
    return replaced_str


def get_mismatched_words():
    csv_path = 'D:\\MyDocument\\Pychrom\\nli_project\\GLUE\\glue_data\\MyData\\test_matched.csv'
    vocab_path = 'D:\\MyDocument\\Pychrom\\nli_project\\GLUE\\BERT_BASE_DIR\\uncased_L-12_H-768_A-12\\vocab.txt'
    save_path = 'D:\\MyDocument\\Pychrom\\nli_project\\GLUE\\glue_data\\MyData\\words_mismatched4.txt'
    vocab_list = []
    words_mismatched = []

    with open(vocab_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        vocab_list.append(line.replace("\n", ''))

    pd_data = pd.read_csv(csv_path, encoding='utf-8', dtype={'project': str, 'post_id': str, 'parent_id': str})

    for index, row in pd_data.iterrows():
        desc = row['crowded_desc'] + ' ' + row['official_desc']
        words = []

        for word in nltk.word_tokenize(desc):
            if word != '':
                words.extend(split_word(word).split(' '))

        for word in words:
            word = word.lower()
            if word != '' and word not in vocab_list and "##" + word not in vocab_list and word not in words_mismatched:
                words_mismatched.append(word)

    with open(save_path, 'w', encoding='utf-8') as f:
        for word in words_mismatched:
            f.write(word + '\n')


def predict_accuracy():
    result_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\predict\\MNLI_MY3\\test_results.tsv'
    test_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData2\\test.tsv'
    save_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\predict\\MNLI_MY3\\test_accuracy.csv'

    classify = []
    result = pd.read_csv(result_path, sep='\t')
    for index, row in result.iterrows():
        if row[0] > row[1] and row[0] > row[2]:
            classify.append('contradiction')
        elif row[1] > row[0] and row[1] > row[2]:
            classify.append('entailment')
        else:
            classify.append('neutral')

    classify_result = []
    data = pd.read_csv(test_path, sep='\t')
    for index, row in data.iterrows():
        if row['info_type'] == classify[index]:
            classify_result.append(1)
        else:
            classify_result.append(0)

    data['contradiction_probability'] = result['contradiction_probability']
    data['entailment_probability'] = result['entailment_probability']
    data['neutral_probability'] = result['neutral_probability']
    data['predict_type'] = classify
    data['is_correct'] = classify_result
    data.to_csv(save_path, encoding='utf-8')


def split_data():
    data_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\test_data\\test_matched6.tsv"
    save_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\train_data\\'
    df_data = pd.read_csv(data_path, encoding='utf-8', sep='\t')
    neutral_data = pd.DataFrame()
    entailment_data = pd.DataFrame()
    contradiction_data = pd.DataFrame()

    for index, row in df_data.iterrows():
        if row['info_type'] == 'neutral':
            neutral_data = neutral_data.append(row)
        elif row['info_type'] == 'entailment':
            entailment_data = entailment_data.append(row)
        else:
            contradiction_data = contradiction_data.append(row)

    train_neutral = neutral_data.sample(frac=0.8, axis=0)
    neutral_data = neutral_data[~neutral_data['index'].isin(train_neutral['index'])]
    test_neutral = neutral_data.sample(frac=0.6, axis=0)
    dev_neutral = neutral_data[~neutral_data['index'].isin(test_neutral['index'])]

    train_entailment = entailment_data.sample(frac=0.8, axis=0)
    entailment_data = entailment_data[~entailment_data['index'].isin(train_entailment['index'])]
    test_entailment = entailment_data.sample(frac=0.6, axis=0)
    dev_entailment = entailment_data[~entailment_data['index'].isin(test_entailment['index'])]

    train_contradiction = contradiction_data.sample(frac=0.8, axis=0)
    contradiction_data = contradiction_data[~contradiction_data['index'].isin(train_contradiction['index'])]
    test_contradiction = contradiction_data.sample(frac=0.6, axis=0)
    dev_contradiction = contradiction_data[~contradiction_data['index'].isin(test_contradiction['index'])]

    train_data = pd.concat([train_neutral, train_entailment, train_contradiction])  # .sample(frac=1, axis=0)
    test_data = pd.concat([test_neutral, test_entailment, test_contradiction])  # .sample(frac=1, axis=0)
    dev_data = pd.concat([dev_neutral, dev_entailment, dev_contradiction])  # .sample(frac=1, axis=0)

    train_data.to_csv(save_path + "train.tsv", encoding='utf-8', sep='\t')
    test_data.to_csv(save_path + "test.tsv", encoding='utf-8', sep='\t')
    dev_data.to_csv(save_path + "dev.tsv", encoding='utf-8', sep='\t')


def split_data2():
    data_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\test_data\\test_matched6.tsv"
    save_path = 'D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData2\\train_data\\'
    df_data = pd.read_csv(data_path, encoding='utf-8', sep='\t', dtype={'index': str, 'post_id': str, 'parent_id': str})

    neutral_data = pd.DataFrame()
    entailment_data = pd.DataFrame()
    contradiction_data = pd.DataFrame()

    for index, row in df_data.iterrows():
        if row['info_type'] == 'neutral':
            neutral_data = neutral_data.append(row)
        elif row['info_type'] == 'entailment':
            entailment_data = entailment_data.append(row)
        else:
            contradiction_data = contradiction_data.append(row)

    train_neutral = neutral_data.head(int(len(neutral_data)*0.8))
    neutral_data = neutral_data[~neutral_data['index'].isin(train_neutral['index'])]
    test_neutral = neutral_data.head(int(len(neutral_data)*0.6))
    dev_neutral = neutral_data[~neutral_data['index'].isin(test_neutral['index'])]

    train_entailment = entailment_data.head(int(len(entailment_data)*0.8))
    entailment_data = entailment_data[~entailment_data['index'].isin(train_entailment['index'])]
    test_entailment = entailment_data.head(int(len(entailment_data)*0.6))
    dev_entailment = entailment_data[~entailment_data['index'].isin(test_entailment['index'])]

    train_contradiction = contradiction_data.head(int(len(contradiction_data)*0.8))
    contradiction_data = contradiction_data[~contradiction_data['index'].isin(train_contradiction['index'])]
    test_contradiction = contradiction_data.head(int(len(contradiction_data)*0.6))
    dev_contradiction = contradiction_data[~contradiction_data['index'].isin(test_contradiction['index'])]
    print(len(dev_contradiction))

    train_data = pd.concat([train_neutral, train_entailment, train_contradiction]).sample(frac=1)
    test_data = pd.concat([test_neutral, test_entailment, test_contradiction]).sample(frac=1)
    dev_data = pd.concat([dev_neutral, dev_entailment, dev_contradiction]).sample(frac=1)

    train_data = train_data[['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                             'official_type','crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    test_data = test_data[['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    dev_data = dev_data[['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]

    train_data.to_csv(save_path + "train.tsv", encoding='utf-8', sep='\t', index=False)
    test_data.to_csv(save_path + "test.tsv", encoding='utf-8', sep='\t', index=False)
    dev_data.to_csv(save_path + "dev.tsv", encoding='utf-8', sep='\t', index=False)


if __name__ == '__main__':
    # nltk.download()
    csv_to_tsv()
    # preprocess_sentence()
    # predict_accuracy()
    # split_data()
    # split_data2()


