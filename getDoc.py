import sys
import os
import gzip
import re
import pickle
from month import month
from Latimes import Latimes
from util import intId2docno, eprint, findDoc


def printUsage():
    eprint("Error: Invalid command line arguments")
    eprint(
        "Usage: getDoc <path to the stored directory> <string 'id' or 'docno'> <the internal integer id or a DOCNO>"
    )
    sys.exit(53)


def main():
    # total # arguments
    n = len(sys.argv)
    if n != 4:
        printUsage()

    import json

    with open(os.path.join(sys.argv[1], "mapping.pkl"), "rb") as m:
        mapping = pickle.load(m)

    if sys.argv[2] == "docno":
        docNo = sys.argv[3]
    else:
        docNo = mapping[sys.argv[3]]

    doc = findDoc(docNo + ".pkl", sys.argv[1])

    with open(doc, "rb") as d:
        myLatimes = pickle.load(d)

    print(myLatimes)


if __name__ == "__main__":
    main()
