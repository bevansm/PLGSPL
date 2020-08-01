# PLGSPL

A Python tool to convert PrarieLearn CSV results and files into a single PDF for upload to GradeScope.

Written at the University of British Columbia, intended for all.

## Context

In 2019W2, [Paul Carter](https://www.cs.ubc.ca/people/paul-carter) created a python script to stitch together files from the `pl-file-editor` element to upload to GradeScope.

Inspired by his work--and in desperate need for a way to grade manually during COVID--we built PLGSPL as a more general, easy way to export PrairieLearn manual grading results to a pdf for gradescope uploads and grading.

There is an [issue open on PL](https://github.com/PrairieLearn/PrairieLearn/issues/2104) to support PDF exports for offline work and grading. We intend for this to be an intermediate solution.

## Setup

### Requirements

- Python 3.x.x+

### Installation

1. Clone the repo
2. Run `pip install .` from the project directory.
3. Read the cli commands in [the doccumentation file](docs/CLI.md) and enjoy!
4. To uninstall, run `pip uninstall plgspl`.

## Doccumentation

- [PLGSPL and Gradescope: Instructions](docs/USE.md)
- [CLI](docs/CLI.md)
- [Technical Notes, Assumptions, and Reference](docs/NOTES.md)

## Roadmap

### Current

- pl element support:
  - [x] `pl-string-input`, `pl-multiple-choice`, `specific array questions`
  - [x] `pl-file-editor`, `pl-file-upload`
  - [ ] `pl-symbolic-input`
- feature support:
  - [x] markdown file formatting
  - [ ] use gs's "export evaluation" feature to get feedback for question
- cli:
  - [x] `classlist`: map pl to gs classlist
  - [x] `pdf`: produce a pdf from pl data
  - [ ] `merge`: merge gs results with a pl manual grading csv for final grades. merges via partials
  - [ ] `config`: reset & set custom json files to override defaults
- fixes
  - [ ] integrate the `partial_scores` field

### Future

- What other elements?
- Can we automate this so we can add a pl endpoint and grab the pdfs from a s3 bucket somewhere?
- [is there a way to check the max file upload size for a question cleanly?](https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python)?
  - if so, update max_file_size for that question

## File Structure

- [plgspl](plgspl): Cli scripts
- [res](res): Sample Data & Outputs
- [ctx](ctx): Paul's files
- [docs](docs): Doccumentation

## Useful Scripts

Run sample pdf && classlist generation: `plgspl classlist ans.csv && plgspl pdf config.json ans.csv files`

## Questions, Concerns, Ect

PLGSPL is very much a POC. We're still waiting on some features in PrairieLearn to be able to succesfully re-import scores. Every university has a different way that they handle Student IDs, and different use cases.

It's a "make do". She may not be beautiful, but she works.
