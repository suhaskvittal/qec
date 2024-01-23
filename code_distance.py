"""
    author: Suhas Vittal
    date:   21 January 2024
"""

import qonstruct.utils
import qonstruct.io
import qonstruct.code_builder.color_code

from sys import argv

code_file = argv[1]

gr = qonstruct.io.read_tanner_graph_file(code_file)
#dx = qonstruct.utils.compute_code_distance(gr, 'x')
dz = qonstruct.utils.compute_code_distance(gr, 'z')
dx = 0
dz = 0

print('X Distance = %d, Z Distance = %d' % (dx, dz))

