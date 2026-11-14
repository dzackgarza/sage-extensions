"""#358 probe 9: the line row on Gamma_{Co,2}, the index per class, and the Schreier family's stop."""
import faulthandler
import time

from sage.all import ZZ

faulthandler.dump_traceback_later(240, repeat=True)
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

gens = {label: L.module_generator(label) for label in L.module_generating_set()}
c_ep = L.discriminant_class(L.primitive_dual(gens["ep"]))
c_fp = L.discriminant_class(L.primitive_dual(gens["fp"]))
point = frozenset({A.zero(), c_ep, c_fp, c_ep + c_fp})
first_summand = int(NamedLattices.U_2.discriminant_group().orthogonal_group().cardinality())
second_summand = int(
    (NamedLattices.E8_2 + NamedLattices.Z_2).discriminant_group().orthogonal_group().cardinality()
)
product = first_summand * second_summand
print("|P| =", first_summand, "*", second_summand, "=", product)
stamp("summand orders")

group = L.Aut()
t = time.time()
ambient = tuple(group.group_generators())
stamp(f"O(T_Co) generators: {len(ambient)} in {round(time.time() - t, 1)}s")
t = time.time()
preimage = group.discriminant_point_stabilizer(point)
stamp(f"preimage constructed in {round(time.time() - t, 1)}s")
quotient = preimage.finite_character_quotient()
stamp(f"image order {quotient.image_order()}")
subgroup_image_order = quotient.subgroup_image_order()
stamp(f"subgroup image order {subgroup_image_order} (== |P|: {subgroup_image_order == product})")
index = quotient.index()
stamp(f"index {index} (index * |P| == |O(q)|: {index * product == order})")

# --- the lifts of P's own generators: a small family of Gamma -----------------
t = time.time()
stabilizer_generators = tuple(og.stabilizer_of_classes(point).group_generators())
print("P's generator count", len(stabilizer_generators))
lifts = tuple(group.discriminant_lift(generator) for generator in stabilizer_generators)
print("lifts built in", round(time.time() - t, 1), "s")
print("every lift lies in the preimage:", all(lift in preimage for lift in lifts))
rho = preimage.preimage_morphism()
lift_images = tuple(rho(lift) for lift in lifts)
generated = og.subgroup(lift_images, "the images of the lifts of P's generators")
print("image order of the lifts:", int(generated.cardinality()), "== |P|:", int(generated.cardinality()) == product)
stamp("lifts")

# --- the row ---------------------------------------------------------------
t = time.time()
representatives = preimage.isotropic_orbit_representatives(1)
row_count = int(representatives.cardinality())
stamp(f"isotropic_orbit_representatives(1): {row_count} in {round(time.time() - t, 1)}s")
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

# --- the index per class, in O(q) -----------------------------------------
elements = tuple(A.elements())
position = {element: index + 1 for index, element in enumerate(elements)}
permutations = [
    libgap.PermList([position[g(c)] for c in elements]) for g in tuple(og.group_generators())
]
G = libgap.Group(permutations)
P = libgap.Subgroup(
    G, [libgap.PermList([position[rho(lift)(c)] for c in elements]) for lift in lifts]
)
print("|P| as a permutation group:", int(libgap.Size(P)), "== product:", int(libgap.Size(P)) == product)
zero = A.zero()
zero_q = A.b(zero, zero)
isotropic_classes = [
    position[c] for c in A.elements()
    if A.b(c, c) == zero_q
]
print("isotropic classes (including zero):", len(isotropic_classes))
orbits = libgap.Orbits(P, libgap.Set(isotropic_classes), libgap.OnPoints)
print("P-orbits on the isotropic classes:", int(libgap.Length(orbits)),
      "sizes", [int(libgap.Length(orbit)) for orbit in libgap.AsList(orbits)])
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
stamp("index per class")

# --- last: the Schreier family's count, which is where the family's realization stops
family = preimage.group_generators()
t = time.time()
try:
    count = int(family.cardinality())
    stamp(f"Schreier family cardinality {count} in {round(time.time() - t, 1)}s")
    print("== letters*index - (index-1):", count == len(ambient) * index - (index - 1))
except MemoryError as error:
    stamp(f"family cardinality raised MemoryError: {error}")
stamp("done")
