from util import tokenize, eprint
import sys, os
import json
import math
from collections import OrderedDict
from porterStemmer import PorterStemmer
from util import *


# empirical constants for BM25 algorithm
k1 = 1.2
b = 0.75
k2 = 10


def printUsage():
    eprint("Error: Invalid command line arguments")
    eprint(
        "Usage: BM25 <path to the index directory> <the queries file> <output file name> <stemming? true or false>"
    )
    sys.exit(53)


def bm25(tokens, lexicon, invIndex, mapping, docLens):
    docScores = {}

    for term in tokens:
        # calculate tf for query
        qf = tokens.count(term)
        tfQuery = ((k2 + 1) * qf) / (k2 + qf)

        # Calculate idf
        try:
            termID = lexicon[term]
        except KeyError:
            print("WARNING: token '{}' not found in lexicon".format(term))
            continue
        posting = invIndex[termID]
        N = len(mapping)
        n = len(posting) // 2  # number of documents with term i in them
        idf = math.log((N - n + 0.5) / (n + 0.5))

        # Calculate BM25 for one term in the query for each document
        for i, docID in enumerate(posting):
            if i % 2 == 0:  # docIDs are the elements at even indices
                f = posting[i + 1]  # freq. of term i in the document`
                avgDocLen = sum(docLens) / len(docLens)
                K = k1 * ((1 - b) + b * (docLens[docID - 1] / avgDocLen))
                tfDoc = ((k1 + 1) * f) / (K + f)  # calculate tf for doc
                score = tfDoc * tfQuery * idf
                if docID in docScores:
                    docScores[docID] += score
                else:
                    docScores[docID] = score
    # sort the scores for each document by their score
    docScores = OrderedDict(sorted(docScores.items(), key=lambda x: x[1], reverse=True))

    return docScores


def main():
    # total # arguments
    n = len(sys.argv)
    if n != 5:
        printUsage()

    with open(os.path.join(sys.argv[1], "mapping.pkl"), "rb") as m:
        mapping = pickle.load(m)

    with open(os.path.join(sys.argv[1], "invIndex.pkl"), "rb") as index:
        invIndex = pickle.load(index)

    with open(os.path.join(sys.argv[1], "lexicon.pkl"), "rb") as lex:
        lexicon = pickle.load(lex)

    with open(os.path.join(sys.argv[1], "doc_lens.pkl"), "rb") as lens:
        docLens = pickle.load(lens)

    # strBuff = ""
    runTag = "y237caiBM25_STEM" if sys.argv[4].lower() == "true" else "y237caiBM25"
    with open(sys.argv[2], "r") as Q:
        with open(sys.argv[3], "w") as result:
            for line in Q:
                rank = 0
                topicID = line.rstrip("\n")
                tokens = tokenize(next(Q), sys.argv[4] == "true")

                print("performing BM25 for {}".format(topicID))
                docScores = bm25(tokens, lexicon, invIndex, mapping, docLens)

                for docID, score in docScores.items():
                    # Retrieve the 1000 top ranked documents for each topic
                    if rank > 999:
                        break
                    rank += 1
                    docNO = mapping[docID]
                    result.write(
                        "{} Q0 {} {} {} {}\n".format(
                            topicID, docNO, rank, score, runTag
                        )
                    )


if __name__ == "__main__":
    main()
