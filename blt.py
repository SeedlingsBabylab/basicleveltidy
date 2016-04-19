import csv
import sys
import os
import pprint

from collections import deque

#subject_files = "/Volumes/seedlings/Subject_Files"
subject_files = "data"

opf_tidy_list = "/Volumes/seedlings/Scripts_and_Apps/opf_tidy_list.txt"


bl_file = ""
bl_edit_file = ""

# id,tier,object,utterance_type,object_present,speaker,timestamp,basic_level,object_edit,utt_type_edit,obj_present_edit,speaker_edit,basic_level_edit
audio_problem_files = []
# "id","ordinal","onset","offset","object","utterance_type","object_present","speaker","basic_level","object_edit","utt_type_edit","obj_pres_edit","speaker_edit", "basic_level_edit"
video_problem_files = []


# key/value = {"subj_visit": [audio_csv, video_csv, cha, opf]}
tidy_paths = {}

audio_diffs = {}
video_diffs = {}

bl_header = ["id", "tier",
             "object",
             "utterance_type",
             "object_present",
             "speaker",
             "timestamp",
             "basic_level"]


class FileGroup:
    def __init__(self, aud_csv, aud_cha, vid_csv, vid_opf):
        self.audio_csv = aud_csv
        self.audio_cha = aud_cha
        self.video_csv = vid_csv
        self.video_opf = vid_opf


class AudBasicLevel:
    def __init__(self,tier, word, utt_type, present,
                 speaker, time, basic_level):
        self.tier = tier
        self.word = word
        self.utt_type  = utt_type
        self.present = present
        self.speaker = speaker
        self.time = time
        self.basic_level = basic_level

    def csv_row(self):
        return [self.tier,
                self.word,
                self.utt_type,
                self.present,
                self.speaker,
                self.time,
                self.basic_level]


class AudBasicLevelEdits:
    def __init__(self, id, tier, word, utt_type, present,
                 speaker, time, basic_level, object_edit,
                 utt_edit, present_edit, speak_edit, bl_edit):
        self.id = id
        self.tier = tier
        self.word = word
        self.utt_type  = utt_type
        self.present = present
        self.speaker = speaker
        self.time = time
        self.basic_level = basic_level
        self.object_edit = object_edit
        self.bl_edit = bl_edit
        self.utt_edit = utt_edit
        self.present_edit = present_edit
        self.speak_edit = speak_edit

        self.needs_full_update = False
        self.needs_only_bl_update = False

        if self.utt_edit or \
            self.present_edit or \
            self.speak_edit or \
            self.object_edit:

            self.needs_full_update = True

        if self.bl_edit and not \
                (self.utt_edit or
                self.present_edit or
                self.speak_edit or
                self.object_edit):
            self.needs_only_bl_update = True



    def csv_row(self):
        return [self.id,
                self.tier,
                self.word,
                self.utt_type,
                self.present,
                self.speaker,
                self.time,
                self.basic_level]



class VidBasicLevel:
    def __init__(self, ordinal, onset, offset, object,
                 utt_type, present, speaker, basic_level):
        self.ordinal = ordinal
        self.onset = onset
        self.offset = offset
        self.object = object
        self.utt_type = utt_type
        self.present = present
        self.speaker = speaker
        self.basic_level = basic_level

    def csv_row(self):
        return [self.ordinal,
                self.onset,
                self.offset,
                self.object,
                self.utt_type,
                self.present,
                self.speaker,
                self.basic_level]


class VidBasicLevelEdits:
    def __init__(self, id, ordinal, onset, offset, object,
                 utt_type, present, speaker, basic_level,
                 object_edit, utt_edit, present_edit, speak_edit,
                 bl_edit):
        self.id = id
        self.ordinal = ordinal
        self.onset = onset
        self.offset = offset
        self.object = object
        self.utt_type = utt_type
        self.present = present
        self.speaker = speaker
        self.basic_level = basic_level
        self.object_edit = object_edit
        self.utt_edit = utt_edit
        self.present_edit = present_edit
        self.speak_edit = speak_edit
        self.bl_edit = bl_edit

        self.needs_full_update = False
        self.needs_only_bl_update = False

        if self.utt_edit or \
                self.present_edit or \
                self.speak_edit or \
                self.object_edit:
            self.needs_full_update = True

        if self.bl_edit and not \
                (self.utt_edit or
                     self.present_edit or
                     self.speak_edit or
                     self.object_edit):
            self.needs_only_bl_update = True

    def csv_row(self):
        return [self.id,
                self.ordinal,
                self.onset,
                self.offset,
                self.object,
                self.utt_type,
                self.present,
                self.speaker,
                self.basic_level,
                self.object_edit,
                self.utt_edit,
                self.present_edit,
                self.speak_edit,
                self.bl_edit]


def read_audio_csv():
    with open(bl_edit_file, "rU") as file:
        reader = csv.reader(file)
        reader.next()
        for row in reader:

            check_audio_row(row)


def read_video_csv():
    with open(bl_edit_file, "rU") as file:
        reader = csv.reader(file)
        reader.next()
        for row in reader:
            check_video_row(row)

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
            writer.writerow(header+["object_level_edit","utt_type_edit",
                                    "obj_present_edit","speaker_edit", "basic_level_edit"])
            for row in reader:
                writer.writerow(row + [""])


def check_audio_row(row):
    if any(x for x in row[8:]):
        edit = AudBasicLevelEdits(*row)
        audio_problem_files.append(edit)

def check_video_row(row):
    if any(x for x in row[9:]):
        edit = VidBasicLevelEdits(*row)
        video_problem_files.append(edit)

def chunk_audio_problem_files():
    for problem in audio_problem_files:
        # if problem[0][0:5] in audio_chunks:
        #     audio_chunks[problem[0][0:5]].append(problem)
        # else:
        #     audio_chunks[problem[0][0:5]] = [problem]

        if problem.id[0:5] in audio_diffs:
            audio_diffs[problem.id[0:5]].append(problem)
        else:
            audio_diffs[problem.id[0:5]] = [problem]
    return audio_diffs

def chunk_video_problem_files():
    for problem in audio_problem_files:
        if problem[0][0:5] in audio_diffs:
            video_diffs[problem[0][0:5]].append(problem)
        else:
            video_diffs[problem[0][0:5]] = [problem]
    return video_diffs

def register_edit_paths():
    keys = chunks.keys()
    audio_keys = audio_diffs.keys()
    video_keys = video_diffs.keys()

    for key in keys:
        tidy_paths[key] = FileGroup(None, None, None, None)

    for root, dirs, files in os.walk(subject_files):
        if any(x in root for x in audio_keys):
            if "Audio_Analysis" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if correct_audio_csv_filename(key, file):
                        tidy_paths[key].audio_csv = os.path.join(root, file)

            if "Audio_Annotation" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if correct_cha_filename(key, file):
                        tidy_paths[key].audio_cha = os.path.join(root, file)

        elif any(x in root for x in video_keys):
            if "Video_Analysis" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if correct_video_csv_filename(key, file):
                        tidy_paths[key].video_csv = os.path.join(root, file)

            if "Video_Annotation" in root:
                split_root = splitall(root)
                key = split_root[-3]
                for file in files:
                    if "check" in file and file.endswith(".opf"):
                        tidy_paths[key].video_opf = os.path.join(root, file)


def tidy_all_audio_changes():
    for subject, diffs in audio_diffs.iteritems():
        print "Making changes to {}'s files".format(subject)

        if any(x.needs_full_update for x in diffs):
            fix_original_audio_csv(subject, diffs)
            update_cha(subject, diffs)
        else:
            fix_original_audio_csv(subject, diffs)


def tidy_all_video_changes():
    for subject, diffs in video_diffs.iteritems():
        print "Making changes to {}'s files".format(subject)

        if any(x.needs_full_update for x in diffs):
            fix_original_video_csv(subject, diffs)
            #update_opf(subject, diffs)
        elif diffs.needs_only_bl_update:
            fix_original_video_csv(subject, diffs)

def fix_original_audio_csv(subject, diffs):
    path = tidy_paths[subject].audio_csv
    new_path = path.replace(".csv", "_bl_tidy.csv")
    basic_levels = audio_csv_to_objects(path)

    diff_deque = deque(diffs)
    edits = []
    current_diff = diff_deque.popleft()

    for basic_level in basic_levels:
        if check_diff_and_bl_match(current_diff, basic_level):
            edit = diff_basic_level_edits(basic_level, current_diff)
            if diff_deque:
                current_diff = diff_deque.popleft()
            else:
                edits.append(basic_level)
                continue
            edits.append(edit)
            continue
        edits.append(basic_level)

    with open(new_path, "wb") as output:
        writer = csv.writer(output)
        for edit in edits:
            writer.writerow(edit.csv_row())


def check_diff_and_bl_match(diff, basic_level):
    if diff.time == basic_level.time and\
        diff.word == basic_level.word and\
        diff.speaker == basic_level.speaker and\
        diff.utt_type == basic_level.utt_type and\
        diff.present == basic_level.present:
        return True
    return False

def diff_basic_level_edits(basic_level, edit):

    if edit.utt_edit:
        basic_level.utt_type = edit.utt_edit
    if edit.present_edit:
        basic_level.present = edit.present_edit
    if edit.speak_edit:
        basic_level.speaker = edit.speak_edit
    if edit.bl_edit:
        basic_level.basic_level = edit.bl_edit

    return basic_level


def audio_csv_to_objects(path):
    with open(path, "rU") as input:
        elements = []
        reader = csv.reader(input)
        for row in reader:
            element = AudBasicLevel(row[0], row[1], row[2],
                                    row[3], row[4], row[5], row[6])
            elements.append(element)
    return elements

def update_cha(subject, diffs):
    print "hello"

def aud_csv_basiclevel_diff(row, problem):
    if problem.bl_edit and (problem.time == row[5])\
        and (problem.word == row[1]):
        return True
    return False

def aud_csv_utt_diff(row, problem):
    if row[2] == problem[3] and row[5] == problem[6]\
            and row[1] == problem[2]:
        return True
    return False


def fix_original_video_csv(subject, diffs):
    path = tidy_paths[subject][0]
    #chunk = video_diffs[subject]
    new_path = path.replace(".csv", "_bl_tidy.csv")
    with open(path, "rU") as input_file:
        with open(new_path, "wb") as output_file:
            reader = csv.reader(input_file)
            reader.next()
            writer = csv.writer(output_file)
            for problem in diffs:
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

def correct_cha_filename(key, file):
    if file.endswith(".cha"):
        if "newclan_merged" in file and key in file:
            return True
        if "final" in file and key in file:
            return True
    return False


def correct_audio_csv_filename(key, file):
    if file.endswith(".csv"):
        if ("check" in file) and ("ready" not in file)\
                and ("audio" in file) and ("bl_tidy" not in file)\
                and (key in file):
            return True
    return False


def correct_video_csv_filename(key, file):
    if file.endswith(".csv"):
        if ("check" in file) and ("ready" not in file) \
                and ("video" in file) and ("bl_tidy" not in file)\
                and (key in file):
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

    if "audio" in bl_edit_file:

        read_audio_csv()
        chunks = chunk_audio_problem_files()
        register_edit_paths()
        tidy_all_audio_changes()

    if "video" in bl_edit_file:
        read_audio_csv()
        chunks = chunk_video_problem_files()
        register_edit_paths()
        tidy_all_video_changes()
