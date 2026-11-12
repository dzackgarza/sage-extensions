"""#370 probe 1: Gamma_{Co,2} at T_Co's cusps 3-5, the reductions K_I, and their chamber walls."""
import faulthandler
import time

faulthandler.dump_traceback_later(300, repeat=True)
T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import HyperbolicLattices, Lattices, NamedLattices, ZZ  # noqa: E402

L = NamedLattices.Tco
labels = tuple(L.module_generating_set())
A = L.discriminant_group()
og = A.orthogonal_group()
stamp(f"T_Co rebuilt, generators {labels}")

# Gamma_{Co,2}: the #358 construction
c_ep = L.discriminant_class(L.primitive_dual(L.module_generator("ep")))
c_fp = L.discriminant_class(L.primitive_dual(L.module_generator("fp")))
point = frozenset({A.zero(), c_ep, c_fp, c_ep + c_fp})
group = L.Aut()
t = time.time()
gamma = group.discriminant_point_stabilizer(point)
stamp(f"Gamma_Co,2 built in {round(time.time() - t, 1)}s")

# the cusp controlling vectors of card 029J, in T_En's basis (e,f,ep,fp,a1..a8)
cards = {
    3: (0, 0, 1, 1, -2, -3, -4, -6, -5, -4, -3, -2),
    4: (0, 0, 2, 1, -4, -5, -7, -10, -8, -6, -4, -2),
    5: (2, 2, 0, 0, -4, -5, -7, -10, -8, -6, -4, -2),
}
names = ["e", "f", "ep", "fp", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]

for number, coordinates in cards.items():
    ring = L.base_ring()
    coefficients = {}
    if coordinates[0] == coordinates[1]:
        if coordinates[0]:
            coefficients["h"] = ring(coordinates[0])
    else:
        print(f"cusp {number}: the representative pairs with delta, not in T_Co")
        continue
    for name, value in zip(names[2:], coordinates[2:]):
        if value:
            coefficients[name] = ring(value)
    vector = L.linear_combination(coefficients)
    print(
        f"cusp {number}: eta {coordinates} -> T_Co vector q = {vector.q()}",
        "primitive:", vector.is_primitive(),
        "div:", L.div(vector),
    )
    t = time.time()
    image = gamma.isotropic_vector_reduction_image(vector)
    stamp(f"cusp {number}: reduction image built in {round(time.time() - t, 1)}s")
    reduction = image.reduction()
    print("  K_I rank", int(reduction.module_rank()), "det", reduction.determinant(),
          "signature", reduction.signature_pair())
    t = time.time()
    hyperbolic = HyperbolicLattices(ZZ)(reduction)
    chamber = hyperbolic.fundamental_chamber()
    walls = tuple(chamber.wall_roots())
    stamp(f"cusp {number}: chamber with {len(walls)} walls in {round(time.time() - t, 1)}s")
    t = time.time()
    decisions = tuple(image.admits_root(wall) for wall in walls)
    print("  admissible walls:", sum(1 for d in decisions if d), "of", len(decisions),
          "in", round(time.time() - t, 1), "s")
stamp("done")
