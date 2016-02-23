import csv
import sys
import os

#subject_files = "/Volumes/seedlings/Subject_Files"
subject_files = "data"

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

def fix_bl_edits():
    chunked_problems = chunk_problem_files()
    for key, value in chunked_problems.iteritems():
        find_audio_bl_file_and_edit(key, value)


def chunk_problem_files():
    chunks = {}

    for problem in problem_files:
        if problem[0][0:5] in chunks:
            chunks[problem[0][0:5]].append(problem)
        else:
            chunks[problem[0][0:5]] = [problem]

    return chunks

def find_audio_bl_file_and_edit(key, problems):
    for root, dirs, files in os.walk(subject_files):
        if key in root and "Audio_Analysis" in root:
            with open(os.path.join(root, problems[0][0]), "rU") as input_file:
                reader = csv.reader(input_file)
                #reader.next()
                with open(os.path.join(root, problems[0][0].replace(".csv", "_bltidy.csv")), "wb") as output_file:
                    writer = csv.writer(output_file)
                    for problem in problem_files:
                        for row in reader:
                            if row[6] == problem[7] and row[5] == problem[6]:
                                row[6] = problem[8]
                                writer.writerow(row)
                            else:
                                writer.writerow(row)


if __name__ == "__main__":
    #bl_file = sys.argv[1]

    bl_edit_file = sys.argv[1]

    #create_edit_csv()

    read_csv()
    fix_bl_edits()
    print problem_files
