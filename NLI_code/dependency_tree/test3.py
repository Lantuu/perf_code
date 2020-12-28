import os
from nltk.parse import stanford
os.environ['STANFORD_PARSER'] = 'D:/softwareInstall/python/stanford/stanford-parser-full-2018-10-17'
os.environ['STANFORD_MODELS'] = 'D:/softwareInstall/python/stanford/stanford-parser-full-2018-10-17'

parser = stanford.StanfordParser(model_path="D:/softwareInstall/python/stanford/stanford-parser-full-2018-10-17/"
                                            "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
sentences = parser.raw_parse_sents(("Hello, My name is Melroy.",
                                    "To preserve dtypes while iterating over the rows, it is better to use"
                                    " :meth:`itertuples` which returns namedtuples of the values and which is generally"
                                    " faster than ``iterrows``."))

print(sentences)
for line in sentences:
    for sentence in line:
        sentence.draw()

