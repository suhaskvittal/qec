#
# Author:   Suhas Vittal
# date:     19 January 2024
#
# Utility code for QEC.
#

LoadPackage("IO");

OperatorWeight :=
    function(operator)
        local w, x;
        w := 0;
        for x in operator do
            if x = One(GF(2)) then
                w := w+1;
            fi;
        od;
        return w;
    end;

ComputeStabilizerGenerators :=
    function(check_list)
        local curr, tmp, V, x;
        curr := [ ];
        for x in check_list do
            tmp := Concatenation(curr, [x]);
            V := VectorSpace(GF(2), tmp);
            if Dimension(V) > Length(curr) then
                Add(curr, x);
            fi;
        od;
        return curr;
    end;

AreCommuting :=
    function(v, w)
        return (v * w) = Zero(GF(2));
    end;

ConvertIndicatorVector :=
    function(v, n)
        local w, i;
        
        w := [];
        for i in [1..n] do
            Add(w, Zero(GF(2)));
        od;
        for i in v do
            w[i] := One(GF(2));
        od;
        return w;
    end;

ConvertVector :=
    function(v, M)
        local w, i;
        w := [];
        for i in [1..Length(v)] do
            if v[i] = One(GF(2)) then
                Add(w, M);
            else
                Add(w, [[1,0], [0,1]]);
            fi;
        od;
        return w;
    end;

# Computes the logical X/Z operators. To compute logical X operators,
# the first argument should be the X checks and the second should be
# the Z checks. For logical Z, vice versa.
CssLXZOperators := 
    function(same_type_checks, opposing_checks)
        local im_osame, ker, op_list;

        im_osame := VectorSpace(GF(2), same_type_checks); 
        
        op_list := [];
        Append(op_list, same_type_checks);
        Append(op_list, NullspaceMat(TransposedMat(opposing_checks)));

        ker := VectorSpace(GF(2), op_list);
        return Filtered(BasisVectors(Basis(ker)), v -> not (v in im_osame));
    end;

MinOperatorWeight :=
    function(operators) 
        local min_w, op, w;

        min_w := OperatorWeight(operators[1]);
        for op in operators do
            w := OperatorWeight(op);
            if w < min_w then   min_w := w; fi;
        od;
        return min_w;
    end;

# Prints generators for tanner graph.
PrintGenerators :=
    function(stabilizers, type, tabs)
        local i, j, s, x;

        i := 0;
        for s in stabilizers do
            Print(tabs, type, i);
            j := 0;
            for x in s do
                if x = One(GF(2)) then
                    Print(",", j);
                fi;
                j := j+1;
            od;
            Print("\n");
            i := i+1;
        od;
    end;

ReadChecksAndOperatorsFromFile :=
    function(fin)
        local x_checks, z_checks, x_ops, z_ops, max_n,
                lines, line, i, c, buf, x_ch_ind, z_ch_ind, x_op_ind, z_op_ind, v, n,
                is_x, is_op, is_rec_to_buf;

        x_ch_ind := []; z_ch_ind := []; x_op_ind := []; z_op_ind := [];
        
        lines := IO_ReadLines(fin);
        max_n := 0;
        for line in lines do
            is_x := false;
            is_op := false;

            if line[1] = 'O' then
                is_op := true;
                if line[2] = 'X' then
                    is_x := true;
                fi;
            elif line[1] = 'X' then
                is_x := true;
            fi;

            is_rec_to_buf := false;
            buf := "";
            v := [];

            i := 3;
            while i < Length(line) do
                c := line[i];
                if c = ',' then
                    if Length(buf) > 0 then
                        n := Int(buf)+1;
                        if n > max_n then
                            max_n := n;
                        fi;
                        Add(v, n);
                    fi;
                    is_rec_to_buf := true;
                    buf := "";
                elif is_rec_to_buf then
                    Add(buf, c);
                fi;
                i := i+1;
            od;
            if Length(buf) > 0 then
                n := Int(buf)+1;
                if n > max_n then
                    max_n := n;
                fi;
                Add(v, n);
            fi;
            if is_op then
                if is_x then
                    Add(x_op_ind, v);
                else
                    Add(z_op_ind, v);
                fi;
            else 
                if is_x then
                    Add(x_ch_ind, v);
                else
                    Add(z_ch_ind, v);
                fi;
            fi;
        od;
        x_checks := []; z_checks := []; x_ops := []; z_ops := [];

        for v in x_ch_ind do Add(x_checks, ConvertIndicatorVector(v, max_n)); od;
        for v in z_ch_ind do Add(z_checks, ConvertIndicatorVector(v, max_n)); od;
        for v in x_op_ind do Add(x_ops, ConvertIndicatorVector(v, max_n)); od;
        for v in z_op_ind do Add(z_ops, ConvertIndicatorVector(v, max_n)); od;

        return rec( n := max_n, x_checks := x_checks, z_checks := z_checks,
                    x_ops := x_ops, z_ops := z_ops );
    end;

WriteChecksAndOperatorsToFile :=
    function(fout, checks, operators, type)
        local line, i, j, s, x;

        i := 0;
        for s in checks do
            line := Concatenation(type, String(i));
            j := 0;
            for x in s do
                if x = One(GF(2)) then
                    line := Concatenation(line, ",", String(j));
                fi;
                j := j+1;
            od;
            i := i+1;

            IO_WriteLine(fout, line);
        od;
        i := 0;
        for s in operators do
            line := Concatenation("O", type, String(i));
            j := 0;
            for x in s do
                if x = One(GF(2)) then
                    line := Concatenation(line, ",", String(j));
                fi;
                j := j+1;
            od;
            i := i+1;

            IO_WriteLine(fout, line);
        od;
    end;

ReadCodeFromFile :=
    function(file)
        local fin;

        fin := IO_File(file, "r");
        Print("Reading file ", file, ": ", IsFile(fin), "\n");
        return ReadChecksAndOperatorsFromFile(fin);
    end;

WriteCodeToFile :=
    function(file, x_checks, z_checks, x_operators, z_operators)
        local fout;

        fout := IO_File(file, "w");
        Print("Creating file ", file, ": ", IsFile(fout), "\n");
        WriteChecksAndOperatorsToFile(fout, x_checks, x_operators, "X");
        WriteChecksAndOperatorsToFile(fout, z_checks, z_operators, "Z");
    end;
