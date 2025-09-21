"""
Calculates the IAA of two joined annotated files (two annotators) in a multi-label setting.
Calculated metrices: 
- number of items per class per person (for general overview)
- avgerage jaccard
- per class percent agreement
- per class cohen's kappa
- average cohen's kappa 
"""
import pandas as pd
from sklearn.metrics import cohen_kappa_score
import numpy as np
import sys

'''
Helper to convert annotations to binary 0/1
'''
def convert_to_binary(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip().lower()
    if val_str == "x":
        return 1
    try:
        num = int(val)
        return 1 if num == 1 else 0
    except ValueError:
        return 0

'''
Calculate observed agreement, jaccard (set) and adapted cohen's kappa
'''
def calculate_multi_label_iaa_binary(file1, file2, label_cols):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    # apply conversion to binary
    for col in label_cols:
        df1[col] = df1[col].apply(convert_to_binary)
        df2[col] = df2[col].apply(convert_to_binary)

    # get column sums
    sums_1 = df1[label_cols].sum()
    sums_2 = df2[label_cols].sum()

    # jaccard 
    jaccards = []
    for i in range(len(df1)):
        a = {label for label in label_cols if df1.loc[i, label] == 1}
        b = {label for label in label_cols if df2.loc[i, label] == 1}
        jaccards.append(1.0 if not a and not b else len(a & b) / len(a | b))
    avg_jaccard = np.mean(jaccards)

    # percent agreement + kappa
    label_percent_agreement = {}
    label_kappa = {}
    for label in label_cols:
        y1 = df1[label].astype(int)
        y2 = df2[label].astype(int)
        # get percentage
        label_percent_agreement[label] = (y1 == y2).mean()
        # get cohens kappa (per label!)
        label_kappa[label] = cohen_kappa_score(y1, y2)
    
    avg_kappa = np.mean(list(label_kappa.values()))

    # exact row matches (all labels identical for an item)
    row_equal = (df1[label_cols] == df2[label_cols]).all(axis=1)
    n_exact_matches = row_equal.sum()
    prop_exact_matches = n_exact_matches / len(df1)

    return {
        "n_items": len(df1),
        "sums_annotator1": sums_1,
        "sums_annotator2": sums_2,
        "avg_jaccard": avg_jaccard,
        "label_percent_agreement": label_percent_agreement,
        "label_kappa": label_kappa,
        "avg_kappa": avg_kappa,
        "n_exact_matches": n_exact_matches,        
        "prop_exact_matches": prop_exact_matches  
    }


def main():
    # get joined aannotated csv by annotator 1
    annotator1_joined = sys.argv[1]
    # get joined aannotated csv by annotator 2
    annotator2_joined = sys.argv[2]
    # column labels
    label_cols=[
        "feeling_pos",
        "feeling_neg",
        "music_ref",         
        "external_ref",
        "phys_react"
        ]
    # calculate IAA (printed to the terminal)
    calculate_multi_label_iaa_binary(annotator1_joined, annotator2_joined, label_cols)
    
if __name__ == "__main__":
    main()