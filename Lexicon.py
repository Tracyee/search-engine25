class Lexicon(dict):
    """
    A lexicon class representing a two-way dictionary.
    Source: https://stackoverflow.com/questions/1456373/two-way-reverse-map
    """
    def __setitem__(self, term, id):
        # Remove any previous connections with these values
        if term in self:
            del self[term]
        if id in self:
            del self[id]
        dict.__setitem__(self, term, id)
        dict.__setitem__(self, id, term)

    def __delitem__(self, term):
        dict.__delitem__(self, self[term])
        dict.__delitem__(self, term)

    def __len__(self):
        return dict.__len__(self) // 2