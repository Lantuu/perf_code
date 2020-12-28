import re
import os
import csv
GIT_LOG=r'git -C {} log -p -u -L {},{}:{}> {}'
GIT_LOG2=r'git -C {} log -p {}> {}'
GIT_LOG1=r'git -C {} checkout tags/{}'
#GIT_LOG1=r'git -C {} checkout {}'

# Repo_Root='G:\\Performance\\clone'
# Doc_Root='G:\\Performance\\project-doc'
# Log_Root='G:\\Performance\\doc-log'

def finalResult(repo_root,doc_root):
    '''处理所有文件'''
    repoList=os.listdir(repo_root)
    for repodir in repoList:
        repo=repo_root+'\\'+repodir
        csv_api_doc=doc_root+'\\'+repodir+'_api_doc_caveats.csv'
        readcsv(csv_api_doc, repo, repodir)

def readcsv(csv_api_doc,repo,repodir):
    '''读取csv文件，处理csv文件的desc'''
    with open(csv_api_doc,'r',encoding='utf-8',errors="ignore") as f:
        reader=csv.reader(f)
        logfile = 'G:\\Performance\\doc-log\\logfile.txt'
        tag=''
        for row in reader:
            url_list=row[4].split('/')
            filepath_list=row[0].split('/')
            for i in range(len(url_list)):
                if url_list[i]==filepath_list[0]:
                    tag=url_list[i-1]
                    break
                #tag = re.search(r'/(.*)\d+\.(.*)\d+/', row[4]).group(0).split('/')[-2]
            print('当前版本：',tag)
            lines=exec_git(repo,row[2],row[0],logfile,tag)
            STATS=parse(lines,row[1],row[3])
            savecsv(STATS, Log_Root + '\\' + repodir + '.csv',row[4],row[1])

def str_split(str):
    '''分割url 得到该句子的行号line和该句子在repo中的路径'''
    url=str.split('#')[0]
    #line=str.split('#')[1].split('L')[1]#句子的行号
    path=url.split(re.match(r'(.*)/(.*)\d(.*)\.(.*)\d/',url).group(0))[1]#句子在repo中的路径
    return(path)

def exec_git(repo,line,path,logfile,tag):
    '''执行git命令'''
    git_log_command1 = GIT_LOG1.format(repo, tag)
    # low=str(int(line)-20)
    # high=str(int(line)+20)
    git_log_command=GIT_LOG.format(repo,line,line,path,logfile)
    #git_log_command = GIT_LOG.format(repo, path, logfile)
    os.system(git_log_command1)
    os.system(git_log_command)
    with open (logfile,'r',encoding='UTF-8') as logfilehandler:
        lines=logfilehandler.readlines()
    return(lines)

def savecsv(stats, csv_log, url,desc):
    '''save stats data to csv file.'''
    #CSV_LOG_HEADER = ["desc", "CommitID", "type"]
    with open(csv_log, 'a+', encoding='utf-8',newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        #writer.writerow(CSV_LOG_HEADER)
        for stat in stats:
            writer.writerow([ desc,stat[0], stat[1],url])#[dec,commitID,type,url]

def parse(lines,desc,kw):
    '''Analyse git log '''
    delete = add = ' '
    desc=desc.lower().strip()  # 把字符串的大写字母变成小写字母，去除开头结尾多余的空格和换行符
    #desc = desc.strip()
    desc2=' '.join(desc.split())  # 去掉多余的空格
    kw = kw.replace('[', '').replace(']', '').replace("'","")  # 替换kw中的（‘’）
    kwList = kw.split(',')  # 把keyword变成列表
    if '' in kwList: #去除空的关键词
        kwList.remove('')
    stats = []  # id:type,id为commit的id，type为修改的类型(add，delete，alter)
    id=type=None
    i=0
    '''分析是否有改变特定的desc，改动的类型是什么'''
    while i<len(lines):
        descList = desc.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].lower()
            #line = lines[i]
            if re.match(r'commit', line):  # lines[i].startswith('commit'):
                if type is not None:
                    stats.append((id, type))
                id = line.split(' ')[1].strip()
                type = None
                i = i + 1
                continue
            elif line.startswith('@@ ') and type is None:
                delete = add = ' '
                i = i + 1
                while i < len(lines):
                    line = lines[i].lower()
                    #line = lines[i]
                    if line.startswith('-'):
                        delete = delete + line.strip()[1:].strip() + ' '
                        #delete=delete.lower()
                        i = i + 1
                        continue
                    elif line.startswith('+'):
                        add = add + line.strip()[1:].strip() + ' '
                       #add=add.lower()
                        i = i + 1
                    #     while i < len(lines):
                    #         line = lines[i].lower()
                    #         if line.startswith('+'):
                    #             add = add + line.strip()[1:].strip() + ' '
                    #             add2 = add2 + line.strip()[1:].strip() + ' '
                    #             i = i + 1
                    #         elif line.startswith('  '):
                    #             add2 = add2 + line.strip()
                    #             i = i + 1
                    #         else:
                    #             break
                        continue
                    elif re.match(r'commit', line):
                        if delete.find(desc2) != -1 and add.find(desc2) == -1:
                            type = 'formating'
                        if type is not None:
                            stats.append((id, type))
                            type=None
                        type = matchDesc(kwList, descList, type, delete, add)
                        break
                    else:
                        i = i + 1
            elif line.startswith('@@ ') and type is not None:
                #stats[id] = type
                stats.append((id,type))
                type = None
                continue
            else:
                i = i + 1

    if id is not None:
        if delete.find(desc2) != -1 and add.find(desc2) == -1:
            type = 'formating'
        if type is not None:
            stats.append((id, type))
            type = None
        descList = desc.split('\n')
        type=matchDesc(kwList,descList,type,delete,add)

    #保存最后一个commit的记录
    if type is not None:
        stats.append((id, type))

    #查看每条desc是否有对应的add
    if len(stats)==0:
        id = 'no'
        type = 'no'
        stats.append((id, type))
    else:
        for i in range(len(stats)):
            if stats[i][1] is 'add':
                break
            elif i==len(stats)-1:
                id='no'
                type='no'
                stats.append((id, type))
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
    Doc_Root = 'G:\\Performance\\projects-doc2'
    Log_Root = 'G:\\Performance\\doc-log'
    finalResult(Repo_Root,Doc_Root)
    #readcsv('G:\\Performance\\projects-doc2\\docs-r1.13.csv','G:\\Performance\\clone\\docs','tensorflow3')