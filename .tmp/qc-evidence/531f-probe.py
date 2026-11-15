r"""Probe: polytope equality and hash, the cone's canonical form, and what the caches buy."""

import time

from sage_extensions.all import *

start = time.time()


def stamp(label):
    print(f"[{time.time() - start:7.2f}s] {label}", flush=True)


def timed(label, work):
    begin = time.time()
    value = work()
    print(f"  {label}: {1000 * (time.time() - begin):8.3f} ms", flush=True)
    return value


lattice = ZZ.free_module(2)
category = ConvexPolytopes(lattice)
triangle = category(((0, 0), (1, 0), (0, 1)))
relocated = category(((1, 0), (0, 1), (0, 0)))
cut = category.from_halfspaces(((0, (1, 0)), (0, (0, 1)), (1, (-1, -1))))
other = category(((0, 0), (2, 0), (0, 1)))
print("triangle == relocated:", triangle == relocated, flush=True)
print("triangle == cut:", triangle == cut, flush=True)
print("triangle == other:", triangle == other, flush=True)
print("hash triangle, relocated, cut, other:",
      hash(triangle), hash(relocated), hash(cut), hash(other), flush=True)
triangles = [
    category(vertices)
    for vertices in (
        ((0, 0), (1, 0), (0, 1)),
        ((0, 0), (2, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 2)),
        ((0, 0), (1, 1), (0, 1)),
        ((0, 0), (1, 0), (1, 1)),
    )
]
print("five triangles, distinct hashes:",
      sum(1 for _ in {hash(each) for each in triangles}), flush=True)

product = Sets().product((triangle, Sets.Δ[1]))
print("a second triangle on the same vertices gives the same product:",
      Sets().product((relocated, Sets.Δ[1])) is product, flush=True)
print("a different triangle gives another product:",
      Sets().product((other, Sets.Δ[1])) is not product, flush=True)
print("the halfspace triangle gives the same product:",
      Sets().product((cut, Sets.Δ[1])) is product, flush=True)
stamp("polytope identity")

# A polygon with many vertices: the first hash reads the private polyhedron.
many = category(tuple((index, index * index) for index in range(1, 120)))
print("polygon vertices:", many.n_vertices(), flush=True)
first = timed("first hash of the 119-gon", lambda: hash(many))
second = timed("second hash of it", lambda: hash(many))
third = timed("third hash of it", lambda: hash(many))
print("  one hash:", first == second == third, flush=True)
stamp("polytope cache")

cones = ((1, 0), (0, 1))
lattice2 = Lattices(ZZ)([[1, 0], [0, 1]])
upper = lattice2.reduction_cell(((0, 1),))
lower = lattice2.reduction_cell(((0, -1),))
steeper = lattice2.reduction_cell(((1, -1),))
mirror = lattice2.reduction_cell(((-1, -1),))
for name, cone in (("upper", upper), ("steeper", steeper), ("mirror", mirror), ("lower", lower)):
    print(f"{name}: pointed {cone.is_pointed()}, dimension {cone.dimension()}, "
          f"canonical form {cone._canonical_form_modulo_lineality()}, hash {hash(cone)}",
          flush=True)
print("upper == lower:", upper == lower, flush=True)
print("three half-planes, distinct hashes:",
      sum(1 for _ in {hash(upper), hash(steeper), hash(mirror)}), flush=True)
print("two sides of one line, distinct hashes:",
      sum(1 for _ in {hash(upper), hash(lower)}), flush=True)
cube = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
quarter = cube.reduction_cell(((0, 1, 0), (0, 0, 1)))
opposite = cube.reduction_cell(((0, -1, 0), (0, 0, 1)))
print("quarter:", quarter._canonical_form_modulo_lineality(), hash(quarter), flush=True)
print("opposite:", opposite._canonical_form_modulo_lineality(), hash(opposite), flush=True)
print("quarter == opposite:", quarter == opposite, flush=True)

# A cone with a large lineality lattice: the first hash builds the form.
big = Lattices(ZZ)([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
wide = big.reduction_cell(((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
print("wide cone pointed:", wide.is_pointed(), flush=True)
timed("first hash of the cone with a lineality space", lambda: hash(wide))
timed("second hash of it", lambda: hash(wide))
timed("third hash of it", lambda: hash(wide))
stamp("cone cache")

points = FiniteOrderedSets()(tuple(range(2000)))
asked = []

def is_even(point):
    asked.append(point)
    return point % 2 == 0

subset = points.power_set().from_predicate(is_even)
before = sum(1 for _ in asked)
timed("first hash of a subset of 2000 points", lambda: hash(subset))
settled = sum(1 for _ in asked)
timed("second hash of it", lambda: hash(subset))
timed("third hash of it", lambda: hash(subset))
after = sum(1 for _ in asked)
print(f"  decisions: before {before}, after the first hash {settled}, after three hashes {after}",
      flush=True)
stamp("subset cache")

# What the canonical form promises: it is a complete invariant of the cone.
small = tuple(
    (first, second)
    for first in (-1, 0, 1)
    for second in (-1, 0, 1)
    if (first, second) != (0, 0)
)
half_planes = [lattice2.reduction_cell((wall,)) for wall in small]
wedges = [
    lattice2.reduction_cell((first, second))
    for first in small
    for second in small
    if first != second
]
for name, family in (("half-planes", half_planes), ("wedges", wedges)):
    forms = [cone._canonical_form_modulo_lineality() for cone in family]
    agreements = 0
    disagreements = []
    for left in range(len(family)):
        for right in range(left + 1, len(family)):
            same_form = forms[left] == forms[right]
            same_cone = family[left].is_equal_to(family[right])
            if same_form == same_cone:
                agreements += 1
            else:
                disagreements.append((left, right, same_form, same_cone))
    print(
        f"{name}: {sum(1 for _ in family)} cones, {sum(1 for _ in set(forms))} forms, "
        f"{agreements} pairs agree, {sum(1 for _ in disagreements)} disagree",
        flush=True,
    )
    for left, right, same_form, same_cone in disagreements[:5]:
        print(
            f"  {family[left].primitive_rays().cardinality()}/"
            f"{family[left].lineality_generators().cardinality()} rays/lineality vs "
            f"{family[right].primitive_rays().cardinality()}/"
            f"{family[right].lineality_generators().cardinality()}: form {same_form}, cone {same_cone}",
            flush=True,
        )
stamp("canonical form is a complete invariant")
