import sys
import os
import gzip
import re
import pickle
import json
from tqdm import tqdm
from month import month
from util import *
from Latimes import Latimes
from Lexicon import Lexicon
from Mapping import Mapping


def printUsage():
    eprint("Error: Invalid command line arguments")
    eprint(
        "Usage: indexEngine <path to the latimes.gz file> <path to the storing directory> <stemming? true or false>"
    )
    sys.exit(51)


def main():
    # total # arguments
    n = len(sys.argv)
    if n != 4:
        printUsage()

    if os.path.exists(sys.argv[2]):
        eprint(
            "Error: The storing directory already exists, please specify another directory"
        )
        sys.exit(52)

    strBuffer = ""  # buffer string to raw document
    enterRaw = False  # flag for entering the raw document
    mapping = Mapping()  # two-way mapping between DOCNO and internal integer ID
    lexicon = Lexicon()  # the lexicon (vocabulary) engine
    invIndex = {}  # the inverted indices
    doc_lens = []  # the document length list

    with gzip.open(sys.argv[1], "rt") as f:
        for line in tqdm(f):
            if re.search("^<DOC>$", line):
                enterRaw = True
                strBuffer += line
                continue

            if re.search("^</DOC>$", line):
                strBuffer += line
                enterRaw = False
                snippetEngine(strBuffer, sys.argv[2], mapping)
                buildIndex(strBuffer, lexicon, invIndex, doc_lens, sys.argv[3])
                strBuffer = ""

            if enterRaw:
                strBuffer += line

    with open(os.path.join(sys.argv[2], "mapping.pkl"), "wb") as m:
        pickle.dump(mapping, m, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join(sys.argv[2], "lexicon.pkl"), "wb") as l:
        pickle.dump(lexicon, l, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join(sys.argv[2], "invIndex.pkl"), "wb") as i:
        pickle.dump(invIndex, i, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join(sys.argv[2], "doc_lens.pkl"), "wb") as d:
        pickle.dump(doc_lens, d, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()
