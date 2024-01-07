"""
    author: Suhas Vittal
    date:   2 January 2024
"""

import networkx as nx

from sys import argv

input_file = argv[1]
reader = open(input_file, 'r')

graph = nx.Graph()

reader.readline() # Just the header
line = reader.readline()
while line != '':
    q1, q2, _ = tuple([int(x) for x in line.split(',')])
    graph.add_edge(q1, q2)
    line = reader.readline()
is_planar, _ = nx.check_planarity(graph)
print('is planar:', is_planar)
