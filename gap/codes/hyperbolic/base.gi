# Utility functions for files in this directory.

ComputeIndicatorVectorsSC :=
    function(check_cosets, qubit_cosets)
        local G, H, v_check_list, v_check;

        v_check_list := [];
        for G in check_cosets do
            v_check := [];
            for H in qubit_cosets do
                if Length(Intersection(AsList(H), AsList(G))) > 0 then
                    Add(v_check, One(GF(2)));
                else
                    Add(v_check, Zero(GF(2)));
                fi;
            od;
            Add(v_check_list, v_check);
        od;
        return v_check_list;
    end;

ComputeIndicatorVectorsCC :=
    function(G, faces)
        local check_list, check, f, x;

        check_list := [];
        for f in faces do 
            check := [];
            for x in Elements(G) do
                if x in f then
                    Add(check, One(GF(2)));
                else
                    Add(check, Zero(GF(2)));
                fi;
            od;
            Add(check_list, check);
        od;
        return check_list;
    end;

TranslateFaces :=
    function(G, faces)
        local face_list, f, vf, i, x, y, j;

        face_list := [];
        for f in faces do
            vf := [];
            for x in f do
                Add(vf, 0);
            od;
            i := 1;
            for x in Elements(G) do
                j := 1;
                for y in f do
                    if x = y then
                        vf[j] := i;
                        break;
                    fi;
                    j := j+1;
                od;
                i := i+1;
            od;
            AddSet(face_list, vf);
        od;
        return face_list;
    end;

CodeFilename :=
    function(folder, n, k)
        local filename;
        filename := Concatenation(folder, "/", 
                                    String(n), "_", String(k), ".txt");
        return filename;
    end;

Rot1 :=
    function(b)
        local arr, i;
        arr := [];
        i := 0;
        while i < Order(b) do
            Add(arr, b^i);
            i := i+1;
        od;
        return arr;
    end;

Rot2 :=
    function(a, b)
        local arr, i, k;
        arr := [];
        i := 0;
        k := 0;
        while i < 2*Order(a*b) do
            if i mod 2 = 0 then
                Add(arr, (a*b)^k);
                k := k+1;
            else
                Add(arr, (a*b)^k * a);
            fi;
            i := i+1;
        od;
        return arr;
    end;

GetCosets :=
    function(G, rots)
        local arr, _arr, x, y;
        arr := [];
        for x in Elements(G) do
            _arr := [];
            for y in rots do
                AddSet(_arr, x*y);
            od;
            AddSet(arr, _arr);
        od;
        return arr;
    end;

FacesShareEdge :=
    function(f1, f2)
        return Length(Intersection(f1, f2)) = 2;
    end;

TilingIsBipartite :=
    function(faces)
        local colors,
                dfs,
                visited,
                i,
                j,
                f1,
                f2;

        # Colors tracks the color of the face. If -1, then the color is not set.
        colors := List(faces, x -> -1);
        colors[1] := 0;

        dfs := [1];
        visited := [];
        while Size(dfs) > 0 do
            i := dfs[Size(dfs)];
            Remove(dfs);
            if i in visited then
                continue;
            fi;
            f1 := faces[i];
            # Iterate through all the faces. Only visit those adjacent to f1.
            j := 1;
            while j <= Size(faces) do
                if i = j then 
                    j := j+1;
                    continue;
                fi;
                f2 := faces[j];
                if not FacesShareEdge(f1, f2) then
                    j := j+1;
                    continue;
                fi;
                if colors[j] >= 0 then
                    if colors[i] = colors[j] then
                        return false;
                    else
                        j := j+1;
                        continue;
                    fi;
                fi;
                colors[j] := 1-colors[i];
                Add(dfs, j);
            od;
            AddSet(visited, i);
        od;
        return true;
    end;

FaceFilename :=
    function(folder, n, k)
        local filename;
        filename := Concatenation(folder, "/",  String(n), "_", String(k), ".faces.txt");
        return filename;
    end;

WriteFacesToFile :=
    function(filename, faces)
        local fout, vf, i, line;

        fout := IO_File(filename, "w");
        Print("Creating file ", filename, ": ", IsFile(fout), "\n");

        for vf in faces do
            i := 1;
            line := "";
            while i <= Length(vf) do
                if i > 1 then
                    line := Concatenation(line, ",");
                fi;
                line := Concatenation(line, String(vf[i]-1));
                i := i+1;
            od;
            IO_WriteLine(fout, line);
        od;
    end;

