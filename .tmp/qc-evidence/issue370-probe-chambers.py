"""#370 probe 3: the norms of the chamber walls of K_I at T_Co's cusps (no group needed)."""
import time

from sage_extensions.all import HyperbolicLattices, NamedLattices, ZZ

L = NamedLattices.Tco
ring = L.base_ring()
names = ["e", "f", "ep", "fp", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]
cards = {
    3: (0, 0, 1, 1, -2, -3, -4, -6, -5, -4, -3, -2),
    4: (0, 0, 2, 1, -4, -5, -7, -10, -8, -6, -4, -2),
    5: (2, 2, 0, 0, -4, -5, -7, -10, -8, -6, -4, -2),
}
T0 = time.time()
for number, coordinates in cards.items():
    coefficients = {}
    if coordinates[0] == coordinates[1] and coordinates[0]:
        coefficients["h"] = ring(coordinates[0])
    for name, value in zip(names[2:], coordinates[2:]):
        if value:
            coefficients[name] = ring(value)
    vector = L.linear_combination(coefficients)
    line = L.primitive_isotropic_subobject(vector)
    reduction = line.isotropic_reduction()
    K = reduction.lattice() if hasattr(reduction, "lattice") else None
    print(f"cusp {number}: eta div {L.div(vector)}, reduction rank {int(reduction.module_rank())}")
    hyperbolic = HyperbolicLattices(ZZ)(reduction)
    walls = tuple(hyperbolic.fundamental_chamber().wall_roots())
    norms = [reduction.q(wall) for wall in walls]
    print("   walls", len(walls), "norms", [int(norm) for norm in norms],
          "roots:", sum(1 for norm in norms if int(norm) == -2))
    # the reduction's own (−2)-classes reachable: how many vectors of K of square -2 within a box?
print("elapsed", round(time.time() - T0, 1), "s")
