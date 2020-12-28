import csv


def get_2_co_occurrence(column_index, input_path):
    knowledge_list = []

    with open(input_path, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for line in reader:
            knowledge_str = line[column_index]
            if knowledge_str == "knowledge":
                continue
            for k in knowledge_str.split(","):
                if k not in knowledge_list:
                    knowledge_list.append(k)
    print(knowledge_list)

    for one in range(len(knowledge_list)):
        knowledge_one = knowledge_list[one]
        for two in range(one+1, len(knowledge_list)):
            count = 0
            knowledge_two = knowledge_list[two]

            with open(input_path, "r", encoding="utf8") as f:
                reader = csv.reader(f)
                for line in reader:
                    knowledge_type = line[column_index]

                    if knowledge_type.find(knowledge_one) != -1 and knowledge_type.find(knowledge_two) != -1:
                        count += 1
                print(knowledge_list[one], knowledge_list[two], count)


if __name__ == "__main__":
    input_path = "D:\\workspace\\perf_DataSet\\201112_perf\\stackoverflow_perf_concerns.csv"
    # knowledge_list = ["alternatives", "attributes", "environment", "functionality", "practice", "references",
    #                   "rationale", "impl", "directives", "attributes"]
    column_index = 12
    get_2_co_occurrence(column_index, input_path)

    # str_1 = "123"
    # str_2 = "3"
    # print(str_1.find(str_2))
    # if str_1.find(str_2) != -1:
    #     print("Yes")
    # else:
    #     print("No")

