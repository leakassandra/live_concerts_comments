import os
import sys
import csv
import settings
from datetime import datetime
from chat_downloader import ChatDownloader
from urllib.parse import urlparse, parse_qs
from pyyoutube import Client, Api

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
Extracts a YouTube video ID from either long or short URL.
'''
def extract_video_id(youtube_url):
    '''
    Supports:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    '''
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query = parse_qs(parsed_url.query)
        return query.get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")
    return None

# download_live_chat('https://www.youtube.com/watch?v=HPPzQgTaLbo', 'comments_live/test_live_chat.csv')

def main():
  # get user api key from settings file
  api = Api(api_key=settings.YOUTUBE_API_KEY)
  # get video URL from command-line argument
  link = sys.argv[1]
  # call func to extract ID from video URL
  video_id = extract_video_id(link)
  # create new directory (named after video_id)
  folder_path = f"comments_live/video_{video_id}"
  os.makedirs(folder_path, exist_ok=True)
  # create metadata text file
  published_at = save_video_metadata(api, video_id, os.path.join(folder_path, "info.txt"))
  # create csv of comment data
  
  save_live_chat(link, os.path.join(folder_path, "comments.csv"), published_at)

if __name__ == "__main__":
    main()