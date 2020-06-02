# Gradescope

## Setting up a Classlist with PLGSPL

1. Run `plgspl classlist < MANUAL_GRADING_CSV >` to autogenerate a classlist.
2. In GradeScope, click `Roster > Add Students or Staff > CSV File`
3. Click submit. **Do not notify students that they have been added via email.**
4. Manually add any students who could not be automatically added.
   - Their email should be their prarielearn UID
   - Their ID should be their prarielearn UIN

## Importing Into Gradescope From PLGSPL

1. Run `plgspl pdf ...` to generate the assignment pdf. Save the resulting "question map" csv.
2. In Gradescope, click `Assignments > Create Assignment > Exam/Quiz`
3. Use the sample pdf as your template
4. Create the sample outline

   1. Assign the UID line on the front page to an "ID Region"
   2. For each question:
      - Create a gradescope question. Note that the same question with multiple variants should be a single question on gradescope; create seperate rubric groups for each variant if needbe.
      - Pair each part of the question with their respective gradescope anchor boxes or the question area, as you see fit.
      - Weight each part as you see fit.

5. Upload submission pdfs. Adjust splits as needed.
6. As these pdfs are programatically generated, you should be able to group them easily.

## Exporting From Gradescope For PLGSPL "merge"

1. Click on `Assignments > <ASSIGNMENT_NAME> > Review Grades > Download Grades > Download CSV`
2.
