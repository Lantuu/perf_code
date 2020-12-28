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


def get_body(url):
  modules = []
  classes = []
  functions = []

  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
  headers = {'User-Agent': user_agent}
  session = requests.session()
  page = session.get(url=url, headers=headers)
  soup = BeautifulSoup(page.content, 'html.parser')

  #soup = get_page(url)
  body = soup.find_all('div',attrs={'class':'devsite-article-body clearfix'})

  if str(body).find('<h2 id="other_members">Other Members</h2>') != -1:
      body = str(body).split('<h2 id="other_members">Other Members</h2>')[0]

  if str(body).find('<h2 id="functions">Functions</h2>') != -1:
    functions = str(body).split('<h2 id="functions">Functions</h2>')[1]
    body = str(body).split('<h2 id="functions">Functions</h2>')[0]

  if str(body).find('<h2 id="classes">Classes</h2>') != -1:
    classes = str(body).split('<h2 id="classes">Classes</h2>')[1]
    body = str(body).split('<h2 id="classes">Classes</h2>')[0]

  if str(body).find('<h2 id="modules">Modules</h2>')!=-1:
    modules = str(body).split('<h2 id="modules">Modules</h2>')[1]

  return [modules,classes,functions]


def modules_parse(modules,moduleName):
    fullname=[]
    moduleNamelist=[]
    soup = BeautifulSoup(str(modules), 'html.parser')
    body = soup.find_all('p')
    for p in body:
        moduleNamelist.append(BeautifulSoup(str(p), 'html.parser').find('code').text)
        modulename = BeautifulSoup(str(p), 'html.parser').find('code').text
        urllist = re.findall(r'"https://[\w\._/]+"',str(p))
        for url in urllist:
            url=url.replace('"','')
            body=get_body(url)
            classes_parse(body[1], moduleName + '.' + modulename)
            fun_parse(body[2], moduleName + '.' + modulename)
            # if len(body[1])!=0:
            #     fullname.extend(classes_parse(body[1], moduleName+'.'+modulename))
            # if len(body[2])!=0:
            #     fullname.extend(fun_parse(body[2], moduleName+'.'+modulename))
        print(url)
    return fullname


def classes_parse(classes,moduleName):
    #fullname=[]
    soup = BeautifulSoup(str(classes), 'html.parser')
    body = soup.find_all('p')
    for p in body:
        className = BeautifulSoup(str(p), 'html.parser').find('code').text.split(' ')[1]
        save_to_csv(moduleName+'.'+className)
        #fullname.append(moduleName+'.'+className)
        url = re.search(r'"https://[\w\._/]+"',str(p)).group().replace('"','')

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}
        session = requests.session()
        page = session.get(url=url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        body = soup.find_all('div', attrs={'class': 'devsite-article-body clearfix'})
        if str(body).find('<h2 id="methods">Methods</h2>')!=-1:
            body = str(body).split('<h2 id="methods">Methods</h2>')[1]
            soup = BeautifulSoup(body, 'html.parser')
            h3List = soup.find_all('h3')
            for h3 in h3List:
                methodName=BeautifulSoup(str(h3), 'html.parser').find('code').text
                save_to_csv(moduleName+'.'+className+'.'+methodName)
                #fullname.append(moduleName+'.'+className+'.'+methodName)
        else:
            print('NO!!!!     ',className,'   ',url)

        print(url)
    #return fullname


def fun_parse(functions,moduleName):
    #fullname=[]
    soup = BeautifulSoup(str(functions), 'html.parser')
    body = soup.find_all('p')
    for p in body:
        funname = BeautifulSoup(str(p), 'html.parser').find('code').text.replace('(...)','')
        save_to_csv(moduleName+'.'+funname)
        #fullname.append(moduleName+'.'+funname)
    #return fullname


def save_to_csv(fullname):
    with open('G:\\Performance\\fullname\\tensorflow.csv','a+',encoding='gb18030',newline='') as f:
        writer=csv.writer(f)
        writer.writerow([fullname])


if __name__ == "__main__":
    body = get_body('https://tensorflow.google.cn/versions/r1.13/api_docs/python/tf')
    modules_parse(body[0],'tensorflow')
    classes_parse(body[1],'tensorflow')
    fun_parse(body[2],'tensorflow')
    # print('*****************************************************************')
    # print("moduleslen: ",len(modules),modules)
    # print('*****************************************************************')
    # print("classes: ",len(classes),classes)
    # print('*****************************************************************')
    # print("funs: ",len(funs),funs)
