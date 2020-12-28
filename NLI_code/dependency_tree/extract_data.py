import pandas as pd


def main(csv_path, save_path):
    df = pd.read_csv(csv_path, encoding='utf-8', header=0)
    df_2 = df[df["info_type"] != "neutral"]
    df_2.to_csv(save_path, index=False, mode="w",
                   header=['index', 'project', 'post_id', 'parent_id', 'post_type', 'kw', 'api', 'url',
                           'official_type', 'crowded_desc', 'official_desc', 'knowledge', 'info_type'],
                   encoding='utf-8')


if __name__ == "__main__":
    csv_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\test_data\\test_matched7.csv"
    save_path = "D:\\workspace\\pychram\\nli_project\\GLUE\\glue_data\\MyData\\dependency_data\\test.csv"
    main(csv_path, save_path)
