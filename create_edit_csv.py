import csv
import sys

bl_file = ""
bl_edit_file = ""


if __name__ == "__main__":
    bl_file = sys.argv[1]

    bl_edit_file = bl_file.replace(".csv", "_edits_final.csv")
    print bl_file
    print bl_edit_file
    with open(bl_file, "rU") as input:
        reader = csv.reader(input)
        header = reader.next()
        with open(bl_edit_file, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(header+["object_edit","utt_type_edit",
                                    "obj_present_edit","speaker_edit", "basic_level_edit"])
            for row in reader:
                writer.writerow(row + ["", "", "", "", ""])