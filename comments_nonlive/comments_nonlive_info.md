# Explanation of structure and python script in `comments_nonlive`
This directory contains the python script to get comments from a YouTube video and the unannotated, raw csv files with the live comments.

## Use of `getcomments_nonlive.py`
Retrieves the normal comment threads from any YouTube video. The script creates a new folder for each video, named after the video's title. 
Inside of each created folder, a file called `info.txt` is created, that contains general information about the video. In addition, a csv file containing all comment-threads (without comment responses) of the video is created. All new folders are generated in `comments_nonlive` which can be dragged to the wanted position (not yet used for anything - to be specified in future).

Example usage:
```
python3 comments_nonlive/getcomments_nonlive.py <VIDEO's URL>
```