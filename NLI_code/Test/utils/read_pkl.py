from spacy.compat import pickle


def reader(input_path):
    f = open(input_path, 'rb')
    data = pickle.load(f)

    print(data)
    print(len(data))


if __name__ == "__main__":
    path = "D:\\workspace\\pychram\\Bert2\\GLUE\\glue_data\\MyData\\NLI_Data\\esmi_data\\premodel_mnli\dataset\\test_data.pkl"
    reader(path)
