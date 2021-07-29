from util import tokenize, eprint
import sys, os
import pickle


def main():
    with open(os.path.join(sys.argv[1], "mapping.pkl"), "rb") as m:
        mapping = pickle.load(m)

    with open(os.path.join(sys.argv[1], "invIndex.pkl"), "rb") as index:
        invIndex = pickle.load(index)

    with open(os.path.join(sys.argv[1], "lexicon.pkl"), "rb") as lex:
        lexicon = pickle.load(lex)

    with open(os.path.join(sys.argv[1], "doc_lens.pkl"), "rb") as lens:
        doc_lens = pickle.load(lens)

    print("Number of documents in the LATimes dataset: {}".format(len(mapping)))
    print("Lexicon length: {}".format(len(lexicon)))
    print("Doc_lens length: {}".format(len(doc_lens)))
    print("invIndex length: {}".format(len(invIndex)))

    cellNo = 0
    for term, posting in invIndex.items():
        cellNo += len(posting)
        # maxI = max(posting[::2])
        for i in range(0, len(posting), 2):
            try:
                docLen = doc_lens[posting[i]]
            except IndexError:
                print("IndexError at index {}".format(posting[i]))
                exit(1)

        # docLen = [doc_lens[p] for p in posting]
    print("Total posting length: {}".format(cellNo))
    # print("max Index: {}".format(maxI))


if __name__ == "__main__":
    main()
