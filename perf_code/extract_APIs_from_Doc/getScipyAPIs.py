import csv
import re


def readTxt():
  txtPath='G:\\Performance\\scipy2.txt'
  with open(txtPath,'r') as f:
    lines=f.readlines()
  return lines

def alterTxt(lines):
    print(lines)
    txtPath = 'G:\\Performance\\scipy.txt'
    f = open(txtPath,'a+')
    for line in lines:
        if line!='\n':
            f.write(line)
    f.close()

def alterTxt2(lines):
    print(lines)
    tag=False
    txtPath = 'G:\\Performance\\scipy2.txt'
    f = open(txtPath,'a+')
    pattern=re.compile('\d+$')
    for i in range(len(lines)):
        if pattern.search(lines[i].strip()) is None:
            f.write(lines[i].replace('\n','')+lines[i+1])
            tag=True
        elif tag:
            tag=False
            continue
        else:
            f.write(lines[i])
    f.close()

#  alterTxt2(readTxt())

def saveToCsv(lines):
  for line in lines:
    fullline=line
    full_name = ''
    #name_type = ''
    pattern_name = re.compile(r'[\w\.]+')
    pattern_module=re.compile(r'[a-zA-Z]+\w*[a-zA-Z\._]*')
    name=pattern_name.match(line)

    if name is not None:
      name=name.group()
      line = line.replace(name, '')
    else:
      print('NAME ERROR!!',line)

    line = line.replace('in module','')
    line = line.replace('in modul', '')
    line = line.replace('class in', '')
    line = line.replace('in ule','')
    moduleName=pattern_module.search(line)

    if moduleName is not None:
        moduleName=moduleName.group()
        if line.find('attribute')==-1 and line.find('variable')==-1:
            if moduleName.find('.')!=-1 or moduleName == 'scipy':
                #name_type='numpy method'
                full_name=moduleName + '.' + name
            elif line.find('C function')!=-1:
                full_name = name
                #name_type='C function'
            elif line.find('ufunc')!=-1:
                full_name = name
                #name_type = 'ufunc'
            else:
                print('NOT METHOD','name : ',name,', modulename:',moduleName,' , full_name: ',full_name,', line: ', fullline)
    else:
      print('MODEL ERROR! ',fullline)

    if full_name!='':
      with open('G:\\Performance\\fullname\\scipy.csv', 'a+', encoding='gb18030', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        writer.writerow([full_name])

if __name__ == '__main__':
    saveToCsv(readTxt())