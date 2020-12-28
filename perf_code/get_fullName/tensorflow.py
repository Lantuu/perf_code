import csv
import re
import time

import requests
from bs4 import BeautifulSoup

requests.adapters.DEFAULT_RETRIES = 5


def get_page_body(url):
    modules_body = []
    classes_body = []
    functions_body = []

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
    headers = {'User-Agent': user_agent}
    session = requests.session()
    time.sleep(2)
    page = session.get(url=url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    body = soup.find_all('div', attrs={'class': 'devsite-article-body clearfix'})

    if str(body).find('<h2 id="other_members">Other Members</h2>') != -1:
        body = str(body).split('<h2 id="other_members">Other Members</h2>')[0]

    if str(body).find('<h2 id="functions">Functions</h2>') != -1:
        functions_body = str(body).split('<h2 id="functions">Functions</h2>')[1]
        body = str(body).split('<h2 id="functions">Functions</h2>')[0]

    if str(body).find('<h2 id="classes">Classes</h2>') != -1:
        classes_body = str(body).split('<h2 id="classes">Classes</h2>')[1]
        body = str(body).split('<h2 id="classes">Classes</h2>')[0]

    if str(body).find('<h2 id="modules">Modules</h2>')!=-1:
        modules_body = str(body).split('<h2 id="modules">Modules</h2>')[1]

    return [modules_body, classes_body, functions_body]


def body_parse(body):
    soup = BeautifulSoup(str(body), 'html.parser')
    href = soup.find_all('a')
    links = []
    for a in href:
        link = a.get('href')
        links.append(link)
    return links


def module_parse(module_link, root_name):

    full_name = []
    module_name = module_link.split('/')[-1]  # 模块名

    body = get_page_body(module_link)
    sub_modules_body = body[0]
    sub_classes_body = body[1]
    sub_functions_body = body[2]

    #  子模块
    sub_modules_links = body_parse(sub_modules_body)  # 得到所有子模块链接
    for link in sub_modules_links:
        full_name.extend(module_parse(link, root_name + '.' + module_name))

    #  子类
    sub_classes_links = body_parse(sub_classes_body)  # 得到所有子类链接
    for link in sub_classes_links:
        full_name.extend(class_parse(link, root_name + '.' + module_name))

    # 子函数
    sub_functions_links = body_parse(sub_functions_body)
    for link in sub_functions_links:
        full_name.extend(function_parse(link, root_name + '.' + module_name))

    return full_name


def class_parse(class_link, root_name):

    full_name = []
    class_name = class_link.split('/')[-1]  # 类名
    methods = get_class_methods(class_link)

    full_name.append(root_name + '.' + class_name)  # 添加类名
    for method in methods:
        full_name.append(root_name + '.' + class_name + '.' + method)

    return full_name


def function_parse(function_link, root_name):

    full_name = []
    function_name = function_link.split('/')[-1]  # 类名
    full_name.append(root_name + '.' + function_name)
    return full_name


def get_class_methods(url):
    class_methods = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}
    session = requests.session()
    time.sleep(2)
    page = session.get(url=url, headers=headers)
    body = str(page.content)

    pattern = re.compile(r'<h3 id="\w+"><code translate="no" dir="ltr">\w+</code></h3>')
    if body.find('Methods</h2>') != -1:
        body = body.split('Methods</h2>')[-1]
        body = body.split('/devsite-content')[0]
        results = pattern.findall(body)
        for r in results:
            class_methods.append(re.search(r'>\w+<', r).group()[1:-1])
    return class_methods


def sav_csv(data, save_path):
    file = open(save_path, 'a+', encoding='utf-8', newline='')
    writer = csv.writer(file)
    for d in data:
        writer.writerow([d])  # [file_path, desc, line_no, kw, url, project, version]
    file.close()


def main():

    save_path = 'D:\\work\\performance\\fullname\\1231\\tensorflow.csv'
    url = 'https://www.tensorflow.org/api_docs/python/tf'
    root_module = 'tensorflow'

    body = get_page_body(url)
    modules_body = body[0]
    classes_body = body[1]
    functions_body = body[2]

    modules_links = body_parse(modules_body)
    classes_links = body_parse(classes_body)
    functions_links = body_parse(functions_body)

    # for link in functions_links:
    #     full_name = function_parse(link, root_module)
    #     sav_csv(full_name, save_path)
    #
    #     for api in full_name:
    #         print(api)
    #
    # for link in classes_links:
    #     full_name = class_parse(link, root_module)
    #     sav_csv(full_name, save_path)
    #
    #     for api in full_name:
    #         print(api)

    for link in modules_links:
        full_name = module_parse(link, root_module)
        sav_csv(full_name, save_path)

        for api in full_name:
            print(api)

    # sav_csv(full_name, save_path)


if __name__ == "__main__":
    main()
