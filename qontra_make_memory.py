"""
    author: Suhas Vittal
    date:   21 January 2024
"""

import qonstruct.io
import qonstruct.scheduling

from qonstruct.code_builder.surface_code import make_rotated
from qonstruct.code_builder.color_code import make_hexagonal, make_hycc_d4

from qonstruct.parsing.cmd import *
from qonstruct.qes.manager import QesManager

from sys import argv

arg_list = parse(argv[3:])

code_file = argv[1]
output_file = argv[2]
rounds = try_get_int(arg_list, 'rounds')
is_memory_x = 'x' in arg_list

if code_file == 'rsc':
    d = try_get_int(arg_list, 'd')
    gr = make_rotated(d)
elif code_file == 'hexcc':
    d = try_get_int(arg_list, 'd')
    gr = make_hexagonal(d)
elif code_file == 'hycc':
    gr = make_hycc_d4()
else:
    gr = qonstruct.io.read_tanner_graph_file(code_file)
    qonstruct.scheduling.compute_syndrome_extraction_schedule(gr)
print('Code has %d qubits and %d checks' % (len(gr.graph['data_qubits']), len(gr.graph['checks']['all'])))

mgr = QesManager(gr)
mgr.memory = 'x' if is_memory_x else 'z'

if 'use-flags' in arg_list:
    # Naive flag setup:
    for ch in gr.graph['checks']['all']:
        support = gr.nodes[ch]['schedule_order']
        support = [x for x in support if x is not None]
        n_qubits = len(support) if len(support) % 2 == 0 else len(support)-1
        for i in range(0, n_qubits, 2):
            q1, q2 = support[i], support[i+1]
            mgr.add_flags_to(q1, q2, ch)
mgr.fopen(output_file)
mgr.write_memory_experiment(rounds)
mgr.fclose()
