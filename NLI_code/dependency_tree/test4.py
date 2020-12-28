
from nltk.tree import Tree
from stanfordcorenlp import StanfordCoreNLP
sentence = 'This converts the rows to Series objects, which can change the dtypes and has some\r\n   performance implications.'
sen2 = "To preserve dtypes while iterating over the rows, it is better to use :meth:`itertuples`" \
       " which returns namedtuples of the values and which is generally faster than ``iterrows``."
sen3 = "This does not mean that dynamic_rnn is less performant, the documentation says that the parameter sequence_length will not affect the performance because the computation is already dynamic."
nlp = StanfordCoreNLP(r'D:\softwareInstall\python\stanford\stanford-corenlp-4.1.0', lang='en')
Tree.fromstring(nlp.parse(sen3)).draw()

# print(tree)
