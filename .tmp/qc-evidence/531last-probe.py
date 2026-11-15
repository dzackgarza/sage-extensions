"""#531: the one canonical form, its invariance, and the polytope vertex set."""
from sage_extensions.all import *


def describe(name, cone):
    print(f"{name}: pointed={cone.is_pointed()} dim={cone.dimension()}")
    print(f"  lines     {[tuple(row) for row in cone._lineality_lattice_basis().rows()]}")
    print(f"  rays      {[tuple(ray) for ray in cone._engine.rays()]}")
    print(f"  images    {cone._image_rays_modulo_lineality()}")
    print(f"  form      {cone._canonical_form_modulo_lineality()}")
    print(f"  hash      {hash(cone)}")


z2 = Lattices(ZZ)([[1, 0], [0, 1]])
z3 = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

quadrant = z2.reduction_cell(((1, 0), (0, 1)))
narrow = z2.reduction_cell(((1, 0), (-1, 2)))
diagonal = z2.reduction_cell(((1, 1), (1, -1)))
doubled = z2.reduction_cell(((2, 0), (0, 1)))
upper = z2.reduction_cell(((0, 1),))
steeper = z2.reduction_cell(((1, -1),))
mirror = z2.reduction_cell(((-1, -1),))
lower = z2.reduction_cell(((0, -1),))
upper3 = z3.reduction_cell(((0, 1, 0), (0, 0, 1)))
lower3 = z3.reduction_cell(((0, -1, 0), (0, 0, 1)))
wedges = z3.reduction_cell(((1, 0, 0), (0, 1, 0)))
scaled_wedges = z3.reduction_cell(((2, 0, 0), (0, 3, 0)))
swapped_wedges = z3.reduction_cell(((0, 1, 0), (1, 0, 0)))
negative_line = z2.reduction_cell(((-1, 0),))
positive_line = z2.reduction_cell(((1, 0),))

for name, cone in (
    ("quadrant", quadrant), ("narrow", narrow), ("diagonal", diagonal),
    ("doubled", doubled), ("upper", upper), ("steeper", steeper),
    ("mirror", mirror), ("lower", lower), ("upper3", upper3),
    ("lower3", lower3), ("wedges", wedges), ("scaled_wedges", scaled_wedges),
    ("swapped_wedges", swapped_wedges), ("negative_line", negative_line),
    ("positive_line", positive_line),
):
    describe(name, cone)

print("--- equality implies one form, and the hash agrees with equality")
every = [quadrant, narrow, diagonal, doubled, upper, steeper, mirror, lower,
         upper3, lower3, wedges, scaled_wedges, swapped_wedges,
         negative_line, positive_line]
bad = 0
for i, left in enumerate(every):
    for right in every[i:]:
        same = (left == right) is True
        same_form = left._canonical_form_modulo_lineality() == right._canonical_form_modulo_lineality()
        same_hash = hash(left) == hash(right)
        if same != same_form or same != same_hash:
            bad += 1
            print(f"  MISMATCH equal={same} form={same_form} hash={same_hash}: {left} vs {right}")
print(f"pairs checked={len(every) * (len(every) + 1) // 2} mismatches={bad}")

print("--- polytope vertex set read from the engine polyhedron")
lattice = Lattices(ZZ)([[1, 0], [0, 1]])
category = ConvexPolytopes(lattice)
triangle = category(((0, 0), (1, 0), (0, 1)))
relocated = category(((1, 0), (0, 1), (0, 0)))
cut = category.from_halfspaces(((0, (1, 0)), (0, (0, 1)), (1, (-1, -1))))
print("engine vertices", [tuple(vertex) for vertex in cut._engine_polyhedron().vertices()])
print("triangle set", triangle._vertex_coordinate_set())
print("cut set     ", cut._vertex_coordinate_set())
print("equal", triangle == relocated, triangle == cut, "hash equal",
      hash(triangle) == hash(relocated), hash(triangle) == hash(cut))

print("--- one product for the three presentations")
product = Sets().product((triangle, Sets.Δ[1]))
other = category(((0, 0), (2, 0), (0, 1)))
other_product = Sets().product((other, Sets.Δ[1]))
print("factor", product.factor(0) is triangle)
print("triangle", Sets().product((triangle, Sets.Δ[1])) is product)
print("relocated", Sets().product((relocated, Sets.Δ[1])) is product)
print("cut", Sets().product((cut, Sets.Δ[1])) is product)
print("other is not", other_product is not product, other_product.factor(0) is other)
print("five hashes", cardinal(sum(1 for _ in {hash(each) for each in (
    category(((0, 0), (1, 0), (0, 1))),
    category(((0, 0), (2, 0), (0, 1))),
    category(((0, 0), (1, 0), (0, 2))),
    category(((0, 0), (1, 1), (0, 1))),
    category(((0, 0), (1, 0), (1, 1))),
)})))
