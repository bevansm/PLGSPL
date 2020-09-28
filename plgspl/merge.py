import json
import re
import pandas as pd
import numpy as np
from functools import reduce
from typing import List
from math import ceil
from plgspl.cfg import get_cfg


def get_part(q: str) -> str:
    '''
        returns the part name of a gradescope question part,
        parsed from a string in the form of "<NAME> (1.0 pts)"
    '''
    return re.search(".*:(.*)\(.*", q).group(1).strip()


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


def merge(qmap_json, gs_csv, instance=1, method=get_cfg('questions', 'mergeMethod', default='partial')):
    '''
        given a gradescope csv and a plgspl question map (per student),
        generates a "manual grading" csv for pl
    '''
    if method == "partial":
        merge_partials(qmap_json, gs_csv, instance)
    elif method == "total":
        merge_total(qmap_json, gs_csv, instance)
    else:
        print("Unsupported merge method.")


def merge_total(qmap_json, gs_csv, instance=1):
    '''
        given a gradescope csv and a plgspl question map (per student),
        generates a "manual grading" csv for pl by just taking the overall score
        of the given question, and uploading it as a final score.
        this assumes that the weight of each part is equal to one.
        it will try to use pre-existing partials when possible.

        this re-weights each question part in accordance to the weights
        detailed by the question config in pl.
    '''
    pl_qmap = json.load(open(qmap_json))
    gs_df = pd.read_csv(gs_csv)

    gs_question_parts = list(gs_df)[10:]
    gs_question_count = get_question_number(gs_question_parts[-1])
    gs_questions = [[] for _ in range(gs_question_count)]

    for p in gs_question_parts:
        qno = get_question_number(p) - 1
        gs_questions[qno].append({'part': get_part(p), 'max': parse_points(p)})

    csv_rows = []
    for r in gs_df.itertuples():
        email = r[1]
        sid = str(r[2])

        if r[4] == "Missing":
            '''
                the student may not have a response on gradescope. in this case, we won't care,
                we'll just leave the partial score that's currently in there
            '''
            continue
        elif sid == 'nan':
            print("Skipping unpaired student...")
            continue

        part_scores = list(r[11:])

        for qInfo, parts in zip(pl_qmap[sid], gs_questions):
            variant = qInfo[0]
            partial_scores = json.loads(qInfo[1])
            for p in parts:
                score = float(part_scores.pop(0)) / p['max']
                if p['part'] in partial_scores:
                    partial_scores[p['part']]['score'] = score
                else:
                    partial_scores[p['part']] = {'score': score, 'weight': 1}

            '''
                code is more or mess copied from merge_partials, but we just calculate the total percentage score rather than the
                individual parts, assuming that each part is max one point.
            '''
            partials = partial_scores.values()
            total_weight = sum(p['weight'] for p in partials)
            score_perc = ceil(100 * sum(p['score'] * (p['weight'] / total_weight)
                                        for p in partials))
            csv_rows.append([email, instance, variant, score_perc])
    pl_df = pd.DataFrame(
        csv_rows, columns=['uid', 'instance', 'qid', 'score_perc'])
    pl_df.to_csv('pl_scores.csv', index=False)


def merge_partials(qmap_json, gs_csv, instance=1):
    '''
        given a gradescope csv and a plgspl question map (per student),
        generates a "manual grading" csv for pl using pl's partial score uploads
        (not supported by pl atm)
    '''
    pl_qmap = json.load(open(qmap_json))
    gs_df = pd.read_csv(gs_csv)

    gs_question_parts = list(gs_df)[10:]
    gs_question_count = get_question_number(gs_question_parts[-1])
    gs_questions = [[] for _ in range(gs_question_count)]

    for p in gs_question_parts:
        qno = get_question_number(p) - 1
        gs_questions[qno].append({'part': get_part(p), 'max': parse_points(p)})

    csv_rows = []
    for r in gs_df.itertuples():
        email = r[1]
        sid = str(r[2])

        if r[4] == "Missing":
            continue

        part_scores = list(r[11:])
        for qInfo, parts in zip(pl_qmap[sid], gs_questions):
            variant = qInfo[0]
            partial_scores = json.loads(qInfo[1])

            for p in parts:
                score = float(part_scores.pop(0)) / p['max']
                if p['part'] in partial_scores:
                    partial_scores[p['part']]['score'] = score
                else:
                    partial_scores[p['part']] = {'score': score, 'weight': 1}

            csv_rows.append([email, instance, variant,
                             json.dumps(partial_scores)])

    pl_df = pd.DataFrame(
        csv_rows, columns=['uid', 'instance', 'qid', 'partial_scores'])
    pl_df.to_csv('pl_scores.csv', index=False)
