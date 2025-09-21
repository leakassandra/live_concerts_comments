# Explanation of structure and python class in `BERT`

This directory contains the classes and data needed to train a BERT model for predicting the classes:
- feeling_pos (feeling positive)
- feeling_neg (feeling negative)
- music_ref (music reference)
- external_ref (external reference)
- phys_react (physical reaction)

For more information on the classes, please take a look at the [annotation guidlines](annotation/Guidelines.pdf)

## Annotation rounds
Once again the subfolders are ordered according to annotation rounds. In those folders, the different trials with BERT can be stored - for example trials with different hyper parameter settings, without synthetic items, with 5 back-translations per item, or 10 back-translations per item..
Because of that, the annotation rounds contain different train sets (raw and vectorized) per trial and the corresponding model. Due to storage reasons and deficient performance, the models of old trials (annotation_round1) were deleted, though training them again can be done quickly if desired.

## Python scripts
Use these scripts in the order of the documentation:

### Use of `create_train_test_split.py`
Helps to concatinate all desired annotated files that the model should be trained on. Provide paths to all annotated files, then drop the two unneccecary columns "comment_id" and username, test size is 0.2 & train 0.8. Provide paths to the resulting train and test set. 

Usage in the command line:
```
python3 split_csvs.py anno_live_comments/anno1_lea/AIR.csv anno_live_comments/anno1_lea/MOBY.csv anno_live_comments/anno1_lea/NF.csv anno_live_comments/anno1_lea/STING.csv \
  --drop-cols comment_id username \
  --test-size 0.2 \
  --train-out BERT/annotation_round1/datasets_raw_x/train.csv \
  --test-out BERT/annotation_round1/datasets_raw_x/test.csv

```

### Use of `data_todict.py`
This script reads in the unformated train/test datasets (from dataset_raw) and turns them into format suitable for actual training (one-hot-encoded vectors). Expects the unformated train- and test set from former script output as input. Also expects a output directory "dataset_dict_x".

Example usage: 
```
python3 data_todict.py BERT/synthetic_items/train_synth_10.csv BERT/annotation_round1/raw/test.csv BERT/annotation_round1/dataset_dict_synth_10
```

### Use of `get_class_counts.py`
This script counts the amount of annotations _per class_. It can be useful when wanting to find out which classes might be underrespresented and how many synthetic items should be augmented to the classes' items to have a more balanced training set.
The command line only expects the (RAW!) training file (eg. BERT/annotation_round1/raw_synth_5/train_synth.csv). It will simply print the information to the terminal.

Example usage: 
```
python3 get_class_counts.py BERT/annotation_round1/raw_synth_5/train_synth.csv
```

### Use of `add_synthetic_items.py`
This script creates synthetic items via back-translation of underrepresented classes. Languages that can be used: German, French, Russian, Chinese, Italian, Spanish, Japanese, Arabic, Portuguese, Dutch. Each minority class receives a new dataframe to which the back-translantions are appended. They are saved as seperate csv files in the current directory. The dataframes need to be merged again afterwards.

The command line expects 3 arguments: 
1. The path to the raw TRAIN csv file of which some classes are supposed to be augmented (eg. BERT/annotation_round1/raw/train.csv)
2. The name of the class you want to augment (eg. "music_ref")
3. The output path to the file of the augmented class (eg. BERT/annotation_round1/augmented_classes/music_ref_synth.csv)

Example usage: 
```
python3 BERT/add_synthetic_items.py BERT/annotation_round1/raw/train.csv "music_ref" BERT/annotation_round1/augmented_classes/music_ref_synth.csv`
```

### Use of `merge_syn_raw.py`
Merges the raw classes of the original csv files without synthetic items and the augmented classes for a given data set. The command line expects: 

- raw_file: the annotated train file without synthetic items (e.g. BERT/annotation_round1/raw/train.csv).
- augmented: one or more paths to augmented csv files 
- unaugmented-classes: takes any number of column names from your raw CSV to pull unaugmented classes
- out: defines where the combined CSV is saved

Example usage:
```
python script.py my_raw.csv \
  --augmented aug1.csv aug2.csv \
  --unaugmented-classes classA classB \
  --out output.csv
```

### Use of `train_model.py`
This is the script that finally trains BERT for multi-label classification with the "feeling_pos", "feeling_neg", "music_ref", "external_ref", "phys_react" classes. This class expects the path to the "dataset_dict_x" directory (depending on which dataset you want to train on). It will find the training and test set inside of that directory automatically (eg. BERT/annotation_round1/dataset_dict_synth_10). It also expects the path to the output directory of the newly trained model (eg. BERT/annotation_round1/models/bert-finetuned_concert_syn10).

Example usage: 
```
python3 train_model.py BERT/annotation_round1/dataset_dict_synth_10 BERT/annotation_round1/models/bert-finetuned_concert_syn10`
```