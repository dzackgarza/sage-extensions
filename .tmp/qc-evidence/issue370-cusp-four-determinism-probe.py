"""#370 probe: T_Co's cusp 4 through the printed transcription, and its determinism.

Prints the eleven walls, the classes of K_I they give, the single root class and its orbit with the
transporter, and the whole coordinate list, so that two runs can be compared line by line.  This is
the probe `results/issue370-the-coble-root-orbits.md` §4 cites: at the card's cusp vector there is no
embedding choice left, so every number here is the same in every process.
"""
import time

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import Lattices, NamedLattices, Sterk, ZZ  # noqa: E402

Tco = NamedLattices.Tco
TEn = NamedLattices.TEn


def gamma_co_2():
    r"""`Gamma_{Co,2} = R_{Gamma_{En,2}}` on `T_Co`, by #358's construction."""
    lattice = Tco
    form = lattice.discriminant_group()
    first = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("ep")))
    second = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("fp")))
    point = frozenset({form.zero(), first, second, first + second})
    return lattice.Aut().discriminant_point_stabilizer(point)


print("the eleven printed walls of Fig. 10, in T_En coordinates")
for wall in Sterk.cusp_roots_in_TEn("Sterk_4"):
    print(" ", [int(wall.to_vector()(label)) for label in TEn.module_generating_set()],
          "square", TEn.q(wall))
print("the cusp vector of (4.3.8):",
      [int(Sterk.sterk4_cusp_vector().to_vector()(label))
       for label in TEn.module_generating_set()],
      "square", TEn.q(Sterk.sterk4_cusp_vector()))
print("(4.2.3)'s vector for the same cusp:",
      [int(Sterk.selected_isotropic_vectors()["Sterk_4"].to_vector()(label))
       for label in TEn.module_generating_set()])

start = time.time()
gamma = gamma_co_2()
stamp(f"Gamma_Co,2 built in {round(time.time() - start, 1)}s")

ring = Tco.base_ring()
labels = tuple(TEn.module_generating_set())
basis = {label: TEn.module_generator(label) for label in labels}
delta = basis["e"] - basis["f"]

cusp = Sterk.sterk4_cusp_vector()
given = {label: int(cusp.to_vector()(label)) for label in labels}
assert given["e"] == given["f"]
coefficients = {"h": ring(given["e"])} if given["e"] else {}
for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
    if given[label]:
        coefficients[label] = ring(given[label])
eta = Tco.linear_combination(coefficients)
image = gamma.isotropic_vector_reduction_image(eta)
reduction = image.reduction()
stamp(f"cusp 4: K_I rank {int(reduction.module_rank())} det {reduction.determinant()} "
      f"signature {tuple(map(int, reduction.signature_pair()))}")

walls = tuple(Sterk.cusp_roots_in_TEn("Sterk_4"))
inside = [wall for wall in walls if TEn.b(wall, delta) == ZZ.zero()]
print("printed walls", len(walls), "in T_Co", len(inside))
classes = []
for wall in inside:
    coordinates = wall.to_vector()
    coefficients = {
        label: ring(int(coordinates(label)))
        for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9))
        if int(coordinates(label))
    }
    alpha = int(coordinates("e"))
    if alpha:
        coefficients["h"] = ring(alpha)
    class_ = image.root_class(Tco.linear_combination(coefficients))
    print("   class",
          [int(class_.to_vector()(label)) for label in reduction.module_generating_set()],
          "square", reduction.q(class_))
    if all(class_ != seen for seen in classes):
        classes.append(class_)
roots_of_the_boundary = [class_ for class_ in classes if reduction.q(class_) == -ZZ(2)]
print("roots of K_I", len(roots_of_the_boundary))

start = time.time()
stabilizer = tuple(image.subgroup().supergroup().isotropic_stabilizer_generators(image.line()))
stamp(f"line stabilizer: {len(stabilizer)} generators in {round(time.time() - start, 1)}s")
start = time.time()
orbits = image.root_class_orbits(tuple(roots_of_the_boundary), stabilizer_generators=stabilizer)
stamp(f"root_class_orbits: {int(orbits.cardinality())} orbits in {round(time.time() - start, 1)}s")
for position, orbit in enumerate(orbits):
    members = tuple(orbit.index_set())
    print(f"  orbit {position}: {len(members)} classes",
          [[int(member.to_vector()(label)) for label in reduction.module_generating_set()]
           for member in members])
    for member in members:
        transporter = orbit.value(member)
        print("    transporter of",
              [int(member.to_vector()(label)) for label in reduction.module_generating_set()],
              "carries the representative to",
              [int(transporter(members[0]).to_vector()(label))
               for label in reduction.module_generating_set()])
stamp("done")
