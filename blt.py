import csv
import sys
import os
import pprint


#subject_files = "/Volumes/seedlings/Subject_Files"
subject_files = "data"

opf_tidy_list = "/Volumes/seedlings/Scripts_and_Apps/opf_tidy_list.txt"


bl_file = ""
bl_edit_file = ""

problem_files = []


# key/value = {"subj_visit": [audio_csv, video_csv, cha, opf]}
tidy_paths = {}

chunks = {}

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
            writer.writerow(header+["basic_level_edit","utt_type_edit",
                                    "obj_present_edit","speaker_edit"])
            for row in reader:
                writer.writerow(row + [""])


def check_row(row):
    if row[8]:
        problem_files.append(row)


def chunk_problem_files():
    for problem in problem_files:
        if problem[0][0:5] in chunks:
            chunks[problem[0][0:5]].append(problem)
        else:
            chunks[problem[0][0:5]] = [problem]
    return chunks


def register_edit_paths():
    keys = chunks.keys()

    for key in keys:
        tidy_paths[key] = [None]*4

    for root, dirs, files in os.walk(subject_files):
        if any(x in root for x in keys):
            if "Audio_Analysis" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if correct_audio_csv_filename(file):
                        tidy_paths[key][0] = os.path.join(root, file)
            if "Video_Analysis" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if correct_video_csv_filename(file):
                        tidy_paths[key][1] = os.path.join(root, file)
            if "Audio_Annotation" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if correct_cha_filename(file):
                        tidy_paths[key][2] = os.path.join(root, file)
            if "Video_Annotation" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if "check" in file and file.endswith(".opf"):
                        tidy_paths[key][3] = os.path.join(root, file)


def tidy_all_changes():
    for subject in chunks:
        print "Making changes to {}'s files".format(subject)

        # update audio basic_levels
        if chunks[subject][0][0]:
            fix_original_audio_csv(subject)

        # update video basic_levels
        if chunks[subject][0][1]:
            fix_original_video_csv(subject)

def fix_original_audio_csv(subject):
    path = tidy_paths[subject][0]
    chunk = chunks[subject]
    new_path = path.replace(".csv", "_bl_tidy.csv")
    with open(path, "rU") as input_file:
        with open(new_path, "wb") as output_file:
            reader = csv.reader(input_file)
            reader.next()
            writer = csv.writer(output_file)
            for problem in chunk:
                for row in reader:
                    if aud_csv_basiclevel_diff(row, problem):
                        row[6] = problem[8]
                        writer.writerow(row)
                    else:
                        writer.writerow(row)

                input_file.seek(0)

def aud_csv_basiclevel_diff(row, problem):
    if row[6] == problem[7] and row[5] == problem[6]:
        return True
    return False


def fix_original_video_csv(subject):
    path = tidy_paths[subject][0]
    chunk = chunks[subject]
    new_path = path.replace(".csv", "_bl_tidy.csv")
    with open(path, "rU") as input_file:
        with open(new_path, "wb") as output_file:
            reader = csv.reader(input_file)
            reader.next()
            writer = csv.writer(output_file)
            for problem in chunk:
                for row in reader:
                    if vid_csv_basiclevel_diff(row, problem):
                        row[6] = problem[8]
                        writer.writerow(row)
                    else:
                        writer.writerow(row)

                input_file.seek(0)

def vid_csv_basiclevel_diff(row, problem):
    if row[6] == problem[7] and row[5] == problem[6]:
        return True
    return False

def correct_cha_filename(file):
    if file.endswith(".cha"):
        if "newclan_merged" in file:
            return True
        if "final" in file:
            return True
    return False


def correct_audio_csv_filename(file):
    if file.endswith(".csv"):
        if ("check" in file) and ("ready" not in file) and ("audio" in file):
            return True
    return False


def correct_video_csv_filename(file):
    if file.endswith(".csv"):
        if ("check" in file) and ("ready" not in file) and ("video" in file):
            return True
    return False


def correct_opf_filename(file):
    if file.endswith(".opf"):
        if "final" in file:
            return True
        if "consensus" in file:
            return True
    return False


def find_audio_bl_file_and_edit(key, problems):
    for root, dirs, files in os.walk(subject_files):
        if key in root and "Audio_Analysis" in root:
            with open(os.path.join(root, problems[0][0]), "rU") as input_file:
                reader = csv.reader(input_file)
                with open(os.path.join(root, problems[0][0].replace(".csv", "_bltidy.csv")), "wb") as output_file:
                    writer = csv.writer(output_file)
                    for problem in problem_files:
                        for row in reader:
                            if row[6] == problem[7] and row[5] == problem[6]:
                                row[6] = problem[8]
                                writer.writerow(row)
                            else:
                                writer.writerow(row)



def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts



if __name__ == "__main__":
    #bl_file = sys.argv[1]

    bl_edit_file = sys.argv[1]

    #create_edit_csv()

    read_csv()
    chunks = chunk_problem_files()
    register_edit_paths()

    # pprint.pprint(tidy_paths)

    #fix_bl_edits()

    # print problem_files

    tidy_all_changes()
