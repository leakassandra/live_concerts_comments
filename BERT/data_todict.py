"""
Reads in the unformated train/test datasets (from datasets_raw) and turns them into format suitable for actual training (one-hot-encoded vectors).
Results saved in "dataset_dict".
"""
import pandas as pd
import sys
from datasets import Dataset, DatasetDict

# set train and test set
df_train = pd.read_csv(sys.argv[1])
df_test = pd.read_csv(sys.argv[2]) 

# label columns
label_cols = ['feeling_pos', 'feeling_neg', 'music_ref', 'external_ref', 'phys_react']

# convert 'X' to 1 and NaN/empty to 0
df_train[label_cols] = df_train[label_cols].fillna('').applymap(lambda x: True if (x.strip() == 'X' or x.strip() == 'x') else False)
df_test[label_cols] = df_test[label_cols].fillna('').applymap(lambda x: True if (x.strip() == 'X' or x.strip() == 'x') else False)

train_dataset = Dataset.from_pandas(df_train)
test_dataset = Dataset.from_pandas(df_test)

# create dataset dict
final_dataset = DatasetDict({
    'train': train_dataset.remove_columns(['__index_level_0__']) if '__index_level_0__' in train_dataset.column_names else train_dataset,
    'test': test_dataset.remove_columns(['__index_level_0__']) if '__index_level_0__' in test_dataset.column_names else test_dataset
})

# save the dictionary
final_dataset.save_to_disk(sys.argv[3])