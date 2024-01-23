#!/bin/sh

QONSTRUCT_CODES_FOLDER="qonstruct/codes"
QONTRA_CODES_FOLDER="qontra/data/tanner"

declare -a TANNER_GRAPH_FILES=(
    "hy_cc/24_8.txt"
    "hy_sc/3_8/168_16.txt"
    "hy_sc/3_8/360_32.txt"
    "hy_sc/4_5/60_8.txt"
    "hy_sc/4_5/180_20.txt"
)

for file in ${TANNER_GRAPH_FILES[@]}
do
    output_filename=`basename $file`
    output_path=$QONTRA_CODES_FOLDER/$output_filename

    echo "Copying ${file} to ${output_path}."

    cp "$QONSTRUCT_CODES_FOLDER/${file}" $output_path
done
