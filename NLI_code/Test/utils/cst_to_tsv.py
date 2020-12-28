import pandas as pd


def csv_to_tsv(csv_path, tsv_path):
    df_data = pd.read_csv(csv_path, encoding='utf-8', dtype={'index': str, 'post_id': str, 'parent_id': str})
    df_data = df_data[['index', 'project', 'kw', 'api', 'url',
                             'official_type','crowded_desc', 'official_desc', 'knowledge', 'info_type']]
    df_data.to_csv(tsv_path, encoding='utf-8', index=False, sep='\t')


def tsv_to_csv(csv_path, tsv_path):
    df_data = pd.read_csv(tsv_path, encoding='utf-8', sep='\t')
    df_data.to_csv(csv_path, encoding='utf-8', index=False)


if __name__ == "__main__":
    tsv_path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\tsv\\train.tsv"
    csv_path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\dataset\\csv\\_train.csv"
    # tsv_to_csv(csv_path, tsv_path)
    csv_to_tsv(csv_path, tsv_path)
