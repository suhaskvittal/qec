#!/bin/sh

QONSTRUCT_CODES_FOLDER="qonstruct/codes"
QONTRA_CODES_FOLDER="qontra/data/tanner"

declare -a CODE_FOLDERS=(
# SURFACE CODES
    "hysc/3_8"
    "hysc/4_5"
    "hysc/4_6"
    "hysc/5_5"
    "hysc/5_6"
    "hysc/6_6"
# COLOR CODES
    "hycc/3_8"
    "hycc/3_10"
    "hycc/4_6"
    "hycc/4_8"
    "hycc/4_10"
    "hycc/5_6"
)

for folder in ${CODE_FOLDERS[@]}
do
    parent=$(dirname $folder)
    echo "Copying ${folder} to ${QONTRA_CODES_FOLDER}/${parent}."
    cp -r "$QONSTRUCT_CODES_FOLDER/${folder}" $QONTRA_CODES_FOLDER/$parent
done
