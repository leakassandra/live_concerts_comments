"""
Reads in all annotated cocert files (from anno_live_comments), concats them to one file and splits to train (80%) and test (20%) files.
Balance of items per concert is retained.
"""
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Load multiple CSVs, drop columns, split into train/test, and combine."
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        help="Paths to CSV files to process (space separated).",
    )
    parser.add_argument(
        "--drop-cols",
        nargs="*",
        default=["comment_id", "username"],
        help="Column names to drop. Default: comment_id username",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of test data. Default: 0.2",
    )
    parser.add_argument(
        "--sep",
        default=";",
        help="CSV separator. Default: ';'",
    )
    parser.add_argument(
        "--train-out",
        default="train.csv",
        help="Output path for combined train CSV.",
    )
    parser.add_argument(
        "--test-out",
        default="test.csv",
        help="Output path for combined test CSV.",
    )
    args = parser.parse_args()

    train_parts = []
    test_parts = []

    for file in args.csv_files:
        df = pd.read_csv(file, sep=args.sep).drop(columns=args.drop_cols, errors="ignore")
        train_df, test_df = train_test_split(df, test_size=args.test_size, random_state=42, shuffle=True)
        train_parts.append(train_df)
        test_parts.append(test_df)

    train_total = pd.concat(train_parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    test_total = pd.concat(test_parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

    Path(args.train_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.test_out).parent.mkdir(parents=True, exist_ok=True)

    train_total.to_csv(args.train_out, index=False)
    test_total.to_csv(args.test_out, index=False)

    print(f"Combined train CSV saved to {args.train_out}")
    print(f"Combined test CSV saved to {args.test_out}")

if __name__ == "__main__":
    main()
