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
read as card `029J`'s `cusp_chambers` row `gamma-en-2` by tag.  At all five cusps the number of
distinct **classes** of `K_J` the printed roots give is the card's wall count: the reduction merges
none of the printed walls, which is what makes the class count a computed value and not a
transcription of the card.  Three of the five families are held in `T_{En}` coordinates by hand
(`Sterk.sterks_in_TEn`); the other two are printed in coordinates of a model of `K_J` and are carried
into `T_{En}` by `Sterk.cusp_roots_in_TEn`, whose docstring states each identification and which one
of them is sage-extensions#298's isometry.

**What the identification of cusps 4 and 5 is.**  Diagram 4.3.9's fourteen roots are printed in
`U + E8(-2)`, a rank-ten model of `K_J` of the same determinant `-256`: that the model *is* the
boundary lattice is an isometry of lattices, and it is decided and witnessed by the call of #298
(`isometry_matrix_to`, through `is_isometric_to`).  Diagram 4.3.8's eleven roots are printed in
`II_{18,2}` coordinates, and no map into `T_{En}` carries them: their span is a rank-ten lattice of
determinant `-1024`, an index-two sublattice of `K_J`, so that identification is an isometric
*embedding* --- the same form equation with a non-unimodular matrix, which #298's isometry call
correctly reports as no isometry between the two lattices.  Either identification may be composed
with any element of `O(K_J)`, so the number of printed classes is identification-free (the call
checks that the pairwise pairings survive) while how many of them lie in `T_Co` is a statement about
the identification in use, and is reported as such rather than compared with a card.

No lattice-database card holds the orbit counts themselves.  The missing row is
`029J.cusp_root_orbits.gamma-en-2` --- per cusp, the number of `Gamma_{Co,2}`-orbits of the root
classes with one representative per orbit --- and the same row on the T_Co card for cusps 3--5; both
are named in `results/issue370-the-coble-root-orbits.md` to be filed on
`dzackgarza/lattice-database`.
"""

from sage_extensions.all import *  # noqa: F401,F403

_ENRIQUES_IMAGES = {}
_COBLE_IMAGES = {}
_GROUPS = {}


def _gamma_en_2():
    r"""`Gamma_{En,2}` on `T_En`, by the construction of #286 item 2 (Alexeev--Engel--Garza--Schaffler, Def. 2.6).

    Built once per session: every cusp image of `T_En` shares the one group.
    """
    if "enriques" in _GROUPS:
        return _GROUPS["enriques"]
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
    _GROUPS["enriques"] = Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()
    return _GROUPS["enriques"]


def _gamma_co_2():
    r"""`Gamma_{Co,2} = R_{Gamma_{En,2}}` on `T_Co`, by the construction of #358.

    `P` is the stabilizer in `O(q)` of the decomposition `A_{U(2)} + A_{E8(-2)}` of `[h/2]^perp`
    (research `prop:gamma-co-images`, `38fa09935a`), and the group is the preimage of its point
    stabilizer --- the call of #354, never a description of its image.

    Built once per session: `T_Co`'s three cusps share the one group, and building it is the
    expensive step of every call that reads a cusp.
    """
    if "coble" in _GROUPS:
        return _GROUPS["coble"]
    lattice = NamedLattices.Tco
    form = lattice.discriminant_group()
    first = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("ep")))
    second = lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator("fp")))
    point = frozenset({form.zero(), first, second, first + second})
    _GROUPS["coble"] = lattice.Aut().discriminant_point_stabilizer(point)
    return _GROUPS["coble"]


def _enriques_cusp_image(name):
    r"""The reduction image at Sterk's cusp `name` of `T_En`, built once per session."""
    if name not in _ENRIQUES_IMAGES:
        vector = Sterk.selected_isotropic_vectors()[name]
        _ENRIQUES_IMAGES[name] = _gamma_en_2().isotropic_vector_reduction_image(vector)
    return _ENRIQUES_IMAGES[name]


def _coble_cusp_image(number):
    r"""The reduction image at `T_Co`'s cusp `number` (3, 4 or 5), built once per session.

    The representative is the library's own cusp vector, `Sterk.selected_isotropic_vectors()`.  For
    cusps 3, 4 and 5 its `e` and `f` coefficients are equal, so it is a vector of `T_Co = delta^perp`
    with that coefficient on `h` and the same coordinates on `ep, fp, a1..a8`; at cusp 1 it is `e` and
    at cusp 2 `ep`.  It is used here rather than card `029J`'s row because it is the line the printed
    roots of the cusp are classes at: the two agree at cusps 1, 2, 3 and 5, and at cusp 4 the card
    states `(0, 0, 2, 1, -4, ...)` where the library's vector is `(0, 0, 1, 2, -4, ...)`, two
    different isotropic lines (they pair to `2`), of which only the second is orthogonal to the eleven
    printed roots of diagram 4.3.8.  That disagreement is recorded in
    `results/issue370-the-coble-root-orbits.md`; the wall counts the tests compare are the card's, read
    by tag, and do not depend on which representative of the cusp is used.
    """
    if number not in _COBLE_IMAGES:
        lattice = NamedLattices.Tco
        ring = lattice.base_ring()
        enriques = NamedLattices.TEn
        cusp = Sterk.selected_isotropic_vectors()[f"Sterk_{number}"]
        coordinates = cusp.to_vector()
        labels = tuple(enriques.module_generating_set())
        given = {label: int(coordinates(label)) for label in labels}
        assert given["e"] == given["f"]
        coefficients = {"h": ring(given["e"])} if given["e"] else {}
        for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
            if given[label]:
                coefficients[label] = ring(given[label])
        eta = lattice.linear_combination(coefficients)
        assert lattice.q(eta) == ZZ.zero()
        assert eta.is_primitive() is True
        _COBLE_IMAGES[number] = _gamma_co_2().isotropic_vector_reduction_image(eta)
    return _COBLE_IMAGES[number]


def _transported_to_coble(root, lattice, enriques, eta):
    r"""Read a vector of `T_{En}` lying in `T_Co` as a vector of `T_Co`, checked.

    A vector of `T_{En}` whose `e` and `f` coefficients agree is the vector of `T_Co` with that
    coefficient on `h` and the same coordinates on `ep, fp, a1..a8`; that is the inclusion
    `T_Co -> T_{En}`, whose image is `{x = y}` in the `U` block.  The pairings with the cusp vector
    and the squares are the two things the caller then asks, and both are checked here.
    """
    coordinates = root.to_vector()
    alpha = int(coordinates("e"))
    assert int(coordinates("f")) == alpha
    ring = lattice.base_ring()
    coefficients = {"h": ring(alpha)} if alpha else {}
    for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
        if int(coordinates(label)):
            coefficients[label] = ring(int(coordinates(label)))
    transported = lattice.linear_combination(coefficients)
    assert lattice.q(transported) == enriques.q(root)
    assert lattice.b(transported, eta) == ZZ.zero()
    return transported


def test_the_printed_cusp_walls_are_distinct_classes_of_the_boundary_lattice() -> None:
    r"""The printed roots at cusps 1--5 are as many distinct classes of `K_J` as the card's walls.

    Card `029J` states 12, 10, 12, 11 and 14 walls for Sterk's diagrams 4.3.5--4.3.9, and
    `Sterk.cusp_roots_in_TEn` holds each family as vectors of `T_{En}` --- the first three by hand,
    the other two by the identifications stated there.  Their classes in `K_J = v^perp/ZZ v` are
    computed here by `root_class`, so a printed wall that were a multiple of the cusp's own vector
    --- or two printed walls in one class --- would show up as a smaller class count than the card's.
    That they agree at all five cusps is what lets an orbit count be compared with the card's
    geometry, and it is the card comparison the identification of cusps 4 and 5 has to survive.
    """
    rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
    walls = [cardinal(row["walls"]) for row in rows]
    names = [f"Sterk_{number}" for number in range(1, 6)]
    for name, expected in zip(names, walls):
        image = _enriques_cusp_image(name)
        roots = tuple(Sterk.cusp_roots_in_TEn(name))
        classes = tuple(image.root_class(root) for root in roots)
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
    image = _coble_cusp_image(3)
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

    transported = _transported_to_coble(negative_two[0], lattice, enriques, eta)
    assert lattice.q(transported) == -ZZ(2)

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

def _orbit_partition(orbits, given, reduction):
    r"""Check that the orbits partition ``given`` and that each transporter is an isometry of `K`.

    The transporters themselves are what `root_class_orbits` verifies, by re-applying each one to its
    orbit's representative; what is checked here is what a caller reads off the result: every class
    lies in exactly one orbit, the orbit sizes add up, and each orbit's transporter is a form-preserving
    isometry of the reduction (an element of `O(K_I)`, not an arbitrary module map).
    """
    covered = [class_ for orbit in orbits for class_ in tuple(orbit.index_set())]
    assert cardinal(sum(1 for _ in covered)) == cardinal(sum(1 for _ in given))
    for class_ in given:
        assert cardinal(sum(1 for other in covered if other == class_)) == cardinal(1)
    for orbit in orbits:
        members = tuple(orbit.index_set())
        assert cardinal(sum(1 for _ in members)) > cardinal(0)
        transporter = orbit.value(members[0])
        assert all(
            reduction.q(transporter(vector)) == reduction.q(vector)
            for vector in reduction.module_generators()
        )


def test_the_cusps_four_and_five_have_their_root_class_orbits_in_the_boundary_lattice() -> None:
    r"""At Sterk's cusps 4 and 5 the `(-2)` classes of `K_J` are orbited by `Gamma_{En,2}`'s stabilizer.

    Diagram 4.3.8 (p. 23) has eleven walls and 4.3.9 (p. 24) fourteen, both read from card `029J`'s
    `cusp_chambers` row by tag in the class-count test above; the **roots** of `K_J` among them are
    the classes of square `-2`, two at cusp 4 and four at cusp 5.  That count is a statement no
    identification can change: the printed roots are carried into `K_J` by an injective form-preserving
    map (`Sterk.cusp_roots_in_TEn`), and such a map preserves squares, so the number of `(-2)` classes
    is the number of `(-2)` printed roots --- which is what the assertion here compares, and *not* a
    count of orbits.

    The acting family is `Gamma_{En,2}`'s own line stabilizer at the cusp, reduced to `K_J` and
    certified in `G_v` by the discriminant criterion.  What is asserted of the result is that the
    orbits partition the classes given and that each transporter is a form-preserving isometry of
    `K_J`.  What is deliberately not asserted is a count of orbits: they have no card, and a singleton
    orbit is not a proof of inequivalence, because `generators_are_certified_complete` is `False` at a
    primitive isotropic line (sage-extensions#312) --- an orbit of more than one class proves those
    roots `Gamma_{En,2}`-equivalent, and only a certified generating family of `G_v` would let a
    singleton prove anything.
    """
    rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
    for number in (4, 5):
        name = f"Sterk_{number}"
        image = _enriques_cusp_image(name)
        reduction = image.reduction()
        roots = tuple(Sterk.cusp_roots_in_TEn(name))
        printed_negative_two = [root for root in roots if root.q() == -ZZ(2)]
        classes = []
        for root in roots:
            class_ = image.root_class(root)
            if all(class_ != seen for seen in classes):
                classes.append(class_)
        roots_of_the_boundary = [
            class_ for class_ in classes if reduction.q(class_) == -ZZ(2)
        ]
        assert cardinal(sum(1 for _ in roots_of_the_boundary)) == cardinal(
            sum(1 for _ in printed_negative_two)
        )
        assert cardinal(sum(1 for _ in roots_of_the_boundary)) < cardinal(
            rows[number - 1]["walls"]
        )
        stabilizer = tuple(
            image.subgroup().supergroup().isotropic_stabilizer_generators(image.line())
        )
        assert cardinal(sum(1 for _ in stabilizer)) > cardinal(0)
        orbits = image.root_class_orbits(
            tuple(roots_of_the_boundary), stabilizer_generators=stabilizer
        )
        _orbit_partition(orbits, tuple(roots_of_the_boundary), reduction)


def test_the_coble_cusp_five_has_its_root_class_orbits_in_the_boundary_lattice_of_t_co() -> None:
    r"""At `T_Co`'s cusp 5 the printed roots of 4.3.9 are carried into `K_I` and their orbits returned.

    This is the one cusp of `T_Co` where the printed family's identification with `K_I` is fixed by a
    map the library holds rather than chosen: diagram 4.3.9 is printed in `U + E8(-2)`, which is a
    model of the boundary lattice `K_J`, and `Embeddings.U_E8_2_into_TEn` carries that model into
    `eta^perp` with the model's own pairings (asserted in `Sterk.cusp_roots_in_TEn`), so the classes of
    `K_J` it gives are determined and not merely one of the `O(K_J)`-many choices.  Generic
    `(-4)`-walls of the diagram are not roots of `K_I` and are dropped, as in the cusp 3 test.

    Cusp 4 is **not** asserted here: diagram 4.3.8 is printed in `II_{18,2}` coordinates, its span
    embeds in `K_J` with index two, and that embedding is one of `O(K_J)`-many --- two runs of this
    library gave one and two root classes of `K_I` there --- so a count of its roots of `K_I`, and the
    orbits of them, are statements about the identification and not about Sterk's diagram.
    `results/issue370-the-coble-root-orbits.md` records the measurements and what would pin it.
    """
    enriques = NamedLattices.TEn
    basis = {
        label: enriques.module_generator(label)
        for label in enriques.module_generating_set()
    }
    delta = basis["e"] - basis["f"]
    image = _coble_cusp_image(5)
    lattice = image.lattice()
    eta = image.vector()
    reduction = image.reduction()
    roots = tuple(Sterk.cusp_roots_in_TEn("Sterk_5"))
    inside = [root for root in roots if enriques.b(root, delta) == ZZ.zero()]
    assert cardinal(sum(1 for _ in inside)) > cardinal(0)
    classes = []
    for root in inside:
        class_ = image.root_class(_transported_to_coble(root, lattice, enriques, eta))
        assert reduction.q(class_) == enriques.q(root)
        if all(class_ != seen for seen in classes):
            classes.append(class_)
    roots_of_the_boundary = [class_ for class_ in classes if reduction.q(class_) == -ZZ(2)]
    assert cardinal(sum(1 for _ in roots_of_the_boundary)) > cardinal(0)
    stabilizer = tuple(
        image.subgroup().supergroup().isotropic_stabilizer_generators(image.line())
    )
    assert cardinal(sum(1 for _ in stabilizer)) > cardinal(0)
    orbits = image.root_class_orbits(
        tuple(roots_of_the_boundary), stabilizer_generators=stabilizer
    )
    _orbit_partition(orbits, tuple(roots_of_the_boundary), reduction)
