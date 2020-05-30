# PLGSPL

A Python tool to convert PrarieLearn CSV results and files into a single PDF for upload to GradeScope.

## Installation

1. Clone the repo
2. Run `pip install .` from the project directory.
3. Enjoy!
4. To uninstall, run `pip uninstall plgspl`.

## Roadmap

- pl element support:
  - [x] `pl-string-input`
  - [x] `pl-file-editor`, `pl-file-upload`
  - [ ] `pl-symbolic-input`
- cli:
  - [x] `classlist`: map pl to gs classlist
  - [x] `pdf`: produce a pdf from pl data
  - [ ] `merge`: merge gs results with a pl manual grading csv for final grades
  - [ ] `config`: reset & set custom json files to override defaults

## Context

In 2019W2, [Paul Carter](https://www.cs.ubc.ca/people/paul-carter) created a python script to stitch together files from the `pl-file-editor` element to upload to GradeScope. We've included his script/sample output under [ctx](ctx) and some of his thoughts in [paul.md](ctx/paul.md). The script is [pl-to-pdf](ctx/pl-to-pdf.py).

## Commands

- `plgspl classlist <CSV>`: Creates a GS classlist from the given PL CSV classlist to autogenerate a "ghost" pl class for grading.
- `plgspl pdf <INFO_JSON> <MANUAL_CSV> <FILE_DIR>`: Creates a template gs file for the given assignment.
  - `INFO_JSON` should be an `assignmentInfo.json` file from prarielearn, with questions you don't want in the pdf dropped from the file.
  - `MANUAL_CSV` should be a `**_submissions_for_manual_grading.csv` pl file.
  - `FILE_DIR` should be an unzipped file directory that corresponds to `**_files_for_manual_grading.zip` for `MANUAL_CSV`
- `plgspl merge <assignment_name> <pl_csv> <gs_csv>`
  - Merges the gs and pl csv files for a given assignment into an updated pl csv file: `<assignment_name>_pl_by_question.csv`.
  - Expects the input pl csv file to be the form of a `best_submissions` or `final_submissions` csv file.

## Notes

Technical notes, requirements, assumptions, ect. may be found in [NOTES.md](NOTES.md).

## File Structure

- [plgspl](plgspl): Cli scripts
- [res](res): Sample Data & Outputs
- [ctx](ctx): Paul's files

### Future

- Support GS batch uploads (or is the one pdf good enough?)
- What other elements?
- Can we automate this so we can add a pl endpoint and grab the pdfs from a s3 bucket somewhere?
- [is there a way to check the max file upload size for a question cleanly?](https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python)?
  - if so, update max_file_size for that question

### Useful Scripts

Run sample pdf && classlist generation: `plgspl classlist ans.csv && plgspl pdf config.json ans.csv files`
