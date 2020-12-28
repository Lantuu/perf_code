import ast
import csv
import re

class CallCollector(ast.NodeVisitor):
    def __init__(self):
        self.calls = []
        self.current = None

    def visit_Call(self, node):
        # new call, trace the function expression
        self.current = ''
        self.visit(node.func)
        self.calls.append(self.current)
        self.current = None

    def generic_visit(self, node):
        if self.current is not None:
            print("warning: {} node in function expression not supported".format(
                  node.__class__.__name__))
        super(CallCollector, self).generic_visit(node)

    # record the func expression
    def visit_Name(self, node):
        if self.current is None:
            return
        self.current += node.id

    def visit_Attribute(self, node):
        if self.current is None:
            self.generic_visit(node)
        self.visit(node.value)
        self.current += '.' + node.attr


def get_apis(code):
    apis = []
    if re.match(r'^\w+$',code) is not None:
        apis.append(code)
        return apis

    try:
        root_node = ast.parse(code)
        cc = CallCollector()
        cc.visit(root_node)
        apis.extend(cc.calls)
        for i in range(len(apis)):
            if apis[i].startswith('np.'):
                apis[i] = apis[i].replace('np.', 'numpy.')

            elif apis[i].startswith('pd.'):
                apis[i] = apis[i].replace('pd.', 'pandas.')

            elif apis[i].startswith('tf.'):
                apis[i] = apis[i].replace('tf.', 'tensorflow.')

            elif apis[i].startswith('df.'):
                apis[i] = apis[i].replace('df.', 'pandas.DataFrame.')

    except:
        parttern = re.compile('[a-zA-Z]\w*\.[\w\.\-]*|\.[a-zA-Z][\w\.]*|[a-zA-Z]\w*\(')
        re_apis = parttern.findall(code)

        if len(re_apis) != 0:
            for i in range(len(re_apis)):
                if re_apis[i].startswith('np.'):
                    re_apis[i] = re_apis[i].replace('np.', 'numpy.')

                elif re_apis[i].startswith('pd.'):
                    re_apis[i] = re_apis[i].replace('pd.', 'pandas.')

                elif re_apis[i].startswith('tf.'):
                    re_apis[i] = re_apis[i].replace('tf.', 'tensorflow.')

                elif re_apis[i].startswith('df.'):
                    re_apis[i]=re_apis[i].replace('df.','pandas.DataFrame.')

                elif re_apis[i].startswith('.'):
                    re_apis[i] = re_apis[i][1:]

                elif re_apis[i][-1] == '(':
                    re_apis[i] = re_apis[i][:-1]

        elif code.startswith('numpy'):
            code = code.replace('numpy ', 'numpy.')
            re_apis.extend(parttern.findall(code))

        elif code.startswith('pandas'):
            code = code.replace('pandas ', 'pandas.')
            re_apis.extend(parttern.findall(code))

        elif code.startswith('scipy'):
            code = code.replace('scipy ', 'scipy.')
            re_apis.extend(parttern.findall(code))

        elif code.startswith('tensorflow'):
            code = code.replace('tensorflow ', 'tensorflow.')
            re_apis.extend(parttern.findall(code))

        elif code.startswith('gensim'):
            code = code.replace('gensim ', 'gensim.')
            re_apis.extend(parttern.findall(code))

        elif code.startswith('sklearn'):
            code = code.replace('sklearn ', 'sklearn.')
            re_apis.extend(parttern.findall(code))

        elif len(re_apis) == 0:
            print('*************************************************************************')
            print("not find: ", code)

        apis.extend(re_apis)

    return apis


def save_to_csv(apis,csvpath):
    with open(csvpath, 'a', newline="",encoding='gb18030') as f:
        writer = csv.writer(f)
        writer.writerow([apis])


def main(codes_list, save_csv_path):

    for codes in codes_list:
        apis = []
        for code in codes:
            apis.extend(get_apis(code))
            apis = list(set(apis))  # 去重
        save_to_csv(apis, save_csv_path)


if __name__ == "__main__":
    save_csv_path = 'D:\\work\\performance\\github_issues\\issues_desc\\extract_api\\comments_extract.csv'

    codesList=[]
    with open('D:\\work\\performance\\github_issues\\issues_desc\\desc_20_0102\\comments.csv', 'r', encoding='gb18030') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row[4])
            codesList.append(ast.literal_eval(row[4]))

    main(codesList, save_csv_path)


