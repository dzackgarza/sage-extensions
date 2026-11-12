"""The T_Co plane-orbit call through the plane's own stabilizer, after the index-one reduction."""
import time

from sage_extensions.all import *  # noqa: F401,F403


def stamp(label, start):
    print(f"[{time.strftime('%H:%M:%S')}] {label}: {round(time.time() - start, 1)} s", flush=True)


def whole_orthogonal_group(lattice):
    target = lattice.discriminant_group().orthogonal_group()
    whole = target.subgroup_on(tuple(target.group_generators()))
    return lattice.Aut().discriminant_preimage(whole)


start = time.time()
coble = NamedLattices.Tco
labels = tuple(coble.module_generating_set())


def vector(coefficients):
    total = coble.zero()
    for label, coefficient in zip(labels, coefficients, strict=True):
        if coefficient:
            total = total + coefficient * coble.module_generator(label)
    return total


plane = coble.primitive_isotropic_subobject(
    vector([0, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1]),
    vector([2, 0, 0, -1, -1, -2, -2, -2, -2, -2, 0]),
)
group = whole_orthogonal_group(coble)
quotient = group.finite_character_quotient()
print("index [O(L) : Gamma] =", quotient.index(), flush=True)
orbit_start = time.time()
orbits = group.isotropic_plane_orbits([plane])
stamp("T_Co isotropic_plane_orbits", orbit_start)
print("T_Co PLANE ROW:", orbits.cardinality(), flush=True)
for orbit in orbits:
    realized = orbit.representative()
    print("  representative:", realized, "| primitive", realized.is_primitive(),
          "| rank", int(realized.module_rank()), flush=True)
    print("  divided classes:", [str(c) for c in orbit.divided_classes()], flush=True)
stamp("whole probe", start)
