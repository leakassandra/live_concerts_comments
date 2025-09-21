"""
Reads in all of the annotators annotated files, joins them to 1 (for each annotator).
"""
import os
import sys
import pandas as pd

'''
Joins annotated csv files (concerts) -> to be done PER ANNOTATER 
'''
def join_annotations(in_path, out_path):

    path_dir = in_path

    # if `path_dir` is a directory, get the file paths in alphabetical order
    if isinstance(path_dir, str):  # path_dir is a folder path
        file_list = sorted([os.path.join(path_dir, f) for f in os.listdir(path_dir) if f.endswith('.csv')])
    else:  # path_dir is already a list of paths
        file_list = sorted(path_dir)

    list_dfs = []

    # read in files
    for file_path in file_list:
        try:
            df_u = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
            list_dfs.append(df_u)
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
    # join them to one big file
    df = pd.concat(list_dfs, axis=0, ignore_index=True)
    # save as joined file
    df.to_csv(out_path, index=False)

def main():
    # get directory of the annotated files that should be joined for the given annotator (eg. annotationr2/anno2_lea)
    annotator_dir = sys.argv[1]
    # get output directory and append the file name automatically
    out_dir = sys.argv[2]
    # set name of file 
    out_filename = sys.argv[3]
    save = f"{out_dir}/{out_filename}"
    
    # join annotations
    join_annotations(annotator_dir, save)

if __name__ == "__main__":
    main()