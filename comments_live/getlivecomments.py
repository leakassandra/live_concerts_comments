"""
Retrieves the live-chat comments from a YouTube Live video. The script creates a new folder 
for each video, named after the video's title. 
"""
import os
import sys
import csv
from datetime import datetime
from chat_downloader import ChatDownloader
from urllib.parse import urlparse, parse_qs
from pyyoutube import Api
from pathlib import Path
import regex as re
from typing import Optional

YOUTUBE_API_KEY = "add your API key here"
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
Writes a csv file of all live-chat comments for a  youtube video (when livestream has already ended).
'''
def save_live_chat(video_url, output_csv, published_at):
    chat = ChatDownloader().get_chat(video_url)
    
    id_pre = "ct_" # just a prefix for id
    comment_id = 1 # unique ascending comment ID
    # write a new csv file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        # define the columns of the csv file
        fieldnames = ['comment_id', 'username', 'comment_date', 'time_delta_since_upload', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # iterate through all live-chat messages
        for message in chat:
            # calculation from timestamp to date is a bit tricky
            try:
                comment_date = datetime.fromtimestamp(message.get('timestamp') / 1_000_000)
            except Exception as e:
                comment_date = ''
            # write information of each chat comment
            writer.writerow({
                'comment_id': id_pre + str(comment_id),
                'username': message.get('author', {}).get('name', ''),
                'comment_date': comment_date,
                'time_delta_since_upload': message.get('time_text'),
                'message': message.get('message', '')
            })
            comment_id = comment_id + 1

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
  # get title of the video
  title = return_title(api, video_id)
  # create new directory (named after title)
  path = Path(f"comments_live/{video_id}")
  os.mkdir(path)
  folder_path = f"comments_live/{video_id}"
  # create metadata text file
  published_at = save_video_metadata(api, video_id, os.path.join(folder_path, f"{title}_info.txt"))
  os.makedirs(folder_path, exist_ok=True)
  # create csv of comment data
  save_live_chat(link, os.path.join(folder_path, "comments.csv"), published_at)

if __name__ == "__main__":
    main()