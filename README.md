# The Project
This project tries to analyze the effects of online live concerts by investigating the live comment section of the live-streams of concerts. The following file explains how experiments can be conducted/reproduced.

# YouTube Live Comments
This directory contains scripts for retrieving comments from YouTube videos. They are saved in csv files.

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

## Preprocessing for annotation (`create_annotation_file.py`)
Gets the raw (live)-comment's csv file from `comments_live/<VIDEO_ID>`, preprecesses the csv file and turns it into a pandas dataframe for LM training. At the moment it removes columns we don't need for analysis removes comments posted by the publisher's/host's of the concert and removes rougly all instances that are non-english. The processed data frame is then saved as `<VIDEO_TITLE>.csv` in `annotation`.

Example usage:
```
python3 create_annotation_file.py <relative_path_to_video_id>
```

# Data Processing
As a heuristic evaluation, as well as the training of a classification model is desired, further scripts and files are needed. The 4 relevant directories all contain their own README file and should be read in the following order:

1. [comments_live](comments_live/comments_live_info.md)
2. [heuristics](heuristics/heuristics_info.md)
3. [annotation](annotation/annotation_info.md) with [annotation guidlines](annotation/Guidelines.pdf)
4. [BERT](BERT/bert_info.md)


