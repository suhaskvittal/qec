"""
    author: Suhas Vittal
    date: 20 April 2024
"""

import qonstruct.io
from qonstruct.code_builder.color_code\
        import make_semihyperbolic, color_tanner_graph, color_code_from_faces

from sys import argv
import os

code = argv[1]
r = int(argv[2])
output_file = argv[3]

#gr = qonstruct.io.read_tanner_graph_file(code)
#color_tanner_graph(gr)
gr = color_code_from_faces(code)
n = len(gr.graph['data_qubits'])
k = n - len(gr.graph['checks']['all'])
print(f'Seed Code parameters: n={n}, k={k}')

ngr = make_semihyperbolic(gr, r)

n = len(ngr.graph['data_qubits'])
k = n - len(ngr.graph['checks']['all'])
print(f'Final Code parameters: n={n}, k={k}')

qonstruct.io.write_tanner_graph_file(ngr, output_file)
