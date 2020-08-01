# Use

## Setting up a Classlist with PLGSPL

1. Run `plgspl classlist < MANUAL_GRADING_CSV >` to autogenerate a classlist.
2. In GradeScope, click `Roster > Add Students or Staff > CSV File`
3. Click submit. **Do not notify students that they have been added via email.**
4. Manually add any students who could not be automatically added.
   - Their email should be their prarielearn UID
   - Their ID should be their prarielearn UIN

## Creating Assignments for Use with PLGSPL

PLGSPL makes a few assumptions about the structure of an assignment:

- A student's email on PL uses their GS id as a prefix, i.e. `peterporker@ubc.ca` will map to a GS id of `peterporker`
- Strings don't _need_ unicode characters. PLGSPL will try its best to simpily strings.

## Creating PDFS for Gradescope

### Downloading Files From PraireLearn

1. Navigate to the assignment downloads page on PL: `<ASSIGNMENT> > Downloads`
2. Download `<ASSIGNMENT NAME>_submissions_for_manual_grading.csv` and `<ASSIGNMENT NAME>_files_for_manual_grading.zip`
3. Download the homework configuration file: `<ASSIGNMENT> > Files > infoAssessment.json`

### Creating a PLGSPL Config File

#### infoAssessment.json

PLGSPL uses a modified version of `infoAssessment.json` to convert a `submissions_for_manual_grading.csv` to a set of pdfs. In each config file, you will see a "zones" array. This contains groupings of student questions. Each object in the "zones" array has a questions array.

You will be adding info to the entries of the question arrays. You should remove questions which you will not grade with PLGSPL from the config file.

#### PLGSPL Specific Fields

PLGSPL allows you to add two fields onto each question object:

- `parts` is an array of part names. This specifies the question parts that PLGSPL should grade.
- `files` is an array of file names. This specifies the files that PLGSPL should try to append to the PDF. A full list of supported file extensions can be found in `__defaults.json`

If you do not specify either field, PLGSPL will try to append all parts and files relating to the given question to the PDF. **Please refer to the "true_answer" field of the CSV for a JSON object with all of the question parts for a given question**.

Below is a sample PLGSPL config for a single zone:

```json
{
  "questions": [
    {
      "id": "h1_2020S_2a_msamericana",
      "parts": ["ans1", "ans2"],
      "files": ["playListAns.cpp", "mdtest.md", "picture.png"],
      "points": 1
    },
    {
      "numberChoose": 1,
      "points": 1,
      "parts": ["a", "b"],
      "alternatives": [
        {
          "id": "lq02_2a_bestworst",
          "points": 1
        },
        {
          "id": "lq02_2b_bestworst",
          "points": 1
        }
      ]
    }
  ]
}
```

### Creating PDFs With PLGSPL

1. Run `plgspl pdf <CONFIG JSON> <ANS CSV> <ANS FILE FOLDER (OPTIONAL)>`
2. Save the resulting files:
   - A sample PDF for GradeScope outlines
   - A series of student answer PDFS
   - A JSON file used for later configuration, ending in `qmap.json`

## Importing PLGSPL PDFS into Gradescope

1. Run `plgspl pdf ...` to generate the assignment pdf. Save the resulting "question map" csv.
2. In Gradescope, click `Assignments > Create Assignment > Exam/Quiz`
3. Use the sample pdf as your template
4. Create the sample outline

   1. Assign the UID line on the front page to an "ID Region"
   2. For each question:
      - Create a gradescope question. Note that the same question with multiple variants should be a single question on gradescope; create seperate rubric groups for each variant if needbe.
      - Pair each part of the question with their respective gradescope anchor boxes or the question area, as you see fit. Each question part should have a title corresponding to the PL part it came from, i.e. if the part was called "bestOrder123" on PL, you should give the GS question part a title of "bestOrder123"
      - Weight each part as you see fit. Remember that each question part will end up being out of max one point when re-uploaded to PL.

5. Upload submission pdfs. Adjust splits as needed.
6. As these pdfs are programatically generated, you should be able to group them easily.

## Exporting From Gradescope to PrairieLearn

1. Click on `Assignments > <ASSIGNMENT_NAME> > Review Grades > Download Grades > Download CSV`
2. Download the resulting CSV.
3. Run `plgspl merge <CONFIG JSON FROM PLGSPL PDF> <GS CSV>`
4. Upload the resulting score CSV to prairielearn.

## Customizing PLGSPL

`_defaults.json` contains default values for different formatting considerations with PLGSPL. Read the `"description"` keys for each to find out more.
