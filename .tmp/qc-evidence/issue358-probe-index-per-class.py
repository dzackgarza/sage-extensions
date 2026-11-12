"""#358 probe 12: the index per class for the four line orbits returned by the row.

The four vectors are transcribed from the row's own output (p358-p11.log), in the named basis of
T_Co; the divided class each of them produces is printed so the transcription checks itself against
that log line.
"""
import time

from sage.all import ZZ

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import NamedLattices  # noqa: E402
from sage.libs.gap.libgap import libgap  # noqa: E402

L = NamedLattices.Tco
A = L.discriminant_group()
og = A.orthogonal_group()
order = int(og.cardinality())
stamp(f"T_Co rebuilt, |O(q)| = {order}")
ring = L.base_ring()

recorded = [
    ({"ep": -1}, "-[fp]"),
    (
        {
            "h": 44168457980, "ep": 1820311546, "fp": 28029145070, "a1": 30120546496,
            "a2": 74620371507, "a3": 65644225591, "a4": 125373851653, "a5": 93881685920,
            "a6": 49779389922, "a7": 31226948905, "a8": 7801536729,
        },
        "44168457980*[h] + 28029145070*[ep] + 1820311546*[fp] + 5403132599*[a1]"
        " - 23866891361*[a2] + 24205946967*[a3] - 16601420288*[a4] - 12610130265*[a5]"
        " + 25549854981*[a6] - 4872971159*[a7] + 15623875447*[a8]",
    ),
    (
        {
            "h": 4, "ep": -1, "fp": -4, "a1": 2, "a2": 5, "a3": 5, "a4": 7, "a5": 4,
            "a7": 1, "a8": 1,
        },
        "4*[h] - 4*[ep] - [fp] + [a1] - 3*[a2] - [a3] - [a5] + 5*[a6] - [a7] - [a8]",
    ),
    (
        {
            "h": -12563877094386, "ep": 1972188049887, "fp": -2958671514421,
            "a1": -4739366612966, "a2": -11144527454303, "a3": -11048550525707,
            "a4": -22422059246811, "a5": -13569369774452, "a6": -2402950410106,
            "a7": -1502118700382, "a8": -71496532492,
        },
        "",
    ),
]

vectors = []
for coordinates, expected in recorded:
    vector = L.linear_combination({label: ring(value) for label, value in coordinates.items()})
    divided = L.divided_discriminant_class(vector)
    print(
        "reconstructed", sorted(coordinates.items())[:3], "...",
        "q", vector.q(), "div", L.div(vector),
        "divided class", divided,
        "matches the row's line:", expected == "" or expected in repr(divided) or repr(divided) == expected,
    )
    vectors.append((vector, divided))
stamp("vectors reconstructed")

c_ep = L.discriminant_class(L.primitive_dual(L.module_generator("ep")))
c_fp = L.discriminant_class(L.primitive_dual(L.module_generator("fp")))
point = frozenset({A.zero(), c_ep, c_fp, c_ep + c_fp})
t = time.time()
stabilizer = og.stabilizer_of_classes(point)
stamp(f"P built in {round(time.time() - t, 1)}s, |P| = {int(stabilizer.cardinality())}")
stabilizer_generators = tuple(stabilizer.group_generators())

elements = tuple(A.elements())
position = {element: index + 1 for index, element in enumerate(elements)}
t = time.time()
permutations = [
    libgap.PermList([position[g(c)] for c in elements]) for g in tuple(og.group_generators())
]
G = libgap.Group(permutations)
P = libgap.Subgroup(
    G,
    [libgap.PermList([position[g(c)] for c in elements]) for g in stabilizer_generators],
)
print("permutation model built in", round(time.time() - t, 1), "s",
      "|G| == |O(q)|:", int(libgap.Size(G)) == order, "|P| =", int(libgap.Size(P)))
zero = A.zero()
zero_q = A.b(zero, zero)
isotropic = [position[c] for c in A.elements() if A.b(c, c) == zero_q]
orbits = libgap.Orbits(P, libgap.Set(isotropic), libgap.OnPoints)
print("P-orbits on the isotropic classes:", int(libgap.Length(orbits)),
      "sizes", sorted(int(libgap.Length(orbit)) for orbit in libgap.AsList(orbits)))
stamp("permutation model")

for index, (vector, divided) in enumerate(vectors):
    stabilizer_of_class = libgap.Stabilizer(G, position[divided], libgap.OnPoints)
    intersection = libgap.Intersection(stabilizer_of_class, P)
    class_order = int(libgap.Size(stabilizer_of_class))
    image_order = int(libgap.Size(intersection))
    print(
        "  orbit", index,
        "|Stab_{O(q)}(c)|", class_order,
        "|rho(Stab_Gamma(v))|", image_order,
        "index", class_order // image_order,
        "divisible:", class_order % image_order == 0,
    )
stamp("done")
