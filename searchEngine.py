from util import *
import os, sys
import pickle
import time
import html
from BM25 import bm25
from Latimes import Latimes
from Lexicon import Lexicon
from Mapping import Mapping
from typing import List, Dict

METADATA_DIR = "./latimes_indices"


def searchEngine(
    query: str,
    lexicon: Lexicon,
    invIndex: Dict[int, list],
    mapping: Mapping,
    docLens: List[int],
) -> List[Latimes]:
    """A wrapper routine to search for the query string in the document collection using BM25 algorithm. 

    :param query: User's query
    :type query: str
    :param lexicon: The vocabulary for the document collection
    :type lexicon: Lexicon
    :param invIndex: The inverted index for the document collection
    :type invIndex: Dict[int, list]
    :param mapping: The two-way mapping between the DOCNO and DOCID
    :type mapping: Mapping
    :param docLens: The document length of each document
    :type docLens: List[int]
    :return: A list of the top 10 ranked documents
    :rtype: List[Latimes]
    """
    startTime = time.time()
    top10DocMetas = []
    tokens = tokenize(query, False)  # no stemming
    docScores = bm25(tokens, lexicon, invIndex, mapping, docLens)

    rank = 1
    for docID, score in docScores.items():
        # Retrieve the 10 top ranked documents for each query
        if rank > 10:
            break

        docNO = mapping[docID]
        docMetaDir = findDoc(docNO + ".pkl", METADATA_DIR)
        with open(docMetaDir, "rb") as d:
            docMeta = pickle.load(d)

        snippet = queryBiasedSnippet(query, docMeta.raw)
        # If a document does not have a headline, simply use
        # the first 50 characters from the snippet and add an ellipsis
        if not docMeta.headline:
            docMeta.headline = "{}...".format(snippet[:50])
        print("{}. {}({})".format(rank, docMeta.headline.strip(), docMeta.date))
        print("{} ({})".format(snippet, docNO))
        top10DocMetas.append(docMeta)
        rank += 1

    stopTime = time.time()
    print("Retrieval took {:.3f} seconds.".format(stopTime - startTime))
    print("\n")
    return top10DocMetas


def main():
    query = input("Please enter your query: ")
    cmd = ""

    top10DocMetas = searchEngine(query, lexicon, invIndex, mapping, docLens)

    while True:
        cmd = input(
            "Please type in the rank of a document to view, or type 'N' for 'new query' or 'Q' for 'quit': "
        )
        if cmd == "Q":
            print("Terminating the search engine...")
            exit(0)

        if cmd == "N":
            main()
            break

        # user types anything other than "Q" or "N"
        try:
            docMeta = top10DocMetas[int(cmd) - 1]
            print(docMeta.raw)
        except (IndexError, ValueError) as e:
            print("Error: invalid rank number or invalid command.")


if __name__ == "__main__":
    # Loading into RAM the inverted index and some other necessary data
    with open(os.path.join(METADATA_DIR, "mapping.pkl"), "rb") as m:
        print("Loading the two-way mapping between DOCNO and DOCID...")
        mapping = pickle.load(m)

    with open(os.path.join(METADATA_DIR, "lexicon.pkl"), "rb") as lex:
        print("Loading the lexicon...")
        lexicon = pickle.load(lex)

    with open(os.path.join(METADATA_DIR, "doc_lens.pkl"), "rb") as lens:
        print("Loading the document lengths...")
        docLens = pickle.load(lens)

    with open(os.path.join(METADATA_DIR, "invIndex.pkl"), "rb") as index:
        print("Loading the inverted index...")
        invIndex = pickle.load(index)

    print("Loaded all necessary data successfully!")
    main()
