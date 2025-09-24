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

# Live comments and Data Processing
As a heuristic evaluation, as well as the training of a classification model is desired, further scripts and files are needed. The 4 relevant directories all contain their own README file and should be read in the following order:

1. [comments_nonlive](comments_nonlive/comments_nonlive_info.md)
2. [comments_live](comments_live/comments_live_info.md)
3. [heuristics](heuristics/heuristics_info.md)
4. [annotation](annotation/annotation_info.md) with [annotation guidlines](annotation/Guidelines.pdf)
5. [BERT](BERT/bert_info.md)


