"""
    author: Suhas Vittal
    date:   2 January 2024
"""

from qontra_params import *

import qonstruct.io
import qonstruct.hgp
import qonstruct.ldpc
import qonstruct.qecolor

import networkx as nx

### COLOR CODES ###

for d in [3, 5, 7]:
    gr = qonstruct.qecolor.make_hexagonal_tanner_graph(d)
    qonstruct.io.write_tanner_graph_file(gr, '%s/hex_cc_d%d.txt' % (QONTRA_TANNER_WRITE_DIRECTORY, d))

### HGP CODES ###

r, c = 3, 4
for s in [3, 4, 5]:
    seed_code = qonstruct.ldpc.make_regular_tanner_graph(r, c, s)
    print('HGP(%d, %d, %d) has girth: %d' % (r, c, s, nx.girth(seed_code)))
    gr = qonstruct.hgp.make_hgp_quantum_tanner_graph(seed_code)
    qonstruct.io.write_tanner_graph_file(gr, '%s/hgp_%d_%d_%d.txt' % (QONTRA_TANNER_WRITE_DIRECTORY, r, c, s))
