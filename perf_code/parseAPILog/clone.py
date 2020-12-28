import re
import sys
import git
import os
import csv
#repo = git.Repo(r'G:\Performance\projects-clone')
#print(repo.bare)
#repo = git.Repo(r'G:\Performance\clone\pandas')
#repo = git.Repo(r'G:\Performance\clone\pandas')
#repo = git.Repo.clone_from(url='https://github.com/tensorflow/docs.git',to_path='G:\\Performance\\clone\\docs')
#repo = git.Repo.clone_from(url='https://github.com/tensorflow/tensorflow.git',to_path='G:\\Performance\\clone\\tensorflow')

# GIT_LOG=r'git -C {} log -p -u -L 283,283:pandas/core/algorithms.py > {}'
GIT_LOG=r'git -C {} log -p -u -L {},{}:{}> {}'
GIT_LOG1=r'git -C {} checkout tags/{}'

Repo_Root='G:\\Performance\\clone'
Doc_Root='G:\\Performance\\doc'
Log_Root='G:\\Performance\\log'

def clone():
    urls=['https://github.com/tensorflow/tensorflow.git',]
    for url in urls:
        path='G:\\Performance\\clone\\'+url.split('\.')[-2]
        print(path)
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        git.Repo.clone_from(url=url,to_path=path)

def finalResult(repo_root,doc_root,log_root):
    '''处理所有文件'''
    #logfile='G:\\Performance\\log\\logfile.txt'
    repoList=os.listdir(repo_root)
    for repodir in repoList:
        repo=repo_root+'\\'+repodir
        csv_api_doc=doc_root+'\\'+repodir+'_api_doc_caveats.csv'
        readcsv(csv_api_doc, repo, repodir)

def readcsv(csv_api_doc,repo,repodir):
    '''读取csv文件，处理csv文件的desc'''
    with open(csv_api_doc,'r',encoding='utf-8') as f:
        reader=csv.reader(f)
        STATS={}
        logfile = 'G:\\Performance\\log\\logfile.txt'
        for row in reader:
            tag = re.search(r'/(.*)\d+\.(.*)\d+/', row[6]).group(0).split('/')[-2]
            print('当前版本：',tag)
            lines=exec_git(repo,row[2],row[0],logfile,tag)
            stats=parse(lines,row[1],row[3])
            for stats_key in stats.keys():
                STATS[stats_key] = [stats[stats_key],row[1]]#STATS[id]=[type,dec]
            savecsv(STATS, Log_Root + '\\' + repodir + '.csv',row[6])
            STATS={}

def str_split(str):
    '''分割url 得到该句子的行号line和该句子在repo中的路径'''
    url=str.split('#')[0]
    #line=str.split('#')[1].split('L')[1]#句子的行号
    path=url.split(re.match(r'(.*)/(.*)\d(.*)\.(.*)\d/',url).group(0))[1]#句子在repo中的路径
    return(path)

def exec_git(repo,line,path,logfile,tag):
    '''执行git命令'''
    git_log_command1 = GIT_LOG1.format(repo, tag)
    git_log_command=GIT_LOG.format(repo,line,line,path,logfile)
    os.system(git_log_command1)
    os.system(git_log_command)
    with open (logfile,'r',encoding='UTF-8') as logfilehandler:
        lines=logfilehandler.readlines()
    return(lines)

def savecsv(stats, csv_log, url):
    '''save stats data to csv file.'''
    #CSV_LOG_HEADER = ["desc", "CommitID", "type"]
    with open(csv_log, 'a+', encoding='utf-8',newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        #writer.writerow(CSV_LOG_HEADER)
        for key in stats.keys():
            writer.writerow([ stats[key][1],key, stats[key][0],url])#[dec,commitID,type]

def parse(lines,desc,kw):
    '''Analyse git log '''
    desc=desc.lower().strip()  # 把字符串的大写字母变成小写字母，去除开头结尾多余的空格和换行符
    #desc=desc.lower().strip()  # 把字符串的大写字母变成小写字母，去除开头结尾多余的空格和换行符
    desc2=' '.join(desc.split())  # 去掉多余的空格
    kw = kw.replace('(', '').replace(')', '').replace("'","")  # 替换kw中的（‘’）
    kwList = kw.split(',')  # 把keyword变成列表
    stats = {}  # id:type,id为commit的id，type为修改的类型(add，delete，alter)
    id=type=None
    i=54
    '''分析是否有改变特定的desc，改动的类型是什么'''
    while i<len(lines):
        line=lines[i].lower()
        if re.match(r'commit',line):#lines[i].startswith('commit'):
            if type is not None:
                stats[id] = type
            id=line.split(' ')[1].strip()
            type=None
            i = i + 1
            continue
        elif line.startswith('@@ '):
            delete=add=' '  # add: commit 中增加的语句, delete: commit 中删除的语句
            i=i+1
            while i<len(lines):
                line = lines[i].lower()
                if line.startswith('-'):
                    while i < len(lines):
                        line = lines[i].lower()
                        if line.startswith('-'):
                            delete = delete + line.strip()[1:].strip() + ' '
                            i = i + 1
                        elif line.startswith('  '):
                            delete=delete+line.strip()
                            i=i+1
                        else:
                            break
                    continue
                elif line.startswith('+'):
                    while i < len(lines):
                        line = lines[i].lower()
                        if line.startswith('+'):
                            add = add + line.strip()[1:].strip() + ' '
                            i = i + 1
                        elif line.startswith('  '):
                            add=add+line.strip()
                            i=i+1
                        else:
                            break
                    continue
                elif re.match(r'commit', line):  # 匹配到下一个commit时，检查delete和add中是否含有desc，保存type
                    delete2=' '.join(delete.split())
                    add2=' '.join(add.split())
                    d = delete.find(desc2)
                    a = add.find(desc2)
                    if delete2.find(desc2)!=-1 and add2.find(desc2)==-1:
                        type='alter'
                        break
                    elif delete2.find(desc2)==-1 and add2.find(desc2)!=-1:
                        type='add'
                        break
                    else:
                        break
                else:
                    i=i+1
        else:
            i=i+1

    # 得到最后一个commit中desc的type
    if id is not None :
        if delete.find(desc2) != -1 and add.find(desc2) == -1:
            type = 'alter'
        elif delete.find(desc2) == -1 and add.find(desc2) != -1:
            type = 'add'

    # 当这个desc没有找到对应的commit时，就分割这个desc，重新匹配
    if len(stats)==0:
        descList=desc.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].lower()
            if re.match(r'commit', line):  # lines[i].startswith('commit'):
                if type is not None:
                    stats[id] = type
                id = line.split(' ')[1].strip()
                type = None
                i = i + 1
                continue
            elif line.startswith('@@ '):
                delete = add = ' '
                i = i + 1
                while i < len(lines):
                    line = lines[i].lower()
                    if line.startswith('-'):
                        while i < len(lines):
                            line=lines[i].lower()
                            if line.startswith('-'):
                                delete = delete + line.strip()[1:].strip() + ' '
                                i = i + 1
                            elif line.startswith('  '):
                                delete = delete + line.strip()
                                i = i + 1
                            else:
                                break
                        continue
                    elif line.startswith('+'):
                        while i < len(lines):
                            line = lines[i].lower()
                            if line.startswith('+'):
                                add = add + line.strip()[1:].strip() + ' '
                                i = i + 1
                            elif line.startswith('  '):
                                add = add + line.strip()
                                i = i + 1
                            else:
                                break
                        continue
                    elif re.match(r'commit', line):
                        if '' in kwList:
                            kwList.remove('')
                        type = matchDesc(kwList, descList, type, delete, add)
                        break
                    else:
                        i = i + 1
            else:
                i = i + 1

    # 得到最后一个commit中desc的type
    if id is not None:
        descList = desc.split('\n')
        type=matchDesc(kwList,descList,type,delete,add)

    #保存最后一个commit的记录
    if type is not None:
        stats[id]=type

    if len(stats)==0:
        id='no'
        type='no'
        stats[id]=type
    return stats

def matchDesc(kwList,descList,type,delete,add):
    '''根据换行符拆分desc, 分别匹配 子desc 得到type类型'''
    for d in descList:
        d=d.strip()
        for w in kwList:
            if d.find(w) != -1:
                # t = delete.find(d)
                # p = add.find(d)
                # print(t,p)
                if delete.find(d)!=-1 and add.find(d)==-1:
                    type = 'alter'
                    break
                elif delete.find(d)==-1 and add.find(d)!=-1:
                    type = 'add'
                    break

        if type is not None:
            break
    return type

if __name__=="__main__":
    # REPO = r'G:\Performance\clone\pandas'  # 仓库的路径
    # logfile = r'G:\Performance\log\logfile.txt'  # 暂存pase的结果
    # CSV_API_DOC = r'G:\Performance\projects-documentation\pandas_api_doc_caveats.csv'  # documentation的路径
    # CSV_LOG = r'G:\Performance\log\pandas.csv'
    # STATS=readcsv(CSV_API_DOC,REPO,logfile)
    # savecsv(STATS,CSV_LOG)
    # print(STATS)
    Repo_Root = 'G:\\Performance\\clone'
    Doc_Root = 'G:\\Performance\\doc'
    Log_Root = 'G:\\Performance\\log'
    #finalResult(Repo_Root,Doc_Root,Log_Root)
    readcsv('G:\\scipy.csv','G:\\Performance\\clone\\scipy','scipy2')