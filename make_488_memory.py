"""
    author: Suhas Vittal
    date:   27 September 2024
"""

from collections import defaultdict

from sys import argv

d = int(argv[1])
mx = '-mx' in argv

ROUNDS = d

'''
    Initializing the data structures
    for the 4.8.8 code.
'''
nbase = 0
qubits_per_row = 2
locs = {}

nmax = (d*d-1)//2 + d
for j in range(0, d, 2):
    y = j//2
    for i in range(0, qubits_per_row, 2):
        x = i//2
        if d % 4 == 1 and j == d-1 and i == 0:
            locs[(x,y)] = ('r', [nmax, nbase, nmax, nbase+qubits_per_row])
            nbase += 1
        else:
            locs[(x,y)] = ('r', [nbase, nbase+1, nbase+qubits_per_row, nbase+qubits_per_row+1])
            nbase += 2
    nbase += qubits_per_row
    qubits_per_row += 2
# Now, given the red checks, connect qubits
# between these checks with green and blue checks.
nmax = (d*d-1)//2 + d
'''
    Organizing red/green/blue checks.
'''
checks = { 'r': [], 'g': [], 'b': [] }
# Compute support counts for each qubit (number of incident checks). Need this to 
# handle edge case G/B weight-4 checks that only need one flag.
suppcnt = defaultdict(int)
for (_,(_, arr)) in locs.items():
    if all(x < nmax for x in arr):
        checks['r'].append(arr)
        for x in arr:
            suppcnt[x] += 1
for ((x0,y0), _) in locs.items():
    if y0 % 2 == 0:
        posdel = [(-1,-1), (-1,0), (0,0), (0,1)]
    else:
        posdel = [(0,-1), (0,0), (1,0), (1,1)]
    cnt = sum( 1 if (x0+xd,y0+yd) in locs else 0 for (xd,yd) in posdel )
    if cnt < 2:
        continue
    all_qubits = [ None for _ in range(8) ]
    for (i, (xd,yd)) in enumerate(posdel):
        x,y = x0+xd, y0+yd
        if (x,y) not in locs:
            continue
        _, qarr = locs[(x,y)]
        if i == 0:
            all_qubits[0], all_qubits[1] = qarr[2], qarr[3]
        elif i == 1:
            all_qubits[6], all_qubits[7] = qarr[3], qarr[1]
        elif i == 2:
            all_qubits[2], all_qubits[3] = qarr[0], qarr[2]
        else:
            all_qubits[4], all_qubits[5] = qarr[1], qarr[0]
    all_qubits = [ None if x is None or x >= nmax else x for x in all_qubits ]
    for x in all_qubits:
        if x is None:
            continue
        suppcnt[x] += 1
    color = 'g' if y0 % 2 == 0 else 'b'
    if len(all_qubits) <= 2 or len(all_qubits) % 2 == 1:
        continue
    checks[color].append(all_qubits)
if '-write-tanner' in argv:
    writer = open(f'488/Td{d}.txt', 'w')
    ctr = 0
    for c in 'rgb':
        for qarr in checks[c]:
            writer.write(f'X{ctr},%s\n' % ','.join(str(x) for x in qarr if x is not None))
            writer.write(f'Z{ctr},%s\n' % ','.join(str(x) for x in qarr if x is not None))
            ctr += 1
    writer.write('OX0,%s\n' % ','.join(str(x) for x in range(nmax)))
    writer.write('OZ0,%s\n' % ','.join(str(x) for x in range(nmax)))
'''
    Setting up flag qubits for all checks (green/blue first).
'''
n = nmax
check_to_color_map = {}
check_to_data_map = {}
check_to_flag_map = defaultdict(list)
data_to_flag_map = defaultdict(dict)
flag_to_check_map = defaultdict(list)
flag_to_data_map = {}
edge_to_flag_map = {}
# Do green and blue checks first.
for c in 'gb':
    for qarr in checks[c]:
        check = n
        check_to_color_map[check] = c
        check_to_data_map[check] = qarr
        n += 1
        for i in range(1, 8, 2):
            q1, q2 = qarr[i], qarr[(i+1)%8]
            if q1 is None and q2 is None:
                continue
            if (q1,q2) in edge_to_flag_map:
                f = edge_to_flag_map[(q1,q2)]
            else:
                f = n
                n += 1
                edge_to_flag_map[(q1,q2)] = f
                edge_to_flag_map[(q2,q1)] = f
                flag_to_data_map[f] = [q1,q2]
            for q in [q1,q2]:
                data_to_flag_map[q][check] = f
            flag_to_check_map[f].append(check)
            check_to_flag_map[check].append(f)
# Now handle red checks.
for qarr in checks['r']:
    # Red checks have one flag and check.
    check = n
    flag = n+1
    n += 2
    # The flag should point to q2,q4
    _,q2,_,q4 = qarr[:]
    # Update data structures
    check_to_color_map[check] = 'r'
    check_to_data_map[check] = qarr
    check_to_flag_map[check].append(flag)
    flag_to_check_map[flag].append(check)
    flag_to_data_map[flag] = [q2,q4]
    for q in [q2,q4]:
        data_to_flag_map[q][check] = flag
'''
    Output an nx.Graph if the user requests it.
'''
if '-plot-arch' in argv:
    import networkx as nx
    G = nx.Graph()
    cnm = {'r': 'red', 'g': 'green', 'b': 'blue'}
    for i in range(n):
        G.add_node(i, color='black')
    # Add connections.
    for (ch, color) in check_to_color_map.items():
        G.nodes[ch]['color'] = cnm[color]
        for q in check_to_data_map[ch]:
            if q is None:
                continue
            if ch in data_to_flag_map[q]:
                f = data_to_flag_map[q][ch]
                G.add_edge(ch, f)
                G.add_edge(f, q)
            else:
                G.add_edge(ch, q)
    for f in flag_to_check_map:
        G.nodes[f]['color'] = 'pink'
    # Now we need to draw the graph.
    import matplotlib.pyplot as plt
    nx.draw_kamada_kawai(G,\
            node_color=[ G.nodes[i]['color'] for i in G.nodes() ],\
            node_size=[ 10 if G.nodes[i]['color'] == 'black' else 100 for i in G.nodes() ],\
            ax=plt.subplot())
    plt.savefig(f'488/d{d}.pdf', bbox_inches='tight')
print(f'N = {n}, n = {nmax}, number of ancilla = {n-nmax}')
'''
    Make syndrome extraction circuit
'''
writer = open(f'488/d{d}.qes', 'w')

def write(name: str, ops: list[int]):
    writer.write('%s %s;\n' % (name, ','.join(str(x) for x in ops)) )

def write_cx(ops: list[int], m: str):
    if m == 'z':
        ops = ops[::-1]
    write('cx', ops)

writer.write('''
#############################################
##              PROLOGUE                   ##
#############################################
''')
# Reset all qubits.
write('reset', list(range(n)))

writer.write('''
#############################################
##                BODY                     ##
#############################################
''')
mctr = 0
mctr_map = {}
ectr = 0
c2i = {'r': 0, 'g': 1, 'b': 2}

all_anc = []
all_anc.extend([ch for ch in check_to_data_map])
all_anc.extend([f for f in flag_to_check_map])

n_events = len(all_anc)
for r in range(ROUNDS):
    writer.write(f'###### ROUND {r} ######\n')
    prev_mctr_map = mctr_map.copy()
    for m in 'xz':
        writer.write('@annotation timing_error\n')
        write('reset', all_anc)
        # Initialize ancilla.
        if m == 'x':
            # Parity need to be in |+>
            write('h', [ ch for ch in check_to_data_map ])
        else:
            # Flags need to be in |+>
            write('h', [ f for f in flag_to_check_map ])
        cx_operands = [[] for _ in range(9)]
        # Handle green and blue checks first.
        dforder = [ 2, 5, 4, 7 ]
        gbflags = [set(), set()]
        for (ch,col) in check_to_color_map.items():
            if col == 'r':
                continue
            qarr = check_to_data_map[ch]
            for i in range(4):
                q = qarr[ dforder[i] ]
                if q is None:
                    continue
                f = data_to_flag_map[q][ch]
                cx_operands[i].extend( [ch,f] )
                cx_operands[i+5].extend( [ch,f] )
                if i <= 1:
                    gbflags[0].add(f)
                else:
                    gbflags[1].add(f)
        # Now do the CNOTs between all GB flags. 
        for i in range(2):
            base = 3 if i == 0 else 5
            for f in gbflags[i]:
                for j in range(2):
                    d = flag_to_data_map[f][j]
                    if d is None:
                        continue
                    cx_operands[base+j].extend([f,d])
        # Now do R checks.
        for (ch,col) in check_to_color_map.items():
            if col != 'r':
                continue
            qarr = check_to_data_map[ch]
            cx_operands[0].extend([ch,qarr[0]])
            f = check_to_flag_map[ch][0]
            cx_operands[1].extend([ch,f])
            cx_operands[2].extend([ch,qarr[2],f,qarr[1]])
            cx_operands[4].extend([f,qarr[3]])
            cx_operands[5].extend([ch,f])
        for cxo in cx_operands:
            write_cx(cxo, m)
        # Measure all checks and flags.
        if m == 'x':
            # Parity need to be in |+>
            write('h', [ ch for ch in check_to_data_map ])
        else:
            # Flags need to be in |+>
            write('h', [ f for f in flag_to_check_map ])
        measure_ops = []
        for ch in check_to_color_map:
            measure_ops.append(ch)
            if (m=='x' and mx) or (m=='z' and not mx):
                mctr_map[ch] = mctr
            mctr += 1
        for f in flag_to_check_map:
            measure_ops.append(f)
            if (m=='x' and not mx) or (m=='z' and mx):
                mctr_map[f] = mctr
            mctr += 1
        write('measure', measure_ops)
    # Make events.
    for (ch,col) in check_to_color_map.items():
        base = (ectr%n_events) + (0 if ROUNDS==1 else n_events)
        writer.write(f'@property color {c2i[col]}\n@property base {base}\n')
        if ch not in prev_mctr_map:
            m = mctr_map[ch]
            writer.write(f'event {ectr},{m};\n')
        else:
            m1,m2 = mctr_map[ch], prev_mctr_map[ch]
            writer.write(f'event {ectr},{m1},{m2};\n')
        ectr += 1
    for f in flag_to_check_map:
        m = mctr_map[f]
        writer.write(f'@annotation flag\nevent {ectr},{m};\n')
        ectr += 1
writer.write('''
#############################################
##             EPILOGUE                    ##
#############################################
''')
data_qubits = list(range(nmax))
for i in range(nmax):
    mctr_map[i] = mctr
    mctr += 1
if mx:
    write('h', data_qubits)
write('measure', data_qubits)
if ROUNDS > 1:
    for (ch,col) in check_to_color_map.items():
        base = (ectr%n_events) + n_events
        writer.write(f'@property color {c2i[col]}\n@property base {base}\n')
        marr = [ mctr_map[x] for x in check_to_data_map[ch] if x is not None ]
        marr.append( mctr_map[ch] )
        writer.write(f'event {ectr},%s;\n' % ','.join(str(x) for x in marr))
        ectr += 1
marr = [ mctr_map[i] for i in data_qubits ]
writer.write('obs 0,%s;\n' % ','.join(str(x) for x in marr))

print('Checks:')
for (i,(ch,col)) in enumerate(check_to_color_map.items()):
    print(f'{i}:\t({col}) ch:', [x for x in check_to_data_map[ch] if x is not None])
