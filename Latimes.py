class Latimes(object):
    def __init__(self, docNo: str = None,
                 internalId: int = 0, 
                 date: str = None, 
                 headline: str = None, 
                 raw: str = None):
        super().__init__()
        self.docNo = docNo
        self.internalId = internalId
        self.date = date
        self.headline = headline
        self.raw = raw

    def __str__(self):
        return "docno: " + self.docNo + "\ninternal id: " + str(self.internalId) +\
                "\ndate: " + self.date + "\nheadline: " + self.headline +\
                    "\nraw document:\n" + self.raw
