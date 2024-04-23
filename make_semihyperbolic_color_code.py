"""
    author: Suhas Vittal
    date: 20 April 2024
"""

import qonstruct.io
from qonstruct.code_builder.color_code import make_semihyperbolic, color_tanner_graph

from sys import argv
import os

code = argv[1]

gr = qonstruct.io.read_tanner_graph_file(code)
color_tanner_graph(gr)
ngr = make_semihyperbolic(gr, '7_1_3')

n = len(ngr.graph['data_qubits'])
k = n - len(ngr.graph['checks']['all'])
print(f'Code parameters: n={n}, k={k}')

id = os.path.basename(code).split('.')[0]
output_folder = f'codes/sehycc_{id}'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
qonstruct.io.write_tanner_graph_file(ngr, f'{output_folder}/{n}_{k}.txt')
