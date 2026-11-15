r"""The corrected locus' cosets and the kernel family they give, at Sterk (4.3.8) (#405).

Coset representatives are read off the Smith form of the section's coefficient matrix
(taken by columns), and every parameter below is a tuple of the parameter lattice's
coordinates, so no two coordinate systems are mixed.  The lift is the owned composition
``t(f, s(a)) * base`` and its integrality is the owned integral restriction.
"""
import time
from math import prod

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.sterk import Sterk

from sage.all import ZZ, gcd, lcm  # noqa: F401
from sage.matrix.constructor import matrix
from sage.rings.rational_field import QQ

T0 = time.time()


def say(*a):
    print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)


L = NamedLattices.TEn
v = Sterk.sterk4_cusp_vector()
line = L.primitive_isotropic_subobject(v)
red = line.isotropic_reduction()
t = red.rational_lifts(red, red.Aut().one())
source = t.source_reduction().isotropic_embedding().codomain()
target = t.target_reduction().isotropic_embedding().codomain()
witt = t._target_witt
f = witt.isotropic_vector()
section_target = witt.rational_lattice()
quotient = t.integral_parameter_quotient()
P = quotient.domain()
classes_module = quotient.codomain()
m = t.integral_parameter_period()
base = t.base_point()
say("built: P rank", P.module_rank(), " m", m)

labels = tuple(P.module_generating_set())
rank = int(P.module_rank())
section = t._target_section
column_lists = [
    list(section_target.rational_coordinates(
        section(P.inclusion()(P.module_generator(label)).underlying_element())
    ).list())
    for label in labels
]
coordinates = matrix(QQ, target.module_rank(), rank, [
    column_lists[column][entry]
    for entry in range(int(target.module_rank()))
    for column in range(rank)
])
denominator = ZZ(1)
for entry in coordinates.list():
    denominator = lcm(denominator, ZZ(entry.denominator()))
integral_coordinates = matrix(ZZ, target.module_rank(), rank,
                              [ZZ((entry * denominator).numerator()) for entry in coordinates.list()])
smith, left, right = integral_coordinates.smith_form()
steps = tuple(denominator // gcd(abs(smith[i, i]), denominator) for i in range(rank))
coset_steps = tuple(gcd(step, ZZ(m)) for step in steps)
counts = tuple(ZZ(m) // step for step in coset_steps)
say("denominator", denominator, "smith", [smith[i, i] for i in range(rank)])
say("steps", steps, "#reps", prod(int(s) for s in coset_steps), "|K|", prod(int(c) for c in counts))

images = tuple(classes_module(quotient(P.module_generator(label))) for label in labels)
zero = classes_module.zero()


def class_of(coefficients):
    return sum(
        (classes_module.scalar_multiple(classes_module.base_ring()(c), image)
         for c, image in zip(coefficients, images) if c % m != 0),
        zero,
    )


def parameter_of(coefficients):
    ring = P.base_ring()
    return P.inclusion()(P.linear_combination(
        {label: ring(c) for label, c in zip(labels, coefficients)}
    )).underlying_element()


def reading(indices):
    column = right * matrix(ZZ, rank, 1, [ZZ(i) for i in indices])
    return tuple(int(entry) % int(m) for entry in column.list())


def enumerations(moduli):
    indices = [0] * rank
    while True:
        yield tuple(indices)
        position = 0
        while position < rank:
            indices[position] += 1
            if ZZ(indices[position]) < ZZ(moduli[position]):
                break
            indices[position] = 0
            position += 1
        if position == rank:
            return


def lift_at(coefficients):
    return (section_target.eichler_transvection(f, section(parameter_of(coefficients))) * base)


def integral_lift(coefficients):
    return lift_at(coefficients).integral_restriction(source, target) is not None


passing, refused = [], []
for indices in enumerations(coset_steps):
    coefficients = reading(indices)
    (passing if integral_lift(coefficients) else refused).append(coefficients)
say("representatives:", len(passing) + len(refused), " passing:", len(passing))

kernel_coefficients = []
for unit in range(rank):
    scaled = tuple(ZZ(1 if position == unit else 0) * step
                   for position, step in zip(range(rank), coset_steps))
    kernel_coefficients.append(reading(scaled))

period_inclusion = quotient.kernel().inclusion()
period_coefficients = [
    tuple(int(period_inclusion(generator).to_vector()(label)) for label in labels)
    for generator in period_inclusion.domain().module_generators()
]
say("period generators:", len(period_coefficients))


def shifted(coefficients, shift):
    return tuple((a + b) % int(m) for a, b in zip(coefficients, shift))


origin = passing[0]
say("origin:", origin)
shifts = [*period_coefficients, *kernel_coefficients]
family_coefficients = [
    *(coefficients for coefficients in passing[1:]),
    *(shifted(origin, shift) for shift in shifts),
]
say("family size", len(family_coefficients), " distinct:",
    len({tuple(int(e) % int(m) for e in c) for c in family_coefficients}))
origin_lift = lift_at(origin)
family = tuple(lift_at(coefficients) * origin_lift.inverse() for coefficients in family_coefficients)
say("every family member integral:",
    all(member.integral_restriction(source, target) is not None for member in family))
rho = target.discriminant_representation()
ambient = target.discriminant_group().orthogonal_group()
images = tuple(rho(member.integral_restriction(source, target)) for member in family)
say("rho-images computed")
subgroup = ambient.subgroup(tuple(image for image in images if image != ambient.one()))
say("rho(K_v) order:", subgroup.cardinality())

say("--- the locus is a union of kernel cosets ---")
for name, coefficients in (("passing", passing[1]), ("refused", refused[0])):
    for unit in (0, 3, 7):
        say(" ", name, "+ kernel", unit, "integral:",
            integral_lift(shifted(coefficients, kernel_coefficients[unit])))
say("--- the period keeps integrality ---")
for unit in (0, 5):
    say("  passing + period", unit, "integral:",
        integral_lift(shifted(passing[1], period_coefficients[unit])),
        " refused + period", unit, "integral:",
        integral_lift(shifted(refused[0], period_coefficients[unit])))
say("done")
