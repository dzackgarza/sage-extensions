"""#370 probe J: the orbit counts of the printed (-2) classes of K_J at T_En's cusps 4 and 5."""
import time

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import (  # noqa: E402
    Involutions,
    NamedLattices,
    Sterk,
    ZZ,
)


def gamma_en_2():
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = [
        (left, right)
        for left in labels
        for right in labels
        if left <= right
        and invariant.q(invariant.module_generator(left)) == ZZ.zero()
        and invariant.q(invariant.module_generator(right)) == ZZ.zero()
        and invariant.b(invariant.module_generator(left), invariant.module_generator(right)) == ZZ(2)
    ]
    left, right = marks[0]
    polarization = invariant.module_generator(left) + invariant.module_generator(right)
    return Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()


start = time.time()
gamma = gamma_en_2()
stamp(f"Gamma_En,2 built in {round(time.time() - start, 1)}s")

for number in (4, 5):
    name = f"Sterk_{number}"
    print("=" * 20, name)
    start = time.time()
    image = gamma.isotropic_vector_reduction_image(Sterk.selected_isotropic_vectors()[name])
    reduction = image.reduction()
    stamp(f"  K_J rank {int(reduction.module_rank())} det {reduction.determinant()} in "
          f"{round(time.time() - start, 1)}s")
    roots = tuple(Sterk.cusp_roots_in_TEn(name))
    classes = []
    for root in roots:
        class_ = image.root_class(root)
        if all(class_ != seen for seen in classes):
            classes.append(class_)
    print("  printed roots", len(roots), "distinct classes", len(classes),
          "squares", [reduction.q(class_) for class_ in classes])
    roots_of_the_boundary = [class_ for class_ in classes if reduction.q(class_) == -ZZ(2)]
    print("  roots of K_J", len(roots_of_the_boundary))
    start = time.time()
    stabilizer = tuple(image.subgroup().supergroup().isotropic_stabilizer_generators(image.line()))
    stamp(f"  line stabilizer: {len(stabilizer)} generators in {round(time.time() - start, 1)}s")
    start = time.time()
    orbits = image.root_class_orbits(tuple(roots_of_the_boundary), stabilizer_generators=stabilizer)
    stamp(f"  root_class_orbits: {int(orbits.cardinality())} orbits in {round(time.time() - start, 1)}s")
    for position, orbit in enumerate(orbits):
        print(f"    orbit {position}: {len(tuple(orbit.index_set()))} classes")
stamp("done")
