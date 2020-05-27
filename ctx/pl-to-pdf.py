from fpdf import FPDF
import os

"""
INPUT - directory containing files downloaded from PrairieLearn that contain files produced by pl-file-editor 
OUTPUT - directory to which PDFs are to be written
CLASSLIST - csv containing comma-separated cwl and cs id, one pair per line for each student in class
FILTER - process only files in INPUT with one of these extensions
DELIMITER - delimiter used by PrairieLearn to separate email_qn id_submission_filename
COMMA - CLASSLIST delimiter

QN_ORDER - specify order in which questions must be written to PDF (using PrairieLearn question ids)
MAX_PAGES - map of PrairieLearn qn id to max number of pages in PDF for corresponding answer 
          - needs to be guestimated and adjusted if errors printed to console during PDF
            generation process
"""

INPUT = './input'
OUTPUT = './output'
CLASSLIST = './data/classlist.csv'
FILTER = ['.java', '.txt']
DELIMITER = '_'
COMMA = ','

QN_ORDER = [['feq3'], ['feq4'], ['feq11'], ['feq21', 'feq22', 'feq23', 'feq24']]
MAX_PAGES = [4,  3,  2,  2]

# QN_ORDER = [['feq11']]
# MAX_PAGES = [3]

PAGE_WIDTH = 180       # width of printable region in mm
BODY_FONT_SIZE = 10    # font size for body of text
SUB_HEADER_FONT_SIZE = 11  # font size for header at top of each page
HEADER_FONT_SIZE = 12  # font size for header at top of each page
TITLE_FONT_SIZE = 48   # font size for title on cover page

def class_list():
    """
    Read CLASSLIST and return map of CWL ID to CS ID for each student on list
    """
    cwl_map = {}
    with open(CLASSLIST, 'r') as inf:
        for line in inf:
            csid, cwl, _, _, _, _ = line.split(COMMA)
            cwl_map[cwl.strip()] = csid.strip()
    return cwl_map


def build_file_map():
    """
    Build map of CWL ID to (map of qn id to filename) from those filenames found in INPUT directory whose name begins
    with CWL and whose extension is in FILTER
    """
    file_map = {}
    for filename in os.listdir(INPUT):
        _, ext = os.path.splitext(filename)
        if ext in FILTER:
            cwl = cwl_from_filename(filename)
            qn = parse_qn(filename)
            if cwl in file_map.keys():
                if qn in file_map[cwl]:
                    file_map[cwl][qn].append(filename)
                else:
                    file_map[cwl][qn] = [filename]
            else:
                file_map[cwl] = {qn: [filename]}
    return file_map


def cwl_from_filename(filename):
    """
    Parse CWL ID from filename - assumed to preceed '@'
    """
    tokens = filename.split(DELIMITER)
    return tokens[0].split('@')[0].strip()


def create_pdfs(file_map, cwl_map):
    """
    Create one PDF for each CWL in file_map containing all files associated with that CWL
    Output to file in OUTPUT named <CS ID.pdf>
    Each file corresponds to the answer to one qn.
    PDF is padded to contain MAX_PAGES[qn] pages for qn.
    If qn is longer than MAX_PAGES[qn], error is printed to console.
    """
    for user in file_map.keys():
        csid = cwl_map[user]
        create_pdf(csid, file_map[user])


def create_pdf(csid, qn_map):
    """
    Create PDF in OUTPUT named <csid>.pdf containing answers to questions in filenames found in qn_map
    qn_map maps each qn in QN_ORDER to a filename containing the answer to question
    """
    pdf = FPDF()
    write_id_to_cover(csid, pdf)
    pdf.set_font('courier', size=BODY_FONT_SIZE)

    for qn_options, max_pages in zip(QN_ORDER, MAX_PAGES):
        qn = find_intersection(qn_options, qn_map)
        if qn:
            add_files(pdf, qn_map[qn], max_pages)
        else:
            no_answer(pdf, qn, max_pages)

    pdf.output(os.path.join(OUTPUT, csid + '.pdf'))


def find_intersection(qn_options, qn_map):
    """
    Return qn in qn_options that is in keys of qn_map, None if no such question.
    Raise Exception if there is more than one qn in qn_options that is in keys of qn_map
    as this indicates student answered more than one question from a zone in which only one
    question should have been answered.
    """
    intersect = []

    for qn in qn_options:
        if qn in qn_map:
            intersect.append(qn)

    if len(intersect) == 0:
        return None
    elif len(intersect) > 1:
        raise Exception
    else:
        return intersect[0]


def write_id_to_cover(csid, pdf):
    """
    Write CS ID to cover page of PDF
    """
    pdf.set_font('courier', size=TITLE_FONT_SIZE)
    pdf.add_page()
    pdf.cell(0, 60, ln=1)
    pdf.cell(0, 20, 'CS ID: {}'.format(csid), ln=1, align='C')


def add_files(pdf, filenames, max_pages):
    """
    Add content of filenames (representing answer to single question) to pdf
    """
    start_page_count = pdf.page_no()
    pdf.add_page()
    qn = parse_qn(filenames[0])
    print_qn_header(pdf, qn)
    pdf.set_font('courier', size=BODY_FONT_SIZE)

    filenames.sort()

    for filename in filenames:
        write_file_to_pdf(pdf, filename)
        pdf.cell(0, 6, txt='', ln=1)

    page_count = pdf.page_no() - start_page_count
    pad_pages(pdf, page_count, max_pages, filenames[0])


def parse_qn(filename):
    """
    Parse qn number from filename - assumed to lie between second and third DELIMITER
    """
    tokens = filename.split(DELIMITER)
    return tokens[1]


def write_file_to_pdf(pdf, filename):
    """
    Write contents of filename to pdf with corresponding qn header
    """
    qn_part = parse_qn_part(filename)
    print_qn_part(pdf, qn_part)
    pdf.set_font('courier', size=BODY_FONT_SIZE)

    with open(os.path.join(INPUT, filename), 'r') as src_file:
        for line in src_file:
            if pdf.get_string_width(line) > PAGE_WIDTH:
                write_longline_to_pdf(pdf, line)
            else:
                pdf.cell(0, 6, txt=line, ln=1)


def parse_qn_part(filename):
    """
    Parse qn part identifier from file name
    """
    tokens = filename.split(DELIMITER)
    return tokens[len(tokens) - 1]


def write_longline_to_pdf(pdf, longline):
    """
    Write line longer than PAGE_WIDTH to pdf
    """
    words = longline.split(' ')
    index = 0
    line = ""
    while (index < len(words)):
        if pdf.get_string_width(line) + pdf.get_string_width(words[index]) > PAGE_WIDTH:
            pdf.cell(0, 6, txt=line, ln=1)
            line = words[index] + " "
        else:
            line = line + words[index] + " "

        index = index + 1

    pdf.cell(0, 6, txt=line, ln=1)


def no_answer(pdf, qn, max_pages):
    """
    Write qn header and 'No answer submitted' when no file is found corresponding to qn
    """
    pdf.add_page()
    print_qn_header(pdf, qn)
    pdf.set_font('courier', size=BODY_FONT_SIZE)
    pdf.cell(0, 4, txt='No answer submitted', ln=1)
    pad_pages(pdf, 1, max_pages, 'no answer provided')


def print_qn_header(pdf, qn):
    """
    Print question header to pdf
    """
    pdf.set_font('arial', style='B', size=HEADER_FONT_SIZE)
    title = 'Question {}'.format(qn)
    pdf.cell(0, 10, title, ln=1)
    draw_line(pdf, pdf.get_string_width(title))


def print_qn_part(pdf, qn):
    """
    Print question header to pdf
    """
    pdf.set_font('arial', style='B', size=SUB_HEADER_FONT_SIZE)
    part = 'Part {}'.format(qn)
    pdf.cell(0, 10, part, ln=1)


def draw_line(pdf, width):
    """
    Underline question header with horizontal red line and advance cursor to next line
    """
    pdf.set_line_width(0.5)
    pdf.set_draw_color(255, 0, 0)
    pdf.line(10, pdf.get_y(), 12 + width, pdf.get_y())
    pdf.ln(6)


def pad_pages(pdf, page_count, max_pages_for_qn, filename):
    """
    Pad pages of PDF so that qn has max_pages_for_qn pages
    Prints error to console if PDF exceeds that number of pages for qn
    """
    pages_to_pad = max_pages_for_qn - page_count

    if pages_to_pad < 0:
        print('Error: {} exceeds maximum {} pages allowed - total {} pages.'
              .format(filename, max_pages_for_qn, page_count))
    else:
        add_blank_pages(pdf, pages_to_pad)


def add_blank_pages(pdf, pages_to_pad):
    """
    Add pages_to_pad blank pages to pdf
    """
    for page in range(pages_to_pad):
        pdf.add_page()


if __name__ == '__main__':
    cwl_map = class_list()
    file_map = build_file_map()
    create_pdfs(file_map, cwl_map)