#!/bin/sh

conda deactivate
conda activate qon_py3.10
for d in 3 5 7
do
    python qontra_make_memory.py rsc qontra/data/protean/rsc/z_d${d}.qes --d $d --rounds $d
    python qontra_make_memory.py rsc qontra/data/protean/rsc/x_d${d}.qes --d $d --rounds $d -x
    python qontra_make_memory.py hexcc qontra/data/protean/hexcc/z_d${d}.qes --d $d --rounds $d -use-flags
    python qontra_make_memory.py hexcc qontra/data/protean/hexcc/x_d${d}.qes --d $d --rounds $d -x -use-flags
done
conda deactivate
