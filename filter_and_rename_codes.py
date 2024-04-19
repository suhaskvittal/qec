"""
    author: Suhas Vittal
    date:   7 March 2024
"""

import stim

import qonstruct.io

import os
from sys import argv

def add_operator(circuit, arr, is_x):
    targets = []
    for (i, q) in enumerate(arr):
        targets.append(stim.target_x(q) if is_x else stim.target_z(q))
        if i < len(arr)-1:
            targets.append(stim.target_combiner())
    circuit.append("MPP", targets)

def measure_checks(circuit, gr):
    for ch in gr.graph['checks']['all']:
        add_operator(circuit, list(gr.neighbors(ch)), gr.nodes[ch]['node_type'] == 'x')

def measure_logical_qubits(circuit, gr, is_x):
    typ = 'x' if is_x else 'z'
    for (i, obs) in enumerate(gr.graph['obs_list'][typ]):
        add_operator(circuit, obs, is_x)
        circuit.append('OBSERVABLE_INCLUDE', [stim.target_rec(-1)], i)

def compute_distance(gr, is_x):
    circuit = stim.Circuit()
    measure_logical_qubits(circuit, gr, is_x)
    measure_checks(circuit, gr)
    # Inject error on the data qubits.
    if is_x:
        circuit.append('Z_ERROR', list(gr.graph['data_qubits']), 0.1)
    else:
        circuit.append('X_ERROR', list(gr.graph['data_qubits']), 0.1)
    # Measure checks and then the logical qubits.
    measure_checks(circuit, gr)
    n_checks = len(gr.graph['checks']['all'])
    t = 'x' if is_x else 'z'
    for (i, ch) in enumerate(gr.graph['checks']['all']):
        if gr.nodes[ch]['node_type'] == t:
            circuit.append('DETECTOR', [stim.target_rec(-(n_checks-i)), stim.target_rec(-(2*n_checks-i))])
    measure_logical_qubits(circuit, gr, is_x)
    errors = circuit.search_for_undetectable_logical_errors(
                dont_explore_edges_increasing_symptom_degree=False,
                dont_explore_detection_event_sets_with_size_above=3,
                dont_explore_edges_with_degree_above=3)
    return len(errors)

code_folder = argv[1]
dmin = int(argv[2])
max_code_size = int(argv[3])

force_recompute = '-recompute' in argv
dist_is_eq = '-dist-eq' in argv

files = []

_files = [f for f in os.listdir(code_folder)]
for f in _files:
    fbase = f.split('.')[0]
    params = [int(x) for x in fbase.split('_')]
    n, k = params[0], params[1]
    if n > max_code_size:
        print(f'Ignored {f}')
        continue
    if len(params) > 2 and not force_recompute:
        # No point in renaming this file.
        dx, dz = params[2], params[3]
        files.append((f, n, k, dx, dz))
        continue
    gr = qonstruct.io.read_tanner_graph_file(os.path.join(code_folder, f))
    print(f'code = {f}')
    try:
        dz = compute_distance(gr, True)
        if dist_is_eq:
            dx = dz
        else:
            dx = compute_distance(gr, False)
    except ValueError as e:
        print(f'encountered {e}: code distance for {f} could not be computed')
        continue
    print(f'\tdx = {dx}, dz = {dz}')
    files.append((f, n, k, dx, dz))

# Now we will go back through and (1) remove all files with dx or dz less than dmin,
# and (2) remove all files with worse distance than a code with fewer qubits.
print('----------------------')
files.sort(key=lambda x: x[1]) 
dzmin, dxmin = dmin, dmin
for (f, n, k, dx, dz) in files:
    if dz < dzmin and dx < dxmin:
        os.remove(os.path.join(code_folder, f))
        print(f'Deleted {f}')
    else:
        dzmin, dxmin = max(dzmin, dz), max(dxmin, dx)
        os.rename(os.path.join(code_folder, f), f'{code_folder}/{n}_{k}_{dx}_{dz}.txt')
        print(f'Renamed {f} to {n}_{k}_{dx}_{dz}')
    
