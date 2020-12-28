import pandas as pd


def reade_csv(file_path):
    """
    读取csv文件
    :param file_path: str
    :return:
    """
    df = pd.read_csv(file_path, encoding='utf_8_sig')
    return df


def main(df1, df2):
    pd.eval()
    note_list = []
    for index2, row2 in df2.iterrows():
        note2 = ''
        docstring2 = row2['desc']
        commit_id2 = row2['id']
        line_no2 = row2['line_no']
        project2 = row2['project']
        sig2 = row2['sigs']
        type2 = row2['type']
        # 	docstring	commit	lineno	filepath	project	sig	type	note
        for index1, row1 in df1.iterrows():
            docstring1 = row1['userguide']
            commit_id1 = row1['commit']
            line_no1 = row1['lineno']
            project1 = row1['project']
            sig1 = row1['sig']
            type1 = row1['type']
            note1 = row1['note']
            if commit_id2 == commit_id1 and line_no2 == line_no1 and project2 == project1 and sig2 == sig1 and type2 == type1:
                note2 = note1
                break
        note_list.append(note2)
    df2['note'] = note_list
    return df2


if __name__ == '__main__':
    path_commit = 'D:\\MyDocument\\performance\\git_log\\commit\\userguide_commits.csv'
    path_commit_correct = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\userguide_evol\\userguide_evo1.csv'
    save_path = 'D:\\MyDocument\\performance\\git_log\\auto_evol_0327\\userguide_evol\\userguide_evo1_note.csv'
    df1 = reade_csv(path_commit)
    df2 = reade_csv(path_commit_correct)
    pf = main(df1, df2)
    pf.to_csv(save_path, encoding='utf_8_sig')
