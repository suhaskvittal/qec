from sys import argv

output_file = argv[1]
d = int(argv[2])

def st(arr):
    return ','.join([str(x) for x in arr])

def get_patch_info(off: int, d: int):
    data_qubits = list(range(off, off+d*d))
    parity_qubits = []

    cnt = off+d*d  # Number of data qubits.
    bulk_stabilizers = {}
    boundary_stabilizers = {}
    x_stab = set()
    for r in range(d-1):
        for c in range(d-1):
            q1,q2,q3,q4 = r*d+c,r*d+c+1,(r+1)*d+c,(r+1)*d+c+1
            if (r+c) % 2 == 0:
                bulk_stabilizers[cnt] = [off+q1,off+q2,off+q3,off+q4]
                x_stab.add(cnt)
            else:
                bulk_stabilizers[cnt] = [off+q1,off+q3,off+q2,off+q4]
            parity_qubits.append(cnt)
            cnt += 1
    # Now do boundary stabilizers.
    for r in range(0,d-1,2):
        q1,q2 = r*d, (r+1)*d
        q3,q4 = (r+1)*d+d-1, (r+2)*d+d-1
        boundary_stabilizers[cnt] = [None,None,off+q1,off+q2]
        boundary_stabilizers[cnt+1] = [off+q3,off+q4,None,None]
        parity_qubits.extend([cnt,cnt+1])
        cnt += 2
    for c in range(0,d-1,2):
        q1,q2 = (d-1)*d+c,(d-1)*d+c+1
        q3,q4 = c+1,c+2
        boundary_stabilizers[cnt] = [off+q1,off+q2,None,None]
        boundary_stabilizers[cnt+1] = [None,None,off+q3,off+q4]
        x_stab.add(cnt)
        x_stab.add(cnt+1)
        parity_qubits.extend([cnt,cnt+1])
        cnt += 2
    x_obs = [ off+r*d for r in range(d) ]
    z_obs = [ off+(d-1)*d+c for c in range(d) ]
    return data_qubits,parity_qubits,bulk_stabilizers,boundary_stabilizers,x_stab,x_obs,z_obs

Q = get_patch_info(0,d)
dq,pq,bus,bos,xs,xo,zo = Q

writer = open(output_file, 'w')

# Perform syndrome extraction on each qubit.
# Initialize qubits.
writer.write('@annotation no_error\nreset %s;\n' % st(dq))
writer.write('@annotation no_error\nh %s;\n' % st(dq))

# Do one round of syndrome extraction with no error.
mctr_map = {}
mctr = 0
ectr = 0
for r in range(d+2):
    prev_mctr_map = mctr_map.copy()
    if r == 0 or r == d+1:
        writer.write('@annotation no_error\nreset %s;\n' % st(pq))
    else:
        writer.write('@annotation timing_error\nreset %s;\n' % st(pq))
    if r == 0 or r == d+1:
        writer.write('@annotation no_error\n')
    writer.write('h %s;\n' % st(xs))
    for j in range(4):
        cxo = []
        for x in pq:
            if x in bus:
                arr = bus[x]
            else:
                arr = bos[x]
            if arr[j] is None:
                continue
            if x in xs:
                cxo.extend([x,arr[j]])
            else:
                cxo.extend([arr[j],x])
        if r == 0 or r == d+1:
            writer.write('@annotation no_error\n')
        writer.write('cx %s;\n' % st(cxo))
    if r == 0 or r == d+1:
        writer.write('@annotation no_error\n')
    writer.write('h %s;\n' % st(xs))
    if r == 0 or r == d+1:
        writer.write('@annotation no_error\n')
    writer.write('measure %s;\n' % st(pq))
    for q in pq:
        mctr_map[q] = mctr
        mctr += 1
    for q in pq:
        if q not in xs:
            continue
        if q not in prev_mctr_map:
            continue
        t1,t2 = mctr_map[q], prev_mctr_map[q]
        writer.write('event %d,%d,%d;\n' % (ectr, t1, t2))
        ectr += 1
writer.write('@annotation no_error\nh %s;\n' % st(dq))
writer.write('@annotation no_error\nmeasure %s;\n' % st(dq))
for x in dq:
    mctr_map[x] = mctr
    mctr += 1
m = [ mctr_map[x] for x in xo ]
writer.write('obs %d,%s;\n' % (0, st(m)))
