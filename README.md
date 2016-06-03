# basicleveltidy

This script helps with making changes to audio and video file annotations.

If you need to make changes to entries in the basic level files, those changes need to ripple back to the original annotated
cha and opf files.

This script acts on aggregated basic_level csv files. You make the annotation changes to these long/concatenated csv's, then pass
that file to the basicleveltidy script. It will crawl through the Subject_Files directory tree and find all the files that need to be updated.
This includes the original basic_level file, cha files, and opf files.

## usage

#### create_edit_csv.py

The concatenated csv doesn't have the edit columns in it yet. It's in this form:

id                                | tier  | object    | utterance_type | object_present | speaker | timestamp       | basic_level |
--------------------------------- | ----- | --------- | -------------- | -------------- | ------- | --------------  | ----------- |
"01_10_coderAR_audio_checkSM.csv" | *MAN  | alligator | d              | n              |  FAT    | 4989390_4990400 |   alligator      


The csv that needs to be fed into basicleveltidy needs to have extra columns where you put your edits. By running the
create_edits_csv.py script, it will create a new csv based on the original concatenated one with those extra columns.

extra columns:

object_edit | utt_type_edit | obj_present_edit | speaker_edit | basic_level_edit
----------- | ------------- | ---------------- | ------------ | ----------------|
            |      s        |                  |              |       gator


```
$: python create_edits_csv.py original_aggregate_basic_level.csv
```


#### blt.py

This is the main script that does the Subject_Files directory traversal and file updates.


```
$: python blt.py output_from_create_edits_csv.csv
```

It will create a new updated file, while keeping the original in tact but adding "_untidy" to the original's file name.

If the csv you pass in is for video files, you might get this message after running blt.py:

```
================================================
#                                              #
#  A file: "opf_diffs.csv" has been created.   #
#  This file needs to be passed through a      #
#  datavyu script to update the opf files.     #
#                                              #
================================================
```

This opf_diffs.csv file needs to be fed into a Datavyu script (blt_opf_update.rb). You run the datavyu script like any other, except you 
need to specify the path to the opf_diffs.csv file within the script itself. for [example](https://github.com/SeedlingsBabylab/datavyu_scripts/blob/master/blt_opf_update.rb#L12)
