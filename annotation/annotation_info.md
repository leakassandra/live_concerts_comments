# Explanation of structure and python classes in `annotation`

This directory has the purpose of joining the seperate annotation files to one joined file per annotator, and then calculating different metrics representing the Inter-Annotator Agreement between the TWO annotators. 

## Annotation rounds
There are directories for each annotation round (numbered strating by 1) that has been done:
- `annotation_round1`
-  `annotation_round2`
- ... 

Inside of those directories are the seperate "raw" annotated csv files per concert. The directories are named after the actual name of the annotator (e.g. `anno1_lea`).

The directory `joined_tables` contains both of the annotators joined annotated files.

## Using the python scripts to create tables, join tables and calculate IAA

### Preprocessing for annotation (`create_annotation_file.py`)
Gets the raw (live)-comment's csv file from `comments_live/<VIDEO_ID>`, preprecesses the csv file and turns it into a pandas dataframe for LM training. At the moment it removes columns we don't need for analysis removes comments posted by the publisher's/host's of the concert and removes rougly all instances that are non-english. The processed data frame is then saved as `<VIDEO_TITLE>.csv` in `annotation`.

Example usage:
```
python3 create_annotation_file.py <relative_path_to_video_id>
```

### Use of: `join_annotations.py`
This is the class that helps to join the seperate tables per annotator per annotation round. It reads in all of the annotators annotated files and joins them to 1 (for each annotator). To obtain the joined tables 3 arguments need to be passed through the command line: 
- path to the directory that contains the annotators seperate "raw" csv files: annotation/annotation_round<x>/anno<x>_<annotator_name> 
- path to the directory where the joined table should be saved to: annotation/annotation_round<x>/joined_tables
- name you want to give to the joined file: "anno<x>_<annotator_name>_joined.csv

Example usage: 
```
python3 annotation/join_annotations.py annotation/annotation_round2/anno2_lea annotation/annotation_round2/joined_tables "anno2_lea_joined.csv"
```

### Use of: `calc_iaa.py`
This class calculates the IAA of two joined annotated files (two annotators) in a multi-label setting. To obtain the results, 2 arguments need to be passed through the command line: 
- path to the joined csv file of annotator 1
- path to the joined csv file od annotator 2

Example usage: 
```
python3 annotation/calc_iaa.py annotation/annotation_round2/joined_tables/anno2_lea_joined.csv annotation/annotation_round2/joined_tables/anno2_lily_joined.csv
```

