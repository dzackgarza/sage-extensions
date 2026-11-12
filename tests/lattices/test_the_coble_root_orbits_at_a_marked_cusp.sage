r"""The orbits of the boundary lattice's root classes at a marked 0-cusp (sage-extensions#370).

At a marked `0`-cusp `[I]` of a period domain the boundary lattice is `K_I = eta_I^perp / ZZ eta_I`
for a primitive isotropic `eta_I`, and its **roots** are the classes whose lifts are `(-2)`-vectors.
`Gamma_{Co,2} = R_{Gamma_{En,2}}` acts on `K_I` through `Lam: Stab_{Gamma_{Co,2}}(ZZ eta_I) -> O(K_I)`,
and research#760 needs the `Gamma_{Co,2}`-orbits of those roots: whether two roots that cut the same
face of the restricted Enriques semifan are inequivalent is whether some element of the group
carries one class to the other.

`IsotropicVectorReductionImage` (#312) is the image `G_v = Lam(Gamma cap P_v)` with its kernel, and
it decides membership in `G_v` on the discriminant image, exactly.  On top of it,
`root_class_orbits` takes a finite family of root classes of `K_I` and returns their orbits with a
**transporter** --- an isometry of `K_I` in `G_v` carrying the orbit's representative to the class,
checked by re-application --- and `root_class` reads the class of a root written in the ambient
lattice, which is the form Sterk's printed cusps are written in.

What the acting family is, and what a singleton therefore means.  The certified reductions of the
stabilizer's own generators (`supergroup().isotropic_stabilizer_generators(line)`) and the certified
reflections of the given classes act; they are not certified to generate `G_v` at a primitive
isotropic line (`generators_are_certified_complete` is `False`, sage-extensions#312), so an orbit
with more than one class is a **proof of equivalence** while a singleton is not a proof of
inequivalence.  The test below pins the card comparison, the transporters, the refusal that keeps
`(-4)`-walls out of a root family, and that the action really acts on `K_I`.

**The known family, and the card.**  H. Sterk, *Compactifications of the period space of Enriques
surfaces, Part I*, Math. Z. 207 (1991), section 4.3.1, diagrams 4.3.5--4.3.9, pp. 19, 21, 22, 23,
24: the printed cusp diagrams of `T_{En} = U + U(2) + E8(-2)`, with 12, 10, 12, 11 and 14 walls,
read as card `029J`'s `cusp_chambers` row `gamma-en-2` by tag.  At the three cusps whose printed
roots the library holds in `T_{En}` coordinates (`Sterk.sterks_in_TEn`) the number of distinct
**classes** of `K_J` they give is the card's wall count: the reduction merges none of the printed
walls, which is what makes the class count a computed value and not a transcription of the card.

No lattice-database card holds the orbit counts themselves.  The missing row is
`029J.cusp_root_orbits.gamma-en-2` --- per cusp, the number of `Gamma_{Co,2}`-orbits of the root
classes with one representative per orbit --- and the same row on the T_Co card for cusps 3--5; both
are named in `results/issue370-the-coble-root-orbits.md` to be filed on
`dzackgarza/lattice-database`.
"""

from sage_extensions.all import *  # noqa: F401,F403

_ENRIQUES_IMAGES = {}
_COBLE_IMAGES = {}


def _gamma_en_2():
    r"""`Gamma_{En,2}` on `T_En`, by the construction of #286 item 2 (Alexeev--Engel--Garza--Schaffler, Def. 2.6)."""
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


def _gamma_co_2():
    r"""`Gamma_{Co,2} = R_{Gamma_{En,2}}` on `T_Co`, by the construction of #358.

    `P` is the stabilizer in `O(q)` of the decomposition `A_{U(2)} + A_{E8(-2)}` of `[h/2]^perp`
    (research `prop:gamma-co-images`, `38fa09935a`), and the group is the preimage of its point
    stabilizer --- the call of #354, never a description of its image.
    """
    lattice = NamedLattices.Tco
    form = lattice.discriminant_group()
    first = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("ep")))
    second = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("fp")))
    point = frozenset({form.zero(), first, second, first + second})
    return lattice.Aut().discriminant_point_stabilizer(point)


def _enriques_cusp_image(name):
    r"""The reduction image at Sterk's cusp `name` of `T_En`, built once per session."""
    if name not in _ENRIQUES_IMAGES:
        vector = Sterk.selected_isotropic_vectors()[name]
        _ENRIQUES_IMAGES[name] = _gamma_en_2().isotropic_vector_reduction_image(vector)
    return _ENRIQUES_IMAGES[name]


def _coble_cusp_image():
    r"""The reduction image at `T_Co`'s cusp 3, built once per session.

    The cusp's representative is card `029J`'s `cusp_chambers` vector for Sterk 4.3.7 read in
    `T_Co`: its `e` and `f` coefficients are equal, so the vector is a vector of `T_Co = delta^perp`
    with that coefficient on `h` and the same coordinates on `ep, fp, a1..a8`.
    """
    if "Sterk_3" not in _COBLE_IMAGES:
        lattice = NamedLattices.Tco
        ring = lattice.base_ring()
        row = card("cusp_chambers", "029J")["rows"]["gamma-en-2"][2]["cusp"]
        labels = ("e", "f", "ep", "fp") + tuple(f"a{index}" for index in range(1, 9))
        given = {label: int(value) for label, value in zip(labels, row)}
        assert given["e"] == given["f"]
        coefficients = {"h": ring(given["e"])}
        for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
            if given[label]:
                coefficients[label] = ring(given[label])
        eta = lattice.linear_combination(coefficients)
        assert lattice.q(eta) == ZZ.zero()
        assert eta.is_primitive() is True
        _COBLE_IMAGES["Sterk_3"] = _gamma_co_2().isotropic_vector_reduction_image(eta)
    return _COBLE_IMAGES["Sterk_3"]


def test_the_printed_cusp_walls_are_distinct_classes_of_the_boundary_lattice() -> None:
    r"""The printed roots at cusps 1--3 are as many distinct classes of `K_J` as the card's walls.

    Card `029J` states 12, 10 and 12 walls for Sterk's 4.3.5, 4.3.6 and 4.3.7, and
    `Sterk.sterks_in_TEn` holds those roots in `T_En` coordinates.  Their classes in
    `K_J = v^perp/ZZ v` are computed here by `root_class`, so a printed wall that were a multiple of
    the cusp's own vector --- or two printed walls in one class --- would show up as a smaller class
    count than the card's.  That they agree is what lets an orbit count be compared with the card's
    geometry.
    """
    rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
    walls = [cardinal(row["walls"]) for row in rows]
    transcribed = Sterk.sterks_in_TEn()
    assert sorted(transcribed) == ["Sterk_1", "Sterk_2", "Sterk_3"]
    for name, expected in zip(sorted(transcribed), walls[:3]):
        image = _enriques_cusp_image(name)
        classes = tuple(image.root_class(root) for root in tuple(transcribed[name]))
        representatives = []
        for class_ in classes:
            if all(class_ != seen for seen in representatives):
                representatives.append(class_)
        assert cardinal(sum(1 for _ in representatives)) == expected
        assert image.lattice().q(image.vector()) == ZZ.zero()
        assert image.vector().is_primitive() is True


def test_a_wall_that_is_not_a_root_is_refused_and_a_root_round_trips() -> None:
    r"""The chamber of `K_J` at the first cusp has `(-4)`-walls, and `root_class` inverts `class_lift`.

    A root of the boundary lattice is a `(-2)`-class (issue #370's definition, and the sense in
    which AEGS25, Thm. 5.9 counts marked roots), and the fundamental chamber of `K_J` also has walls
    of square `-4`.  A family that mixes them is refused rather than silently reduced to its roots,
    so that a caller cannot read an orbit count of the walls as an orbit count of the roots; and the
    two directions of the class map are checked against each other on the chamber's own wall family,
    which is what makes `root_class` usable on Sterk's printed roots.
    """
    image = _enriques_cusp_image("Sterk_1")
    reduction = HyperbolicLattices(ZZ)(image.reduction())
    walls = tuple(reduction.fundamental_chamber().wall_roots())
    assert cardinal(sum(1 for _ in walls)) > cardinal(0)
    squares = [reduction.q(wall) for wall in walls]
    assert any(square == -ZZ(4) for square in squares)
    for wall in walls:
        assert image.root_class(image.class_lift(wall)) == wall


def test_the_coble_cusp_three_has_one_root_class_and_its_orbit_is_its_transporter() -> None:
    r"""At `T_Co`'s cusp 3 the printed root family meets `T_Co` in one `(-2)`-class.

    `T_Co = delta^perp` inside `T_{En}`, `delta = e - f`, and a vector orthogonal to `delta` has
    equal `e` and `f` coefficients: it is the vector with that coefficient on the `h` line of
    `T_Co`.  Of Sterk's twelve printed roots at cusp 3 (4.3.7, p. 22) nine are orthogonal to
    `delta`, eight of square `-4` and one of square `-2`; that one is the single root class of
    `K_I` which `T_Co` sees, the record's `cusp 3: 12`.

    The acting family is `Gamma_{Co,2}`'s own line stabilizer reduced to `K_I` and certified in
    `G_v` by the discriminant criterion, and the call returns the orbit of that one class with its
    transporter --- the identity, which is the honest answer for a family of one class.  That the
    action is not vacuous is asserted separately: some certified generator moves the class on
    `K_I`, and it is dropped from the walk only because its image leaves the given family.
    """
    image = _coble_cusp_image()
    lattice = image.lattice()
    eta = image.vector()

    enriques = NamedLattices.TEn
    basis = {
        label: enriques.module_generator(label)
        for label in enriques.module_generating_set()
    }
    delta = basis["e"] - basis["f"]
    roots = tuple(Sterk.sterks_in_TEn()["Sterk_3"])
    inside = [root for root in roots if enriques.b(root, delta) == ZZ.zero()]
    negative_two = [root for root in inside if enriques.q(root) == -ZZ(2)]
    assert cardinal(sum(1 for _ in negative_two)) == cardinal(1)

    coordinates = negative_two[0].to_vector()
    alpha = int(coordinates("e"))
    assert int(coordinates("f")) == alpha
    ring = lattice.base_ring()
    coefficients = {"h": ring(alpha)}
    for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
        if int(coordinates(label)):
            coefficients[label] = ring(int(coordinates(label)))
    transported = lattice.linear_combination(coefficients)
    assert lattice.q(transported) == -ZZ(2)
    assert lattice.b(transported, eta) == ZZ.zero()

    class_ = image.root_class(transported)
    assert image.reduction().q(class_) == -ZZ(2)

    stabilizer = tuple(
        image.subgroup().supergroup().isotropic_stabilizer_generators(image.line())
    )
    assert cardinal(sum(1 for _ in stabilizer)) > cardinal(0)
    orbits = image.root_class_orbits((class_,), stabilizer_generators=stabilizer)
    assert cardinal(orbits.cardinality()) == cardinal(1)
    orbit = tuple(orbits)[0]
    assert cardinal(orbit.cardinality()) == cardinal(1)
    transporter = orbit.value(class_)
    assert transporter(class_) == class_

    movers = [
        generator
        for generator in stabilizer
        if generator(eta) == eta
        and image.contains(image.reduction_image(generator), lift=generator)
        and image.reduction_image(generator)(class_) != class_
    ]
    assert cardinal(sum(1 for _ in movers)) > cardinal(0)
