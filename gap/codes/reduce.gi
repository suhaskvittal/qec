# Precondition: "filename" must be loaded.

Read("gap/utils/qec.gi");

data := ReadCodeFromFile(filename);
x_checks := data.x_checks;
z_checks := data.z_checks;

x_checks := ComputeStabilizerGenerators(x_checks);
z_checks := ComputeStabilizerGenerators(z_checks);
x_ops := CssLXZOperators(x_checks, z_checks);
z_ops := CssLXZOperators(z_checks, x_checks);

Print("Checks: ", Length(x_checks), ", ", Length(z_checks), "\n");
Print("Operators: ", Length(x_ops), "\n");

WriteCodeToFile(filename, x_checks, z_checks, x_ops, z_ops);

