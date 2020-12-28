import spacy
import networkx as nx
from spacy import displacy
from matplotlib import pyplot as plt
from nltk import Tree


# edges = []

# for token in doc:
#     for child in token.children:
#         edges.append(('{0}'.format(token.lower_),
#                       '{0}'.format(child.lower_)))
#
# graph = nx.Graph(edges)
# print('shortest path lenth: ', nx.shortest_path_length(graph, source=entity1, target=entity2))
# print('shortest path: ',nx.shortest_path(graph, source=entity1, target=entity2))

# displacy.serve(doc)
# nx.draw_networkx(graph)
# plt.show()

# perf_token = []
# for token in doc:
#     if token.text == 'efficient':
#         # words.append(token.text)
#         # # t = token.head
#         # while token is not None:
#         #     if token.dep_ == "neg":
#         #         words.append(token.head.text)
#         #     if token.dep_ == "nsubj":
#         #         words.append(token.head.text)
#         #         break
#         #     token = token.head
#         # break
#         perf_token.append(token)
#         break
#
#     print('{0}({1}) <-- {2} -- {3}({4})'.format(token.text, token.tag_, token.dep_, token.head.text, token.head.tag_))
#
# for token in perf_token:
#     word = []


# displacy.serve(doc, style='dep')


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


if __name__ == "__main__":
    text = "fit_transform may be more convenient and efficient for modelling and transforming the training data simultaneously."
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    print("sentence:", format(doc))
    [to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]

