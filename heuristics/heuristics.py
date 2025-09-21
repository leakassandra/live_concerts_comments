"""
Creates a table (csv) containing heuristic information about the live comments of YouTube concerts.
The following collumns/data are/is added:
- "clarity_mean", "arousal_mean", "valence_mean", "familarity_mean", "complexity_mean" (from "https://tscheffler.github.io/2024-Face-Emoji-Norming/ratings.html")
- "plu_pro" (plural pronouns), "sin_pro" (singular pronouns), "word_count","char_count","allcaps_c","emoji_count", "emoji_categories"
"""
import pandas as pd 
import emoji
import pandas as pd
import re
import os
import sys

# define columns to drop
cols_to_drop = ["username", "comment_date", "time_delta_since_upload"]
col_to_add = ["concert_w_ID"]

'''
Joins all comments.csv files from subfolders of in_path. Builds concert_w_ID = <subfolder_name>_<comment_id> and puts it at column 0.
Drops comment_id and other unwanted columns.
'''
def join_comments_live(in_path):
    
    list_dfs = []
    # walk through all folders and files under in_path
    for root, dirs, files in os.walk(in_path):
        if "comments.csv" in files:
            
            # check if this folder contains a file named 'comments.csv'
            csv_path = os.path.join(root, "comments.csv")
            # the folder name (immediately above the file) will be the concert name
            subdir = os.path.basename(root)  
            # read in csv
            df_u = pd.read_csv(csv_path, delimiter=',', encoding='utf-8')
            
            # check that 'comment_id' column exists before using it
            if "comment_id" not in df_u.columns:
                raise KeyError(f"'comment_id' column missing in {csv_path}")
            
            # build new 'concert_w_ID' column by combining folder name and comment_id
            concert_ids = subdir + "_" + df_u["comment_id"].astype(str)
            # drop the original 'comment_id' column, as requested
            df_u = df_u.drop(columns=["comment_id"])
            # insert 'concert_w_ID' at the first column position (index 0)
            df_u.insert(0, "concert_w_ID", concert_ids)
            # drop other unwanted columns 
            df_u = df_u.drop(columns=[c for c in cols_to_drop if c in df_u.columns], errors='ignore')
            # append this processed DataFrame to list
            list_dfs.append(df_u)

    return pd.concat(list_dfs, axis=0, ignore_index=True)

# get expected directory from command line argument
total_df = join_comments_live(sys.argv[1])
# colmns from study "https://tscheffler.github.io/2024-Face-Emoji-Norming/ratings.html"
ratings_list = ["clarity_mean", "arousal_mean", "valence_mean", "familarity_mean", "complexity_mean"]
# other columns for heuristic data to be counted
basic_heuristics = ["plu_pro", "sin_pro", "word_count","char_count","allcaps_c","emoji_count", "emoji_categories"]
# all categories we need
total_list = basic_heuristics + ratings_list  

# initialize with 0's
for col in total_list:
    total_df[col] = 0  # or 0, np.nan, '', etc. 

'''
Count all-caps words with > 1 character.
'''
def count_allcaps_words(text):
    return len(re.findall(r'\b[A-Z]{2,}\b', text))

# apply to each row in the "message" column
total_df['allcaps_c'] = total_df['message'].apply(count_allcaps_words)
# de-render emojis
total_df["message"] = total_df["message"].apply(lambda x: emoji.demojize(x.lower()))

# dictionaries containing pronouns to check
sin_pronouns = {'i', 'id', 'i\'d', 'i\'ll', 'im', 'i\'m', 'ive', 'i\'ve', 'me', 'mine', 'my', 'myself'}
plu_pronouns = {'lets', 'let\'s', 'our', 'ours', 'ourselves', 'us', 'we', 'we\'d', 'we\'ll', 'we\'re', 'weve', 'we\'ve'}

'''
Count singular pronouns.
'''
def count_sin_pronouns(text):
    words = text.lower().split()
    return sum(word.strip(".,!?\"'()[]") in sin_pronouns for word in words)
# apply to the "message" column
total_df['sin_pro'] = total_df['message'].apply(count_sin_pronouns)

'''
Count plural pronouns.
'''
def count_plu_pronouns(text):
    words = text.lower().split()
    return sum(word.strip(".,!?\"'()[]") in plu_pronouns for word in words)
# apply to the "message" column
total_df['plu_pro'] = total_df['message'].apply(count_plu_pronouns)

'''
Count word amount.
'''
def count_words(text):
    words = text.lower().split()
    return len(words)
# apply to the "message" column
total_df['word_count'] = total_df['message'].apply(count_words)

'''
Count character amount.
'''
def count_chars(text):
    chars = 0
    for i in text:
        chars = chars + 1
    return chars
# apply to the "message" column
total_df['char_count'] = total_df['message'].apply(count_chars)

'''
Count emojis.
'''
def count_emojis(text):
    em_list = re.findall(r':[a-z_]+:',text)
    return len(em_list)
# apply to the "message" column
total_df['emoji_count'] = total_df['message'].apply(count_emojis)

'''
Helper: make emojis.csv processable.
'''
def read_ragged_csv(filepath):
    # open the file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip().split(',') for line in f if line.strip()]
    
    # get max number of columns
    max_len = max(len(line) for line in lines)
    
    # pad each line with empty strings if necessary
    padded_lines = [line + [''] * (max_len - len(line)) for line in lines]
    
    # convert to data frame
    df = pd.DataFrame(padded_lines)
    return df
# get emoji data frame for further data analysis
df_emoji = read_ragged_csv("heuristics/emojis/emojis.csv")

'''
Get emoji categories of given emojis (as list).
'''
def emoji_category(text):
    df = read_ragged_csv("heuristics/emojis/emojis.csv")
    matching_indices = []
    # help to get emojis in message with regex
    em_list = re.findall(r':[a-z_]+:',text)
    # iterate through the emoji list
    for i in em_list:
        # try to match categories from emojis.csv file
        mask = df.astype(str).apply(lambda row: row.str.contains(i, case=False, na=False)).any(axis=1)
        matches = df.index[mask].tolist()
        matching_indices.extend(matches) 
    # append categories to list
    first_elements = [df.iloc[i, 0] for i in matching_indices]
    return sorted(first_elements)
# apply to "message"
total_df['emoji_categories'] = total_df['message'].apply(emoji_category)

# remove some of the crawled categories
drops_crawled = ["emoji","twitter_freq","whatsapp_freq","num_ratings"]

'''
Get values of clarity for all emojis found in message (as list).
'''
def clarity_means(text):
    # get crawled_data.csv 
    crawled_data = pd.read_csv('heuristics/emojis/crawled_data.csv', sep=',').drop(columns=drops_crawled, errors='ignore')
    # list to store results in
    clarity_means_l = []
    # find emojis and store them in list
    em_list = re.findall(r':[a-z_]+:',text)
    # iterate through emoji list
    for i in em_list:
        for idx, emoji in enumerate(crawled_data['unicode_name']):
            # append clarity value to clarity list if emoji is found in crawled_data dataframe
            if i == str(emoji):
                clarity_means_l.append(crawled_data['clarity_mean'].iloc[idx])
    return clarity_means_l
# apply to message
total_df['clarity_mean'] = total_df['message'].apply(clarity_means)

'''
Get values of arousal for all emojis found in message (as list).
'''
def arousal_means(text):
    # get crawled_data.csv 
    crawled_data = pd.read_csv('heuristics/emojis/crawled_data.csv', sep=',').drop(columns=drops_crawled, errors='ignore')
    # list to store results in
    arousal_means_l = []
    # find emojis and store them in list
    em_list = re.findall(r':[a-z_]+:',text)
    # iterate through emoji list
    for i in em_list:
        for idx, emoji in enumerate(crawled_data['unicode_name']):
            # append arousal value to arousal list if emoji is found in crawled_data dataframe
            if i == str(emoji):
                arousal_means_l.append(crawled_data['arousal_mean'].iloc[idx])
    return arousal_means_l
# apply to message
total_df['arousal_mean'] = total_df['message'].apply(arousal_means)

'''
Get values of valence for all emojis found in message (as list).
'''
def valence_means(text):
    # get crawled_data.csv from study
    crawled_data = pd.read_csv('heuristics/emojis/crawled_data.csv', sep=',').drop(columns=drops_crawled, errors='ignore')
    # list to store results in
    valence_means_l = []
    # find emojis and store them in list
    em_list = re.findall(r':[a-z_]+:',text)
    # iterate through emoji list
    for i in em_list:
        for idx, emoji in enumerate(crawled_data['unicode_name']):
            # append valence value to valence list if emoji is found in crawled_data dataframe
            if i == str(emoji):
                valence_means_l.append(crawled_data['valence_mean'].iloc[idx])
    return valence_means_l
# apply to message
total_df['valence_mean'] = total_df['message'].apply(valence_means)

'''
Get values of familarity for all emojis found in message (as list).
'''
def familarity_means(text):
    # get crawled_data.csv from study
    crawled_data = pd.read_csv('heuristics/emojis/crawled_data.csv', sep=',').drop(columns=drops_crawled, errors='ignore')
    # list to store results in
    familarity_means_l = []
    # find emojis and store them in list
    em_list = re.findall(r':[a-z_]+:',text)
    # iterate through emoji list
    for i in em_list:
        for idx, emoji in enumerate(crawled_data['unicode_name']):
            # append familarity value to familirity list if emoji is found in crawled_data dataframe
            if i == str(emoji):
                familarity_means_l.append(crawled_data['familarity_mean'].iloc[idx])
    return familarity_means_l
# apply to message
total_df['familarity_mean'] = total_df['message'].apply(familarity_means)

'''
Get values of complexity for all emojis found in message (as list).
'''
def complexity_means(text):
    # get crawled_data.csv from study
    crawled_data = pd.read_csv('heuristics/emojis/crawled_data.csv', sep=',').drop(columns=drops_crawled, errors='ignore')
    # list to store results in
    complexity_means_l = []
    # find emojis and store them in list
    em_list = re.findall(r':[a-z_]+:',text)
     # iterate through emoji list
    for i in em_list:
        for idx, emoji in enumerate(crawled_data['unicode_name']):
            # append complexity value to complexity list if emoji is found in crawled_data dataframe
            if i == str(emoji):
                complexity_means_l.append(crawled_data['complexity_mean'].iloc[idx])
    return complexity_means_l
# apply to message
total_df['complexity_mean'] = total_df['message'].apply(complexity_means)

# get out directory as command line argument
total_df.to_csv(sys.argv[2], index=False)

# get some information on data of whole table as well
sum_plu_pro = total_df['plu_pro'].sum()
sum_sin_pro = total_df['sin_pro'].sum()
sum_word_count = total_df['word_count'].sum()
sum_char_count = total_df['char_count'].sum()
sum_allcaps_c = total_df['allcaps_c'].sum()
sum_emoji_count = total_df['emoji_count'].sum()

# print to terminal
print(f"Sum plural pronouns: {sum_plu_pro} \nSum singular pronouns: {sum_sin_pro} \nSum word counts: {sum_word_count} \nSum character counts: {sum_char_count}\nSum all-caps words: {sum_allcaps_c}\nSum emoji count: {sum_emoji_count}")



