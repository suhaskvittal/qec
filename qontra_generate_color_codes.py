from qontra_params import *

from qonstruct.parsing.cmd import *
from qonstruct.prebuilt import asm_hexagonal_color_code

from sys import argv

inputs = parse(argv)

use_flags = ('f' in inputs)
both_at_once = ('bac' in inputs)

for d in [3, 5, 7, 9, 11, 13, 15, 17]:
    for memory in ['x', 'z']:
        filename = '%s/memory_%s_d%d.asm' % (QONTRA_ASM_WRITE_DIRECTORY, memory, d)
        asm_hexagonal_color_code(filename, d, d, memory=memory, use_flags=use_flags, both_at_once=both_at_once)

