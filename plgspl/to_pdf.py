
import pandas as pd
import plgspl.questions as qs
from plgspl.pdf import PDF
import os
import json


def to_pdf(out_file, info_json, manual_csv, file_dir=None):
    submissions = dict()
    config = qs.AssignmentConfig()

    # load the raw assignment config file
    print(f'Loading config from {info_json}...')
    zones = json.load(open(info_json))['zones']
    for z in zones:
        for i, raw_q in enumerate(z['questions']):
            q = None
            if 'id' not in raw_q:
                vs = list(map(lambda q: q['id'], raw_q['alternatives']))
                q = qs.QuestionInfo(
                    vs[0], i, variants=vs, number_choose=raw_q['numberChoose'])
            else:
                q = qs.QuestionInfo(raw_q['id'], i)
            config.add_question(q)
    print(
        f'Parsed config. Created {config.get_question_count()} questions and {config.get_variant_count()} variants.', end='\n\n')

    # iterate over the rows of the csv and parse the data
    print(
        f'Parsing submissions from {manual_csv} and provided file directory (if any)')
    manual = pd.read_csv(manual_csv)
    for i, m in manual.iterrows():
        uid = str(m['UIN'])
        qid = m['qid']
        sid = m['submission_id']
        submission = submissions.get(uid)
        if not submission:
            submission = qs.Submission(uid)
            submissions[uid] = submission
        q = config.get_question(qid)

        # look for any files related to this question submission
        fns = []
        if file_dir:
            for fn in os.listdir(file_dir):
                if fn.find(f'{uid}_{qid}_{sid}') > -1:
                    fns.append(os.path.join(file_dir, fn))
                    q.add_file(os.path.join(file_dir, fn))
        submission.add_student_question(
            qs.StudentQuestion(q,
                               m['params'], m['true_answer'], m['submitted_answer'],
                               qs.StudentFileBundle(fns, qid), qid, int(m[3])))
    print(f'Created {len(submissions)} submission(s)..')

    pdf = PDF()
    for k, v in submissions.items():
        v.render_submission(pdf, config)
    pdf.output(os.path.join(os.getcwd(), f'{out_file}_submissions.pdf'))

    sample_pdf = PDF()
    qs.Submission('SAMPLE').render_submission(pdf, config, True)
    pdf.output(os.path.join(os.getcwd(), f'{out_file}_sample.pdf'))
