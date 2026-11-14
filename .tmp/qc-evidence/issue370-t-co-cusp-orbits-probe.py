"""#370 probe I: the orbit counts at T_Co's cusps 4 and 5, with the lanterns the test asserts.

Prints, at each cusp: K_I, the transported printed roots, the classes in T_Co, the root classes, and
the orbits of `root_class_orbits` with their sizes and transporters.
"""
import time

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import Lattices, NamedLattices, Sterk, ZZ  # noqa: E402

Tco = NamedLattices.Tco
TEn = NamedLattices.TEn


def gamma_co_2():
    lattice = Tco
    form = lattice.discriminant_group()
    first = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("ep")))
    second = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("fp")))
    point = frozenset({form.zero(), first, second, first + second})
    return lattice.Aut().discriminant_point_stabilizer(point)


start = time.time()
gamma = gamma_co_2()
stamp(f"Gamma_Co,2 built in {round(time.time() - start, 1)}s")

ring = Tco.base_ring()
labels_ten = tuple(TEn.module_generating_set())
basis = {label: TEn.module_generator(label) for label in labels_ten}
delta = basis["e"] - basis["f"]

for number in (4, 5):
    print("=" * 20, f"cusp {number}")
    cusp = Sterk.selected_isotropic_vectors()[f"Sterk_{number}"]
    coordinates = cusp.to_vector()
    given = {label: int(coordinates(label)) for label in labels_ten}
    coefficients = {"h": ring(given["e"])} if given["e"] else {}
    for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
        if given[label]:
            coefficients[label] = ring(given[label])
    eta = Tco.linear_combination(coefficients)
    image = gamma.isotropic_vector_reduction_image(eta)
    reduction = image.reduction()
    stamp(f"  K_I rank {int(reduction.module_rank())} det {reduction.determinant()} "
          f"signature {tuple(map(int, reduction.signature_pair()))}")
    roots = tuple(Sterk.cusp_roots_in_TEn(f"Sterk_{number}"))
    inside = [root for root in roots if TEn.b(root, delta) == ZZ.zero()]
    print("  printed roots", len(roots), "in T_Co", len(inside),
          "squares in T_En", [TEn.q(root) for root in inside])
    classes = []
    for root in inside:
        transported = Tco.linear_combination(
            {
                label: ring(int(root.to_vector()(label)))
                for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9))
                if int(root.to_vector()(label))
            }
            | ({"h": ring(int(root.to_vector()("e")))} if int(root.to_vector()("e")) else {})
        )
        classes.append(image.root_class(transported))
    print("  classes", len(classes), "squares in K_I", [reduction.q(class_) for class_ in classes])
    roots_of_the_boundary = [class_ for class_ in classes if reduction.q(class_) == -ZZ(2)]
    print("  root classes", len(roots_of_the_boundary))
    start = time.time()
    stabilizer = tuple(image.subgroup().supergroup().isotropic_stabilizer_generators(image.line()))
    stamp(f"  line stabilizer: {len(stabilizer)} generators in {round(time.time() - start, 1)}s")
    start = time.time()
    orbits = image.root_class_orbits(tuple(roots_of_the_boundary), stabilizer_generators=stabilizer)
    stamp(f"  root_class_orbits: {int(orbits.cardinality())} orbits in {round(time.time() - start, 1)}s")
    for position, orbit in enumerate(orbits):
        members = tuple(orbit.index_set())
        print(f"    orbit {position}: {len(members)} classes, squares",
              [reduction.q(member) for member in members])
stamp("done")
