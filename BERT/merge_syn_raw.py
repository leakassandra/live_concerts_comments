"""
Merges the raw classes of the original csv files without synthetic items and the augmented classes for a given data set.
"""

import argparse
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Combine augmented and unaugmented class dataframes")
    
    # path to raw CSV file
    parser.add_argument(
        "raw_file",
        help="Path to raw train.csv file"
    )

    # paths to augmented csv files (variable amount)
    parser.add_argument(
        "--augmented",
        nargs="+",
        required=True,
        help="Paths to augmented csv files (space-separated)"
    )

    # names of unaugmented columns in the raw csv (variable amount)
    parser.add_argument(
        "--unaugmented-classes",
        nargs="+",
        required=True,
        help="Column names of unaugmented classes in raw CSV"
    )

    # output file
    parser.add_argument(
        "--out",
        default="train_synth.csv",
        help="Output CSV path (default: train_synth.csv)"
    )

    args = parser.parse_args()

    # read raw file
    df = pd.read_csv(args.raw_file)

    # load augmented CSVs and drop bt_lang if present
    augmented_dfs = [
        pd.read_csv(path, sep=',').drop(columns="bt_lang", errors='ignore')
        for path in args.augmented
    ]

    # collect unaugmented class dfs from the raw df
    unaugmented_dfs = []
    for col in args.unaugmented_classes:
        # for each column, select rows where 'X' or 'x'
        subset = df[df[col].isin(['X', 'x'])]
        unaugmented_dfs.append(subset)

    # combine everything
    result = pd.concat(augmented_dfs + unaugmented_dfs, ignore_index=True)

    # save output
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(f"Saved combined file to {args.out}")

if __name__ == "__main__":
    main()