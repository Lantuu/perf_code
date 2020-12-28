import csv
import re

import requests
from bs4 import BeautifulSoup

def get_page(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
    headers = {'User-Agent': user_agent}
    session = requests.session()
    page = session.get(url=url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def get_modules(url):
    soup = get_page(url)
    body = soup.find('div',attrs={'class':'section','id':'api-reference'})
    soup = BeautifulSoup(str(body), 'html.parser')
    modules = soup.find_all('div', attrs={'class':'section','id':re.compile('^module-sklearn.[\w]+$')})
    modules.insert(3,soup.find('div',attrs={'class':'section','id':'module-sklearn.cluster.bicluster'}))
    modules.insert(23, soup.find('div', attrs={'class': 'section', 'id': 'sklearn-metrics-metrics'}))
    modules.append(soup.find('div',attrs={'class':'section','id':'recently-deprecated'}))
    return(modules)

def module_parse(module):
    soup = BeautifulSoup(str(module),'html.parser')
    tables = soup.find_all('tbody')
    for table in tables:
        apis = BeautifulSoup(str(table),'html.parser').find_all('span', attrs={'class': 'pre'})
        for api in apis:
            api = 'sklearn.'+ str(BeautifulSoup(str(api), 'html.parser').get_text())
            save_to_csv(api)
            print(api)

            if re.match(r'^[A-Z]',api.split('.')[-1]) is not None:
                url = 'https://scikit-learn.org/stable/modules/generated/' + api + '.html'
                classe_parse(url, api)

def classe_parse(url,moduleName):
    soup=get_page(url)
    body = soup.find_all('dd')
    if str(body).find('<p class="rubric">Methods</p>')!=-1:
        body=str(body).split('<p class="rubric">Methods</p>')[1]
        table=BeautifulSoup(body,'html.parser').find('tbody')
        apis = BeautifulSoup(str(table), 'html.parser').find_all('span', attrs={'class': 'pre'})
        for api in apis:
            api = moduleName + '.' + str(BeautifulSoup(str(api), 'html.parser').get_text())
            save_to_csv(api)
            print(api)

def save_to_csv(fullname):
    with open('G:\\Performance\\fullname\\sklearn4.csv','a+',encoding='gb18030',newline='') as f:
        writer=csv.writer(f)
        writer.writerow([fullname])

if __name__=='__main__':
    modules = get_modules('https://scikit-learn.org/stable/modules/classes.html')
    for i in range(len(modules)-21):
        module_parse(modules[i+21])