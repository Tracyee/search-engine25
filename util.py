from datetime import date, datetime, timedelta
from typing import List
import xml.etree.ElementTree as ET
import sys
import os
import re
import pickle
from collections import Counter
from month import month
from Latimes import Latimes
from Lexicon import Lexicon
from Mapping import Mapping
from porterStemmer import PorterStemmer


def snippetEngine(raw: str, storeDir: str, mapping: Mapping):
    docNo = ""
    date = ""
    headline = ""
    if not hasattr(snippetEngine, "intId"):
        snippetEngine.intId = 0
    snippetEngine.intId += 1

    root = ET.ElementTree(ET.fromstring(raw)).getroot()
    for child in root:
        if child.tag == "HEADLINE":
            for grand in child:
                headline += grand.text

        if child.tag == "DOCNO":
            docNo = child.text.strip()
            mapping[docNo] = snippetEngine.intId
            storeDir = os.path.join(storeDir, docNo[6:8], docNo[2:4], docNo[4:6])
            date = month[docNo[2:4]] + " " + str(int(docNo[4:6])) + ", 19" + docNo[6:8]

    if not os.path.exists(storeDir):
        os.makedirs(storeDir)
    storeDir = os.path.join(storeDir, docNo + ".pkl")
    with open(storeDir, "wb") as s:
        myLatimes = Latimes(docNo, snippetEngine.intId, date, headline, raw)
        pickle.dump(myLatimes, s, pickle.HIGHEST_PROTOCOL)

    del myLatimes


def findDoc(fileName, path):
    docno = fileName[:-4]
    month = docno[2:4]
    day = docno[4:6]
    year = docno[6:8]
    targetDir = os.path.join(path, year, month, day, fileName)
    return targetDir
    # for root, dirs, files in os.walk(targetDir):
    #     if fileName in files:
    #         return os.path.join(root, fileName)


def daysDiff(d1, d2):
    """
    Input: d1, d2: string of the form YYYY-MM-DD
    Output: the difference between two dates
    Source: https://stackoverflow.com/questions/8419564/difference-between-two-dates-in-python
    """
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def getDate(start, diff):
    """
    Calculate the new date based on a starting date and the day difference.
    Input:start the starting date of the form YYYY-MM-DD
    Input:diff the day difference
    Output: the new date of the form YYYY-MM-DD
    """
    start_date = date.fromisoformat(start)
    real_date = start_date + timedelta(days=diff)
    real_date = real_date.isoformat()  # 'YYYY-MM-DD'
    return real_date


def docno2intId(docno):
    """
    Map DOCNO to internal integer ID.
    DOCNO is encoded as LAMMDDYY-NNNN where MM is the month (01-12), 
    DD is the day (01-31), YY is the year, 19YY, and NNNN is the offset.
    The mapping first calculates the difference between the date inside
    DOCNO and December 31, 1988, then concatenates the date difference 
    with the last three digits of the offset.
    """
    month = docno[2:4]
    day = docno[4:6]
    year = docno[6:8]
    offset = docno[-3:]
    intId = daysDiff("1988-12-31", "19" + year + "-" + month + "-" + day)
    intId = str(intId) + offset
    return int(intId)


def intId2docno(intId):
    """
    Map internal integer ID to DOCNO.
    Internal integer ID is encoded as DDFNNN where DDF is the date difference
    between the date inside DOCNO and December 31, 1988 and NNN is the offset. 
    """
    offset = "0" + str(intId)[-3:]
    day_diff = int(str(intId)[:-3])
    date = getDate("1989-01-01", day_diff)  # YYYY-MM-DD
    year = date[2:4]
    month = date[5:7]
    day = date[-2:]
    docno = "LA" + month + day + year + "-" + offset
    return docno


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def tokenize(text: str, stem: bool):
    """
    This function takes a string and breaks it up into "words".  
    It returns a list of these words.

    Based on SimpleTokenizer by Trevor Strohman, 
    http://www.galagosearch.org/
    """

    if not text:
        return []

    tokens = []
    text = text.lower()
    p = PorterStemmer()

    start = 0
    for i in range(len(text)):
        if not text[i].isalnum():
            if start != i:
                token = text[start:i]
                if stem:
                    token = p.stem(token, 0, len(token) - 1)
                tokens.append(token)
            start = i + 1

    if start < i:
        tokens.append(text[start:])

    return tokens


def tokens2ids(tokens: List[str], lexicon):
    token_ids = []
    for token in tokens:
        if token in lexicon:
            token_ids.append(lexicon[token])
        else:
            id = len(lexicon)
            lexicon[token] = id
            token_ids.append(id)

    return token_ids


def countWords(token_ids: List[int]):
    word_counts = Counter()
    for id in token_ids:
        if id in word_counts:
            word_counts[id] += 1
        else:
            word_counts[id] = 1

    return word_counts


def addToPosting(word_counts, docID, invIndex):
    for termid in word_counts:
        count = word_counts[termid]
        if termid not in invIndex:
            invIndex[termid] = []
        posting = invIndex[termid]
        posting.append(docID)
        posting.append(count)


def xmlParser(strBuf):
    root = ET.ElementTree(ET.fromstring(strBuf)).getroot()
    text = ""
    for child in root:
        if child.tag == "TEXT" or child.tag == "HEADLINE" or child.tag == "GRAPHIC":
            for grand in child:
                text += grand.text

    return text


def buildIndex(raw, lexicon, invIndex, doc_lens, stem):
    if not hasattr(buildIndex, "docID"):
        buildIndex.docID = 0
    buildIndex.docID += 1
    doc = xmlParser(raw)
    tokens = tokenize(doc, (stem.lower() == "true"))
    doc_lens.append(len(tokens))
    token_ids = tokens2ids(tokens, lexicon)
    word_counts = countWords(token_ids)
    addToPosting(word_counts, buildIndex.docID, invIndex)
