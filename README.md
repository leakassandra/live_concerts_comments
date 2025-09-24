# The Project
This project tries to analyze the effects of online live concerts by investigating the live comment section of the live-streams of concerts. The following file explains how experiments can be conducted/reproduced.

# Setup for usage
Before using, create a virtual environment. There are two options: for conda as well as non-conda users.

## Conda users
Create and activate the virtual environment:
```
conda env create -f setup/environment.yml
conda activate my_env
```

## Non-Conda users
Create and activate the virtual environment:
```
python -m venv venv
source venv/bin/activate
pip install -r setup/requirements.txt
```

# YouTube Comments
This directory contains scripts for retrieving comments from YouTube videos. They are saved in csv files.

## Get comments (`getcomments.py`)
Retrieves the normal comment threads from any YouTube video. The script creates a new folder for each video, named after the video's title. 
Inside of each created folder, a file called `info.txt` is created, that contains general information about the video. In addition, a csv file containing all comment-threads (without comment responses) of the video is created. All new folders are generated in `comments_normal`.

Example usage:
```
python3 getcomments.py <VIDEO's URL>
```

# Live comments and Data Processing
As a heuristic evaluation, as well as the training of a classification model is desired, further scripts and files are needed. The 4 relevant directories all contain their own README file and should be read in the following order:

1. [comments_live](comments_live/comments_live_info.md)
2. [heuristics](heuristics/heuristics_info.md)
3. [annotation](annotation/annotation_info.md) with [annotation guidlines](annotation/Guidelines.pdf)
4. [BERT](BERT/bert_info.md)


