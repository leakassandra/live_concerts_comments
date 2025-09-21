"""
Get emojis according to official emoji-categories (all-emoji.json) and save as csv (emojis.csv) according to category.
"""

import json
import regex as re
import csv

'''
Get the official emoji (sub) categories
'''
def list_categories(json_path, txt_path):
    # load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # new csv
    with open(txt_path, 'w', encoding='utf-8', newline='') as f:
        # iterate through rows
        for row in data:
            # get emoji's parent categories (but not parent parent category)
            if isinstance(row, list) and len(row) == 1 and not row[0][0].isupper():
                f.write(row[0] + ",")  
    
# use
list_categories('emojis/all-emoji.json', 'emojis/emoji_categories.csv')

'''
Get the emojis and put them into correct category. Saved in `auto_emoji.py`
'''
def extract_emoji_blocks(json_path, csv_path):
    # load 2D list from the crawled JSON file (all-emoji.json)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # lists to temp. store data
    results = []
    current_row = []
    collecting = False
    # iterate through the list
    for row in data:
        if isinstance(row, list):
            if len(row) == 1 and not row[0][0].isupper():
                # if we were collecting before, save the previous row
                if current_row:
                    results.append(current_row)
                # start a new row with this single item
                current_row = [row[0]]
                collecting = True
            elif collecting and len(row) > 3:
                # if we are collecting, add the 4th item
                em = ":"+row[3]+":"
                em_clean = re.sub(r"[ \t\-,]", "_", em)
                current_row.append(em_clean)

    # add the last collected row
    if current_row:
        results.append(current_row)

    # write to csv
    with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(results)

# use
extract_emoji_blocks('emojis/all-emoji.json', 'emojis/emojis.csv')