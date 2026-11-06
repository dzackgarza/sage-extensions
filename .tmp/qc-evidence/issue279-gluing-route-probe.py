"""Issue #279: one delta per O(q_C)-orbit, on the consumer specimen."""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


T = NamedLattices.TEn
C = NamedLattices.Tco
square = ZZ(-2)
M = Lattices(ZZ)([[square]]) + C
A_C = C.discriminant_quadratic_form()
A_M = M.discriminant_group()
labels_MD = tuple(M.dual_lattice().module_generating_set())
labels_CD = tuple(C.dual_lattice().module_generating_set())
stage(f"M rank {M.module_rank()}; A_M {A_M.cardinality()}; dual labels {len(labels_MD)} and {len(labels_CD)}")
print("first dual label of M:", labels_MD[0], "| C labels start:", labels_CD[0], flush=True)

values = A_C.quadratic_value_module()
half = values(QQ(1) / QQ(2))

# q and b on A_C from the form's own generators, so the filter is one pass
generators = tuple(A_C.module_generators())
diagonal = tuple(A_C.q(generator) for generator in generators)
off_diagonal = {
    (left, right): A_C.q(generators[left] + generators[right])
    - diagonal[left] - diagonal[right]
    for left in range(len(generators))
    for right in range(left + 1, len(generators))
}
stage(f"form data read on {len(generators)} generators")


def half_integral_class(coefficients):
    value = A_C.zero().q()
    for position, coefficient in enumerate(coefficients):
        if coefficient:
            if coefficient == 1:
                value = value + diagonal[position]
            else:
                value = value + coefficient * coefficient * diagonal[position]
            for other in range(position + 1, len(coefficients)):
                if coefficients[other]:
                    value = value + coefficient * coefficients[other] * off_diagonal[(position, other)]
    return value


candidates = []
for element in A_C.elements():
    lifted = A_C.dual_lattice_lift(element)
    coordinates = lifted.to_vector()
    coefficients = tuple(int(coordinates(label)) for label in labels_CD)
    if half_integral_class(coefficients) != half:
        continue
    if int(element.additive_order()) != 2:
        continue
    candidates.append((element, coefficients))
stage(f"candidates of order 2 and q = 1/2: {len(candidates)}")

group = A_C.orthogonal_group()
group_generators = tuple(group.group_generators())
stage(f"|O(q_C)| generators: {len(group_generators)}")


def orbit_of(seed):
    orbit = {seed}
    frontier = [seed]
    while frontier:
        current = frontier.pop()
        for generator in group_generators:
            image = generator(current)
            if image not in orbit:
                orbit.add(image)
                frontier.append(image)
    return orbit


remaining = {element for element, _coordinates in candidates}
representatives = []
while remaining:
    seed = next(iter(remaining))
    orbit = orbit_of(seed)
    representatives.append(seed)
    remaining -= orbit
    stage(f"orbit of size {len(orbit)}; {len(remaining)} left")
print("orbit representatives:", len(representatives), flush=True)

e_star = M.dual_lattice().module_generator(labels_MD[0])
for element, coefficients in candidates:
    if element not in representatives:
        continue
    images = {
        labels_MD[1 + position]: coefficient
        for position, coefficient in enumerate(coefficients)
        if coefficient
    }
    glue_class = M.discriminant_class(e_star + M.dual_lattice().linear_combination(images))
    print("   glue class q in A_M:", glue_class.q(), "order", glue_class.additive_order(), flush=True)
    inclusion = M.overlattice(glue_class)
    enlarged = inclusion.codomain()
    stage(f"   overlattice index {inclusion.index()}, det {enlarged.determinant()}, signature {enlarged.signature()}")
    if enlarged.signature() != T.signature():
        print("   signature mismatch", flush=True)
        continue
    is_isometric = enlarged.is_isometric_to(T)
    stage(f"   isometric to T_En: {is_isometric}")
    if is_isometric is not True:
        continue
    witness = enlarged.isometry_to(T)
    delta = witness(enlarged.module_generator(enlarged.module_generating_set()[0]))
    print(
        "   DELTA square", delta.q(), "primitive", delta.is_primitive(),
        "| complement is T_Co:", T.orthogonal_complement(delta).domain().is_isometric_to(C),
        flush=True,
    )
print("DONE", flush=True)
