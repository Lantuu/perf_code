import csv

import pandas as pd


def predict_acc_esmi(test_path, predict_path, save_path):
    predict_label = []
    with open(predict_path, "r", encoding="utf8") as f:
        predict_reader = csv.reader(f)
        for line in predict_reader:
            if line[1] == "gold_label":
                continue
            predict_label.append(line[1])

    test_label = []
    with open(test_path, "r", encoding="utf8") as f:
        test_reader = csv.reader(f)
        for line in test_reader:
            if line[9] == "info_type":
                continue
            test_label.append(line[9])

    res = []
    for i in range(len(predict_label)):
        if predict_label[i] == test_label[i]:
            res.append(1)
        else:
            res.append(-1)

    data = pd.read_csv(test_path)
    data['predict_label'] = predict_label
    data['is_correct'] = res
    data.to_csv(save_path, encoding='utf-8')


def predict_acc_bert(test_path, predict_path, save_path):

    predict_label = []
    contradiction_probability = []
    entailment_probability = []
    neutral_probability = []

    with open(predict_path, "r", encoding="utf8") as f:
        predict_reader = csv.reader(f)
        for row in predict_reader:
            contradiction_probability.append(row[0])
            entailment_probability.append(row[1])
            neutral_probability.append(row[2])
            if row[0] > row[1] and row[0] > row[2]:
                predict_label.append('contradiction')
            elif row[1] > row[0] and row[1] > row[2]:
                predict_label.append('entailment')
            else:
                predict_label.append('neutral')
    # predict_data = pd.read_csv(predict_path, sep='\t')
    # for index, row in predict_data.iterrows():
    #     contradiction_probability.append(row[0])
    #     entailment_probability.append(row[1])
    #     neutral_probability.append(row[2])
    #     if row[0] > row[1] and row[0] > row[2]:
    #         predict_label.append('contradiction')
    #     elif row[1] > row[0] and row[1] > row[2]:
    #         predict_label.append('entailment')
    #     else:
    #         predict_label.append('neutral')

    test_label = []
    with open(test_path, "r", encoding="utf8") as f:
        test_reader = csv.reader(f)
        for line in test_reader:
            if line[9] == "info_type":
                continue
            test_label.append(line[9])

    res = []
    for i in range(len(predict_label)):
        if predict_label[i] == test_label[i]:
            res.append(1)
        else:
            res.append(-1)

    data = pd.read_csv(test_path)
    data['contradiction_probability'] = contradiction_probability
    data['entailment_probability'] = entailment_probability
    data['neutral_probability'] = neutral_probability
    data['predict_label'] = predict_label
    data['is_correct'] = res
    data.to_csv(save_path, encoding='utf-8')


def csv_to_tsv(csv_path, tsv_path):
    df_data = pd.read_csv(csv_path, encoding='utf-8', dtype={'index': str})
    df_data = df_data[['index', 'project', 'kw', 'api', 'url',
                         'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    df_data.to_csv(tsv_path, encoding='utf-8', index=False, sep='\t')


def tsv_to_csv(csv_path, tsv_path):
    df_data = pd.read_csv(tsv_path, encoding='utf-8', sep='\t')
    df_data.to_csv(csv_path, encoding='utf-8', index=False)


if __name__ == "__main__":
    # test_path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\original\\csv\\_test.csv"
    # predict_path = "D:/workspace/pychram/Bert2/GLUE/glue_data/MyData/NLI_Data/esmi_data/allDataset_o/result/matched_predictions.csv"
    # save_path = "D:/workspace/pychram/Bert2/GLUE/glue_data/MyData/NLI_Data/esmi_data/allDataset_o/result/acc.csv"
    # predict_acc_esmi(test_path, predict_path, save_path)

    test_path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\original\\csv\\_test.csv"
    predict_path_tsv = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\bert_data\\allData_c\\uncased_L-12_H-768_A-12\\result\\test_results.tsv"
    predict_path_csv = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\bert_data\\allData_c\\uncased_L-12_H-768_A-12\\result\\test_results.csv"
    save_path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\bert_data\\allData_c\\uncased_L-12_H-768_A-12\\result\\acc.csv"
    tsv_to_csv(predict_path_csv, predict_path_tsv)
    predict_acc_bert(test_path, predict_path_csv, save_path)
