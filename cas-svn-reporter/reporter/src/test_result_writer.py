import csv


class TestResultCSVWriter:

    def __init__(self, csv_file="test_results.csv"):
        self.csv_file = csv_file
        self.handle = None

    def __enter__(self):
        self.handle = open(self.csv_file, 'w', newline='')
        return self

    def __exit__(self, *args):
        self.handle.close()

    def write_result(self, result):
        test_writer = csv.writer(self.handle)
        test_writer.writerow(result.to_list())

    def write_results(self, result_set):
        for result in result_set:
            self.write_result(result)
