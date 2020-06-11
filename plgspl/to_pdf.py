
import pandas as pd
import plgspl.questions as qs
from plgspl.types import PDF
import os
import json
from plgspl.cfg import get_cfg


def to_pdf(info_json, manual_csv, file_dir=None):
    submissions = dict()
    config = qs.AssignmentConfig()

    # load the raw assignment config file
    cfg = json.load(open(info_json))
    out_file = cfg.get("title", "assignment").replace(" ", "_")
    zones = cfg['zones']
    print(f'Parsing config for {out_file}...')
    for z in zones:
        for i, raw_q in enumerate(z['questions']):
            parts = raw_q['parts'] if 'parts' in raw_q else []
            if 'id' not in raw_q:
                vs = list(map(lambda q: q['id'], raw_q['alternatives']))
                q = qs.QuestionInfo(
                    vs[0], i + 1, variants=vs, number_choose=raw_q['numberChoose'], parts=parts)
            else:
                q = qs.QuestionInfo(raw_q['id'], i + 1, parts=parts)
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
        if not q:
            continue

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

    def pdf_output(pdf, name):
        pdf.output(os.path.join(os.getcwd(), f'{out_file}_{name}.pdf'))

    prev = 1
    for i, (_, v) in enumerate(submissions.items()):
        v: qs.Submission
        v.render_submission(pdf, config)
        if i == 0:
            pdf_output(pdf, "sample")
            max_submissions = get_cfg('gs', 'pagesPerPDF') / pdf.page_no()
            if max_submissions < 1:
                print('Cannot create submissions given the current max page constraint.')
                print('Please adjust your defaults.')
                exit(1)
            max_submissions = int(max_submissions)
        if i != 0 and i % max_submissions == 0:
            pdf_output(pdf, f'{i - max_submissions + 1}-{i + 1}')
            prev = i + 1
            pdf = PDF()
    if prev < len(submissions) or len(submissions) == 1:
        pdf_output(pdf, f'{prev}-{len(submissions)}')

    json.dump({k: v.list_questions(config)
               for k, v in submissions.items()}, open(f'{out_file}_qmap.json', 'w'))
