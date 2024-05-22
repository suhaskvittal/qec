#
# Author:   Suhas Vittal
# date:     19 January 2024 
#
# Code for generating Hyperbolic Color Codes.
#
# Load:
#   R, S, T, L -- the Wythoff parameters for the surface and L is the tiling rate.
#   min_index max_index -- min and max index of normal subgroup

# Get functions.
Read("gap/utils/qec.gi");
Read("gap/utils/operations.gi");
Read("gap/codes/hyperbolic/base.gi");

LoadPackage("LINS");

# Compute normal subgroups.

G := FreeGroup(3);
G := G / [ G.1^2, G.2^2, G.3^2,
            (G.1*G.2)^R, (G.2*G.3)^S, (G.3*G.1)^T ];

gr := LowIndexNormalSubgroupsSearch(G, max_index);
lins := ComputedNormalSubgroups(gr);

Print("# of normal subgroups = ", Length(lins), "\n");

G := Grp(LinsRoot(gr));

# Make folder for codes.
if L = 1 then
    code_folder := Concatenation("codes/hycc/", String(R), "_", String(S), "_", String(T));
else
    code_folder := Concatenation("codes/shycc/", String(R), "_", String(S), "_", String(T), "_", String(L));
fi;
IO_mkdir(code_folder, 448);

# Iterate through subgroups.
i := 2;
version := 1;
while i <= Length(lins) do
    n_data := Index(lins[i]); # This is the number of qubits.
    if Index(lins[i]) < min_index then
        i := i+1;
        continue;
    fi;
    if Index(lins[i]) = Index(lins[i-1]) and i > 2 then
        version := version+1;
    else
        version := 1;
    fi;
    Print("Index: ", Index(lins[i]), "\n");

    H := Grp(lins[i]);
    # Compute quotient group.
    G_mod_H := G / H;
    gens := GeneratorsOfGroup(G_mod_H);
    # Print generator orders.
    a := gens[1];
    b := gens[2];
    c := gens[3];
    Print("Orders of ab, bc, and ca: ", Order(a*b), ", ", Order(b*c), ", ", Order(c*a), "\n");
    if not (Order(a*b) = R and Order(b*c) = S and Order(c*a) = T) then
        i := i+1;
        continue;
    fi;
    # Cosets of ab, bc, and ac correspond to faces of different colors.
    # Cosets of a, b, c correspond to edges on the surface. If x<a> <= x<ab>,
    # then the vertices incident to x<a> are in the face x<ab>.
    r_faces := RightCosets(G_mod_H, Subgroup(G_mod_H, [a, b]));
    g_faces := RightCosets(G_mod_H, Subgroup(G_mod_H, [a, c]));
    b_faces := RightCosets(G_mod_H, Subgroup(G_mod_H, [b, c]));
    
    a_edges := RightCosets(G_mod_H, Subgroup(G_mod_H, [a]));
    b_edges := RightCosets(G_mod_H, Subgroup(G_mod_H, [b]));
    c_edges := RightCosets(G_mod_H, Subgroup(G_mod_H, [c]));

    face_cosets := [];
    Append(face_cosets, r_faces);
    Append(face_cosets, g_faces);
    Append(face_cosets, b_faces);

    edge_cosets := [];
    Append(edge_cosets, a_edges);
    Append(edge_cosets, b_edges);
    Append(edge_cosets, c_edges);

    all_elements := [];
    for e in edge_cosets do
        for x in AsList(e) do
            AddSet(all_elements, x);
        od;
    od;

    _i := i;

    # Compute semi-hyperbolic tiling if L > 1.
    if L > 1 then
        new_faces := [];
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
                Add(new_faces, nf);
            od;
        od;
        Print("Type1 faces: ", Length(new_faces), "\n");
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
                    Add(new_faces, nf);
                od;
            od;
        od;
        # Create boundary stabilizers for each edge.
        edge_lists := [ a_edges, b_edges, c_edges ];
        for k in [1..3] do
            for e in edge_lists[k] do
                ele := AsList(e);
                # If we cannot find two incident faces, then ignore the edge.
#               cnt := 0;
#               for f in face_cosets do
#                   if Length(Intersection(AsList(f), ele)) = 2 then
#                       cnt := cnt+1;
#                   fi;
#               od;
#               if cnt < 2 then continue; fi;
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
                        Add(new_faces, nf);
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
                        Add(new_faces, nf);
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
                        Add(new_faces, nf);
                    od;
                fi;
            od;
        od;
        faces := new_faces;
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
    else 
        faces := ComputeIndicatorVectorsCC1(all_elements, face_cosets, edge_cosets);
    fi;

    checks := ComputeStabilizerGenerators(faces);
    ops := CssLXZOperators(checks, checks);

    n_data := L^2 * n_data;
    n_checks := 2*Length(checks);
    n_ops := Length(ops);
    n_log := n_data - n_checks;
    d := MinOperatorWeight(ops);

    Print("\tData qubits: ", n_data, "\n");
    Print("\tLogical qubits: ", n_log, "\n");
    Print("\tChecks: ", n_checks, "\n");
    Print("\tOperators: ", n_ops, "\n");
    Print("\t\tMin weight: ", d, "\n");

    WriteCodeToFile(CodeFilename(code_folder, n_data, n_log, version),
                        checks,
                        checks,
                        ops,
                        ops);
    i := _i+1;
od;

