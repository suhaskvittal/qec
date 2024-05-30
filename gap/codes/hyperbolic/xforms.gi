#
# Author:   Suhas Vittal
# date:     19 January 2024 
#
# Code for transformations.
#

Read("gap/utils/qec.gi");

VerifyComm :=
    function(faces)
        local f1,f2,i,j;
        # Check if any faces anticommute.
        for i in [1..Length(faces)] do
            f1 := faces[i];
            for j in [i+1..Length(faces)] do
                f2 := faces[j];
                if not AreCommuting(f1, f2) then
                    Print("Faces ", i, " and ", j, " anticommute\n");
                fi;
            od;
        od;
    end;

HiggottSemiHyperbolic := 
    function(n_data, L, all_elements, r_faces, g_faces, b_faces, a_edges, b_edges, c_edges)
        local faces,
                bv,
                i,j,k,ii,
                x,y,f,e,
                _q,q,qx,qy,q1,q2,q3,q4,q5,q6,
                nf,
                all_faces,
                r,c,m,ele,
                edge_lists;

        faces := [];
        # Create base vector for ease of computation
        bv := [];
        for i in [1..(L^2*n_data)] do
            Add(bv, Zero(GF(2)));
        od;
        # Replace each face in the current tiling with a new face.
        all_faces := [r_faces, g_faces, b_faces];
        for k in [1..3] do
            for f in all_faces[k] do
                nf := ShallowCopy(bv);
                for x in f do
                    q := Position(all_elements, x);
                    q := (q-1)*L^2 + 1;
                    if k = 1 then
                        nf[q] := One(GF(2));
                    elif k = 2 then
                        nf[q+(L-1)^2] := One(GF(2));
                    else
                        nf[q+L^2-1] := One(GF(2));
                    fi;
                od;
                Add(faces, nf);
            od;
        od;
        # Create bulk stabilizers for each original element.
        for _q in [1..n_data] do
            q := (_q-1)*L^2 + 1;
            for r in [2..L-1] do
                for ii in [1..(r-1)] do
                    i := 2*ii-1;
                    q1 := q + (r-1)^2 + (i-1);
                    q2 := q1+1; q3 := q1+2;
                    q4 := q + r^2 + i;
                    q5 := q4+1; q6 := q4+2;
                    nf := ShallowCopy(bv);
                    for j in [q1,q2,q3,q4,q5,q6] do
                        nf[j] := One(GF(2));
                    od;
                    Add(faces, nf);
                od;
            od;
        od;
        # Create boundary stabilizers for each edge.
        edge_lists := [ a_edges, b_edges, c_edges ];
        for k in [1..3] do
            for e in edge_lists[k] do
                ele := AsList(e);
                x := ele[1]; y := ele[2];
                qx := Position(all_elements, x); qy := Position(all_elements, y);
                qx := (qx-1)*L^2 + 1;
                qy := (qy-1)*L^2 + 1;
                if k = 1 then
                    for r in [1..(L-1)] do
                        q1 := qx + (r-1)^2;
                        q2 := qx + r^2;
                        q3 := q2+1;
                        q4 := qy + (r-1)^2;
                        q5 := qy + r^2;
                        q6 := q5+1;
                        nf := ShallowCopy(bv);
                        for i in [q1,q2,q3,q4,q5,q6] do
                            nf[i] := One(GF(2));
                        od;
                        Add(faces, nf);
                    od;
                elif k = 2 then
                    for r in [1..(L-1)] do
                        q1 := qx + r^2-1;
                        q2 := qx + (r+1)^2-1;
                        q3 := q2-1;
                        q4 := qy + r^2-1;
                        q5 := qy + (r+1)^2-1;
                        q6 := q5-1;
                        nf := ShallowCopy(bv);
                        for i in [q1,q2,q3,q4,q5,q6] do
                            nf[i] := One(GF(2));
                        od;
                        Add(faces, nf);
                    od;
                else
                    m := 2*L-1;
                    for c in [1..(m-1)/2] do
                        q1 := qx + (L-1)^2 + 2*(c-1);
                        q2 := q1+1; q3 := q1+2;
                        q4 := qy + (L-1)^2 + 2*(c-1);
                        q5 := q4+1; q6 := q4+2;
                        nf := ShallowCopy(bv);
                        for i in [q1,q2,q3,q4,q5,q6] do
                            nf[i] := One(GF(2));
                        od;
                        Add(faces, nf);
                    od;
                fi;
            od;
        od;
        VerifyComm(faces);
        return faces;
    end;

SteaneSemiHyperbolic :=
    function(n_data, all_elements, r_faces, g_faces, b_faces)
        local faces,
                bv,
                i,j,k,
                f,nf,x,_q,q,y,q1,q2,q3,qarr,
                all_faces;
        # Position of qubits in Steane's code:
        #       1
        #      2 r
        #     g 0 3
        #    4 5 b 6
        faces := [];
        bv := [];
        for i in [1..(7*n_data)] do
            Add(bv, Zero(GF(2)));
        od;
        # Add first type of faces (replacements of existing faces).
        all_faces := [r_faces, g_faces, b_faces];
        for k in [1..3] do
            for f in all_faces[k] do
                nf := ShallowCopy(bv);
                for x in f do
                    q := Position(all_elements, x);
                    q := 7*(q-1)+1;
                    if k = 1 then
                        q1 := q+4; q2 := q+5; q3 := q+6;
                    elif k = 2 then
                        q1 := q+1; q2 := q+3; q3 := q+6;    
                    else
                        q1 := q+1; q2 := q+2; q3 := q+4;
                    fi;
                    for y in [q1,q2,q3] do
                        nf[y] := One(GF(2));
                    od;
                od;
                Add(faces, nf);
            od;
        od;
        # Add second type of faces (Steane's code faces).
        all_faces := [[0,1,2,3],[0,2,4,5],[0,3,5,6]];
        for _q in [1..n_data] do
            q := 7*(_q-1)+1;
            for f in all_faces do
                qarr := List(f, x -> (q+x));
                nf := ShallowCopy(bv);
                for y in qarr do
                    nf[y] := One(GF(2));
                od;
                Add(faces, nf);
            od;
        od;
        VerifyComm(faces);
        return faces;
    end;

SteaneSHGetGaugeOperators :=
    function(n_data, all_elements, r_faces, g_faces, b_faces)
        local gauges,
                all_faces,
                gaf,
                bv,
                f,
                ng1,ng2,
                i,j,k,x,y,q,q1,q2,q3;
        # Position of qubits in Steane's code:
        #       1
        #      2 r
        #     g 0 3
        #    4 5 b 6
        gauges := [];
        bv := [];
        for i in [1..(7*n_data)] do
            Add(bv, Zero(GF(2)));
        od;
        all_faces := [r_faces, g_faces, b_faces];
        for k in [1..3] do
            for f in all_faces[k] do
                ng1 := ShallowCopy(bv); ng2 := ShallowCopy(bv);
                i := 1;
                for x in f do
                    q := Position(all_elements, x);
                    q := 7*(q-1)+1;
                    if k = 1 then
                        q1 := q+4; q2 := q+5; q3 := q+6;
                    elif k = 2 then
                        q1 := q+1; q2 := q+3; q3 := q+6;    
                    else
                        q1 := q+1; q2 := q+2; q3 := q+4;
                    fi;
                    for y in [q1,q2,q3] do
                        if i <= 4 then
                            ng1[y] := One(GF(2));
                        else
                            ng2[y] := One(GF(2));
                        fi;
                    od;
                    i := i+1;
                od;
            od;
            Add(gauges, ng1);
            Add(gauges, ng2);
        od;
        return gauges;
    end;
