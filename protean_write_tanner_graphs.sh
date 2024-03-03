#!/bin/sh

QONSTRUCT_CODES_FOLDER="qonstruct/codes"
QONTRA_CODES_FOLDER="qontra/data/tanner/hysc"

declare -a TANNER_GRAPH_FILES=(
    "hysc/3_8/48_6_4.txt"
    "hysc/3_8/168_16_6.txt"
    "hysc/4_5/60_8_6.txt"
    "hysc/4_5/160_18_6.txt"
    "hysc/5_5/30_8_3.txt"
    "hysc/5_5/80_18_5.txt"
    "hysc/5_6/60_18_4.txt"
    "hysc/5_6/120_34_5.txt"
    "hysc/6_6/42_16_6.txt"
    "hysc/6_6/120_42_4.txt"
)

for file in ${TANNER_GRAPH_FILES[@]}
do
    output_filename=`basename $file`
    output_path=$QONTRA_CODES_FOLDER/$output_filename

    echo "Copying ${file} to ${output_path}."

    cp "$QONSTRUCT_CODES_FOLDER/${file}" $output_path
done
