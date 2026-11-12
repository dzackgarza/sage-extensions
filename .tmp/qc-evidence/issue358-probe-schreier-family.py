"""#358 probe 6: the line row on Gamma_{Co,2} = rho^{-1}(P) over T_Co, and the index per class."""
import faulthandler
import time

from sage.all import ZZ

faulthandler.dump_traceback_later(2300, exit=True)
T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import NamedLattices  # noqa: E402
from sage.libs.gap.libgap import libgap  # noqa: E402

L = NamedLattices.Tco
A = L.discriminant_group()
og = A.orthogonal_group()
order = int(og.cardinality())
stamp(f"T_Co rank {int(L.module_rank())}, |A| {int(A.cardinality())}, |O(q)| {order}")

labels = tuple(L.module_generating_set())
gens = {label: L.module_generator(label) for label in labels}
h_class = L.discriminant_class(L.primitive_dual(gens["h"]))
c_ep = L.discriminant_class(L.primitive_dual(gens["ep"]))
c_fp = L.discriminant_class(L.primitive_dual(gens["fp"]))
point = frozenset({A.zero(), c_ep, c_fp, c_ep + c_fp})


def span(generators):
    out = {A.zero()}
    for generator in generators:
        out |= {element + generator for element in out}
    return frozenset(out)


A_U2 = span((c_ep, c_fp))
A_E8 = span(tuple(L.discriminant_class(L.primitive_dual(gens[f"a{i}"])) for i in range(1, 9)))
zero_q = A.b(A.zero(), A.zero())
print("A_U2 perp A_E8:", all(A.b(a, b) == zero_q for a in A_U2 for b in A_E8))
print("[h/2]^perp order", sum(1 for c in A.elements() if A.b(c, h_class) == zero_q))
print("summand order product", len(A_U2) * len(A_E8))

first_summand = int(NamedLattices.U_2.discriminant_group().orthogonal_group().cardinality())
second_summand = int(
    (NamedLattices.E8_2 + NamedLattices.Z_2).discriminant_group().orthogonal_group().cardinality()
)
product = first_summand * second_summand
print("|P| = product of the summands:", first_summand, "*", second_summand, "=", product)
stamp("summand orders")

group = L.Aut()
t = time.time()
ambient = tuple(group.group_generators())
stamp(f"O(T_Co) generators: {len(ambient)} in {round(time.time() - t, 1)}s")

t = time.time()
preimage = group.discriminant_point_stabilizer(point)
print("preimage constructed in", round(time.time() - t, 1), "s")
quotient = preimage.finite_character_quotient()
t = time.time()
image_order = quotient.image_order()
print("character image order", image_order, round(time.time() - t, 1), "s")
t = time.time()
subgroup_image_order = quotient.subgroup_image_order()
print("subgroup image order", subgroup_image_order, round(time.time() - t, 1), "s")
t = time.time()
index = quotient.index()
print("index [O(L) : Gamma] =", index, round(time.time() - t, 1), "s")
print("index * product == |O(q)|:", index * product == order, "subgroup image order == product:", subgroup_image_order == product)
stamp("quotient orders")

family = preimage.group_generators()
t = time.time()
count = int(family.cardinality())
print("Schreier family cardinality", count, round(time.time() - t, 1), "s")
print("== letters*index - (index-1):", count == len(ambient) * index - (index - 1))
stamp("family cardinality")

t = time.time()
subfamily = group.discriminant_point_stabilizer_image_generators(point)
print("selected subfamily cardinality", int(subfamily.cardinality()), round(time.time() - t, 1), "s")
rho = preimage.preimage_morphism()
members = tuple(subfamily)
images = tuple(rho(member) for member in members)
t = time.time()
generated = og.subgroup(images, "the image of the selected subfamily")
print("image order of the selected subfamily:", int(generated.cardinality()), round(time.time() - t, 1), "s")
print("equals |P|:", int(generated.cardinality()) == product)
stamp("image generators")

t = time.time()
representatives = preimage.isotropic_orbit_representatives(1)
row_count = int(representatives.cardinality())
print("isotropic_orbit_representatives(1):", row_count, "in", round(time.time() - t, 1), "s")
for position_index in range(row_count):
    subobject = representatives.value(position_index)
    for label in subobject.module_generating_set():
        vector = subobject.inclusion()(subobject.module_generator(label))
        coordinates = vector.to_vector()
        coefficients = {
            str(name): int(coordinates(name))
            for name in L.module_generating_set()
            if int(coordinates(name))
        }
        print(
            "  representative", position_index, coefficients,
            "q", vector.q(), "div", L.div(vector),
            "divided class", L.divided_discriminant_class(vector),
        )
stamp("row")

elements = tuple(A.elements())
position = {element: index + 1 for index, element in enumerate(elements)}
permutations = [
    libgap.PermList([position[g(c)] for c in elements]) for g in tuple(og.group_generators())
]
G = libgap.Group(permutations)
P = libgap.Subgroup(
    G,
    [libgap.PermList([position[rho(member)(c)] for c in elements]) for member in members],
)
print("|P| as a permutation group:", int(libgap.Size(P)), "== product:", int(libgap.Size(P)) == product)
print("P-orbits on the nonzero isotropic classes:")
isotropic = [
    libgap.Set([position[c]])
    for c in A.elements()
    if A.q(c) != A.q(A.zero()) and A.b(c, c) == zero_q
]
print("  isotropic nonzero classes:", len(isotropic))
orbits = libgap.Orbits(P, libgap.Set([next(iter(s)) for s in isotropic]), libgap.OnPoints)
print("  orbit count", int(libgap.Length(orbits)), "sizes", [int(libgap.Length(o)) for o in libgap.AsList(orbits)])
for position_index in range(row_count):
    subobject = representatives.value(position_index)
    label = next(iter(subobject.module_generating_set()))
    vector = subobject.inclusion()(subobject.module_generator(label))
    divided = L.divided_discriminant_class(vector)
    stabilizer = libgap.Stabilizer(G, position[divided], libgap.OnPoints)
    intersection = libgap.Intersection(stabilizer, P)
    print(
        "  class", position_index,
        "|Stab_{O(q)}(c)|", int(libgap.Size(stabilizer)),
        "|rho(Gamma_v)|", int(libgap.Size(intersection)),
        "index", int(libgap.Size(stabilizer)) // int(libgap.Size(intersection)),
    )
stamp("done")
