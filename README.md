# PLGSPL

A Python tool to convert PrarieLearn CSV results and files into a single PDF for upload to GradeScope.

## Installation

1. Clone the repo
2. Run `pip install .` from the project directory.
3. Enjoy!
4. To uninstall, run `pip uninstall plgspl`.

## Roadmap

- pl element support:
  - [ x ] `pl-string-input`
  - [ ] `pl-file-editor`, `pl-file-upload`
  - [ ] `pl-symbolic-input`
- cli:
  - [ ] `classlist`: map pl to gs classlist
  - [ ] `pdf`: produce a pdf from pl data
  - [ ] `merge`: merge gs results with a pl manual grading csv for final grades
  - [ ] `config`: reset & set custom json files to override defaults

## Context

In 2019W2, [Paul Carter](https://www.cs.ubc.ca/people/paul-carter) created a python script to stitch together files from the `pl-file-editor` element to upload to GradeScope. We've included his script/sample output under [ctx](ctx) and some of his thoughts in [paul.md](ctx/paul.md). The script is [pl-to-pdf](ctx/pl-to-pdf.py).

## Student Assignment Layout

We are basing our assignment layout upon [paul's sample pdf output](ctx/h5j7k.pdf).

### Assumptions

- All variants of a given question have the same type, length, and structure.
- A given question variant is only used in one question (the config uses the `numberChoose` instead)
- We are given the `infoAssessment.json` file from the assignment configuration.
  - We will use the `zones` field to build the outline for the assignment, including question alternatives.
- Student "fill in the blank" questions should not take more than two pages.
  - We should configure this through an enviroment variable.
- All scores in the manual grading csv are displayed as percentages out of 100

### Layout Requirements

- The front page should have the student's pl UUID so we can easily use the gs ai to match uploads.
- A question should have:
  - A question number, corresponding to its index in `infoAssesment.json`
  - A list of the variants, if more than one.
  - Context of the question at the top of the page, so the grader can see the answer.
  - A "correctness indicator" box, so we can use the gs AI to autogroup correct and incorrect questions.
  - The student answer below the above "correctness indicator", so we can actually grade!
- A file upload question should be preceeded by a page just with the question title/context for the grader. The remaining pages should be appended after that.

### The "Correctness Box"

To take advantage of gradescope's autogrouping AI, we append a "correctness box" onto different questions.

`QUID` refers to the question variant.

- A green box with the phrase "CORRECT `QUID`" corresponds to a correct answer.
- A light blue box with the phrase "NO ANSWER `QUID`" corresponds to no given answer.
- A yellow box with with the phrase "PARTIAL `QUID`" corresponds to a partial credit answer.
- A red box with the phrase "INCORRECT `QUID`" corresponds to an incorrect answer.
  We intend for this box to be used as the question matching anchor.

## PDF Generation Workflow

1. parse `infoAssesement.json`
   1. pull out the `zones` object
   2. pull out the questions list
   3. build an assignment outline out of the questions list.
      - set the max file size of each question to the env/cli var
      - add this to some sort of config so we might be able to smartly update down the line
2. for each student in the csv:

   1. If they're the first student, prepare the template gs file.
   2. put together the questions in the order provided. if we cannot find the quid in the csv, we assume that it's a file upload and look for the file in the zip folder.
      - add the question number & title w/main variant
      - parse the "params" object from the manual grading pdf.
      - format the params & true_answer object to give the ta context.
      - add correctness box
      - add submitted_answer
      - add the file if there's a provided file upload

3. append the student to the main pdf
4. move on to next student. continue until we've reached the end of the csv.

## Commands

- `plgspl classlist <CSV>`: Creates a GS classlist from the given PL CSV classlist to autogenerate a "ghost" pl class for grading.
- `plgspl pdf <assignment_name> <INFO_JSON> <MANUAL_CSV> <FILE_DIR>`: Creates a template gs file for the given assignment.
  - `SCORE_CSV` should be a `best_submissions` or `final_submissions` pl file. We use this for 'correctness indicators' on gs to build a wholelistic assignment.
  - `MANUAL_CSV` should be a `**_submissions_for_manual_grading.csv` pl file.
  - `FILE_DIR` should be an unzipped file directory that corresponds to `**_files_for_manual_grading.zip` for `MANUAL_CSV`
  - `INFO_JSON` should be the `infoAssesment.json` file that we used to build the assignment.
- `plgspl merge <assignment_name> <pl_csv> <gs_csv>`
  - Merges the gs and pl csv files for a given assignment into an updated pl csv file: `<assignment_name>_pl_by_question.csv`.
  - Expects the input pl csv file to be the form of a `best_submissions` or `final_submissions` csv file.

## File Structure

- [plgspl](plgspl): Cli scripts
- [res](res): Scrubbed Sample Data (taken from 2020S1 MT2)
- [ctx](ctx): Paul's files

## Scratch

### Future

- Support GS batch uploads (or is the one pdf good enough?)
- What other elements?
- Can we automate this so we can add a pl endpoint and grab the pdfs from a s3 bucket somewhere?
- [is there a way to check the max file upload size for a question cleanly?](https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python)?
  - if so, update max_file_size for that question

### Notes & Useful Scripts

Run sample pdf generation: `plgspl pdf tst config.json ans.csv files`
