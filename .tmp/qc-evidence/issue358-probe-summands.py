"""#358 probe 1: T_Co's discriminant data, |O(q)|, the point of A_{U(2)}, and |P| two ways."""
import time
from sage.all import ZZ

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import NamedLattices  # noqa: E402

stamp("imported")
L = NamedLattices.Tco
rank = int(L.module_rank())
gram = L.gram_tensor()
print("rank", rank)
print("gram", [[int(gram[i, j]) for j in range(rank)] for i in range(rank)])
print("det", L.determinant() if hasattr(L, "determinant") else "n/a")
print("generators", L.module_generating_set())
A = L.discriminant_group()
n_classes = int(A.cardinality())
print("|A|", n_classes)

stamp("A built")
og = A.orthogonal_group()
t = time.time()
order = int(og.cardinality())
print("|O(q)| =", order, "in", round(time.time() - t, 2), "s")
stamp("|O(q)| done")

from sage_extensions.categories.group.groups import _gap_model  # noqa: E402

engine = _gap_model(og)
print("engine type", type(engine).__name__)
try:
    print("GAP HasSize", bool(__import__("sage.libs.gap.libgap", fromlist=["libgap"]).libgap.eval("HasSize")(engine)))
except Exception as error:  # noqa: BLE001
    print("HasSize read failed:", type(error).__name__, error)

# --- the three summands of A_{T_Co} from the named generators -----------------
labels = tuple(L.module_generating_set())
print("labels", labels)
gens = {label: L.module_generator(label) for label in labels}
h, ep, fp = gens["h"], gens["ep"], gens["fp"]


def disc(vector):
    return L.discriminant_class(L.primitive_dual(vector))


h_class = disc(h)
print("[h/2] =", h_class, "q =", A.q(h_class), "b(self,self) =", A.b(h_class, h_class))
c_ep, c_fp = disc(ep), disc(fp)
stamp("classes built")


def span(generators):
    out = {A.zero()}
    for generator in generators:
        out |= {element + generator for element in out}
    return frozenset(out)


A_U2 = span((c_ep, c_fp))
A_E8 = span(tuple(disc(gens[f"a{index}"]) for index in range(1, 9)))
A_h = frozenset({A.zero(), h_class})
print("|A_U2|", len(A_U2), "|A_E8|", len(A_E8), "|A_h|", len(A_h))
print("A_U2 q values", sorted({str(A.q(c)) for c in A_U2}))
print("A_U2 b(c_ep,c_fp)", A.b(c_ep, c_fp))

point = A_U2
print("point size", len(point))

direct = frozenset({a + b + c for a in A_U2 for b in A_E8 for c in A_h})
print("A_U2 + A_E8 + A_h has order", len(direct), "equals A:", direct == frozenset(A.elements()))

# [h/2]^perp: classes pairing to zero with h_class
zero_q = A.b(A.zero(), A.zero())
perp = frozenset(c for c in A.elements() if A.b(c, h_class) == zero_q)
print("|[h/2]^perp|", len(perp))
print("[h/2]^perp == A_U2 + A_E8:", perp == frozenset({a + b for a in A_U2 for b in A_E8}))
# the radical of [h/2]^perp is <[h/2]>
t = time.time()
radical = frozenset(c for c in perp if all(A.b(c, d) == zero_q for d in perp))
print("radical of [h/2]^perp", len(radical), "is <[h/2]>:", radical == A_h, round(time.time() - t, 2), "s")
# A_E8 is the radical's perp inside [h/2]^perp
inner = frozenset(c for c in perp if all(A.b(c, d) == zero_q for d in radical))
print("radical^perp cap [h/2]^perp == A_U2 + A_E8:", inner == perp)

stamp("summands verified")

# --- |P| from the summands ---------------------------------------------------
t = time.time()
o_u2 = int(NamedLattices.U_2.discriminant_group().orthogonal_group().cardinality())
print("|O(q_{U(2)})| =", o_u2, round(time.time() - t, 2), "s")
t = time.time()
E8_plus_2 = NamedLattices.E8_2 + NamedLattices.Z_2
print("E8_2 + Z_2 rank", int(E8_plus_2.module_rank()))
o_rest = int(E8_plus_2.discriminant_group().orthogonal_group().cardinality())
print("|O(q_{E8(-2) + <2>})| =", o_rest, round(time.time() - t, 2), "s")
product = o_u2 * o_rest
print("product", product, "|O(q)| / product =", order // product, "remainder", order % product)

# --- the orbit of A_U2 under O(q), read as permutations of the classes -------
from sage.libs.gap.libgap import libgap  # noqa: E402

elements = tuple(A.elements())
position = {element: index + 1 for index, element in enumerate(elements)}
t = time.time()
owned_generators = tuple(og.group_generators())
print("O(q) generator count from the owned group", len(owned_generators), round(time.time() - t, 2), "s")
t = time.time()
permutations = [libgap.PermList([position[g(c)] for c in elements]) for g in owned_generators]
print("permutations built in", round(time.time() - t, 2), "s")
G = libgap.Group(permutations)
t = time.time()
gap_order = int(libgap.Size(G))
print("|G| =", gap_order, "== |O(q)|:", gap_order == order, round(time.time() - t, 2), "s")

mask_point = libgap.Set(sorted(position[c] for c in point))
t = time.time()
orbit = libgap.Orbit(G, mask_point, libgap.OnSets)
orbit_size = int(libgap.Length(orbit))
print("orbit size of A_U2 under O(q):", orbit_size, round(time.time() - t, 2), "s")
t = time.time()
stab = libgap.Stabilizer(G, mask_point, libgap.OnSets)
stab_order = int(libgap.Size(stab))
print("|Stab_{O(q)}(A_U2)| =", stab_order, round(time.time() - t, 2), "s")
print("orbit * stabilizer == |O(q)|:", orbit_size * stab_order == order)
print("product * orbit == |O(q)|:", product * orbit_size == order)
print("stabilizer == product:", stab_order == product)
stamp("done")
