# Technical Notes and Assumptions

### The "Correctness Box"

To take advantage of gradescope's autogrouping AI, we append a "correctness box" onto different questions.

`QUID` refers to the question variant.

- A green box with the phrase "CORRECT `QUID`" corresponds to a correct answer.
- A light blue box with the phrase "NO ANSWER `QUID`" corresponds to no given answer.
- A yellow box with with the phrase "PARTIAL `QUID`" corresponds to a partial credit answer.
- A red box with the phrase "INCORRECT `QUID`" corresponds to an incorrect answer.
  We intend for this box to be used as the question matching anchor.

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
