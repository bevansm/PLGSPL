from fpdf import FPDF
from enum import Enum
from typing import List
import json
import os


def get_max_pages():
    try:
        return int(os.environ.get("MAX_PAGES"))
    except:
        return 2


def render_gs_anchor(pdf: FPDF, variant, score=0):
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


class QuestionInfo:
    def __init__(self, qid: str,
                 number: int,
                 variants: List[str] = None,
                 expect_files: bool = False,
                 number_choose: int = 1,
                 max_pages: int = get_max_pages()):
        self.qid = qid
        self.number = number
        self.expect_files = expect_files
        self.number_choose = number_choose
        self.max_pages = max_pages
        self.variants = variants if variants else [qid]

    def render(self, pdf: FPDF):
        # TODO: render question header/info on page.
        return None


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


class StudentCSV():
    def set_question_ctx(self, params, answer):
        # TODO: parse this
        self.ctx = params

    def set_student_ans(self, answer):
        # TODO: parse this
        self.answer = answer

    def __init__(self, params: str, true_answer: str, student_answer: str):
        self.set_student_ans(student_answer)
        self.set_question_ctx(params, true_answer)

    def render_ctx(self, pdf: FPDF):
        # TODO: render the question ctx onto the page
        return None

    def render_student_ans(self, pdf: FPDF):
        # TODO: render the parsed answer onto the page
        return None

    def render(self, pdf: FPDF):
        self.render_ctx(pdf)
        self.render_ans(pdf)


class StudentFileBundle():
    def parse_filename(self, filename):
        # TODO: parse off filename
        return filename

    def __init__(self, files: List[str] = []):
        self.files = dict()
        for file in files:
            self.files[self.parse_filename(file)] = file

    def add_file(self, file):
        self.files[self.parse_filename(file)] = file

    def render_file(self, pdf: FPDF, filename):
        # TODO: write the name of the file to the pdf like a part header
        # TODO: remove file from bundle once done
        return None

    def render_all(self, pdf: FPDF):
        for f in self.files:
            render_file(pdf, f)


class StudentQuestion:
    def __init__(self, q: QuestionInfo, csv: StudentCSV, file_bundle: StudentFileBundle,
                 variant: str = None, score: float = 0, override_score: float = None):
        self.question = q
        self.csv = csv
        self.file_bundle = file_bundle
        self.variant = variant if variant else q.qid
        self.score = score if not override_score else override_score

    def render(self, pdf: FPDF):
        self.question.render(pdf)
        render_gs_anchor(pdf, self.variant, self.score)
        self.csv.render(pdf)
        if self.q.expect_files:
            self.file_bundle.render(pdf)


class Submission:
    def __init__(self, uid: str):
        self.uid = uid
        self.questions = dict()

    def add_student_question(self, q: StudentQuestion):
        self.questions[q.variant] = q

    def get_student_question(self, variant) -> StudentQuestion:
        return self.questions.get(variant)

    def render_front_page(self, pdf: FPDF):
        # TODO: render the pl uid page
        return None

    def render_submission(self, pdf: FPDF, qMap: AssignmentConfig):
        for q in qMap.get_question_list():
            count = q.number_choose
            for qv in q.variants:
                if count == 0:
                    break
                sq = self.get_student_question(qv)
                if sq != None:
                    count -= 1
                    sq.render(pdf)
            while count != 0:
                qMap.get(q.qid).render(pdf)
                render_gs_anchor(pdf, q.qid, -1)
                # TODO: pad with empty pages
                count -= 1
