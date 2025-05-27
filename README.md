# YouTube Live Comments
Scripts for retrieving comments from YouTube videos. Saves them in a csv file.
At the moment it uses a visible youtube API key. Should stay private while it is visible.
The directory "annotation" contains first test annotations.

## Get comments (`getcomments.py`)
Retrieves the normal comment threads from any YouTube video. The script creates a new folder for each video, named after the video's title. 
Inside of each created folder, a file called `info.txt` is created, that contains general information about the video. In addition, a csv file containing all comment-threads (without comment responses) of the video is created. All new folders are generated in `comments_normal`.

Example usage:
```
python3 getcomments.py <VIDEO's URL>
```


## Get Live comments (`getlivecomments.py`)
Retrieves the live-chat comments from past YouTube Live video. The script creates a new folder for each video, named after the video's title. 
Inside of each created folder, a file called `info.txt` is created, that contains general information about the live video. In addition, a csv file with all live-comments of the video is created. All new folders are generated in `comments_live`.

Example usage:
```
python3 getlivecomments.py <VIDEO's URL>
```

## Preprocessing for LM training (`preprocessdf.py`)
Gets the raw (live)-comment's csv file from `comments_live/<VIDEO_ID>`, preprecesses the csv file and turns it into a pandas dataframe for LM training. At the moment it removes columns we don't need for analysis removes comments posted by the publisher's/host's of the concert and removes rougly all instances that are non-english. The processed data frame is then saved as `<VIDEO_TITLE>.csv` in `anno_live_comments`.

Example usage:
```
python3 preprocessdf.py <relative_path_to_video_id>
```

## Required packages/installs
`pyyoutube`, `pandas`, `chat_downloader` .. 