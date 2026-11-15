"""#531: one cone is one canonical form, however it is cut out."""
from sage.misc.randstate import set_random_seed
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.all import *

z3 = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


def show(name, cone):
    print(f"{name}: pointed={cone.is_pointed()} dim={cone.dimension()}")
    print("  lines ", [tuple(line) for line in cone._engine.lines()])
    print("  rays  ", [tuple(ray) for ray in cone._engine.rays()])
    print("  form  ", cone._canonical_form_modulo_lineality())
    print("  hash  ", hash(cone))


short = z3.reduction_cell(((-1, 3, 0), (3, -11, 1)))
longer = z3.reduction_cell(((-1, 3, 0), (3, -11, 1), (0, -2, 1)))
show("short ", short)
show("longer", longer)
print("the reviewer's pair: equal", short == longer,
      "| hash equal", hash(short) == hash(longer),
      "| one set", cardinal(sum(1 for _ in {short, longer})))

# the two sides of one line must stay two sets
upper = z3.reduction_cell(((0, 1, 0),))
lower = z3.reduction_cell(((0, -1, 0),))
print("two sides of a line: equal", upper == lower, "hash equal", hash(upper) == hash(lower))

# a random search over cones with a lineality, cut out twice
set_random_seed(20261115)
disagreements = 0
checked = 0
cones = []
for trial in range(400):
    first = tuple(SageZZ.random_element(-6, 7) for _ in range(3))
    second = tuple(SageZZ.random_element(-6, 7) for _ in range(3))
    if any(entry for entry in first) is False or any(entry for entry in second) is False:
        continue
    cone = z3.reduction_cell((first, second))
    if cone.is_pointed():
        continue
    multiple = SageZZ.random_element(1, 4)
    redundant = tuple(
        second[i] + multiple * first[i] for i in range(3)
    )
    other = z3.reduction_cell((first, second, redundant))
    checked += 1
    cones.append((cone, other))
    if cone != other or hash(cone) != hash(other):
        disagreements += 1
        if disagreements <= 3:
            print("  DISAGREEMENT", (first, second), "vs redundant", redundant)
            print("   ", cone._canonical_form_modulo_lineality())
            print("   ", other._canonical_form_modulo_lineality())
print(f"two presentations of one cone: {checked} cones, {disagreements} disagreements")

# the form separates distinct cones on the same sample
same = 0
pairs = 0
for i, (left, _) in enumerate(cones):
    for right, _ in cones[i + 1:]:
        pairs += 1
        equal = left == right
        same_form = left._canonical_form_modulo_lineality() == right._canonical_form_modulo_lineality()
        if equal != same_form or equal != (hash(left) == hash(right)):
            same += 1
            if same <= 3:
                print("  FORM DISAGREES WITH EQUALITY", equal, same_form)
print(f"distinct cones of the sample: {pairs} pairs, {same} where the form or the hash "
      f"disagrees with the cone equality")

# diagnose every form collision: which side is finer
collisions = 0
for i, (left, _) in enumerate(cones):
    for right, _ in cones[i + 1:]:
        if left == right:
            continue
        if left._canonical_form_modulo_lineality() == right._canonical_form_modulo_lineality():
            collisions += 1
            print("  FORM COLLISION between unequal cones")
            for label, cone in (("left ", left), ("right", right)):
                form = cone._canonical_form_modulo_lineality()
                print("   ", label, "dim", cone.dimension(),
                      "halfspaces", list(cone.halfspace_covectors()))
                print("        lines", [tuple(line) for line in cone._engine.lines()],
                      "rays", [tuple(ray) for ray in cone._engine.rays()])
                print("        form", form, "hash of the form", hash(form))
                print("        engine H", list(cone._engine_polyhedron().Hrepresentation()))
            print("    equal both ways:", left.is_equal_to(right), right.is_equal_to(left))
            print("    engine polyhedra equal:",
                  left._engine_polyhedron() == right._engine_polyhedron())
            print("    hash of the cones:", hash(left), hash(right))
print(f"form collisions among unequal cones of the sample: {collisions}")

for i, (left, _) in enumerate(cones):
    for right, _ in cones[i + 1:]:
        if left == right:
            same_hash = hash(left) == hash(right)
            if not same_hash:
                print("  EQUAL CONES WITH TWO HASHES", left._canonical_form_modulo_lineality(),
                      right._canonical_form_modulo_lineality())
        elif hash(left) == hash(right):
            print("  UNEQUAL CONES WITH ONE HASH: a plain hash collision, or an equality that is too fine")
            for label, cone in (("left ", left), ("right", right)):
                form = cone._canonical_form_modulo_lineality()
                print("   ", label, "dim", cone.dimension(),
                      "halfspaces", list(cone.halfspace_covectors()))
                print("        lines", [tuple(line) for line in cone._engine.lines()],
                      "rays", [tuple(ray) for ray in cone._engine.rays()])
                print("        form", form, "hash of the form", hash(form))
                print("        engine H", list(cone._engine_polyhedron().Hrepresentation()))
            print("    equal both ways:", left.is_equal_to(right), right.is_equal_to(left))
            print("    engine polyhedra equal:",
                  left._engine_polyhedron() == right._engine_polyhedron())
            print("    hash of the cones:", hash(left), hash(right))

# cost: the first hash of a cone with a lineality, then the cached ones
import time
fresh = [z3.reduction_cell(((1, 0, k), (0, 1, 0))) for k in range(1, 51)]
start = time.perf_counter()
for cone in fresh:
    hash(cone)
first = (time.perf_counter() - start) / len(fresh) * 1000
start = time.perf_counter()
for cone in fresh:
    hash(cone)
again = (time.perf_counter() - start) / len(fresh) * 1000
print(f"hash of a cone with a lineality: first {first:.3f} ms, cached {again:.3f} ms")
