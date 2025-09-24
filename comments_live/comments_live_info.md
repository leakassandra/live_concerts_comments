# Explanation of structure and python class in `comments_live`

This directory contains the python script to get live comments from a YouTube video and the unannotated, raw csv files with the live comments.

## Annotation rounds
There are directories for each annotation round (numbered strating by 1) that has been done:
- `annotation_round1`
- `annotation_round2`
- ... 

Inside of those directories are further directories named after the video ID where comments have been 'crawled' from. They contain a csv file (`comments.csv`) with the live comments and meta-data, as well as a seperate txt file with further information about the YouTube concert. (e.g.: `Nils Frahm - Live at the Philharmonie de Paris - ARTE Concert_info.txt`).
The amount of directories in `annotation_round<x>` are dependent simply on how many videos were tested in that round.

## Use of `getlivecomments.py`
The class retrieves the live-chat comments from a YouTube Live video. It creates a new folder for each video, named after the video's ID (see info above). The class makes use of `settings.py` to access the API through a key.

The command line expects one argument: 
- YouTube link/video URL (e.g.: 'https://www.youtube.com/watch?v=HPPzQgTaLbo')

Example usage:
```
python3 comments_live/getlivecomments.py <VIDEO's URL>
```

The folder is stored in `comments_live` by default and can be dragged into the correct round (e.g.: `annotation_round2`)