# MSCI 541/720 - HW3 - Yi Cai

The programs are tested on Ubuntu 20.04 with Python 3.8.8 built in. Some importance packages
include `pickle`, `gzip`, and `datetime`, which can be installed with `pip install XXX`.

There is no need to build, just run the programs directly with the following commands:

```python indexEngine.py <path to the latimes.gz file> <path to the storing directory>```

```python getDoc.py <path to the stored directory> <string 'id' or 'docno'> < the internal integer id or a DOCNO >```

```python BooleanAND <path to the index directory> <the queries file> <output file name>```

For evaluating a set of result files given a test collection, run the `evaluation.py` as follows. 

```usage: evaluate.py [-h] --qrel QREL --output_dir OUTPUT_DIR --results_dir RESULTS_DIR```