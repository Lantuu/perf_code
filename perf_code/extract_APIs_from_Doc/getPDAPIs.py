import csv
import re

def readTxt():
  txtPath='G:\\Performance\\pandas.txt'
  with open(txtPath,'r') as f:
    lines=f.readlines()
  return lines

# def saveToCsv(lines):
#   for line in lines:
#     fullline=line
#     full_name = ''
#     name_type = ''
#     pattern_name = re.compile(r'\w+[a-zA-Z\._]*')
#     pattern_module=re.compile(r'[a-zA-Z]+\w*[a-zA-Z\._]*')
#     name=pattern_name.match(line)
#
#     if name is not None:
#       name=name.group()
#       line = line.replace(name, '')
#     else:
#       print('NAME ERROR!!',line)
#
#     line=line.replace('in module','')
#     line = line.replace('in modul', '')
#     line = line.replace('class in', '')
#     line = line.replace('in ule','')
#     moduleName=pattern_module.search(line)
#
#     if moduleName is not None:
#       moduleName=moduleName.group()
#       if line.find('attribute')==-1 and line.find('variable')==-1:
#         if moduleName.find('.')!=-1 or moduleName == 'numpy':
#           name_type='numpy method'
#           full_name=moduleName + '.' + name
#         else:
#           if line.find('C function')!=-1:
#             full_name = name
#             name_type='C function'
#           elif line.find('ufunc')!=-1:
#             full_name = name
#             name_type = 'ufunc'
#           else:
#             print('name : ',name,', modulename:',moduleName,' , full_name: ',full_name,', line: ', fullline)
#     else:
#       print('MODEL ERROR! ',fullline)
#     if full_name!='':
#       with open('G:\\Performance\\fullname\\numpy.csv', 'a+', encoding='gb18030', newline="") as csvfilehandler:
#         writer = csv.writer(csvfilehandler)
#         writer.writerow([full_name, name_type])

def saveToCsv(lines):
  pattern=re.compile(r'[a-zA-z0-9\._]+')
  for line in lines:
    fullname = ''
    name=pattern.match(line)
    if name is not None:
      name=name.group(0)
      if name=='11111111':
        moduleName=line.strip().split(' ')[1]
        continue
      fullname=moduleName + '.' + name
    else:
      print('NAME ERROR!!!',line)

    if fullname!='':
      with open('G:\\Performance\\fullname\\pandas.csv', 'a+', encoding='gb18030', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        writer.writerow([fullname])

if __name__ == "__main__":
  lines=readTxt()
  saveToCsv(lines)
