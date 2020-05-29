from plgspl.pdf import PDF
from enum import Enum
from functools import reduce
from typing import List, Dict
import json
import os


def get(dictionary, *keys, default=None, cast=lambda x: x):
    '''
        get returns the nested field from a dict.
        it will try to perform the given cast on the field value.
        if the cast fails or the value dne, the default is returned
    '''
    v = reduce(lambda d, key: d.get(key, default) if isinstance(
        d, dict) else default, keys, dictionary)
    try:
        return cast(v)
    except:
        return default


cfg = json.load(open(os.path.join(os.path.dirname(__file__), 'defaults.json')))
lineWidth = get(cfg, 'page', 'lineWidth', default=180, cast=int)
lineHeight = int(get(cfg, 'page', 'lineHeight', default=0, cast=int))


def draw_line(pdf: PDF, width=lineWidth, color=get(cfg, 'font', 'header', 'line', default={"r": 0, "b": 0, "g": 0})):
    pdf.ln(6)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(color['r'], color['b'], color['g'])
    pdf.line(10, pdf.get_y(), 12 + width, pdf.get_y())
    pdf.ln(6)


def pad(pdf):
    pdf.add_page()
    draw_line(pdf)
    pdf.cell(lineWidth, txt="This is a blank page.")


def pad_until(pdf: PDF, page_number, info=''):
    if pdf.page_no() > page_number:
        print('Warning: A question exceeds expected length. Please re-adjust your configuration.', info)
        print('Dumping current pdf as incomplete_assignment.pdf')
        pdf.output(os.path.join(os.getcwd(), 'incomplete_assignment.pdf'))
        exit(1)
    while pdf.page_no() < page_number:
        pad(pdf)


def render_header(pdf: PDF, txt, header_cfg=get(cfg, 'font', 'header')):
    pdf.set_font(header_cfg['font'], size=header_cfg['size'])
    pdf.cell(lineWidth, txt=txt)
    draw_line(pdf, pdf.get_string_width(txt), header_cfg['line'])


def render_part_header(pdf: PDF, txt):
    render_header(pdf, txt, get(cfg, 'font', 'subheader'))


def render_gs_anchor(pdf: PDF, variant, score=0):
    '''
        Renders the gs anchor box for a given question/question part.
        -1:     Empty box. Intended for template variants.
         0:     Completely incorrect answer.
        < 100:  Partially correct answer.
        100:    Completely correct answer.
    '''
    if score == -2:
        # TODO: blank template box anchor
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
    return raw.rsplit(qid + "_", 1).pop().split("_", 1).pop()


class QuestionInfo():
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
        self.expected_files.add(parse_filename(filename, self.qid))

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
            font = get(cfg, 'font', 'code')
            if os.path.splitext(file["path"])[1] in str(font['ext']):
                font = get(cfg, 'font', 'body')
            pdf.set_font(font['font'], size=font['size'])

            for line in open(file["path"], 'r'):
                pdf.multi_cell(lineWidth, lineHeight, txt=line)

        pad_until(pdf, start + get(cfg, 'maxPages', 'file', cast=int, default=1),
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
        self.max_pages = get(
            cfg, 'maxPages', 'default', cast=int, default=1)

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
        pdf.set_font(get(cfg, 'font', 'body', 'font', default='arial'),
                     size=get(cfg, 'font', 'body', 'font', cast=int, default=10))
        self.render_ctx(pdf)
        draw_line(pdf)
        self.render_expected(pdf)
        draw_line(pdf)
        render_gs_anchor(pdf, self.key, -1 if as_template else score)
        if not as_template:
            self.render_ans(pdf)
        pad_until(pdf, start + self.max_pages - 1,
                  f'padding for question {self.question_number}.{self.part}')


class FileQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, files=[], file_bundle=None):
        super().__init__(question_number, part, key)
        self.files = files
        self.file_bundle = file_bundle
        self.max_pages = get(cfg, "maxPages", "file",
                             cast=int, default=1) * len(files)

    def render_ans(self, pdf: PDF):
        if self.file_bundle:
            for f in self.files:
                pdf.add_page()
                self.file_bundle.render_file(pdf, f)


class StringQuestionPart(QuestionPart):
    def __init__(self, question_number: int, part: int, key, ctx='', true_ans='', ans=''):
        super().__init__(question_number, part, key)
        self.ans = str(ans)
        self.ctx = ctx
        self.true_ans = str(true_ans)
        self.max_pages = get(cfg, 'maxPages', 'string', cast=int, default=1)

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

        parts = []
        params = json.loads(raw_params)
        ans_key = json.loads(raw_ans_key)
        student_answer = json.loads(raw_student_answer)

        student_answer: dict()
        ans_key: dict()
        params: dict()
        while len(student_answer) > 0:
            k, v = student_answer.popitem()
            k: str
            if "file_editor" in k or "required_files" in k:
                continue
            elif (k.find('res') == 0
                  and isinstance(ans_key.get(k, False), list)
                    and isinstance(params.get(k, False), list)):
                parts.append(MCQuestionPart(q.number, len(parts),
                                            k, params.get(k, []), ans_key.get(k, []), v))
            elif isinstance(v, dict) and v.get("_type", "") == "sympy":
                parts.append(SymbolicQuestionPart(q.number, len(
                    parts), k, v["_value"], v["_variables"]))
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
                k = f'Array {arr_key}'
                parts.append(ArrayQuestionPart(
                    q.number, len(parts), k, ans=ans))
            elif not isinstance(v, (dict, list)):
                parts.append(StringQuestionPart(q.number, len(
                    parts), k, params.get(k, params), ans_key.get(k, ""), v))
            else:
                print("Skipping unsupported question part:", k, json.dumps(v))

        if params.get('_required_file_names', False):
            parts.append(FileQuestionPart(
                q.number, len(parts), 'required_files', files=params['_required_file_names']))

        parts.reverse()
        self.parts = parts

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
    def __init__(self, uid: str):
        self.uid = uid
        self.questions = dict()

    def add_student_question(self, q: StudentQuestion):
        self.questions[q.variant] = q

    def get_student_question(self, variant) -> StudentQuestion:
        return self.questions.get(variant)

    def render_front_page(self, pdf: PDF):
        pdf.set_font(get(cfg, 'font', 'title', 'font', default="arial"),
                     size=get(cfg, 'font', 'title', 'size', default=10, cast=int))
        pdf.cell(0, 60, ln=1)
        pdf.cell(0, 20, f'PL UID: {self.uid}', ln=1, align='C')

    def render_submission(self, pdf: PDF, qMap: AssignmentConfig, template=False):
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
