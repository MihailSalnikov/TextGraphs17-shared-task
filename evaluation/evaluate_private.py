import argparse
import os

import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)

    args = parser.parse_args()

    return args


def get_submitted(parent):
    names = [name for name in os.listdir(parent)]
    if len(names) == 0:
        raise RuntimeError('No files in submitted')
    if len(names) > 1:
        raise RuntimeError('Multiple files in submitted: {}'.format(' '.join(names)))
    return os.path.join(parent, names[0])


def get_reference(parent):
    names = [os.path.join(parent, name) for name in os.listdir(parent)]
    if len(names) == 0:
        raise RuntimeError('No files in reference')
    if len(names) != 1:
        raise RuntimeError('There should be exact one file in reference: {}'.format(' '.join(names)))
    return names[0]


def evaluate(df):
    pred_labels = df["prediction"].values
    true_labels = df["label"].values

    p = precision_score(true_labels, pred_labels)
    r = recall_score(true_labels, pred_labels)
    f1 = f1_score(true_labels, pred_labels)
    acc = accuracy_score(true_labels, pred_labels)

    return p, r, f1, acc


def main(args):
    input_dir = args.input_dir
    submit_dir = os.path.join(input_dir, 'res')
    truth_dir = os.path.join(input_dir, 'ref')
    output_dir = args.output_dir
    if not os.path.exists(output_dir) and output_dir != '':
        os.makedirs(output_dir)

    predictions_path = get_submitted(submit_dir)
    gold_labels_path = get_reference(truth_dir)

    predictions_df = pd.read_csv(predictions_path, sep='\t')
    predictions_df["prediction"] = predictions_df["prediction"].astype(np.int32)
    if "prediction" not in predictions_df.columns:
        raise RuntimeError('prediction column is not found in submission file')
    predictions_unique_values = set((int(x) for x in predictions_df["prediction"].unique()))
    assert len(predictions_unique_values.intersection({0, 1})) == 2
    test_df = pd.read_csv(gold_labels_path, sep='\t')
    test_df["label"] = test_df["correct"].astype(np.int32)
    test_df["prediction"] = predictions_df["prediction"]

    public_test_df = test_df[test_df["subset"] == "public"]
    private_test_df = test_df[test_df["subset"] == "private"]

    pub_p, pub_r, pub_f1, pub_acc = evaluate(public_test_df)
    priv_p, priv_r, priv_f1, priv_acc = evaluate(private_test_df)
    output_pub_scores_fname = os.path.join(output_dir, 'public_scores.txt')
    output_all_scores_fname = os.path.join(output_dir, 'all_scores.txt')
    with open(output_pub_scores_fname, 'w', encoding="utf-8") as out_pub, \
            open(output_all_scores_fname, 'w', encoding="utf-8") as out_all:

        out_pub.write("Public test\n")
        out_pub.write(f"\tPublic precision: {pub_p}\n")
        out_pub.write(f"\tPublic recall: {pub_r}\n")
        out_pub.write(f"\tPublic F1: {pub_f1}\n")
        out_pub.write(f"\tPublic accuracy: {pub_acc}\n")

        out_all.write("Public test\n")
        out_all.write(f"\tPublic precision: {pub_p}\n")
        out_all.write(f"\tPublic recall: {pub_r}\n")
        out_all.write(f"\tPublic F1: {pub_f1}\n")
        out_all.write(f"\tPublic accuracy: {pub_acc}\n")

        out_all.write("Private test\n")
        out_all.write(f"\tPrivate precision: {priv_p}\n")
        out_all.write(f"\tPrivate recall: {priv_r}\n")
        out_all.write(f"\tPrivate F1: {priv_f1}\n")
        out_all.write(f"\tPrivate accuracy: {priv_acc}\n")


if __name__ == '__main__':
    args = parse_args()
    main(args)
