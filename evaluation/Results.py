from collections import defaultdict


class Result:
    def __init__(self, doc_id: str, score, rank):
        self.doc_id = doc_id
        self.score = score
        self.rank = rank

    def __lt__(self, other):
        return (self.score, self.doc_id) > (other.score, other.doc_id)


class Results:
    def __init__(self):
        self.query_2_results = defaultdict(list)

    def add_result(self, query_id: str, result: Result):
        self.query_2_results[query_id].append(result)

    def get_result(self, query_id: str):
        return self.query_2_results.get(query_id, None)
