from util import *
import os, sys
import pickle
import time
from BM25 import bm25
from Latimes import Latimes
from Lexicon import Lexicon
from Mapping import Mapping
from typing import List, Dict
import sys
from PyQt5.QtWidgets import (
    QWidget,
    QScrollArea,
    QMainWindow,
    QToolTip,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QGridLayout,
    QApplication,
    QDesktopWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication, Qt

METADATA_DIR = "./latimes_indices"


class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)


class RawDocumentPage(QWidget):
    def __init__(self, docString):
        super().__init__()

        self.docString = docString
        self.initUI()

    def initUI(self):
        # QToolTip.setFont(QFont("SansSerif", 10))

        # self.qbtn = QPushButton("Quit", self)
        # self.qbtn.clicked.connect(QCoreApplication.instance().quit)
        # self.qbtn.resize(self.qbtn.sizeHint())

        # self.qbtn.setToolTip("Click to <b>quit</b>")

        self.raw = QLabel("Raw document")
        self.rawDoc = ScrollLabel()
        self.rawDoc.setText(self.docString)

        self.raw.setFont(QFont("Helvetica", 14, QFont.Bold))
        self.rawDoc.setFont(QFont("TypeWriter", 12))

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.raw, 1, 0)
        grid.addWidget(self.rawDoc, 1, 1, 10, 1)

        # grid.addWidget(self.qbtn, 10, 5)

        self.setLayout(grid)

        self.setGeometry(500, 500, 1000, 1000)
        self.center()
        self.setWindowTitle("Raw Document Page")

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class SearchEngineGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.top10DocMetas = []
        self.dialog = None
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont("SansSerif", 10))

        self.sbtn = QPushButton("Search", self)
        self.nbtn = QPushButton("New Query", self)
        self.qbtn = QPushButton("Quit", self)
        self.qbtn.clicked.connect(QCoreApplication.instance().quit)
        self.qbtn.resize(self.qbtn.sizeHint())

        self.sbtn.clicked.connect(self.buttomClicked)
        self.nbtn.clicked.connect(self.buttomClicked)

        self.sbtn.setToolTip("Click to <b>Search</b>")
        self.nbtn.setToolTip("Click to <b>Start a new query</b>")
        self.qbtn.setToolTip("Click to <b>quit</b>")

        self.query = QLabel("Query")
        self.result = QLabel("Result")
        self.timeCost = QLabel()
        self.resultSummary = ScrollLabel()

        self.queryEdit = QLineEdit()

        self.query.setFont(QFont("Helvetica", 14, QFont.Bold))
        self.result.setFont(QFont("Helvetica", 14, QFont.Bold))
        self.resultSummary.setFont(QFont("TypeWriter", 12))
        self.timeCost.setFont(QFont("TypeWriter", 12))
        self.sbtn.setFont(QFont("Cursive", 14, QFont.Bold))
        self.nbtn.setFont(QFont("Cursive", 14, QFont.Bold))
        self.qbtn.setFont(QFont("Cursive", 14, QFont.Bold))
        self.queryEdit.setFont(QFont("System", 14))

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.query, 1, 0)
        grid.addWidget(self.queryEdit, 1, 1)

        grid.addWidget(self.timeCost, 2, 1)
        grid.addWidget(self.result, 3, 0)
        grid.addWidget(self.resultSummary, 3, 1, 10, 1)

        grid.addWidget(self.sbtn, 1, 5)
        grid.addWidget(self.nbtn, 10, 5)
        grid.addWidget(self.qbtn, 11, 5)

        self.setLayout(grid)

        self.setGeometry(500, 500, 1000, 1000)
        self.center()
        self.setWindowTitle("Search Engine")
        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def buttomClicked(self):
        sender = self.sender()
        if sender.text() == "Search":
            query = self.queryEdit.text()
            resSummary, self.top10DocMetas, timeCost = searchEngine(
                query, lexicon, invIndex, mapping, docLens
            )
            self.timeCost.setText(
                "Retrieval took {:.3f} seconds. Press 0-9 to view the raw document.".format(
                    timeCost
                )
            )
            self.resultSummary.setText(resSummary)

    def keyPressEvent(self, e):
        if self.top10DocMetas:
            if e.key() == Qt.Key_0:
                docMeta = self.top10DocMetas[0]
            elif e.key() == Qt.Key_1:
                docMeta = self.top10DocMetas[1]
            elif e.key() == Qt.Key_2:
                docMeta = self.top10DocMetas[2]
            elif e.key() == Qt.Key_3:
                docMeta = self.top10DocMetas[3]
            elif e.key() == Qt.Key_4:
                docMeta = self.top10DocMetas[4]
            elif e.key() == Qt.Key_5:
                docMeta = self.top10DocMetas[5]
            elif e.key() == Qt.Key_6:
                docMeta = self.top10DocMetas[6]
            elif e.key() == Qt.Key_7:
                docMeta = self.top10DocMetas[7]
            elif e.key() == Qt.Key_8:
                docMeta = self.top10DocMetas[8]
            elif e.key() == Qt.Key_9:
                docMeta = self.top10DocMetas[9]
            else:
                return

            self.showRawDocument(docMeta.raw)

    def showRawDocument(self, docString):
        if self.dialog is None:
            self.dialog = RawDocumentPage(docString)
            self.dialog.show()
        else:
            self.dialog.close()  # Close window.
            self.dialog = None  # Discard reference.


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
    resultSummary = ""
    tokens = tokenize(query, False)  # no stemming
    docScores = bm25(tokens, lexicon, invIndex, mapping, docLens)

    rank = 0
    for docID, score in docScores.items():
        # Retrieve the 10 top ranked documents for each query
        if rank > 9:
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
        resultSummary += "{}. {}({})\n".format(
            rank, docMeta.headline.strip(), docMeta.date
        )
        resultSummary += "{} ({})\n\n".format(snippet, docNO)
        top10DocMetas.append(docMeta)
        rank += 1

    stopTime = time.time()
    return (resultSummary, top10DocMetas, stopTime - startTime)


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

    app = QApplication(sys.argv)
    gui = SearchEngineGUI()
    sys.exit(app.exec_())
