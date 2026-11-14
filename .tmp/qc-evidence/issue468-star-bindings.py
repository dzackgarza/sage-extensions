r"""What ``sage_extensions.all`` binds, and which package declares each name (#468).

Run from a repository tree inside the research image:

    /sage/.venv/bin/python -u .scratch/issue468-bindings.py

The session contract: every name an area package declares in its ``__all__`` is
bound in ``sage_extensions.all`` to the very object the declaring package
exports; a name declared by two areas is one object; and where Sage's own
namespace has a constructor of the same name, the session's binding wins (API-06).
"""

import importlib
import pathlib
import re

import sage.all_cmdline
import sage_extensions.all as session

SOURCE = pathlib.Path(session.__file__).read_text()
AREAS = re.findall(r"^from (sage_extensions[\w.]*) import \*", SOURCE, re.M)
STAR_IMPORTS = len(AREAS)
if not AREAS:
    AREAS = list(getattr(session, "_AREA_PACKAGES", ()))

print(f"module: {session.__file__}")
print(f"area packages: {len(AREAS)}; star imports in all.py: {STAR_IMPORTS}")

declared = {}
for area in AREAS:
    module = importlib.import_module(area)
    for name in module.__all__:
        declared.setdefault(name, []).append((area, getattr(module, name)))

unbound = sorted(name for name in declared if name not in session.__dict__)
rebound = sorted(
    name
    for name, owners in declared.items()
    if name in session.__dict__
    and any(obj is not session.__dict__[name] for _, obj in owners)
)
shared = {
    name: [area for area, _ in owners]
    for name, owners in declared.items()
    if len(owners) > 1
}
leaked = sorted(name for name in session.__dict__ if name.startswith("_area"))

print(f"declarations: {sum(len(owners) for owners in declared.values())} "
      f"over {len(declared)} distinct names")
print(f"declared by more than one area: {len(shared)}")
print(f"unbound in the session: {len(unbound)} {unbound}")
print(f"bound to an object no declarer exports: {len(rebound)} {rebound}")
print(f"loop temporaries left in the module: {leaked}")

NAMES_407 = (
    "Subgroups",
    "SymmetricGroups",
    "GeneralLinearGroups",
    "FreeGroupQuotients",
    "Torsors",
    "CoxeterGroups",
)
NAMES_408 = (
    "AbsoluteGaloisGroups",
    "AbsoluteGaloisGroupsOfFiniteFields",
    "FinitelyGeneratedGroups",
    "FinitelyPresentedGroups",
    "ProfiniteGroups",
    "AlternatingAlgebras",
    "SymmetricAlgebras",
    "TensorAlgebras",
    "StrictlyGradedCommutativeAlgebras",
    "FractionalIdeals",
    "ModulesWithConnection",
    "ModulesWithFlatConnection",
    "FinitelyGeneratedModules",
    "FinitelyPresentedModules",
    "ProjectiveModules",
    "TorsionModules",
    "TensorProductModules",
    "SymmetricBilinearFormModules",
)


def origin(obj):
    module = getattr(obj, "__module__", type(obj).__module__)
    qualname = getattr(obj, "__qualname__", type(obj).__name__)
    return f"{module}.{qualname}"


print()
print(f"{'name':36s} {'declared by':46s} {'sage namesake':14s} binding")
for name in NAMES_407 + NAMES_408:
    obj = session.__dict__.get(name)
    declarers = [area for area, other in declared.get(name, ()) if other is obj]
    backend = getattr(sage.all_cmdline, name, None)
    if backend is None:
        shadow = "none"
    elif backend is obj:
        shadow = "same object"
    else:
        shadow = "SHADOWED"
    print(f"{name:36s} {(declarers[0] if declarers else 'UNDECLARED'):46s} "
          f"{shadow:14s} {origin(obj)}")

print()
a2 = session.CoxeterGroups()([[1, 3], [3, 1]])
print("CoxeterGroups()([[1, 3], [3, 1]]).order():", a2.order())
print("  in FreeGroupQuotients():", a2 in session.FreeGroupQuotients())
print("  in OwnedGroups().Finite():", a2 in session.OwnedGroups().Finite())
s3 = session.SymmetricGroups()(session.Sets.Δ[2])
print("SymmetricGroups()(Sets.Δ[2]).order():", s3.order())
s3_group = session.Groups.S(3)
alternating = s3_group.predicate_subgroup(lambda g: g.sign() == 1, "sgn(g) = 1")
print("Subgroups(S_3) contains S_3.predicate_subgroup(sgn = 1):",
      alternating in session.Subgroups(s3_group), "of order", alternating.cardinality())
gl2 = session.GeneralLinearGroups()(session.GF(2), 2)
print("GeneralLinearGroups()(GF(2), 2).order():", gl2.order())
c3 = session.Groups.C(3)
torsor = session.Torsors(c3)(
    session.FiniteGSets(c3)(tuple(c3), lambda g, x: g * x)
)
print("Torsors(C_3)(regular C_3-set).cardinality():", torsor.cardinality())
