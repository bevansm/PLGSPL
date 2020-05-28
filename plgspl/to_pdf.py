
import pandas as pd
import plgspl.questions as qs
from fpdf import FPDF
import os
import json


def to_pdf(out_file, info_json, manual_csv, file_dir=None):
    submissions = dict()
    config = qs.AssignmentConfig()

    # load the raw assignment config file
    zones = json.load(open(info_json))['zones']
    for z in zones:
        for i, raw_q in enumerate(z['questions']):
            q = None
            if 'id' not in raw_q:
                vs = raw_q['alternatives']
                q = qs.QuestionInfo(vs[0], i, vs, False, raw_q['numberChoose'])
            else:
                q = qs.QuestionInfo(raw_q['id'], i)
            config.add_question(q)
        print(
            f'Parsed config... Created {config.get_question_count()} questions and {config.get_variant_count()} variants...')

    # iterate over the rows of the csv and parse the data
    manual = pd.concat(pd.read_csv(manual_csv))
    for m in manual.iterrows():
        uid = m['UIN']
        qid = m['QID']
        sid = m['submission_id']
        submission = submissions.get(uid)
        if not submission:
            submission = qs.Submission(uid)
            submissions[uid] = submission
        q = config.get_question(qid)

        csv = qs.StudentCSV(
            q, m['params'], m['true_answer'], m['submitted_answer'])

        # look for any files related to this question submission
        if file_dir:
            fns = []
            for fn in os.listdir(file_dir):
                if fn.find(f'{uid}_{qid}_{sid}'):
                    fn.append(os.path.join(file_dir, fn))
            if len(fns):
                q.expect_files = True
            file_bundle = qs.StudentFileBundle(fns)
            sq = qs.StudentQuestion(q, csv, file_bundle,
                                    qid, int(m['old_score']))

    json.dump(submissions, 'tst.json')
    # pdf = FPDF()
    # for k, v in submissions:
    #     v.render_submission(pdf, config)
    # pdf.output(os.path.join(os.getcwd(), f'{out_file}_submissions.pdf'))

    # sample_pdf = FPDF()
    # qs.Submission('SAMPLE').render_submission(pdf, config)
    # pdf.output(os.path.join(os.getcwd(), f'{out_file}_sample.pdf'))
