"""
    author: Suhas Vittal
    date:   19 February 2024
"""

from qonstruct.code_builder.surface_code import make_rotated
from qonstruct.code_builder.color_code import make_hexagonal

from qonstruct.io import write_tanner_graph_file

from sys import argv

code = argv[1]
d = int(argv[2])
output_file = argv[3]

if code == 'rsc':
    gr = make_rotated(d)
elif code == 'hexcc':
    gr = make_hexagonal(d)
write_tanner_graph_file(gr, output_file)
