"""#370 probe 5: the stabilizer's generators at a T_Co cusp, and the reduction images certified in G_v."""
import faulthandler
import time

faulthandler.dump_traceback_later(300, repeat=True)
T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import NamedLattices, Sterk, ZZ  # noqa: E402

L = NamedLattices.Tco
ring = L.base_ring()
A = L.discriminant_group()
c_ep = L.discriminant_class(L.primitive_dual(L.module_generator("ep")))
c_fp = L.discriminant_class(L.primitive_dual(L.module_generator("fp")))
point = frozenset({A.zero(), c_ep, c_fp, c_ep + c_fp})
t = time.time()
gamma = L.Aut().discriminant_point_stabilizer(point)
stamp(f"Gamma_Co,2 built in {round(time.time() - t, 1)}s")

names = ["e", "f", "ep", "fp", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]
coordinates = (0, 0, 1, 1, -2, -3, -4, -6, -5, -4, -3, -2)
coefficients = {}
for name, value in zip(names[2:], coordinates[2:]):
    if value:
        coefficients[name] = ring(value)
eta = L.linear_combination(coefficients)
image = gamma.isotropic_vector_reduction_image(eta)
reduction = image.reduction()
stamp(f"cusp 3 reduction: rank {int(reduction.module_rank())}, det {reduction.determinant()}")

t = time.time()
stabilizer = gamma.supergroup().isotropic_stabilizer_generators(image.line())
stabilizer = tuple(stabilizer)
stamp(f"line stabilizer generators: {len(stabilizer)} in {round(time.time() - t, 1)}s")

t = time.time()
certified = []
for generator in stabilizer:
    if generator(image.vector()) != image.vector():
        continue
    reduced = image.reduction_image(generator)
    if image.contains(reduced, lift=generator):
        certified.append((generator, reduced))
stamp(f"certified in G_v: {len(certified)} of {len(stabilizer)} in {round(time.time() - t, 1)}s")
print("kernel discriminant image trivial:", image.kernel_discriminant_image_is_trivial())

# the printed T_Co roots at this cusp: Sterk_3's roots that are delta-orthogonal and of square -2
TEn = NamedLattices.TEn
engen = {label: TEn.module_generator(label) for label in TEn.module_generating_set()}
delta = engen["e"] - engen["f"]
roots = tuple(Sterk.sterks_in_TEn()["Sterk_3"])
inside = [root for root in roots if TEn.b(root, delta) == ZZ.zero()]
print("Sterk_3 printed roots in T_Co:", len(inside),
      "squares:", [int(TEn.q(root)) for root in inside])
neg_two = [root for root in inside if int(TEn.q(root)) == -2]
print("of square -2:", len(neg_two))
stamp("roots identified")
