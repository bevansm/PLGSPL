from plgspl.pdf import PDF
from enum import Enum
from typing import List, Dict
import json
import os

cfg = json.load(os.path.join(os.path.dirname(__file__), 'defaults.json'))
lineWidth = cfg['page', 'lineWidth']
lineHeight = cfg['page', 'lineHeight']


def pad(pdf):
    pdf.add_page()
    pdf.cell(lineWidth,  txt="This is a blank page.")


def pad_until(pdf: PDF, page_number, info=''):
    if pdf.page_no() > page_number:
        print('Warning: A question exceeds expected length. Please re-adjust your configuration.', info)
        exit(1)
    while pdf.page_no() < page_number:
        pad(pdf)


def draw_line(pdf: PDF, width=lineWidth, color=cfg['font', 'header', 'line']):
    pdf.set_line_width(0.5)
    pdf.set_draw_color(color['r'], color['b'], color['g'])
    pdf.line(10, pdf.get_y(), 12 + width, pdf.get_y())
    pdf.ln(6)


def render_header(pdf: PDF, txt, header_cfg=cfg['font', 'header']):
    pdf.set_font(header_cfg['font'], size=header_cfg['size'])
    pdf.cell(lineWidth, txt=txt)
    draw_line(pdf, pdf.get_string_width(txt), header_cfg['line'])


def render_part_header(pdf: PDF, txt):
    render_header(pdf, txt, cfg['font', 'subheader'])


def render_gs_anchor(pdf: PDF, variant, score=0):
    if score == -1:
        # TODO: no answer, so do that
        return None
    elif score == 0:
        # TODO: render incorrect box
        return None
    elif score < 100:
        # TODO: render partial box
        return None
    elif score == 100:
        # TODO: render correct box
        return None


def parse_filename(raw: str, qid):
    return raw.split(qid + "_").pop()


class QuestionInfo(ABC):
    def __init__(self, qid: str,
                 number: int,
                 variants: List[str] = None,
                 expected_files=set(),
                 number_choose: int = 1):
        self.qid = qid
        self.number = number
        self.expected_files = expected_files
        self.number_choose = number_choose
        self.variants = variants if variants else [qid]

    def add_file(self, filename):
        self.expected_files.add(parse_filename(filename))

    def render(self, pdf: PDF):
        render_header(pdf, f'Question {self.number}: {self.qid}')


class AssignmentConfig:
    def __init__(self):
        self.questions = dict()
        self.qlist = []

    def get_question_count(self):
        return len(self.qlist)

    def get_variant_count(self):
        return len(self.questions)

    def get_question_list(self) -> List[QuestionInfo]:
        return self.qlist

    def add_question(self, q: QuestionInfo):
        self.questions[q.qid] = q
        self.qlist.append(q)
        for v in q.variants:
            self.questions[v] = q

    def get_question(self, qid) -> QuestionInfo:
        return self.questions.get(qid)


class StudentFileBundle():
    def __init__(self, files: List[str] = []):
        self.files = dict()
        for file in files:
            self.files[parse_filename(file, qid)] = {
                "path": file, "rendered": False}

    def add_file(self, qid, file):
        self.files[parse_filename(file, qid)] = {
            "path": file, "rendered": False}

    def was_rendered(self, file):
        file = self.files[file]
        return file and file["rendered"]

    def render_file(self, pdf: PDF, filename):
        '''
            Renders a file to a pdf.
            Pads out the pages with blank pages if the file does not exist & has not been rendered.
            else, does nothing
        '''
        start = pdf.page_no()
        if self.was_rendered(filename):
            return

        file = self.files[filename]
        render_part_header(pdf, filename)
        if not file:
            self.files[filename] = {"path": "", "rendered": True}
        if file and not file["rendered"]:
            file["rendered"] = True
            font = cfg['font', 'code']
            if font['ext'].index(os.path.splitext(file)[1]) == -1:
                font = cfg['font', 'body']
            pdf.set_font(font['font'], size=font['size'])

            for line in open(file, 'r'):
                pdf.multi_cell(lineWidth, lineHeight, txt=line)

        pad_until(pdf, start + cfg['maxPages', 'file'],
                  f'padding for file {filename}')

    # dumps the remainder of the files in this bundle into the question.
    def render_all(self, pdf: PDF):
        for f in self.files:
            render_file(pdf, f)


class QuestionPart():
    def __init__(self, question_number: int, part: int, key):
        self.question_number = question_number
        self.part = part
        self.key = key
        self.max_pages = cfg['maxPages', 'default']

    def render_ctx(self, pdf: PDF):
        '''
            renders any question context to the pdf.
            renders the string "No context provided." if not overloaded
        '''
        pdf.cell(lineWidth, txt="No context provided.")

    def render_ans(self, pdf: PDF):
        '''
            renders the answer content to the pdf.
            renders the string "no answer provided" if not overloaded
        '''
        pdf.cell(lineWidth, txt="No answer provided.")

    def render(self, pdf: PDF, score=0):
        """
            render a question part onto the pdf.
            1. creates a new page
            2. renders the question ctx, if any
            3. adds the gs grading anchor
            4. renders the given answer, if any
            5. pads until we've reached the max pages for the question.
        """
        pdf.add_page()
        start = pdf.page_no()
        render_part_header(
            pdf, f'Question {self.question_number}.{self.part}: {self.key}')
        draw_line(pdf)
        render_gs_anchor(pdf, self.key, score)
        pdf.set_font(cfg['font', 'body', 'font'],
                     size=cfg['font', 'body', 'font'])
        self.render_ans(pdf)
        pad_until(pdf, start + self.max_pages,
                  f'padding for question {self.question_number}.{self.part}')


class FileQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, ctx='', true_ans='', files=[], file_bundle=None):
        super().__init__(question_number, part, key, ctx, true_ans)
        self.files = files
        self.max_pages = cfg["maxPages", "file"] * len(files)

    def render_ans(self, pdf):
        if self.file_bundle:
            for f in self.files:
                self.file_bundle.render_file(pdf, f)


class StringQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, ctx='', true_ans='', ans=''):
        super().__init__(question_number, part, key)
        self.ans = ans
        self.ctx = ctx
        self.true_ans = true_ans
        self.max_pages = cfg['maxPages', 'string']

    def render_ctx(self, pdf: PDF):
        if isinstance(self.ctx, str):
            if self.ctx == "":
                super().render_ctx(pdf)
            else:
                pdf.multi_cell(lineWidth, lineHeight, txt=self.ctx)
        else:
            pdf.multi_cell(lineWidth, lineHeight, txt=json.dumps(self.ctx))
        draw_line(pdf)
        pdf.multi_cell(lineWidth, lineHeight, txt=f'Expected: {self.true_ans}')

    def render_ans(self, pdf: PDF):
        pdf.multi_cell(lineWidth, lineHeight, self.ans)


class MCQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, ctx=[], true_ans=[], ans=[]):
        super().__init__(question_number, part, key, ctx, true_ans)
        self.ans = ans
        self.ctx = ctx
        self.true_ans = true_ans

    def render_mc(self, pdf: PDF, mc):
        for a in mc:
            if a["html"]:
                pdf.write_html(f'<span>{a["key"]}:{a["html"]}</span>')
            else:
                pdf.multi_cell(lineWidth, lineHeight,
                               f'{a["key"]}: {a["val"]}')

    def render_ctx(self, pdf):
        render_mc(self, pdf, self.ctx)
        draw_line(pdf)
        render_part_header(pdf, "Expected Answer(s)")
        render_mc(self, pdf, self.true_ans)

    def render_ans(self, pdf):
        self.render_mc(pdf, self.ans)


class StudentQuestion:
    def __init__(self, q: QuestionInfo,
                 raw_params: str, raw_true_answer: str, raw_student_answer: str,
                 file_bundle: StudentFileBundle,
                 variant: str = None, score: float = 0, override_score: float = None):
        self.question = q
        self.file_bundle = file_bundle
        self.variant = variant if variant else q.qid
        self.score = score if not override_score else override_score

        parts = dict()
        params = json.loads(raw_params)
        student_answer = json.loads(raw_student_answer)

        for k, v in json.loads(raw_true_answer).items():
            if isinstance(v, list):
                k: str
                # this handles mc questions. other list type questions are up in the air.
                # some pl string have list types attached to the answer, but they also have
                #   the list map to raw key value parts in the parent object.
                if v[0] and v[0]['key']:
                    res = params[k]
                    if k.index('ans') > -1:
                        if k == 'ans':
                            p_ctx = params['res']
                        else:
                            p_ctx = params[f'res{k.split("ans").pop()}']
                    parts[k] = MCQuestionPart(q.number, len(
                        parts), k, p_ctx, v, student_answer[k])
                continue
            elif v["_type"] == "sympy":
                # TODO: handle symbolic questions (doesn't look like there's an easy mapping...)
                print('Skipping unsupported symbolic question part',
                      k, json.dumps(v))
                continue
            elif isinstance(student_answer[k], str):
                p_ctx = params[k] or params
                parts[k] = StringQuestionPart(q.number, len(
                    parts), k, p_ctx, v, student_answer[k])
            else:
                print("Skipping unsupported question part", k, json.dumps(v))
                return None

        if params['_required_file_names']:
            self.parts[f'required_files {len(parts)}'](FileQuestionPart(
                q.number, len(parts), 'required_files', files=params['_required_file_names']))

        self.parts = parts

    def render(self, pdf: PDF):
        self.question.render(pdf)
        for p in self.parts:
            p.render(pdf, score=self.score)
        for f in self.q.expect_files:
            if not self.file_bundle.was_rendered(f):
                render_gs_anchor(pdf, f, -1)
                self.file_bundle.render_file(pdf, f, score=self.score)


class Submission:
    def __init__(self, uid: str):
        self.uid = uid
        self.questions = dict()

    def add_student_question(self, q: StudentQuestion):
        self.questions[q.variant] = q

    def get_student_question(self, variant) -> StudentQuestion:
        return self.questions.get(variant)

    def render_front_page(self, pdf: PDF):
        pdf.add_page(cfg['page', 'size'])
        pdf.set_font(cfg['font', 'title', 'font'],
                     size=cfg['font', 'title', 'size'])
        pdf.cell(0, 60, ln=1)
        pdf.cell(0, 20, f'PL UID: {self.uid}', ln=1, align='C')
        return None

    def render_submission(self, pdf: PDF, qMap: AssignmentConfig):
        for q in qMap.get_question_list():
            count = q.number_choose
            for qv in q.variants:
                if count == 0:
                    break
                sq = self.get_student_question(qv)
                if sq != None:
                    count -= 1
                    sq.render(pdf)
