import csv
import base64 as b64
from io import StringIO

# def list_to_csv(list_values):
#     with open('csv_to_base64.csv', 'w', newline='') as csv_file:
#         wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
#         wr.writerow(list_values)
#         return wr
def list_to_csv(success, list_values):
    # with open('csv_to_base64.csv', 'w', newline='') as csv_file:
    #     wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    #     wr.writerow(list_values)
    #     return wr
    f = StringIO()
    pre_values = []
    if success:
        if len(list_values) > 0:
            pre_values.append(list(list_values[0].keys()))
            for row in list_values:
                pre_values.append(list(row.values()))
    csv.writer(f).writerows(pre_values)
    encoded = b64.b64encode(f.getvalue().encode()).decode('utf-8')
    return "data:text/csv;base64," + encoded
    