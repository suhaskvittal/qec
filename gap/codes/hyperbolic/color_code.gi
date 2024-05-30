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
Read("gap/codes/hyperbolic/xforms.gi");

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
elif L = -1 then
    code_folder := Concatenation("codes/sthycc/", String(R), "_", String(S), "_", String(T));
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
    Print("Index: ", Index(lins[i]), ", i = ", i, "\n");

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
        faces := HiggottSemiHyperbolic(
                    n_data, L, all_elements,
                    r_faces, g_faces, b_faces,
                    a_edges, b_edges, c_edges);
    elif L = -1 then
        faces := SteaneSemiHyperbolic(n_data, all_elements, r_faces, g_faces, b_faces);
    else 
        faces := ComputeIndicatorVectorsCC1(all_elements, face_cosets, edge_cosets);
    fi;

    checks := ComputeStabilizerGenerators(faces);
    ops := CssLXZOperators(checks, checks);

    if L >= 1 then
        n_data := L^2 * n_data;
    elif L = -1 then
        n_data := 7 * n_data;
    fi;
    n_checks := 2*Length(checks);
    n_ops := Length(ops);
    n_log := n_data - n_checks;
    d := MinOperatorWeight(ops);

    Print("\tData qubits: ", n_data, "\n");
    Print("\tLogical qubits: ", n_log, "\n");
    Print("\tChecks: ", n_checks, "\n");
    Print("\tOperators: ", n_ops, "\n");
    Print("\t\tMin weight: ", d, "\n");
    if L = -1 then
#       # Report on gauge operators.
#       gauges := SteaneSHGetGaugeOperators(n_data, all_elements, r_faces, g_faces, b_faces);
#       gaf := [];
#       Append(gaf, gauges);
#       Append(gaf, checks);
#       VerifyComm(gaf);
#       n_log_left := 0;
#       for opv in ops do
#           if All(List(gauges, x -> AreCommuting(opv, x))) then
#               n_log_left := n_log_left+1;
#           fi;
#       od;
#       Print("\tLogical qubits with gauge operators: ", n_log_left, "\n");
    fi;

    WriteCodeToFile(CodeFilename(code_folder, n_data, n_log, version),
                        checks,
                        checks,
                        ops,
                        ops);
    i := _i+1;
od;

