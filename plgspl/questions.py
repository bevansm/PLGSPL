from plgspl.types import PDF
from enum import Enum
from functools import reduce
from typing import List, Dict
import json
import os
import collections
from plgspl.cfg import cfg, get_cfg
import markdown2


lineWidth = get_cfg('page', 'lineWidth', default=180, cast=int)
lineHeight = get_cfg('page', 'lineHeight', default=0, cast=int)


def draw_line(pdf: PDF, width=lineWidth, color=get_cfg('font', 'header', 'line', default={"r": 0, "b": 0, "g": 0})):
    '''
        draws a line on the page.
        by default, the line is the page width.
    '''
    pdf.ln(6)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(color['r'], color['b'], color['g'])
    pdf.line(10, pdf.get_y(), 12 + width, pdf.get_y())
    pdf.ln(6)


def pad(pdf):
    '''
        pads the pdf with a blank page.
    '''
    pdf.add_page()
    draw_line(pdf)
    pdf.cell(lineWidth, txt="This is a blank page.")


def pad_until(pdf: PDF, page_number, info=''):
    '''
        pads the pdf until the target page number.
    '''
    if pdf.page_no() > page_number:
        print('Warning: A question exceeds expected length. Please re-adjust your configuration.', info)
        print('Dumping current pdf as incomplete_assignment.pdf')
        pdf.output(os.path.join(os.getcwd(), 'incomplete_assignment.pdf'))
        exit(1)
    while pdf.page_no() < page_number:
        pad(pdf)


def render_header(pdf: PDF, txt, header_cfg=get_cfg('font', 'header')):
    '''
        renders a question header with the given text.
    '''
    pdf.set_font(header_cfg['font'], size=header_cfg['size'])
    pdf.cell(lineWidth, txt=txt)
    draw_line(pdf, pdf.get_string_width(txt), header_cfg['line'])


def render_part_header(pdf: PDF, txt):
    '''
        renders a part header with the given text.
    '''
    render_header(pdf, txt, get_cfg('font', 'subheader'))


def render_gs_anchor(pdf: PDF, variant, score=0):
    '''
        Renders the gs anchor box for a given question/question part.
        -1:     Empty box. Intended for template variants.
         0:     Completely incorrect answer.
        < 100:  Partially correct answer.
        100:    Completely correct answer.
    '''
    if score == -1:
        a_cfg = get_cfg('gsAnchor', 'blank')
    elif score == 0:
        a_cfg = get_cfg('gsAnchor', 'incorrect')
    elif score < 100:
        a_cfg = get_cfg('gsAnchor', 'partial')
    elif score == 100:
        a_cfg = get_cfg('gsAnchor', 'correct')
    else:
        return
    fill = a_cfg['fill']
    pdf.set_font(cfg['font']['body']['font'])
    pdf.set_fill_color(fill['r'], fill['g'], fill['b'])
    pdf.cell(lineWidth,
             h=get_cfg('gsAnchor', 'height'),
             txt=a_cfg["text"],
             fill=True)
    pdf.ln()


def parse_filename(raw: str, qid):
    '''
        parses a pl filename, assuming it belongs to a question
        with the given question id.
    '''
    return raw.rsplit(qid + "_", 1).pop().split("_", 1).pop()


class QuestionInfo():
    '''
        encapsulates the general question information for a pl question
        (i.e. qid, variants, number of variants to choose)
    '''

    def __init__(self, qid: str,
                 number: int,
                 variants: List[str] = False,
                 parts: List[str] = False,
                 expected_files: set = False,
                 number_choose: int = 1):
        self.qid = qid
        self.number = number
        self.expected_files = expected_files or set()
        self.parts = set(map(str.upper, parts or []))
        self.number_choose = number_choose
        self.variants = variants or [qid]

    def add_file(self, filename):
        self.expected_files.add(parse_filename(filename, self.qid))
    
    def is_part(self, part_name: str):
        return len(self.parts) == 0 or part_name.upper() in self.parts

    def render(self, pdf: PDF):
        render_header(pdf, f'Question {self.number}: {self.qid}')


class AssignmentConfig:
    '''
        manages a group of QuestionInfo objects that compose an assignment
    '''

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
        return self.questions.get(qid, None)


class StudentFileBundle():
    '''
        manages and provides utility functions for a "file bundle",
        i.e. a set of absolute file paths for pl student file uploads
    '''

    def __init__(self, files: List[str] = [], qid=""):
        self.files = dict()
        for file in files:
            self.files[parse_filename(file, qid)] = {
                "path": file, "rendered": False}

    def add_file(self, qid, file):
        self.files[parse_filename(file, qid)] = {
            "path": file, "rendered": False}

    def was_rendered(self, file):
        file = self.files.get(file, False)
        return file and file["rendered"]

    def render_file(self, pdf: PDF, filename):
        '''
            Renders a file to a pdf. Does not start a fresh page.
            Pads out the pages with blank pages if the file does not exist & has not been rendered.
            else, does nothing
        '''
        start = pdf.page_no()
        if self.was_rendered(filename):
            return
        file = self.files.get(filename, False)
        render_part_header(pdf, filename)
        if not file:
            self.files[filename] = {"path": "", "rendered": True}
        if file and not file["rendered"]:
            file["rendered"] = True
            path = file["path"]
            ext = os.path.splitext(path)[1][1:]

            font = get_cfg('font', 'code') if ext in get_cfg('files', 'code') else get_cfg('font', 'body')
            pdf.set_font(font['font'], size=font['size'])

            if ext in get_cfg('files', 'md'):
                pdf.write_html(markdown2.markdown_path(path))
            elif ext in get_cfg('files', 'pics'):
                pdf.image(path, w=lineWidth)
            else:
                for line in open(path, 'r'):
                    pdf.multi_cell(lineWidth, lineHeight, txt=line)

        pad_until(pdf, start + get_cfg('maxPages', 'file', cast=int, default=1) - 1,
                  f'padding for file {filename}')

    # dumps the remainder of the files in this bundle into the question.
    def render_all(self, pdf: PDF):
        for f in self.files:
            self.render_file(pdf, f)


class QuestionPart():
    '''
        encapsulates a part of a question.
    '''

    def __init__(self, question_number: int, part: int, key):
        self.question_number = question_number
        self.part = part
        self.key = key
        self.max_pages = get_cfg('maxPages', 'default', cast=int, default=1)

    def render_ctx(self, pdf: PDF):
        '''
            renders any question context to the pdf.
            renders the string "No context provided." if not overloaded
        '''
        pdf.cell(lineWidth, txt="No context provided.")

    def render_expected(self, pdf: PDF):
        '''
            renders the expected anwer to the pdf.
            renders the string "No context provided." if not overloaded

        '''
        pdf.cell(lineWidth, txt="No expected answer provided.")

    def render_ans(self, pdf: PDF):
        '''
            renders the answer content to the pdf.
            renders the string "no answer provided" if not overloaded
        '''
        pdf.cell(lineWidth, txt="No answer provided.")

    def render(self, pdf: PDF, score=0, as_template=False):
        """
            render a question part onto the pdf.
            1. renders the question ctx, if any
            2. adds the gs grading anchor
            3. renders the given answer, if any
            4. pads until we've reached the max pages for the question.

            if as_template is true, will not render answer, and anchor will be empty.
        """
        start = pdf.page_no()
        render_part_header(
            pdf, f'Question {self.question_number}.{self.part}: {self.key}')
        pdf.set_font(get_cfg('font', 'body', 'font', default='arial'),
                     size=get_cfg('font', 'body', 'font', cast=int, default=10))
        self.render_ctx(pdf)
        draw_line(pdf)
        render_gs_anchor(pdf, self.key, -1 if as_template else score)
        draw_line(pdf)
        self.render_expected(pdf)
        draw_line(pdf)
        if not as_template:
            self.render_ans(pdf)
        pad_until(pdf, start + self.max_pages - 1,
                  f'padding for question {self.question_number}.{self.part}')


class FileQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, files=[], file_bundle=None):
        super().__init__(question_number, part, key)
        self.files = files
        self.file_bundle = file_bundle
        self.max_pages = get_cfg("maxPages", "file",
                                 cast=int, default=1) * len(files)

    def render_ctx(self, pdf): pass
    def render_expected(self, pdf): pass

    def render_ans(self, pdf: PDF):
        if self.file_bundle:
            if len(self.files) > 0:
                self.file_bundle.render_file(pdf, self.files[0])
            for f in self.files[1:]:
                pdf.add_page()
                self.file_bundle.render_file(pdf, f)


class StringQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, ctx='', true_ans='', ans=''):
        super().__init__(question_number, part, key)
        self.ans = str(ans)
        self.ctx = ctx
        self.true_ans = str(true_ans)
        self.max_pages = get_cfg('maxPages', 'string', cast=int, default=1)

    def render_ctx(self, pdf: PDF):
        if isinstance(self.ctx, str):
            if self.ctx == "":
                super().render_ctx(pdf)
            else:
                pdf.multi_cell(lineWidth, lineHeight, txt=self.ctx)
        else:
            pdf.multi_cell(lineWidth, lineHeight, txt=json.dumps(self.ctx))

    def render_expected(self, pdf):
        pdf.multi_cell(lineWidth, lineHeight, txt=f'Expected: {self.true_ans}')

    def render_ans(self, pdf: PDF):
        pdf.multi_cell(lineWidth, lineHeight, self.ans)


class MCQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, ctx=[], true_ans=[], ans=[]):
        super().__init__(question_number, part, key)
        self.ans = ans
        self.ctx = ctx
        self.true_ans = true_ans

    def render_mc(self, pdf: PDF, mc: list):
        for a in mc:
            if isinstance(a, str):
                pdf.cell(lineWidth, txt=str(a))
            elif a.get("html", False):
                pdf.write_html(f'<span>{a["key"]}:{a["html"]}</span>')
            elif a.get("val", False):
                pdf.multi_cell(lineWidth, lineHeight,
                               txr=f'{a["key"]}: {a["val"]}')
            else:
                pdf.cell(lineWidth, txt=json.dumps(a))

    def render_ctx(self, pdf):
        self.render_mc(pdf, self.ctx)

    def render_expected(self, pdf):
        render_part_header(pdf, "Expected Answer(s)")
        self.render_mc(pdf, self.true_ans)

    def render_ans(self, pdf):
        self.render_mc(pdf, self.ans if not isinstance(
            self.ans, (dict, list)) else json.dumps(self.ans))


class ArrayQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, true_ans=[], ans=[]):
        super().__init__(question_number, part, key)
        self.ans = ans
        self.true_ans = true_ans

    def render_expected(self, pdf):
        pdf.multi_cell(lineWidth, lineHeight, txt=str(self.true_ans))

    def render_ans(self, pdf):
        pdf.multi_cell(lineWidth, lineHeight, txt=str(self.ans))


class SymbolicQuestionPart(QuestionPart):
    def __init__(self, question_number, part, key, ans_value="", ans_vars=[]):
        super().__init__(question_number, part, key)
        self.val = ans_value
        self.vars = ans_vars

    def render_ans(self, pdf: PDF):
        pdf.cell(lineWidth, lineHeight, txt=f'{self.key}: {self.val}')
        pdf.ln()
        pdf.cell(lineWidth, lineHeight, txt=f'Variables: {self.vars}')


class StudentQuestion:
    def __init__(self, q: QuestionInfo,
                 raw_params: str, raw_ans_key: str, raw_student_answer: str,
                 file_bundle: StudentFileBundle,
                 variant: str = None, score: float = 0, override_score: float = None):
        self.question = q
        self.file_bundle = file_bundle
        self.variant = variant if variant else q.qid
        self.score = score if not override_score else override_score
        self.max_parts = len(q.expected_files)
        self.parts = self.get_question_parts(
            json.loads(raw_params),
            json.loads(raw_ans_key),
            collections.OrderedDict(json.loads(raw_student_answer).items()))

    def get_question_parts(self, params: dict(), ans_key: dict(), student_answer: collections.OrderedDict):
        parts = []
        q_no = self.question.number
        while len(student_answer) > 0:
            k, v = student_answer.popitem(False)
            k: str
            part_no = len(parts) + 1
            if k.find("_file_editor") == 0:
                continue

            self.max_parts = self.max_parts + 1
            if not self.question.is_part(k):
                continue
            elif (k.find('res') == 0
                  and isinstance(ans_key.get(k, False), list)
                    and isinstance(params.get(k, False), list)):
                parts.append(MCQuestionPart(q_no, part_no, k,
                                            params.get(k, []), ans_key.get(k, []), v))
            elif isinstance(v, dict) and v.get("_type", "") == "sympy":
                parts.append(SymbolicQuestionPart(q_no, part_no, k,
                                                  v["_value"], v["_variables"]))
            elif k.find(".") > 0 and k.rsplit(".", 1).pop().isnumeric():
                ans = []
                arr_key = k.rsplit(".", 1)[0]
                for i in range(len(student_answer)):
                    nxt_key = f'{arr_key}.{i}'
                    if nxt_key == k and v:
                        nxt = v
                        v = False
                    else:
                        nxt = student_answer.pop(nxt_key, False)
                    if not nxt:
                        break
                    ans.append(nxt)
                if v:
                    ans.append(v)
                self.max_parts = self.max_parts - 1 + len(ans)
                parts.append(ArrayQuestionPart(
                    q_no, part_no, f'Array {arr_key}', ans=ans))
            elif not isinstance(v, (dict, list)):
                parts.append(StringQuestionPart(q_no, part_no, k,
                                                params.get(k, params), ans_key.get(k, ""), v))
            else:
                print("Skipping unsupported question part:", k, json.dumps(v))

        if params.get('_required_file_names', False):
            file_names = list(filter(lambda p: p in self.question.expected_files, params['_required_file_names']))
            parts.append(FileQuestionPart(
                q_no, len(parts) + 1, 'required_files', files=file_names, file_bundle=self.file_bundle ))
        return parts

    def render(self, pdf: PDF, template=False):
        '''
            renders the question to the page.
            by default, does not start a new page.
        '''
        self.question.render(pdf)

        if len(self.parts) > 0:
            self.parts[0].render(pdf, self.score, template)
        for p in self.parts[1:]:
            pdf.add_page()
            p.render(pdf, self.score, template)

        for f in self.question.expected_files:
            if not self.file_bundle.was_rendered(f):
                pdf.add_page()
                render_gs_anchor(pdf, f, -1)
                self.file_bundle.render_file(pdf, f)


class Submission:
    '''
        encapsulates a student pl submission.
    '''

    def __init__(self, uid: str):
        self.uid = uid
        self.questions = dict()

    def add_student_question(self, q: StudentQuestion):
        self.questions[q.variant] = q

    def get_student_question(self, variant) -> StudentQuestion:
        return self.questions.get(variant)

    def render_front_page(self, pdf: PDF):
        pdf.set_font(get_cfg('font', 'title', 'font', default="arial"),
                     size=get_cfg('font', 'title', 'size', default=10, cast=int))
        pdf.cell(0, 60, ln=1)
        pdf.cell(0, 20, f'PL UID: {self.uid}', ln=1, align='C')

    def render_submission(self, pdf: PDF, qMap: AssignmentConfig, template=False):
        '''
            renders all of the student's answers/questions to the given question,
            in the order described by the given question map.
        '''
        pdf.add_page()
        self.render_front_page(pdf)
        for q in qMap.get_question_list():
            count = q.number_choose
            for qv in q.variants:
                if count == 0:
                    break
                sq = self.get_student_question(qv)
                if sq != None:
                    count -= 1
                    pdf.add_page()
                    sq.render(pdf, template)

    def list_questions(self, qMap: AssignmentConfig):
        '''
            lists the question variants the student has, in the order expected by qMap
            alongside the the variant, the number of parts in the question, and the max parts in the question (for regrading purposes).
        '''
        row = []
        for q in qMap.get_question_list():
            count = q.number_choose
            for qv in q.variants:
                if count == 0:
                    break
                sq = self.get_student_question(qv)
                if sq != None:
                    count -= 1
                    row.append([sq.variant, len(sq.parts), sq.max_parts, sq.score])
        return row
