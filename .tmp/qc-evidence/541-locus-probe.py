"""#541: where the integral lift locus pays, on a control and on T_Co.

A   the control `U(2) + A2` at the specimen of
    `tests/lattices/test_the_integral_lift_locus_is_a_union_of_transvection_cosets.sage`:
    the sizes |C|, |passing|, |kernel|, the cost of building the residue locus, the
    cost of `integral_members()`, and which set operations the locus answers;
B   what a subset of the torsor costs instead: `torsor.condition_set`, its
    membership, its emptiness with one admitted point;
C   T_Co itself, at its first isotropic vector: the same sizes and the same two
    costs, so the row's per-candidate price is measured rather than inferred.
"""
import faulthandler
import sys
import time

from sage_extensions.all import *

faulthandler.dump_traceback_later(500, repeat=True, file=sys.stdout)
START = time.perf_counter()


def mark(label):
    print(f"[{time.perf_counter() - START:8.2f} s] {label}", flush=True)


def specimen_control():
    lattice = Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2, -1], [-1, 2]])
    labels = tuple(lattice.module_generating_set())
    marked = lattice.linear_combination({
        label: ZZ(coefficient)
        for label, coefficient in zip(labels, (-2, 1, 0, -2), strict=True)
        if coefficient
    })
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    root = next(label for label in tuple(reduction.module_generating_set())
                if reduction.module_generator(label).q() == ZZ(2))
    isometry = reduction.reflection(reduction.module_generator(root))
    return lattice, reduction, isometry


def isotropic_vector(lattice):
    labels = tuple(lattice.module_generating_set())
    ordered = [lattice.module_generator(label) for label in labels]
    head = ordered[0]
    candidates = list(ordered)
    for other in ordered[3:]:
        candidates.extend((head + other, head - other))
    for i in range(3, len(ordered)):
        for j in range(i + 1, len(ordered)):
            candidates.append(ordered[i] + ordered[j])
            candidates.append(ZZ(2) * head + ordered[i] + ordered[j])
    for vector in candidates:
        if lattice.q(vector) == 0:
            return vector
    raise RuntimeError("no isotropic vector found")


def report_sizes(torsor):
    passing, kernel, parameters = torsor._integral_parameter_cosets()
    representatives, kernel_generators, period_generators = parameters
    print(f"  |passing| {len(tuple(passing))} |kernel| {len(tuple(kernel))} "
          f"|representatives| {len(representatives)} period {torsor.integral_parameter_period()}", flush=True)


def measure(name, lattice, marked, isometry):
    print(f"\n===== {name} =====", flush=True)
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    began = time.perf_counter()
    torsor = reduction.rational_lifts(reduction, isometry)
    print(f"  torsor built in {time.perf_counter() - began:.3f} s", flush=True)
    report_sizes(torsor)
    began = time.perf_counter()
    classes = torsor.integral_parameter_classes()
    print(f"  residue locus built in {time.perf_counter() - began:.3f} s, "
          f"cardinality {classes.cardinality()}", flush=True)
    began = time.perf_counter()
    members = torsor.integral_members()
    print(f"  integral_members() in {time.perf_counter() - began:.3f} s", flush=True)
    began = time.perf_counter()
    empty = members.is_empty()
    print(f"  is_empty() in {time.perf_counter() - began:.3f} s -> {empty}", flush=True)
    for attribute in ("inclusion", "is_parent_of", "predicate", "universe"):
        print(f"  locus answers {attribute}: {hasattr(members, attribute)}", flush=True)
    began = time.perf_counter()
    point = torsor.integral_base_point_or_none()
    print(f"  integral_base_point_or_none() in {time.perf_counter() - began:.3f} s "
          f"-> {'a lift' if point is not None else 'None'}", flush=True)
    # B: what a subset of the torsor costs instead.
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    parameterization = torsor.parameterization()
    coordinates = parameterization.inverse()

    def parameter_of(lift):
        return inclusion.lift(inclusion.codomain().wrap(coordinates(lift)))

    def in_residue(lift):
        return quotient(parameter_of(lift)) in classes

    began = time.perf_counter()
    subset = torsor.condition_set(in_residue)
    print(f"  subset of the torsor built in {time.perf_counter() - began:.3f} s", flush=True)
    if point is not None:
        began = time.perf_counter()
        admitted = subset(point)
        print(f"  admitted one point in {time.perf_counter() - began:.3f} s", flush=True)
        began = time.perf_counter()
        print(f"  subset.is_empty() in {time.perf_counter() - began:.3f} s -> {subset.is_empty()}", flush=True)
        began = time.perf_counter()
        print(f"  membership asked again in {time.perf_counter() - began:.3f} s "
              f"-> {subset.is_parent_of(point)}", flush=True)
    print(f"  empty residue locus? {classes.is_empty()}", flush=True)


control_lattice, control_reduction, control_isometry = specimen_control()
control_labels = tuple(control_lattice.module_generating_set())
control_marked = control_lattice.linear_combination({
    label: ZZ(coefficient)
    for label, coefficient in zip(control_labels, (-2, 1, 0, -2), strict=True)
    if coefficient
})
measure("A. the control U(2) + A2 at its non-integral reflection lift",
        control_lattice, control_marked, control_isometry)

tco = NamedLattices.Tco
tco_marked = isotropic_vector(tco)
print(f"\nT_Co isotropic marked vector {tco_marked}, div {tco.div(tco_marked)}", flush=True)
tco_reduction = tco.primitive_isotropic_subobject(tco_marked).isotropic_reduction()
measure("C. T_Co at its first isotropic vector, identity reduction isometry",
        tco, tco_marked, tco_reduction.Isom(tco_reduction).identity())
mark("done")
