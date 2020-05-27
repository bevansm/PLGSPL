# PLGSPL

A Python tool to convert PrarieLearn CSV results and files into a single PDF for upload to GradeScope.

## Roadmap

- pl element support:
  - [] `pl-string-input`
  - [] `pl-file-editor`
  - [] `pl-file-upload`
  - [] `pl-symbolic-input`
- cli:
  - [] `classlist`
  - [] `pdf`
  - [] `merge`

## Context

In 2019W2, [Paul Carter](https://www.cs.ubc.ca/people/paul-carter) created a python script to stitch together files from the `pl-file-editor` element to upload to GradeScope. We've included his script/sample output under [ctx](ctx) and some of his thoughts in [paul.md](ctx/paul.md). The script is [pl-to-pdf](ctx/pl-to-pdf.py).

## Student Assignment Layout

We are basing our assignment layout upon [paul's sample pdf output](ctx/h5j7k.pdf).

### Assumptions

- All variants of a given question have the same type.
- We are given the `infoAssessment.json` file from the assignment configuration.
  - We will use the `zones` field to build the outline for the assignment, including question alternatives.
- Student "fill in the blank" questions should not take more than two pages.
  - We should configure this through an enviroment variable.
- We can find the number of pages of a given pdf upload from the pdf metadata.
  - We will use this to build the template gs question.

### Layout Requirements

- The front page should have the student's pl UUID so we can easily use the gs ai to match uploads.
- A question should have:
  - A question number, corresponding to its index in `infoAssesment.json`
  - A list of the variants, if more than one.
  - Context of the question at the top of the page, so the grader can see the answer.
  - A "correctness indicator" box, so we can use the gs AI to autogroup correct and incorrect questions.
  - The student answer below the above "correctness indicator", so we can actually grade!
- A file upload question should be preceeded by a page just with the question title/context for the grader. The remaining pages should be appended after that.

## PDF Generation Workflow

1. parse `infoAssesement.json`
   1. pull out the `zones` object
   2. pull out the questions list
   3. build an assignment outline out of the questions list.
2. for each student in the csv:
   If they're the first student, prepare the template gs file.
   2. put together the questions in the order provided. if we cannot find the quid in the csv, we assume that it's a file upload and look for the file in the zip folder.
      - stitch in the question similar to paul if it's a file upload
      - if it's a string/mc question:
        1. parse the "params" object from the manual grading pdf.
        2. format the params & true_answer object to give the ta context.
        3. format submitted_answer
   3. if it's already been graded by pl as correct (i.e. matched answer), add a "CORRECT" flag at the top of the question so we can use the gs ai to filter out these answers.
3. append the student to the main pdf
4. move on to next student. continue until we've reached the end of the csv.

## Commands

- `plgspl classlist <CSV>`: Creates a GS classlist from the given PL CSV classlist to autogenerate a "ghost" pl class for grading.
- `plgspl pdf <assignment_name> <SCORE_CSV> <MANUAL_CSV> <FILE_DIR> <INFO_JSON>`: Creates a template gs file for the given assignment.
  - `SCORE_CSV` should be a `best_submissions` or `final_submissions` pl file. We use this for 'correctness indicators' on gs to build a wholelistic assignment.
  - `MANUAL_CSV` should be a `**_submissions_for_manual_grading.csv` pl file.
  - `FILE_DIR` should be an unzipped file directory that corresponds to `**_files_for_manual_grading.zip` for `MANUAL_CSV`
  - `INFO_JSON` should be the `infoAssesment.json` file that we used to build the assignment.
- `plgspl merge <assignment_name> <pl_csv> <gs_csv>`
  - Merges the gs and pl csv files for a given assignment into an updated pl csv file: `<assignment_name>_pl_by_question.csv`. Expects the input pl csv file to be the form of a `best_submissions` or `final_submissions` csv file.

## File Structure

- [src](src): Python Scripts
- [res](res): Scrubbed Sample Data (taken from 2020S1 MT2)
- [ctx](ctx): Paul's files

## Future Questions

- Support GS batch uploads (or is the one pdf good enough?)
- What other elements?
- Can we automate this so we can add a pl endpoint and grab the pdfs from a s3 bucket somewhere?
