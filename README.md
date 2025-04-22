# YouTube Live Comments
Scripts for retrieving comments from YouTube videos. Saves them in a csv file.
At the moment it uses a visible youtube API key. Should stay private while it is visible.

## Scrape Comments (`scrape-comments.py`)
Retrieves the normal comment threads from any YouTube video. The script creates a new folder for each video, named "video_<url_id>". 
Inside of each created folder, there is a file called `info.txt` that contains general information about the video. There is also a csv file containing all comment-threads (without comment responses) of the video. All new folders are generated in `comments_normal`.

Example usage:
```
python3 scrape-comments.py <VIDEO's URL>
```


## Scrape Live (`scrape-live.py`)
Retrieves the live-chat comments from past YouTube Live video. The script creates a new folder for each video, named "video_<url_id>". 
Inside of each created folder, there is a file called `info.txt` that contains general information about the live video. It also contains a csv file with all live-comments of the video. All new folders are generated in `comments_live`.

Example usage:
```
python3 scrape-live.py <VIDEO's URL>
```

## Required packages/installs
`pyyoutube`, `pandas`, `chat_downloader` .. 