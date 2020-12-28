import csv
import re

import requests
from bs4 import BeautifulSoup

def get_link(url):

  linkList=[]
  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
  headers = {'User-Agent': user_agent}
  session = requests.session()
  page = session.get(url=url, headers=headers)
  soup = BeautifulSoup(page.content, 'html.parser')
  liList=soup.find_all('li',attrs={'class':'toctree-l1'})
  for li in liList:
    a = re.search(r'<a class="reference internal" href="[\w\./]*">', str(li))
    if a is not None:
      linkList.append('https://radimrehurek.com/gensim/' + a.group().split('"')[3])
    else:
      print("GET LINK ERROR!!!")
  return linkList

def get_fullName():

  linkList=get_link('https://radimrehurek.com/gensim/apiref.html')
  for link in linkList:
    dlList = get_dl(link)
    classlist = dlList[0]
    funlist = dlList[1]
    className = get_className(classlist)
    funName = get_funName(funlist)
    for c in className:
      with open('G:\\Performance\\fullname\\gensim.csv', 'a+', encoding='gb18030', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        writer.writerow([c])

    for fun in funName:
      with open('G:\\Performance\\fullname\\gensim.csv', 'a+', encoding='gb18030', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        writer.writerow([fun])

def get_dl(url):
  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
  headers = {'User-Agent': user_agent}
  session = requests.session()
  #url = 'https://radimrehurek.com/gensim/models/ldamodel.html'
  page = session.get(url=url, headers=headers)
  soup = BeautifulSoup(page.content, 'html.parser')
  classlist = soup.find_all('dl', attrs={'class': 'class'})
  functionlist = soup.find_all('dl', attrs={'class': 'function'})
  return [classlist,functionlist]

def get_className(classlist):
  fullName=[]
  for i in classlist:
    fullName.append(get_id(i))  # 类名

    # 该类的方法
    soup = BeautifulSoup(str(i), 'html.parser')
    methodlist=soup.find_all('dl',attrs={'class':re.compile("\.*method\.*")})
    for m in methodlist:
      fullName.append(get_id(m))
  return fullName

def get_funName(functionlist):
  fullName=[]
  for f in functionlist:
    fullName.append(get_id(f))
  return fullName

def get_id(html):
  html=str(html)
  dt=re.search(r'<dt id="[\w\.]*">',html)
  if dt is not None:
    id=dt.group().split('"')[1]
  else:
    print('GET ID ERROR!!!')
  return id



if __name__ == "__main__":
    get_fullName()