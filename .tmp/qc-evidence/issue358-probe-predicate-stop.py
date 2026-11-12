"""#358 probe 2: the point, |P| two ways, the preimage's generators, and the line row on T_Co."""
import faulthandler
import time

from sage.all import ZZ

faulthandler.dump_traceback_later(2300, exit=True)
T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import NamedLattices  # noqa: E402

L = NamedLattices.Tco
A = L.discriminant_group()
stamp(f"built T_Co: rank {int(L.module_rank())}, |A| {int(A.cardinality())}")

og = A.orthogonal_group()
order = int(og.cardinality())
stamp(f"|O(q)| = {order}")
part = A.primary_part(2)
print("two-primary invariants", part.invariants())
print("orthogonal group type", type(og).__name__)

# --- the point: A_{U(2)} inside A_{T_Co}, and the two summands ----------------
labels = tuple(L.module_generating_set())
gens = {label: L.module_generator(label) for label in labels}
h, ep, fp = gens["h"], gens["ep"], gens["fp"]


def disc(vector):
    return L.discriminant_class(L.primitive_dual(vector))


h_class, c_ep, c_fp = disc(h), disc(ep), disc(fp)


def span(generators):
    out = {A.zero()}
    for generator in generators:
        out |= {element + generator for element in out}
    return frozenset(out)


A_U2 = span((c_ep, c_fp))
A_E8 = span(tuple(disc(gens[f"a{index}"]) for index in range(1, 9)))
point = A_U2
zero = A.zero()
zero_q = A.b(zero, zero)
print("q([h/2])", A.q(h_class), "b([h/2],[h/2])", A.b(h_class, h_class))
print("|A_U2|", len(A_U2), "|A_E8|", len(A_E8), "q(A_U2)", sorted({str(A.q(c)) for c in A_U2}))
print("A_U2 perp A_E8:", all(A.b(a, b) == zero_q for a in A_U2 for b in A_E8))
print("A_U2 perp [h/2]:", all(A.b(a, h_class) == zero_q for a in A_U2))
print("[h/2]^perp order", sum(1 for c in A.elements() if A.b(c, h_class) == zero_q))
print("summand product order", len(A_U2) * len(A_E8))
stamp("point built")

# --- |P| two ways -----------------------------------------------------------
o_u2 = int(NamedLattices.U_2.discriminant_group().orthogonal_group().cardinality())
o_rest = int(
    (NamedLattices.E8_2 + NamedLattices.Z_2).discriminant_group().orthogonal_group().cardinality()
)
product = o_u2 * o_rest
print("|O(q_{U(2)})|", o_u2, "|O(q_{E8(-2) + <2>})|", o_rest, "product", product)

from sage.libs.gap.libgap import libgap  # noqa: E402

elements = tuple(A.elements())
position = {element: index + 1 for index, element in enumerate(elements)}
owned = tuple(og.group_generators())
permutations = [libgap.PermList([position[g(c)] for c in elements]) for g in owned]
G = libgap.Group(permutations)
print("|G| == |O(q)|:", int(libgap.Size(G)) == order)
class_point = libgap.Set(sorted(position[c] for c in point))
orbit_size = int(libgap.Length(libgap.Orbit(G, class_point, libgap.OnSets)))
stab_order = int(libgap.Size(libgap.Stabilizer(G, class_point, libgap.OnSets)))
print("orbit", orbit_size, "setwise stabilizer", stab_order)
print("product * orbit == |O(q)|:", product * orbit_size == order)
print("stabilizer == product:", stab_order == product)
stamp("|P| two ways")

# --- the public call: the preimage and its image generators ------------------
group = L.Aut()
t = time.time()
ambient = tuple(group.group_generators())
stamp(f"O(T_Co) group generators: {len(ambient)} in {round(time.time() - t, 1)}s")

t = time.time()
point_orbit = group.discriminant_point_orbit(point)
print("public orbit cardinality", int(point_orbit.cardinality()), round(time.time() - t, 1), "s")
stamp("discriminant_point_orbit")

t = time.time()
preimage = group.discriminant_point_stabilizer(point)
print("preimage constructed in", round(time.time() - t, 1), "s")
quotient = preimage.finite_character_quotient()
print("quotient index", quotient.index(), "image order", quotient.image_order(), "subgroup image order", quotient.subgroup_image_order())
stamp("discriminant_point_stabilizer")

family = preimage.group_generators()
t = time.time()
print("Schreier family cardinality", int(family.cardinality()), round(time.time() - t, 1), "s")
stamp("family cardinality")

t = time.time()
subfamily = group.discriminant_point_stabilizer_image_generators(point)
print("selected subfamily cardinality", int(subfamily.cardinality()), round(time.time() - t, 1), "s")
rho = preimage.preimage_morphism()
members = tuple(subfamily)
images = tuple(rho(member) for member in members)
generated = og.subgroup(images, "the image of the selected subfamily")
print("image order of the selected subfamily:", int(generated.cardinality()))
print("equals |P|:", int(generated.cardinality()) == product)
stamp("image generators")

# --- the row ---------------------------------------------------------------
t = time.time()
representatives = preimage.isotropic_orbit_representatives(1)
count = int(representatives.cardinality())
print("isotropic_orbit_representatives(1):", count, "in", round(time.time() - t, 1), "s")
for position_index in range(count):
    subobject = representatives.value(position_index)
    for label in subobject.module_generating_set():
        vector = subobject.inclusion()(subobject.module_generator(label))
        coordinates = vector.to_vector()
        coefficients = {
            str(name): int(coordinates(name))
            for name in L.module_generating_set()
            if int(coordinates(name))
        }
        divided = L.divided_discriminant_class(vector)
        print(
            "  representative", position_index, "vector", coefficients,
            "q", vector.q(), "div", L.div(vector), "divided class", divided,
        )
stamp("row")

# --- the index per class, in O(q) -----------------------------------------
P = libgap.Subgroup(G, [libgap.PermList([position[rho(member)(c)] for c in elements]) for member in members])
print("|P| as a permutation group:", int(libgap.Size(P)), "== product:", int(libgap.Size(P)) == product)
for position_index in range(count):
    subobject = representatives.value(position_index)
    label = next(iter(subobject.module_generating_set()))
    vector = subobject.inclusion()(subobject.module_generator(label))
    divided = L.divided_discriminant_class(vector)
    stabilizer = libgap.Stabilizer(G, position[divided], libgap.OnPoints)
    intersection = libgap.Intersection(stabilizer, P)
    print(
        "  class", position_index, "|Stab_{O(q)}(c)|", int(libgap.Size(stabilizer)),
        "|rho(Gamma_v)|", int(libgap.Size(intersection)),
        "index", int(libgap.Size(stabilizer)) // int(libgap.Size(intersection)),
    )
stamp("done")
