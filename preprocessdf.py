"""
Gets the raw (live)-comments csv file from comments_live/<DESIRED_VIDEO>, or comments_normal/<DESIRED_VIDEO> 
and preprecesses the csv file for LM training.
"""
# wieviele instanzen sind nur emojis, mischung und keine
import csv
import os
import sys
import pandas as pd
import settings
from pyyoutube import Api
import regex as re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException # might also use this to detect english lang
import emoji
from pathlib import Path


# Raw pattern strings
emoji_unicode_pattern = (
    "[" +
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags
    "]"
)

shortcode_pattern = r":[a-zA-Z0-9_]+:"

# Combine the two raw strings
combined_pattern = f"({emoji_unicode_pattern}|{shortcode_pattern})"

# Compile the final regex
emoji_pattern = re.compile(combined_pattern, flags=re.UNICODE)

'''
Helper: turn csv file into pandas dataframe.
'''
def get_comments_csv(file_path):
    df = pd.read_csv(file_path) 
    return df

'''
Helper: get the name of the publisher/host of the live concert.
'''
def get_publisher(api, video_id):
    # get video object using YouTube Data API
    video = api.get_video_by_id(video_id=video_id).items[0]
    snippet = video.snippet
    # get publisher's name through snippet
    publisher = snippet.channelTitle
    return publisher

'''
Removes the comments of the video's host.
'''
def remove_publisher_comments(file_path, api, video_id):
    # turn the live-video comment file we want to preprocess into pandas dataframe
    df = get_comments_csv(file_path)
    # remove columns we don't need for this analysis
    df = df.drop(columns=['comment_date', 'time_delta_since_upload'])
    # get the publisher of the live-video
    publisher = get_publisher(api, video_id)
    
    # iterate through dataframe
    for index, row in df.iterrows():
        # remove row/comment if it is by host of life-video
        if row['username'].strip() == publisher.strip():
            df.drop(index, inplace=True)

    return df

'''
Removes instances from datafram that contain non-ascii characters (broadly non-english instances)
'''
def remove_non_en(df):
    counter_emoji = 0
    counter_mixed = 0
    counter_text = 0
    # list that stores the indices of the instances that will be removed from dataframe
    drop_indices = [] # -> nochmal ausgeben!
    # iterate through dataframe
    for index, row in df.iterrows():
        # get the content of the live comment
        comment = str(row['message']).strip()
        # leave in comment that only contains emojis
        if is_emoji_only(comment):
            counter_emoji = counter_emoji + 1
            continue
        # if the comment contains emoji(s)
        if contains_emoji(comment):
            counter_mixed = counter_mixed + 1
            # remove them from the string
            rest = emoji_pattern.sub(r'', comment)
            # if the rest of that string contains non-ascii
            if not rest.isascii():
                # remove from df
                drop_indices.append(index)
            # if it doesn't: leave it in
            else:
                continue
        # if the comment does not contain emojis
        else:
            counter_text = counter_text + 1
            # check if it contains non-ascii
            if not comment.isascii():
                # remove instance if so
                drop_indices.append(index)
            # leave it in otherwise
            else:
                continue
    # remove the "non-english" instances
    df.drop(index=drop_indices, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    res_count = f"contains: {counter_emoji} only-emoji instances, {counter_mixed} emoji-text instances and {counter_text} text-only instances."
    return df, res_count

'''
Goes over messages once again and removes instances that do not contain ascii-chars but are still probably not english.
'''
def remove_langs(df):
    drop_indices = []
    for index, row in df.iterrows():
        # get the content of the live comment
        comment = str(row['message']).strip()
        try:
            if detect(comment) != 'en':
                drop_indices.append(index)
        except:
            continue

    df.drop(index=drop_indices, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df        
    
'''
Adds the columns we later want for annotation (gerade noch imporvisiert).
'''
def add_anno_items(df):
    df['pronoun_use'] = pd.Series(dtype='int')
    df['emotion_lang'] = pd.Series(dtype='int')
    df['emoji_use'] = pd.Series(dtype='int')
    df['exclamation_sync'] = pd.Series(dtype='int')
    df['reference_other'] = pd.Series(dtype='int')
    df['group_call'] = pd.Series(dtype='int')
    df['fandom_lang'] = pd.Series(dtype='int')
    return df

'''
Helper: check if message contains emoji at all
'''
def contains_emoji(text):
    for character in text:
        if character in emoji.EMOJI_DATA:
            return True
    return False

'''
Helper: detect if a string contains only emojis or non-alphanumerics
'''
def is_emoji_only(text):
    # True if the text contains only emojis and spaces
    return bool(emoji_pattern.match(text.strip()))

'''
Writes the preprocessed dataframe back into a csv so that it can be annotated.
Goal directory: "anno_live_comments"
'''
def to_anno_file(df,api,video_id):
    video = api.get_video_by_id(video_id=video_id).items[0]
    snippet = video.snippet
    # get videos name through snippet
    title = snippet.title
    df.to_csv(Path(f'anno_live_comments/{title}.csv'), index=False) 
    

def main():
    # get user api key from settings file
    api = Api(api_key=settings.YOUTUBE_API_KEY)
    # get video URL from command-line argument
    rel_dir_path = sys.argv[1]
    #rel_dir_path = "comments_live/xSqL-_RSyJw"
    video_id = os.path.basename(rel_dir_path)
    file_path = Path(f"comments_live/{video_id}/comments.csv")
    # turn to dataframe
    df_wo_publisher = remove_publisher_comments(file_path,api,video_id)
    df_cleaned, res = remove_non_en(df_wo_publisher)
    df_cleaned_2 = remove_langs(df_cleaned)
    print(res)
    #df_annotation = add_anno_items(df_cleaned_2)

    # check if worked kinda
    #print(df_wo_nonascii.iloc[:20])
    to_anno_file(df_cleaned_2,api,video_id)


if __name__ == "__main__":
    main()




        



