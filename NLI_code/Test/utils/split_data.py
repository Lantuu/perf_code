import ast
import os

import numpy
import pandas as pd


def to_csv(file_path):
    df_data = pd.read_csv(file_path, encoding='utf-8',
                          dtype={'project': str, 'desc': str, 'kw': str,
                                 'api': str, 'docstrings': str, 'docstrings_urls': str, 'userguide': str,
                                 'guide_urls': str, 'info_type': str, 'knowledge': str}
                          )
    df_save = pd.DataFrame(columns=['index', 'project', 'kw', 'api', 'url',
                                    'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type'])
    dic_save = {'index': 0}

    for index, row in df_data.iterrows():
        print(row)
        list_docstring = []
        list_userguide = []
        print(row['docstrings'])
        if not pd.isna(row['docstrings']) and row['docstrings'] != "":
            list_docstring = ast.literal_eval(row['docstrings'])
        if not pd.isna(row['userguide']) and row['userguide'] != "":
            list_userguide = ast.literal_eval(row['userguide'])

        if len(list_docstring) == 0 and len(list_userguide) == 0:
            continue

        dic_save['project'] = str(row['project'])
        dic_save['crowded_desc'] = strip_str(str(row['desc']))
        dic_save['kw'] = str(row['kw'])
        dic_save['api'] = str(row['api'])
        dic_save['knowledge'] = row['knowledge']

        if row['info_type'] == 'additional':
            dic_save['info_type'] = 'neutral'
        elif row['info_type'] == 'consistent':
            dic_save['info_type'] = 'entailment'
        else:
            dic_save['info_type'] = 'contradiction'

        list_docstring_url = []
        list_guide_url = []
        if not pd.isna(row['docstrings_urls']) and row['docstrings_urls'] != "":
            list_docstring_url = ast.literal_eval(row['docstrings_urls'])
        if not pd.isna(row['guide_urls']) and row['guide_urls'] != "":
            list_guide_url = ast.literal_eval(row['guide_urls'])

        print('==================docstring========================')
        for i in range(len(list_docstring)):
            dic_save['official_desc'] = strip_str(str(list_docstring[i]))
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
            dic_save['official_desc'] = strip_str(str(list_userguide[i]))
            if len(list_guide_url) > i:
                dic_save['url'] = str(list_guide_url[i]).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            else:
                dic_save['url'] = ''
            dic_save['official_type'] = 'userguide'
            df_save = df_save.append(dic_save, ignore_index=True)
            dic_save['index'] = dic_save['index'] + 1
            # print(dic_save['official_desc'])
    return df_save


def to_csv2(file1, file2, save_path):
    df_save1 = to_csv(file1)
    df_save2 = to_csv(file2)
    df_save = pd.concat([df_save1, df_save2])
    df_save.to_csv(save_path, index=False, mode="w",
                   header=['index', 'project', 'kw', 'api', 'url',
                           'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type'],
                   encoding='utf-8')


def strip_str(s):
    """
    去掉多余空格和换行符
    :param s: 需格式化的字符串
    :return:格式化后字符串
    """
    # print("old=======", s)
    format_s = ""
    for word in s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').split(' '):
        if word != '':
            format_s = format_s + ' ' + word
    format_s = format_s[1:]
    # print("new=======", s)
    return ' ' + format_s


def split_data_frac(input_path, target_dir):
    df_data = pd.read_csv(input_path, encoding='utf-8', dtype={'index': str, 'post_id': str, 'parent_id': str})
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

    train_data = pd.concat([train_neutral, train_entailment, train_contradiction]).sample(frac=1)  # .sample(frac=1, axis=0)
    test_data = pd.concat([test_neutral, test_entailment, test_contradiction]).sample(frac=1)  # .sample(frac=1, axis=0)
    dev_data = pd.concat([dev_neutral, dev_entailment, dev_contradiction]).sample(frac=1)  # .sample(frac=1, axis=0)

    train_data = train_data[['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    test_data = test_data[['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    dev_data = dev_data[['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]

    train_data.to_csv(os.path.join(target_dir, "_train.csv"), encoding='utf-8', index=False)
    test_data.to_csv(os.path.join(target_dir, "_test.csv"), encoding='utf-8', index=False)
    dev_data.to_csv(os.path.join(target_dir, "_dev.csv"), encoding='utf-8', index=False)


def split_data_head(input_path, target_dir):
    df_data = pd.read_csv(input_path, encoding='utf-8', dtype={'index': str})
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

    train_neutral = neutral_data.head(int(len(neutral_data)*0.6))
    neutral_data = neutral_data[~neutral_data['index'].isin(train_neutral['index'])]
    test_neutral = neutral_data.head(int(len(neutral_data)*0.5))
    dev_neutral = neutral_data[~neutral_data['index'].isin(test_neutral['index'])]

    train_entailment = entailment_data.head(int(len(entailment_data)*0.6))
    entailment_data = entailment_data[~entailment_data['index'].isin(train_entailment['index'])]
    test_entailment = entailment_data.head(int(len(entailment_data)*0.5))
    dev_entailment = entailment_data[~entailment_data['index'].isin(test_entailment['index'])]

    train_contradiction = contradiction_data.head(int(len(contradiction_data)*0.6))
    contradiction_data = contradiction_data[~contradiction_data['index'].isin(train_contradiction['index'])]
    test_contradiction = contradiction_data.head(int(len(contradiction_data)*0.5))
    dev_contradiction = contradiction_data[~contradiction_data['index'].isin(test_contradiction['index'])]
    print(len(dev_contradiction))

    train_data = pd.concat([train_neutral, train_entailment, train_contradiction]).sample(frac=1)
    test_data = pd.concat([test_neutral, test_entailment, test_contradiction]).sample(frac=1)
    dev_data = pd.concat([dev_neutral, dev_entailment, dev_contradiction]).sample(frac=1)

    train_data = train_data[['index', 'project', 'kw', 'api', 'url',
                             'official_type','crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    test_data = test_data[['index', 'project', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    dev_data = dev_data[['index', 'project', 'kw', 'api', 'url',
                             'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]

    train_data.to_csv(os.path.join(target_dir, "_train.csv"), encoding='utf-8', index=False)
    test_data.to_csv(os.path.join(target_dir, "_test.csv"), encoding='utf-8', index=False)
    dev_data.to_csv(os.path.join(target_dir, "_dev.csv"), encoding='utf-8', index=False)


if __name__ == "__main__":
    # file_path1 = 'D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\original\\github_perf_concerns.csv'
    # file_path2 = 'D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\original\\stackoverflow_perf_concerns.csv'
    # save_path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\perf_pair.csv"
    # to_csv2(file_path1, file_path2, save_path)

    input_path = 'D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\perf_pair.csv'
    target_dir = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\csv"
    # split_data_frac(input_path, target_dir)
    split_data_head(input_path, target_dir)



