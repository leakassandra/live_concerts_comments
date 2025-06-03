import pandas as pd

def get_filtered_out_instances(original_csv, filtered_csv):
    
    # read the CSV files into DataFrames
    base_df = pd.read_csv(original_csv)
    filtered_df = pd.read_csv(filtered_csv)

    # assume the ID is in the first column (use position 0 to get the column name)
    id_column = base_df.columns[0]
    
    # find the rows in base_df that are NOT in filtered_df based on the ID column
    filtered_out_df = base_df[~base_df[id_column].isin(filtered_df[id_column])]
    
    filtered_out_df.to_csv("filtered_out_by_preprocessing/filtered_sting.csv", index=False)


get_filtered_out_instances("comments_live/ZDtjDThed7o/comments.csv", "anno_live_comments/Sting - live session at the Panthéon in Paris - ARTE Concert.csv")