"""
    author: Suhas Vittal
    date:   4 March 2024
"""

from qonstruct.code_builder.surface_code import make_rotated
from qonstruct.code_builder.color_code import make_hexagonal
from qonstruct.code_builder.base import make_check_graph

from qonstruct.io import read_tanner_graph_file

from sys import argv

import matplotlib.pyplot as plt
import networkx as nx

code = argv[1]

if code == 'rsc':
    d = int(argv[2])
    gr = make_rotated(d)
elif code == 'hexcc':
    d = int(argv[2])
    gr = make_hexagonal(d)
else:
    gr = read_tanner_graph_file(code)
cgr = make_check_graph(gr,'x')
color_map = nx.coloring.greedy_color(cgr)

nx.draw(cgr, node_color=color_map)
plt.show()
