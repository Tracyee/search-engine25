import argparse
import csv
import os.path
import sys
from statistics import mean
from Parsers import QrelsParser, ResultsParser
from Measures import Measures

FIELD_NAMES_5A = [
    'Run Name', 'Mean Average Precision', 'Mean P@10', 'Mean NDCG@10',
    'Mean NDCG@1000', 'Mean TBG'
]


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Program that take as input the qrels and result files '
        'measures the Average Precision, Precision@10, NDCG@10, NDCG@1000 and Time-Based Gain'
    )
    parser.add_argument('--qrel', required=True, help='Path to qrel file')
    parser.add_argument('--output_dir',
                        required=True,
                        help='Path to the output directory')
    parser.add_argument('--results_dir',
                        required=True,
                        help='Path to the result files directory')
    args = parser.parse_args()
    return args


def save_as_csv(run, measure_res, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    csv_name = os.path.join(output_dir, '{}.csv'.format(run))
    with open(csv_name, 'w') as f:
        csv_writer = csv.DictWriter(
            f, fieldnames=['measure', 'query_id', 'score'])
        csv_writer.writeheader()
        for measure_name, measure in measure_res.items():
            for query_id, score in measure.items():
                csv_writer.writerow({
                    'measure': measure_name,
                    'query_id': query_id,
                    'score': '{:.4f}'.format(score)
                })


def add_row(csv_name, name, measures):
    with open(csv_name, 'a') as f:
        csv_writer = csv.DictWriter(f, fieldnames=FIELD_NAMES_5A)
        csv_writer.writerow({
            'Run Name':
            name,
            'Mean Average Precision':
            '{:.3f}'.format(mean(measures.AP.values())),
            'Mean P@10':
            '{:.3f}'.format(mean(measures.PAt10.values())),
            'Mean NDCG@10':
            '{:.3f}'.format(mean(measures.NDCG_10.values())),
            'Mean NDCG@1000':
            '{:.3f}'.format(mean(measures.NDCG_1000.values())),
            'Mean TBG':
            '{:.3f}'.format(mean(measures.TBG.values()))
        })


def evaluate(qrel, results_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    result_file = os.path.join(output_dir, 'hw3-5a-y237cai.csv')
    with open(result_file, 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=FIELD_NAMES_5A)
        csv_writer.writeheader()

    for r in os.listdir(results_dir):
        run = r.split(".")[0]
        print("Evaluating {}".format(run))
        try:
            result_name = os.path.join(results_dir, r)
            _, results = ResultsParser(result_name).parse()
            measures = Measures(qrel, results)
            save_as_csv(run, measures.measuring(), output_dir)
            add_row(result_file, run, measures)
        except (ResultsParser.ResultsParseError, ValueError, KeyError) as e:
            print("{} is incorrectly formatted".format(run))
            continue


def main():
    args = arg_parser()
    (qrel_dir, output_dir, results_dir) = (args.qrel, args.output_dir,
                                           args.results_dir)
    qrel = QrelsParser(qrel_dir).parse()

    evaluate(qrel, results_dir, output_dir)


if __name__ == '__main__':
    main()
