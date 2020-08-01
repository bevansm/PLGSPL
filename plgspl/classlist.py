import pandas as pd


def classlist(pl_csv):
    '''
        generates a mock classlist csv for easy setup of a "mock" class on GradeScope
        from PL information
    '''
    pl_csv = pd.read_csv(pl_csv)
    students = dict()
    for uin, uid in zip(pl_csv.UIN, pl_csv.uid):
        students[uin] = {'id': uin, 'email': uid}

    def to_gs_row(s):
        return [s['email'], s['email'], s['email'].split("@", 1)[0]]
    gs_csv = pd.DataFrame(map(to_gs_row, list(students.values())),
                          columns=['Full Name', 'Email', 'SID'])
    gs_csv.to_csv('classlist.csv', index=False)
