import csv
from datetime import date

def transform_csv_cell_type(cell_str):
    try:
        return int(cell_str)
    except:
        pass

    try:
        return float(cell_str)
    except:
        pass

    try:
        return date.strptime(cell_str,"%Y-%m-%d")
    except:
        pass

    if cell_str == 'None':
        return None

    return cell_str

def read_csv_data(filename):
    with open(filename) as file:
        csv_reader = csv.reader(file)
        list_of_tuples = list()
        for row in csv_reader:
            list_ = list()
            for element in row:
                data = transform_csv_cell_type(element)
                list_.append(data)
            list_of_tuples.append(tuple(list_))
    return list_of_tuples