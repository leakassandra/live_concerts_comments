"""
Counts amount of annotations per class. Can be used to calculate how many synthetic items need to be augmented to get more balanced training set.
"""
import sys
import pandas as pd

# check how many annotations exist per class in train set
df_train = pd.read_csv(sys.argv[1])

# columns to count
target_cols = ['feeling_pos',
    'feeling_neg',
    'music_ref',
    'external_ref',
    'phys_react'
    ]

df_subset_train = df_train[target_cols]

# count how many 'X' or 'x' (case-insensitive) annotations exist per column
annotation_counts_train = df_subset_train.apply(
    lambda col: col.astype(str).str.strip().str.lower().eq('x').sum()
)

print(annotation_counts_train)

# also check if classes occur in test set
df_test = pd.read_csv("BERT/datasets_raw/test.csv")
df_subset_test = df_test[target_cols]

# count how many 'X' or 'x' (case-insensitive) annotations exist per column
annotation_counts_test = df_subset_test.apply(
    lambda col: col.astype(str).str.strip().str.lower().eq('x').sum()
)

print(annotation_counts_test)