# Explanation of structure and python class in `heuristics`

This directory contains the classes and data needed to get heuristic information about the live comments collected.

## Annotation rounds
There are directories for each annotation round (numbered strating by 1) that has been done:
- `annotation_round1`
-  `annotation_round2`
- ... 

They contain a csv file called `counts.csv` that contains all of the gathered heuristic information of the data.

## The `emojis` directory
This directory contains two main things: 
1. `crawled_data.csv`: data from a github page from a study "Face-Emoji Data" with  information on the ratings (on a scale of 0-100) given to each of the face emojis (to later be used for analyzing data). Link: https://tscheffler.github.io/2024-Face-Emoji-Norming/ratings.html

2. `emojis.csv`: file containing emojis according to their official emoji-category (all-emoji.json). Link: https://unicode.org/emoji/charts/full-emoji-list.html 

## The script `heuristics.py``
Reads in the csv concert files from the respective annotation round in `comments_live` and adds columns representing heuristic information. The script fills the table out automatically, so that it can be futher analysed. When called it also prints additional information on the sums of categories to the terminal.

It expects two arguments when using: 
- the path to the directory containing the concert csv's (e.g. `comments_live/annotation_round2`)
- the path to the output file (e.g. `heuristics/annotation_round2/counts.csv`)

Example usage: `python3 heuristics/heuristics.py comments_live/annotation_round2 heuristics/annotation_round2/counts.csv`

