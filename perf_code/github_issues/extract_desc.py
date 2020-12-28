import ast
import csv


def get_data(csv_path):
    with open(csv_path, 'r', encoding='gb18030', errors='ignore') as f:
        lines = []
        reader = csv.reader(f)
        # lines = [line for line in reader]
        for line in reader:
            print(line)
            lines.append(line)
    return lines


def save_csv(save_path, line):
    with open(save_path, 'a+', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(line)


def save_lines_csv(save_path, lines):
    with open(save_path, 'a+', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        for line in lines:
            writer.writerow([line])


def save_data(save_path, lines):
    for row in lines:
        try:
            print(row[4])
            api_list = (ast.literal_eval(row[4]))  # 包含的api
            if len(api_list) != 0:
                save_csv(save_path, row)

        except:
            print('***********************AST ERROR!***************************')
            print(row[4])


def get_issues_link(lines):
    link_list = []
    for line in lines:
        link = 'https://github.com/' + line[1] + '/issues/' + str(line[0])
        link_list.append(link)
    return link_list


def get_comments_link(lines):
    link_list = []
    for line in lines:
        link = 'https://github.com/' + line[1] + '/issues/' + str(line[0])  + '#issuecomment-' + str(line[5])
        link_list.append(link)
    return link_list


def main_link():
    comments_save_path = 'D:\\work\\performance\\github_issues\\issues_desc\\github_issues_desc_200107_2\\comments_link.csv'
    issues_save_path = 'D:\\work\\performance\\github_issues\\issues_desc\\github_issues_desc_200107_2\\issues_link.csv'
    comments_path = 'D:\\work\\performance\\github_issues\\issues_desc\\github_issues_desc_200107_2\\comments.csv'
    issues_path = 'D:\\work\\performance\\github_issues\\issues_desc\\github_issues_desc_200107_2\\issues.csv'
    comments = get_data(comments_path)
    issues = get_data(issues_path)
    comments_link = get_comments_link(comments)
    issues_link = get_issues_link(issues)
    save_lines_csv(comments_save_path, comments_link)
    save_lines_csv(issues_save_path, issues_link)


if __name__ == '__main__':
    comments_path = 'D:\\work\\performance\\github_issues\\issues_desc\\desc_20_0107_complete\\comments.csv'
    issues_path = 'D:\\work\\performance\\github_issues\\issues_desc\\desc_20_0107_complete\\issues.csv'
    comments_save_path = 'D:\\work\\performance\\github_issues\\issues_desc\\github_issues_desc_200107_2\\comments.csv'
    issues_save_path = 'D:\\work\\performance\\github_issues\\issues_desc\\github_issues_desc_200107_2\\issues.csv'
    comments = get_data(comments_path)
    issues = get_data(issues_path)
    save_data(comments_save_path, comments)
    save_data(issues_save_path,issues)
    main_link()

