import csv
import sys

bl_file = ""
bl_edit_file = ""

problem_files = []

bl_header = ["id", "tier",
             "object",
             "utterance_type",
             "object_present",
             "speaker",
             "timestamp",
             "basic_level"]


def read_csv():
    with open(bl_edit_file, "rU") as file:
        reader = csv.reader(file)
        reader.next()
        for row in reader:
            check_row(row)


def create_edit_csv():
    global bl_edit_file
    bl_edit_file = bl_file.replace(".csv", "_edits.csv")
    print bl_file
    print bl_edit_file
    with open(bl_file, "rU") as input:
        reader = csv.reader(input)
        header = reader.next()
        with open(bl_edit_file, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(header+["basic_level_edit"])
            for row in reader:
                writer.writerow(row + [""])


def check_row(row):
    if row[8]:
        problem_files.append(row)


if __name__ == "__main__":
    bl_file = sys.argv[1]

    create_edit_csv()
    read_csv()

    print problem_files
