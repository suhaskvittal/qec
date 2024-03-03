"""
    author: Suhas Vittal
    date:   14 February 2024
"""

import qonstruct.io
import qonstruct.scheduling

from qonstruct.code_builder.surface_code import make_rotated

from qonstruct.parsing.cmd import *
from qonstruct.qes.manager import QesManager

from sys import argv
from collections import deque, defaultdict

## MAIN ##

arg_list = parse(argv)

code_file = try_get_string(arg_list, 'tanner')

if code_file == 'rsc':
    d = try_get_int(arg_list, 'd')
    gr = make_rotated(d)
else:
    gr = qonstruct.io.read_tanner_graph_file(code_file)
    qonstruct.scheduling.compute_syndrome_extraction_schedule(gr)

# Attempt to compute the X and Z distance of the code via BFS.
for s in ['x', 'z']:
    _s = 'x' if s == 'z' else 'z'
    d = 1000
    for qstart in gr.graph['data_qubits']:
        bfsq = deque([qstart])
        visited = set()

        prev = {qstart : None}
        depth = {qstart : 1}
        while len(bfsq) > 0:
            v = bfsq[0]
            bfsq.popleft()

            all_neighbors_visited = True
            for w in gr.neighbors(v):
                if gr.nodes[w]['node_type'] != 'data' and gr.nodes[w]['node_type'] != _s:
                    continue
                if gr.nodes[v]['node_type'] == 'data':
                    if w in visited:
                        continue
                    bfsq.append(w)
                    depth[w] = depth[v] + 1
                    prev[w] = v
                    all_neighbors_visited = False
                else:
                    if w in visited:
                        if w != prev[v]:
                            d = min(depth[v], d)
                    else:
                        bfsq.append(w)
                        depth[w] = depth[v]
                        prev[w] = prev[v]
            if all_neighbors_visited and gr.nodes[v]['node_type'] == 'data':
                # This is a boundary condition.
                pass
            visited.add(v)
    print('%s distance is %d' % (s, d))
