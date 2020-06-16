import json
import pandas as pd
import numpy as np
from functools import reduce
from typing import List
from math import ceil


def parse_points(q: str) -> float:
    '''
        returns the point value of a gradescope question part,
        parsed from a string in the form of "<NAME> (1.0 pts)"
    '''
    return float(q.rsplit("(", 1)[1].split(" ", 1)[0])


def get_total_points(ql: List[str]):
    '''
        given a list of gradescope question parts,
        returns the total number of marks in the question
    '''
    return reduce(lambda acc, x: acc + parse_points(x), ql, 0)

def get_question_number(q):
    '''
        returns the question number given a string in the form of "<NO>.<PART>: "
    '''
    return int(q.split(":", 1)[0].split(".", 1)[0]) 


def merge(qmap_json, gs_csv, instance=1):
    '''
        given a gradescope csv and a plgspl question map (per student),
        generates a "manual grading" csv for pl 
    '''
    pl_qmap = json.load(open(qmap_json))
    gs_df = pd.read_csv(gs_csv)

    gs_question_parts = list(gs_df)[10:]
    gs_question_count = get_question_number(gs_question_parts[-1])
    gs_questions = [[] for _ in range(gs_question_count)]
    for p in gs_question_parts:
        gs_questions[get_question_number(p) - 1].append(p)
    gs_max_score = list(map(get_total_points, gs_questions))
    csv_rows = []
    for r in gs_df.itertuples():
        email = r[1]
        sid = str(r[2])

        if r[4] == "Missing":
            continue

        part_scores = list(r[10:])
        for qInfo, parts, max_score in zip(pl_qmap[sid], gs_questions, gs_max_score):
            variant = qInfo[0]
            new_weight = ceil(qInfo[1]/qInfo[2] * 100)
            old_score = qInfo[3]

            score = 0
            for _ in range(len(parts)):
                score += float(part_scores.pop())
            score_perc = 0 if score == 0 else score/max_score
            score_perc = min(new_weight * score_perc +  old_score, 100)
            csv_rows.append([email, instance, variant, score_perc, f'{old_score} + {score}/{max_score} on gs'])

    pl_df = pd.DataFrame(
        csv_rows, columns=['uid', 'instance', 'qid', 'score_perc', 'feedback'])
    pl_df.to_csv('pl_scores.csv', index=False)
