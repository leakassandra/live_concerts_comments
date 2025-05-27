"""
Gets the raw (live)-comments csv file from comments_live/<DESIRED_VIDEO>, or comments_normal/<DESIRED_VIDEO> 
and preprecesses the csv file for LM training.
"""

import csv
import os
import sys
import pandas as pd
import settings
from pyyoutube import Api
from urllib.parse import urlparse, parse_qs
import regex as re
import langdetect 
import emoji

# needed to check for emojis in a string
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)


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

"""
Removes the comments of the video's host.
"""
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
    # list that stores the indices of the instances that will be removed from dataframe
    drop_indices = []
    # iterate through dataframe
    for index, row in df.iterrows():
        # get the content of the live comment
        comment = str(row['message']).strip()
        # leave in comment that only contains emojis
        if is_emoji_only(comment):
            continue
        # if the comment contains emoji(s)
        if contains_emoji(comment):
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
    df.to_csv(f'anno_live_comments/{title}.csv', index=False) 

def main():
    # get user api key from settings file
    api = Api(api_key=settings.YOUTUBE_API_KEY)
    # get video URL from command-line argument
    rel_dir_path = sys.argv[1]
    #rel_dir_path = "comments_live/xSqL-_RSyJw"
    video_id = os.path.basename(rel_dir_path)

    file_path = f"comments_live/{video_id}/comments.csv"
    # turn to dataframe
    df_wo_publisher = remove_publisher_comments(file_path,api,video_id)
    df_cleaned = remove_non_en(df_wo_publisher)
    # check if worked kinda
    #print(df_wo_nonascii.iloc[:20])
    to_anno_file(df_cleaned,api,video_id)


if __name__ == "__main__":
    main()

        



