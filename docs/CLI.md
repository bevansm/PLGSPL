# CLI Commands

- `plgspl classlist <CSV>`: Creates a GS classlist from the given PL CSV classlist to autogenerate a "ghost" pl class for grading.
- `plgspl pdf <INFO_JSON> <MANUAL_CSV> <FILE_DIR>`: Creates a template gs file & json config for the given assignment.
  - `INFO_JSON` should be an `assignmentInfo.json` file from prarielearn, with questions you don't want in the pdf dropped from the file.
  - `MANUAL_CSV` should be a `**_submissions_for_manual_grading.csv` pl file.
  - `FILE_DIR` should be an unzipped file directory that corresponds to `**_files_for_manual_grading.zip` for `MANUAL_CSV`
- `plgspl merge <assignment_name> <gs_csv> <config json> <instance>`
  - Converts the gs file for a given assignment into an pl file for upload: `pl.csv`.
  - Instance defaults to 1
