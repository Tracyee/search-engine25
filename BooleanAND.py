from util import tokenize, eprint
import sys, os
import pickle


def printUsage():
    eprint("Error: Invalid command line arguments")
    eprint(
        "Usage: BooleanAND <path to the index directory> <the queries file> <output file name>"
    )
    sys.exit(53)


def main():
    # total # arguments
    n = len(sys.argv)
    if n != 4:
        printUsage()

    with open(os.path.join(sys.argv[1], "mapping.pkl"), "rb") as m:
        mapping = pickle.load(m)

    with open(os.path.join(sys.argv[1], "invIndex.pkl"), "rb") as index:
        invIndex = pickle.load(index)

    with open(os.path.join(sys.argv[1], "lexicon.pkl"), "rb") as lex:
        lexicon = pickle.load(lex)

    strBuff = ""
    runTag = "y237caiAND"
    with open(sys.argv[2], "r") as Q:
        for line in Q:
            docCount = {}
            rank = 0
            topicID = line.rstrip("\n")
            tokens = tokenize(next(Q))
            for term in tokens:
                term_id = lexicon[term]
                posting = invIndex[str(term_id)]
                for i, docID in enumerate(posting):
                    if i % 2 == 0:  # docIDs are the elements at even indices
                        if docID in docCount:
                            docCount[docID] += 1
                        else:
                            docCount[docID] = 1

            for docID, count in docCount.items():
                if count == len(tokens):
                    rank += 1
                    docNO = mapping[str(docID)]
                    res = (
                        topicID
                        + " Q0 "
                        + docNO
                        + " "
                        + str(rank)
                        + " 1 "
                        + runTag
                        + "\n"
                    )
                    strBuff += res

    with open(sys.argv[3], "w") as result:
        result.write(strBuff)


if __name__ == "__main__":
    main()
