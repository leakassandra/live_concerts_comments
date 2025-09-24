"""
Retrieves the normal comment threads from any YouTube video. The script creates a new folder for each video, 
named after the video's title. 
"""

import os
import sys
from datetime import datetime
import pandas as pd
from pyyoutube import Api
from urllib.parse import urlparse, parse_qs
import regex as re
from typing import Optional

YOUTUBE_API_KEY ="enter your API key here"
base_url = "https://www.googleapis.com/youtube/v3/"

'''
Returns the Title of the video (for storing).
'''
def return_title(api, video_id):
    # get video object using YouTube Data API
    video = api.get_video_by_id(video_id=video_id).items[0]
    snippet = video.snippet
    return snippet.title


'''
Save basic metadata about a YouTube video as a text file.
'''
def save_video_metadata(api, video_id, filename):
    # get video object using YouTube Data API
    video = api.get_video_by_id(video_id=video_id).items[0]
    # separate descriptive data (snippet) and video's statistics
    snippet = video.snippet
    statistics = video.statistics

    # publishedAt (ISO string) into Python datetime object
    published_at = datetime.fromisoformat(snippet.publishedAt.replace("Z", "+00:00"))
    
    # write video's metadata to text file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Title: {snippet.title}\n")
        f.write(f"Publisher: {snippet.channelTitle}\n")
        f.write(f"Published at: {published_at}\n")
        f.write(f"Views: {statistics.viewCount}\n")
        f.write(f"Comment count: {statistics.commentCount}\n")
        f.write(f"Video Description:\n{snippet.description}\n")
    
    # return video's publish date to later calculate time delta for comments
    return published_at

'''
Save all top-level comments (not including replies) to csv file
'''
def save_comments_to_csv(api, video_id, published_at, filename):
    # fetch all top-level comment threads 
    comment_threads = api.get_comment_threads(video_id=video_id, count=None)
    rows = []
    
    id_pre = "ct_" # just a prefix for id
    comment_id = 1 # unique ascending comment ID

    # iterate through all comments
    for ct in comment_threads.items:
        # only retreive the top-level comment
        top_comment = ct.snippet.topLevelComment.snippet
        # get username of commentor and published time
        username = top_comment.authorDisplayName
        comment_date = datetime.fromisoformat(top_comment.publishedAt.replace("Z", "+00:00"))
        # compute time difference from when the video was published
        time_delta = comment_date - published_at
        # get the actual comment content
        content = top_comment.textOriginal
        # remove line-breaks from comment (better readability in csv format)
        content_one_row = re.sub(r'\s*\n\s*', '', content)

        # to the row-list append all extracted info
        rows.append({
            "comment_id": id_pre + str(comment_id),
            "username": username,
            "comment_date": comment_date.isoformat(),
            "time_delta_since_upload": str(time_delta),
            "comment_text": content_one_row,
        })
        # increment unique id for next comment
        comment_id += 1

    # create pandas dataframe
    df = pd.DataFrame(rows)
    # write to csv
    df.to_csv(filename, index=False, encoding='utf-8')


'''
Extract YouTube video ID from many URL forms:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - https://www.youtube.com/live/VIDEOID
    - https://www.youtube.com/shorts/VIDEOID
'''
def extract_video_id(youtube_url: str, follow_redirects: bool = False) -> Optional[str]:
    if not youtube_url:
        return None

    # quick acceptance of a plain 11-char id
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", youtube_url):
        return youtube_url

    # optionally resolve redirects (useful for /live/ stubs)
    if follow_redirects:
        try:
            import requests
            # follow redirects to get the final watch URL
            resp = requests.head(youtube_url, allow_redirects=True, timeout=5)
            youtube_url = resp.url or youtube_url
        except Exception:
            # ignore resolution errors and continue parsing the original url
            pass

    parsed = urlparse(youtube_url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""

    # common case: watch?v=ID
    if host in ("www.youtube.com", "youtube.com", "m.youtube.com", "music.youtube.com"):
        qs = parse_qs(parsed.query)
        if "v" in qs:
            vid = qs["v"][0]
            if re.fullmatch(r"[0-9A-Za-z_-]{11}", vid):
                return vid

        # check path segments like /live/<id>, /shorts/<id>, /embed/<id>
        parts = [p for p in path.split("/") if p]
        # e.g. ["live", "HOIVqee1qLk"]
        if len(parts) >= 2 and parts[0] in ("live", "shorts", "embed"):
            candidate = parts[1]
            if re.fullmatch(r"[0-9A-Za-z_-]{11}", candidate):
                return candidate

        # fallback: any 11-char segment in path (reverse to prefer last segment)
        for seg in reversed(parts):
            if re.fullmatch(r"[0-9A-Za-z_-]{11}", seg):
                return seg

    # short youtu.be
    if host == "youtu.be":
        candidate = path.lstrip("/")
        if re.fullmatch(r"[0-9A-Za-z_-]{11}", candidate):
            return candidate

    # last resort: search the whole string for an 11-char token
    m = re.search(r"([0-9A-Za-z_-]{11})", youtube_url)
    if m:
        return m.group(1)

    return None
  

def main():
  # get user api key from settings file
  api = Api(api_key=YOUTUBE_API_KEY)
  # get video URL from command-line argument
  link = sys.argv[1]
  # call func to extract ID from video URL
  video_id = extract_video_id(link)
  title = return_title(api,video_id)
  os.mkdir(f"comments_nonlive/{title}")
  # create new directory (named after video title
  folder_path = f"comments_nonlive/{title}"
  os.makedirs(folder_path, exist_ok=True)
  # create metadata text file
  published_at = save_video_metadata(api, video_id, os.path.join(folder_path, "info.txt"))
  # create csv of comment data
  save_comments_to_csv(api, video_id, published_at, os.path.join(folder_path, "comments.csv"))

if __name__ == "__main__":
    main()

""" def get_live_chat_comments(video_id):
api_url = "https://www.googleapis.com/youtube/v3/liveBroadcasts" """


""" def get_top_level_comments(api, video_id):
    comment_threads = api.get_comment_threads(video_id=video_id, count=None)
    comments = []
    for ct in comment_threads.items:
        top_comment = ct.snippet.topLevelComment.snippet.textOriginal
        comments.append(top_comment)
    return comments """