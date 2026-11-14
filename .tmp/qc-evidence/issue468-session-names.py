import sage.all_cmdline
import sage_extensions.all as A
import sage_extensions.groups as G

names = ["Subgroups", "SymmetricGroups", "GeneralLinearGroups", "FreeGroupQuotients", "Torsors",
         "CoxeterGroups", "AbsoluteGaloisGroups", "FinitelyGeneratedGroups", "FinitelyPresentedGroups",
         "ProfiniteGroups", "AlternatingAlgebras", "SymmetricAlgebras", "TensorAlgebras",
         "StrictlyGradedCommutativeAlgebras", "FractionalIdeals", "ModulesWithConnection",
         "ModulesWithFlatConnection", "FinitelyGeneratedModules", "FinitelyPresentedModules",
         "ProjectiveModules", "TorsionModules", "TensorProductModules",
         "SymmetricBilinearFormModules"]
for name in names:
    preamble = getattr(A, name)
    owner = getattr(G, name, None)
    backend = getattr(sage.all_cmdline, name, None)
    same_as_owner = "owner" if (owner is not None and owner is preamble) else "other-area-or-private"
    verdict = "SHADOWS-SAGE" if (backend is not None and backend is not preamble) else ("same-as-sage" if backend is preamble else "no-sage-namesake")
    print(f"{name:34s} {type(preamble).__name__:22s} {same_as_owner:22s} {verdict}")
print()
print("area names published:", sum(len(getattr(__import__(a, fromlist=['x']), '__all__')) for a in A._AREA_PACKAGES) if hasattr(A, "_AREA_PACKAGES") else "n/a")
print("private loop names leaked:", [n for n in ("_area_package_name", "_area_package", "_area_name") if n in A.__dict__])
