from collections import OrderedDict
import math
import pickle
import json
import sys, os, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Mapping import Mapping
from Lexicon import Lexicon

# Calibration values for TBG:
HALF_LIFE = 224  # half−life for Exponential decay
P_C1R1 = 0.64  # Probability of click on relevant summary
P_C1R0 = 0.39  # Probability of click on non-rel. summary
P_S1R1 = 0.77  # Prob. of save/judge relevant document as rel
# P_S1R0 = 0.27  # Prob. of save/judge nonrelevant doc. as rel. not used
Ts = 4.4  # Time to evaluate a summary (seconds)


class Measures:
    def __init__(self, qrel, results):
        self.results = results
        self.qrel = qrel
        self.AP = {}
        self.PAt10 = {}
        self.NDCG_10, self.NDCG_1000 = {}, {}
        self.TBG = {}

    def measuring(self):
        self.average_precision()
        self.precision_at_10()
        self.ndcg_10_1000()
        self.time_based_gain()
        measures_res = {
            "ap": self.AP,
            "P_10": self.PAt10,
            "ndcg_cut_10": self.NDCG_10,
            "ndcg_cut_1000": self.NDCG_1000,
            "tbg": self.TBG,
        }
        return measures_res

    def average_precision(self):
        for qid in self.qrel.get_query_ids():
            rel_docs = 0
            scores = []

            result = self.results.get_result(qid)
            if result:
                result.sort(key=lambda x: x.score, reverse=True)

                for i, r in enumerate(result, start=1):
                    if self.qrel.get_relevance(qid, r.doc_id) > 0:
                        rel_docs += 1
                        scores.append(float(rel_docs / i))

                self.AP[qid] = sum(scores) / float(
                    len(self.qrel.query_2_reldoc_nos[qid])
                )
            else:
                self.AP[qid] = float(0)

        self.AP = OrderedDict(sorted(self.AP.items(), key=lambda x: x[0]))

    def precision_at_10(self):
        for qid in self.qrel.get_query_ids():
            rel_docs = 0

            result = self.results.get_result(qid)
            if result:
                result.sort(key=lambda x: x.score, reverse=True)

                for r in result[:10]:
                    if self.qrel.get_relevance(qid, r.doc_id) > 0:
                        rel_docs += 1

                self.PAt10[qid] = float(rel_docs / 10)
            else:
                self.PAt10[qid] = float(0)

        self.PAt10 = OrderedDict(sorted(self.PAt10.items(), key=lambda x: x[0]))

    def ndcg_10_1000(self):
        self.NDCG_10 = {}
        self.NDCG_1000 = {}

        for qid in self.qrel.get_query_ids():
            dcg = 0
            rel_docs = len(self.qrel.query_2_reldoc_nos[qid])

            result = self.results.get_result(qid)
            if result:
                result.sort(key=lambda x: x.score, reverse=True)
                for i, r in enumerate(result, start=1):
                    if self.qrel.get_relevance(qid, r.doc_id) > 0:
                        dcg += 1 / math.log2(i + 1)
                    if i == 10:
                        self.NDCG_10[qid] = dcg / self.idcg(rel_docs, i)
                    if i == min(len(result), 1000):
                        self.NDCG_1000[qid] = dcg / self.idcg(rel_docs, i)
            else:
                self.NDCG_10[qid] = float(0)
                self.NDCG_1000[qid] = float(0)

        self.NDCG_10 = OrderedDict(sorted(self.NDCG_10.items(), key=lambda x: x[0]))
        self.NDCG_1000 = OrderedDict(sorted(self.NDCG_1000.items(), key=lambda x: x[0]))

    def time_based_gain(self):
        for qid in self.qrel.get_query_ids():
            tbg = 0
            tk = 0
            result = self.results.get_result(qid)
            if result:
                result.sort(key=lambda x: x.score, reverse=True)

                with open("../latimes_indices/mapping.pkl", "rb") as f:
                    mapping = pickle.load(f)

                with open("../latimes_indices/doc_lens.pkl", "rb") as d:
                    doc_lens = pickle.load(d)

                for i, r in enumerate(result, start=1):
                    if self.qrel.get_relevance(qid, r.doc_id) > 0:
                        gk = P_C1R1 * P_S1R1
                        tk += (
                            Ts
                            + (0.018 * doc_lens[mapping[r.doc_id] - 1] + 7.8) * P_C1R1
                        )
                        dtk = math.exp(-tk * (math.log(2) / HALF_LIFE))
                        gain = gk * dtk
                        tbg += gain
                    else:
                        tk += (
                            Ts
                            + (0.018 * doc_lens[mapping[r.doc_id] - 1] + 7.8) * P_C1R0
                        )
                self.TBG[qid] = tbg
            else:
                self.TBG[qid] = float(0)

        self.TBG = OrderedDict(sorted(self.TBG.items(), key=lambda x: x[0]))

    def idcg(self, rel_docs, max_bound):
        idcg = 0
        if rel_docs > 0:
            for i in range(1, min(max_bound + 1, rel_docs + 1)):
                idcg += 1 / math.log2(i + 1)
            return idcg
        else:
            return 1
