import ast

import pandas as pd
from APIPerfEvol.PredictEvolType.FormatDesc import FormatDesc


class PreproccessData:

    def __init__(self, csv_path, save_path, root_path):
        self.csv_path = csv_path
        self.save_path = save_path
        self.root_path = root_path
        self.csv_data = PreproccessData.reade_csv(csv_path)

    def main(self):
        one_line_desc_list = []
        format_desc_list = []
        line_start_list = []
        line_end_list = []

        for row in range(len(self.csv_data)):
            # if row != 4:
            #     continue
            project = self.csv_data['project'][row]
            sub_path = self.csv_data['filepath'][row]
            line_no = self.csv_data['lineno'][row]
            desc = PreproccessData.get_sen_desc(self.csv_data['userguide'][row])

            project_path = self.root_path + '\\' + project
            file_path = project_path + '\\' + sub_path.replace('/', '\\')

            if file_path.endswith('ipynb'):
                one_line_desc = desc
                format_desc = PreproccessData.get_ipynb_desc(desc, line_no, file_path)
                line_start = line_end = line_no
            else:
                try:
                    one_line_desc = PreproccessData.get_one_line_desc(desc, line_no, file_path)
                except:
                    one_line_desc_list.append('no')
                    format_desc_list.append('no')
                    line_start_list.append(-1)
                    line_end_list.append(-1)
                    continue
                print("###################################################")
                print(one_line_desc)
                formatDesc = FormatDesc()
                formatDesc.format_desc(one_line_desc, line_no-1, PreproccessData.read_txt(file_path))
                format_desc = formatDesc.desc
                line_start = line_no - formatDesc.line_forward
                line_end = line_no + formatDesc.line_back
                # format_desc = FormatDesc.format_desc(one_line_desc, line_no, PreproccessData.read_txt(file_path))
                # format_desc, line_start, line_end = get_format_desc(one_line_desc, line_no, file_path)
                print('')
                print(format_desc)
            one_line_desc_list.append(one_line_desc)
            if format_desc.startswith('-') or format_desc.startswith('+'):
                format_desc_list.append(' ' + format_desc)
            else:
                format_desc_list.append(format_desc)
            line_start_list.append(line_start)
            line_end_list.append(line_end)

        self.csv_data['one_line_desc'] = one_line_desc_list
        self.csv_data['format_desc'] = format_desc_list
        self.csv_data['line_start'] = line_start_list
        self.csv_data['line_end'] = line_end_list

        pd.DataFrame.to_csv(self.csv_data, self.save_path, encoding='utf_8_sig')

    @staticmethod
    def get_sen_desc(desc):
        kws = ['fast', 'slow', 'expensive', 'cheap', 'perform', 'speed', 'computation', 'accelerate', 'intensive',
               'scalab', 'efficien']
        sens = FormatDesc.token_sent(desc)

        if len(sens) == 1:
            return desc

        for sen in sens:
            sen = sen
            for kw in kws:
                if sen.lower().find(kw) != -1:
                    desc = sen
        return desc

    @staticmethod
    def get_ipynb_desc(desc, line_no, file_path):
        lines = PreproccessData.read_txt(file_path)
        line = lines[line_no - 1]
        sens = FormatDesc.token_sent(line)
        lines_desc = desc.split('\n')

        format_desc = ""
        for sen in sens:
            for d in lines_desc:
                if sen.find(d) != -1:
                    format_desc = sen
                    break
            if len(format_desc) != 0:
                break
        return format_desc

    @staticmethod
    def get_one_line_desc(desc, line_no, file_path):
        one_line_desc = ''
        lines = PreproccessData.read_txt(file_path)

        line = lines[line_no - 1]
        descs = desc.strip().split('\n')
        line_sens = FormatDesc.token_sent(line.strip())
        for line_sen in line_sens:
            line_sen = line_sen
            for desc_line in descs:
                if line_sen.lower().find(desc_line.lower().strip()) != -1:
                    one_line_desc = line_sen
                    break
            if len(one_line_desc) != 0:
                break

        if len(one_line_desc) == 0:
            raise SystemExit('ERROR GET ONE LINE DESC! ', file_path, line_no)
            # print("\033[0;32;40mERROR GET ONE LINE DESC!\033[0m")

        return one_line_desc

    @staticmethod
    def reade_csv(csv_path):
        """
        读取csv文件
        """
        csv_data = pd.read_csv(csv_path, encoding='utf-8', dtype={'lineno': int})
        return csv_data

    @staticmethod
    def read_txt(txt_path):
        """
        读txt文件
        :param txt_path: str, txt文件路径
        :return: list, 返回txt所有行
        """
        file = open(txt_path, 'r', encoding='UTF-8')
        list = file.readlines()
        file.close()
        return list


if __name__ == '__main__':
    csv_path = 'D:\\MyDocument\\performance\\git_log\\commit\\unique_commit\\userguide_commits.csv'
    save_path = 'D:\\MyDocument\\performance\\git_log\\commit\\format_commit\\userguide_commits.csv'
    root_path = 'D:\\MyDocument\\performance\\download'
    preproccess = PreproccessData(csv_path, save_path, root_path)
    preproccess.main()
    # data = PreproccessData.reade_csv(save_path)
    # for row in range(len(data)):
    #     print(row)
    #     sig = data['sig'][row]
    #     print(sig)
    #     ast.literal_eval(sig)










