import ast
import csv
import fnmatch
import os
import pickle
import string

import pandas as pd

from esim.data import Preprocessor


def main(inputdir,
         embeddings_file,
         targetdir,
         lowercase=False,
         ignore_punctuation=False,
         num_words=None,
         stopwords=[],
         labeldict={},
         bos=None,
         eos=None):
    """
        Preprocess the data from the SNLI corpus so it can be used by the
        ESIM model.
        Compute a worddict from the train set, and transform the words in
        the sentences of the corpus to their indices, as well as the labels.
        Build an embedding matrix from pretrained word vectors.
        The preprocessed data is saved in pickled form in some target directory.

        Args:
            inputdir: The path to the directory containing the NLI corpus.
            embeddings_file: The path to the file containing the pretrained
                word vectors that must be used to build the embedding matrix.
            targetdir: The path to the directory where the preprocessed data
                must be saved.
            lowercase: Boolean value indicating whether to lowercase the premises
                and hypotheseses in the input data. Defautls to False.
            ignore_punctuation: Boolean value indicating whether to remove
                punctuation from the input data. Defaults to False.
            num_words: Integer value indicating the size of the vocabulary to use
                for the word embeddings. If set to None, all words are kept.
                Defaults to None.
            stopwords: A list of words that must be ignored when preprocessing
                the data. Defaults to an empty list.
            bos: A string indicating the symbol to use for beginning of sentence
                tokens. If set to None, bos tokens aren't used. Defaults to None.
            eos: A string indicating the symbol to use for end of sentence tokens.
                If set to None, eos tokens aren't used. Defaults to None.
        """

    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

        # Retrieve the train, dev and test data files from the dataset directory.
    train_file = ""
    dev_file = ""
    test_file = ""
    for file in os.listdir(inputdir):
        if fnmatch.fnmatch(file, "*_train.csv"):
            train_file = file
        elif fnmatch.fnmatch(file, "*_dev.csv"):
            dev_file = file
        elif fnmatch.fnmatch(file, "*_test.csv"):
            test_file = file
    preprocessor = Preprocessor(lowercase=lowercase,
                                ignore_punctuation=ignore_punctuation,
                                num_words=num_words,
                                stopwords=stopwords,
                                labeldict=labeldict,
                                bos=bos,
                                eos=eos)

    # -------------------- Train data preprocessing -------------------- #
    print(20*"=", " Preprocessing train set ", 20*"=")
    print("\t* Reading data...")
    data = read_data(os.path.join(inputdir, train_file), lowercase, ignore_punctuation, stopwords)
    # data = preprocessor.read_data(os.path.join(inputdir, train_file))

    print("\t* Computing worddict and saving it...")
    preprocessor.build_worddict(data)
    with open(os.path.join(targetdir, "worddict.pkl"), "wb") as pkl_file:
        pickle.dump(preprocessor.worddict, pkl_file)

    print("\t* Transforming words in premises and hypotheses to indices...")
    transformed_data = preprocessor.transform_to_indices(data)
    print("\t* Saving result...")
    with open(os.path.join(targetdir, "train_data.pkl"), "wb") as pkl_file:
        pickle.dump(transformed_data, pkl_file)

    # -------------------- Validation data preprocessing -------------------- #
    print(20*"=", " Preprocessing dev set ", 20*"=")
    print("\t* Reading data...")
    # data = preprocessor.read_data(os.path.join(inputdir, dev_file))
    data = read_data(os.path.join(inputdir, dev_file), lowercase, ignore_punctuation, stopwords)

    print("\t* Transforming words in premises and hypotheses to indices...")
    transformed_data = preprocessor.transform_to_indices(data)
    print("\t* Saving result...")
    with open(os.path.join(targetdir, "dev_data.pkl"), "wb") as pkl_file:
        pickle.dump(transformed_data, pkl_file)

    # -------------------- Test data preprocessing -------------------- #
    print(20*"=", " Preprocessing test set ", 20*"=")
    print("\t* Reading data...")
    # data = preprocessor.read_data(os.path.join(inputdir, test_file))
    data = read_data(os.path.join(inputdir, test_file), lowercase, ignore_punctuation, stopwords)

    print("\t* Transforming words in premises and hypotheses to indices...")
    transformed_data = preprocessor.transform_to_indices(data)
    print("\t* Saving result...")
    with open(os.path.join(targetdir, "test_data.pkl"), "wb") as pkl_file:
        pickle.dump(transformed_data, pkl_file)

    # -------------------- Embeddings preprocessing -------------------- #
    print(20*"=", " Preprocessing embeddings ", 20*"=")
    print("\t* Building embedding matrix and saving it...")
    embed_matrix = preprocessor.build_embedding_matrix(embeddings_file)
    with open(os.path.join(targetdir, "embeddings.pkl"), "wb") as pkl_file:
        pickle.dump(embed_matrix, pkl_file)


def read_data(filepath, lowercase, ignore_punctuation, stopwords):
    """
    Read the premises, hypotheses and labels from some NLI dataset's
    file and return them in a dictionary. The file should be in the same
    form as SNLI's .txt files.

    Args:
        filepath: The path to a file containing some premises, hypotheses
            and labels that must be read. The file should be formatted in
            the same way as the SNLI (and MultiNLI) dataset.
        lowercase: A boolean indicating whether the words in the datasets
            being preprocessed must be lowercased or not. Defaults to
            False.
        ignore_punctuation: A boolean indicating whether punctuation must
            be ignored or not in the datasets preprocessed by the object.
        stopwords: A list of words that must be ignored when building the
                worddict for a dataset. Defaults to an empty list.

    Returns:
        A dictionary containing three lists, one for the premises, one for
        the hypotheses, and one for the labels in the input data.
    """
    with open(filepath, "r", encoding="utf8") as input_data:
        ids, premises, hypotheses, labels = [], [], [], []

        # Translation tables to remove parentheses and punctuation from
        # strings.
        # parentheses_table = str.maketrans({"(": None, ")": None})
        punct_table = str.maketrans({key: " "
                                        for key in string.punctuation})

        # Ignore the headers on the first line of the file.
        reader = csv.reader(input_data)
        # next(input_data)

        for line in reader:
            if line[0] == "index":
                continue
            pair_id = line[0]
            premise = line[6]
            hypothesis = line[7]

            # Remove '(' and ')' from the premises and hypotheses.
            # premise = premise.translate(parentheses_table)
            # hypothesis = hypothesis.translate(parentheses_table)

            if lowercase:
                premise = premise.lower()
                hypothesis = hypothesis.lower()

            if ignore_punctuation:
                premise = premise.translate(punct_table)
                hypothesis = hypothesis.translate(punct_table)

            # Each premise and hypothesis is split into a list of words.
            premises.append([w for w in premise.rstrip().split()
                                 if w not in stopwords])
            hypotheses.append([w for w in hypothesis.rstrip().split()
                                   if w not in stopwords])
            labels.append(line[9])
            ids.append(pair_id)

        return {"ids": ids,
                "premises": premises,
                "hypotheses": hypotheses,
                "labels": labels}


if __name__ == "__main__":
    # D:\workspace\pychram\Bert2\GLUE\glue_data\MyData\NLI_Data\esmi_data\dataset
    inputdir = "D:/workspace/pychram/Bert2/GLUE/glue_data/MyData/NLI_Data/dataset/original/csv"
    targetdir = "D:/workspace/pychram/Bert2/GLUE/glue_data/MyData/NLI_Data/esmi_data/allDataset_c/dataSet"
    embeddings_file = "D:\\workspace\\pychram\\Bert2\\ESIM-master\\data\\embeddings\\glove.840B.300d.txt"
    main(inputdir,
         embeddings_file,
         targetdir,
         lowercase=True,
         ignore_punctuation=False,
         num_words=None,
         stopwords=[],
         labeldict={"entailment": 0,
                    "neutral": 1,
                    "contradiction": 2},
         bos="_BOS_",
         eos="_EOS_")
