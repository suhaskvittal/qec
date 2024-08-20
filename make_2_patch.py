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

Q1 = get_patch_info(0,d)
Q2 = get_patch_info(2*d*d-1,d)

writer = open(output_file, 'w')

# Perform syndrome extraction on each qubit.
# Initialize qubits.
all_data = []
all_parity = []
all_xs = []
for Q in [Q1,Q2]:
    dq,pq,bs,bos,xs,xo,zo = Q
    all_data.extend(dq)
    all_parity.extend(pq)
    all_xs.extend(list(xs))
writer.write('@annotation no_error\nreset %s;\n' % st(all_data))
writer.write('@annotation no_error\nh %s;\n' % st(all_data))

# Do one round of syndrome extraction with no error.
mctr_map = {}
mctr = 0
for (i,Q) in enumerate([Q1,Q2]):
    dq,pq,bus,bos,xs,xo,zo = Q

    writer.write('@annotation no_error\nreset %s;\n' % st(pq))
    writer.write('@annotation no_error\nh %s;\n' % st(xs))
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
        writer.write('@annotation no_error\ncx %s;\n' % st(cxo))
    writer.write('@annotation no_error\nh %s;\n' % st(xs))
    writer.write('@annotation no_error\nmeasure %s;\n' % st(pq))
    for q in pq:
        mctr_map[q] = mctr
        mctr += 1
# Now perform the merge operation.
extra_data = [4*d*d-1 + x for x in range(d)]
extra_pq = []
extra_xs = set()
# Compute merge boundary stabilizers.
merge_bos = {}
for (i,Q) in enumerate([Q2,Q1]):
    _,_,_,bos,xs,_,_ = Q
    # Merge Z stabilizers.
    off = (1-i)*(2*d*d-1) + d*d + (d-1)*(d-1)
    for j in range(0,d-1,2):
        s = off+j+i
        arr = bos[s]
        jj = 0
        for ii in range(len(arr)):
            if arr[ii] is None:
                arr[ii] = extra_data[i+j+jj]
                jj += 1
        merge_bos[s] = arr
# Make new X stabilizers.
#   Q1 | Q2
cnt = 4*d*d-1 + d
for i in range(d-1):
    if i % 2 == 0:
        q1,q2 = i*d+(d-1),(i+1)*d+(d-1)
    else:
        off = 2*d*d-1
        q1,q2 = off+i*d, off+(i+1)*d
    q3,q4 = extra_data[i], extra_data[i+1]
    if i % 2 == 0:
        arr = [q1,q3,q2,q4]
    else:
        arr = [q3,q1,q4,q2]
    merge_bos[cnt] = arr
    all_parity.append(cnt)
    extra_pq.append(cnt)
    extra_xs.add(cnt)
    all_xs.append(cnt)
    cnt += 1
writer.write('reset %s;\n' % st(extra_data))
ectr = 0
for r in range(d+1): # Last round is noiseless
    prev_mctr_map = mctr_map.copy()

    if r == d:
        writer.write('@annotation no_error\n')
    writer.write('reset %s;\n' % st(all_parity))
    if r == d:
        writer.write('@annotation no_error\nh %s;\n' % st(all_xs))
    else:
        writer.write('@annotation timing_error\nh %s;\n' % st(all_xs))
    for i in range(4):
        cxo = []
        for Q in [Q1,Q2]:
            _,pq,bus,bos,xs,_,_ = Q
            for x in pq:
                if x in bus:
                    arr = bus[x]
                elif x in bos and x in merge_bos:
                    arr = merge_bos[x]
                else:
                    arr = bos[x]
                if arr[i] is None:
                    continue
                if x in xs:
                    cxo.extend([x,arr[i]])
                else:
                    cxo.extend([arr[i],x])
        for x in extra_pq:
            arr = merge_bos[x]
            if arr[i] is None:
                continue
            if x in extra_xs:
                cxo.extend([x,arr[i]])
            else:
                cxo.extend([arr[i],x])
        if r == d:
            writer.write('@annotation no_error\n')
        writer.write('cx %s;\n' % st(cxo))
    # Measure all checks.
    if r == d:
        writer.write('@annotation no_error\n')
    writer.write('h %s;\n' % st(all_xs))
    if r == d:
        writer.write('@annotation no_error\n')
    writer.write('measure %s;\n' % st(all_parity))
    for x in all_parity:
        mctr_map[x] = mctr
        mctr += 1
    for x in all_parity:
        if x not in prev_mctr_map:
            continue
        t1,t2 = mctr_map[x], prev_mctr_map[x]
        writer.write('event %d,%d,%d;\n' % (ectr,t1,t2))
        ectr += 1
# Do one round of syndrome extraction with no error.
"""
prev_mctr_map = mctr_map.copy()
for (i,Q) in enumerate([Q1,Q2]):
    dq,pq,bus,bos,xs,xo,zo = Q

    writer.write('@annotation no_error\nreset %s;\n' % st(pq))
    writer.write('@annotation no_error\nh %s;\n' % st(xs))
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
        writer.write('@annotation no_error\ncx %s;\n' % st(cxo))
    writer.write('@annotation no_error\nh %s;\n' % st(xs))
    writer.write('@annotation no_error\nmeasure %s;\n' % st(pq))
    for q in pq:
        mctr_map[q] = mctr
        mctr += 1
    for q in pq:
        t1,t2 = mctr_map[q], prev_mctr_map[q]
        writer.write('event %d,%d,%d;\n' % (ectr,t1,t2))
        ectr += 1
"""
writer.write('@annotation no_error\nh %s;\n' % st(all_data))
writer.write('@annotation no_error\nmeasure %s;\n' % st(all_data))
for x in all_data:
    mctr_map[x] = mctr
    mctr += 1
for (i,Q) in enumerate([Q1,Q2]):
    _,_,_,_,_,x_obs,z_obs = Q
    m = [ mctr_map[x] for x in x_obs ]
    writer.write('obs %d,%s;\n' % (i, st(m)))
"""
all_obs = []
for (_,Q) in enumerate([Q1,Q2]):
    _,_,_,_,_,_,z_obs = Q
    m = [ mctr_map[x] for x in z_obs ]
    all_obs.extend(m)
writer.write('obs 0,%s;\n' % st(all_obs))
"""
