## Notes From Paul

The following constants will need to be updated on a per-assessment basis:

```
QN_ORDER = [['feq3'], ['feq4'], ['feq11'], ['feq21', 'feq22', 'feq23', 'feq24']]
MAX_PAGES = [4, 3, 2, 2]
```

`QN_ORDER` defines the order in which questions will be written to the PDF based on their PL ID. So, in the example above, there are 4 questions, the fourth having four variants `(feq21, feq22,…feq24)`.

`MAX_PAGES` defines the maximum number of pages assigned to each question in the PDF (to facilitate putting together the outline in Gradescope)

At the moment, you have to guesstimate `MAX_PAGES`. When the script runs, it will list any student answers that exceed the maximum - you then tweak `MAX_PAGES` accordingly, and run the whole thing again. (Yep, that can definitely be improved upon!)
