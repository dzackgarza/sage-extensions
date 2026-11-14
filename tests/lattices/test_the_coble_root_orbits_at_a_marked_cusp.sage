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
24: the printed cusp diagrams of the Enriques period lattice `T_{En} = U + U(2) + E8(-2)`, with 12,
10, 12, 11 and 14 walls, read as card `029J`'s `cusp_chambers` row `gamma-en-2` by tag.  At all five
cusps the number of distinct **classes** of `K_J` the walls give is that row's wall count: the
reduction merges none of the printed walls, which is what makes the class count a computed value and
not a transcription of the card.

**Where the walls and the cusp vectors come from: the row, by tag.**  Card `029J`'s
`integral.cusp_chambers['gamma-en-2']` row for each diagram stores the chamber's cusp vector *and*
every wall as a vector in the card's Gram coordinates, which are `T_{En}`'s, so this test reads both
from `card("cusp_diagrams", "029J")` and transcribes neither.  Sterk prints the same vectors --- his
coordinates are `L_- = H + H(2) + E8(-2)` (1.2--1.4, pp. 3--4), which is `T_{En}` --- and
`Sterk.cusp_roots_in_TEn` returns them, so the two sources are compared rather than one assumed.

Cusp 4 is the one place where the paper prints **two** vectors for the cusp: (4.2.3), p. 16, lists
`e' + 2f' + \gamma` among the five cusp representatives, and (4.3.8), p. 23, draws its chamber at
`2e' + f' + \bar\alpha_1`, the two pairing to `2`.  The card's row stores the second, because a row
holds a chamber, and the eleven walls of Fig. 10 are orthogonal to it and pair `4, -2, -4` with
`α_{10}, α_{11}, α_{12}` against the first.  So the cusp vector of the diagram is the card's, and
`Sterk.sterk4_cusp_vector()` is it; `Sterk.selected_isotropic_vectors()` keeps (4.2.3)'s, which is
what a *cusp* is and what the reduction lattice is read at.

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


def _card_cusp(number):
    r"""Return card `029J`'s row for Sterk's diagram `number` as `(cusp vector, walls)`.

    The card's `cusp_diagrams` row for the statement of that diagram stores the chamber's cusp vector
    and every wall in the card's Gram coordinates, which are this library's `T_{En}`: `number` 4 is
    (4.3.8) with Fig. 10 and `number` 5 is (4.3.9) with Fig. 12.  Reading them here is what makes a
    run of this file choose no vector and no map.
    """
    rows = card("cusp_diagrams", "029J")["rows"]["gamma-en-2"]
    lattice = NamedLattices.TEn
    labels = tuple(lattice.module_generating_set())
    row = rows[number - 1]

    def vector(entries):
        return lattice.linear_combination(
            {
                label: lattice.base_ring()(int(entry))
                for label, entry in zip(labels, entries, strict=True)
                if int(entry)
            }
        )

    cusp = vector(row["cusp"])
    assert lattice.q(cusp) == ZZ.zero()
    assert cusp.is_primitive() is True
    walls = tuple(vector(entries) for entries in row["wall_vectors"])
    assert cardinal(sum(1 for _ in walls)) == cardinal(row["wall_count"])
    return cusp, walls


def _enriques_cusp_image(number):
    r"""The reduction image at Sterk's cusp `number` of `T_En`, built once per session.

    The cusp vector is the card's, `_card_cusp(number)[0]`: the chamber of the diagram printed for
    that cusp sits there.  At cusps 1, 2, 3 and 5 it is also `Sterk.selected_isotropic_vectors()`';
    at cusp 4 the card and `Sterk.sterk4_cusp_vector()` have `2e' + f' + \bar\alpha_1` where (4.2.3),
    p. 16, lists `e' + 2f' + \gamma`, and it is at the first that Fig. 10's eleven walls are classes.
    """
    if number not in _ENRIQUES_IMAGES:
        vector, _walls = _card_cusp(number)
        _ENRIQUES_IMAGES[number] = _gamma_en_2().isotropic_vector_reduction_image(vector)
    return _ENRIQUES_IMAGES[number]


def _coble_cusp_image(number):
    r"""The reduction image at `T_Co`'s cusp `number` (3, 4 or 5), built once per session.

    The representative is read from card `029J`'s `cusp_diagrams` row for that cusp's statement, by
    tag.  For cusps 3, 4 and 5 its `e` and `f` coefficients are equal, so it is a vector of
    `T_Co = delta^\perp` with that coefficient on `h` and the same coordinates on `ep, fp, a1..a8`.

    At cusps 3 and 5 the card's vector is also `Sterk.selected_isotropic_vectors()`' --- (4.2.3),
    p. 16, lists the five cusp representatives --- and at cusp 4 it is not: (4.3.8), p. 23, draws that
    chamber at `2e' + f' + \bar\alpha_1`, which is the card's vector and `Sterk.sterk4_cusp_vector()`'s,
    while (4.2.3) lists `e' + 2f' + \gamma`; the two pair to `2`.  Both are asserted here, so a card
    that changed either would fail.
    """
    if number not in _COBLE_IMAGES:
        lattice = NamedLattices.Tco
        ring = lattice.base_ring()
        enriques = NamedLattices.TEn
        cusp, _walls = _card_cusp(number)
        if number == 4:
            assert cusp == Sterk.sterk4_cusp_vector()
            assert cusp != Sterk.selected_isotropic_vectors()["Sterk_4"]
        else:
            assert cusp == Sterk.selected_isotropic_vectors()[f"Sterk_{number}"]
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
    `Sterk.cusp_roots_in_TEn` holds each family as vectors of `T_{En}` --- the first three hand-read,
    the last two from the printed vectors of (4.3.8) and (4.3.9).  Their classes in `K_J =
    v^perp/ZZ v` are computed here by `root_class`, so a wall that were a multiple of the cusp's own
    vector --- or two walls in one class --- would show up as a smaller class count than the card's.
    That they agree at all five cusps is what makes a class count a computed value, and it is the
    comparison the cusp-4 and cusp-5 transcriptions have to survive.  The cusp vector each is read at
    is the card's own row (`_card_cusp`), which is the chamber's line at every cusp.
    """
    rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
    walls = [cardinal(row["walls"]) for row in rows]
    for number, expected in zip(range(1, 6), walls):
        name = f"Sterk_{number}"
        image = _enriques_cusp_image(number)
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
    image = _enriques_cusp_image(1)
    reduction = HyperbolicLattices(ZZ)(image.reduction())
    walls = tuple(reduction.fundamental_chamber().wall_roots())
    assert cardinal(sum(1 for _ in walls)) > cardinal(0)
    squares = [reduction.q(wall) for wall in walls]
    assert any(square == -ZZ(4) for square in squares)
    for wall in walls:
        assert image.root_class(image.class_lift(wall)) == wall


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

    Diagram 4.3.8 (p. 23) has eleven walls and 4.3.9 (p. 24) fourteen, read from card `029J`'s
    `cusp_chambers` row by tag in the class-count test above; the **roots** of `K_J` among them are
    the classes of square `-2`, two at cusp 4 and four at cusp 5.  That count is a statement no choice
    can change: each wall is a vector the card stores and `Sterk.cusp_roots_in_TEn` reproduces, and a
    form-preserving map preserves squares, so the number of `(-2)` classes is the number of `(-2)`
    walls --- which is what the assertion compares, and *not* a count of orbits.

    The acting family is `Gamma_{En,2}`'s own line stabilizer at the cusp, reduced to `K_J` and
    certified in `G_v` by the discriminant criterion.  What is asserted of the result is that the
    orbits partition the classes given and that each transporter is a form-preserving isometry of
    `K_J`.  What is deliberately not asserted is a count of orbits: they have no card, and a singleton
    orbit is not a proof of inequivalence, because `generators_are_certified_complete` is `False` at a
    primitive isotropic line (sage-extensions#312).
    """
    for number in (4, 5):
        name = f"Sterk_{number}"
        image = _enriques_cusp_image(number)
        reduction = image.reduction()
        cusp_vector, card_walls = _card_cusp(number)
        printed = tuple(Sterk.cusp_roots_in_TEn(name))
        # The card's cusp vector spans the line the image was built at: its class in K_J is zero.
        assert image.root_class(cusp_vector) == image.reduction().zero()
        # Sterk's transcription and the card's row are the same vectors, wall for wall.
        assert set(printed) == set(card_walls)
        assert cardinal(sum(1 for _ in printed)) == cardinal(sum(1 for _ in card_walls))
        classes = []
        for wall in card_walls:
            class_ = image.root_class(wall)
            if all(class_ != seen for seen in classes):
                classes.append(class_)
        roots_of_the_boundary = [class_ for class_ in classes if reduction.q(class_) == -ZZ(2)]
        negative_two = [wall for wall in card_walls if wall.q() == -ZZ(2)]
        assert cardinal(sum(1 for _ in roots_of_the_boundary)) == cardinal(
            sum(1 for _ in negative_two)
        )
        stabilizer = tuple(
            image.subgroup().supergroup().isotropic_stabilizer_generators(image.line())
        )
        assert cardinal(sum(1 for _ in stabilizer)) > cardinal(0)
        orbits = image.root_class_orbits(
            tuple(roots_of_the_boundary), stabilizer_generators=stabilizer
        )
        _orbit_partition(orbits, tuple(roots_of_the_boundary), reduction)


def test_the_coble_cusps_three_four_and_five_have_their_root_class_orbits() -> None:
    r"""At `T_Co`'s cusps 3, 4 and 5 the walls are carried into `K_I` and their orbits returned.

    `T_Co = delta^\perp` inside `T_{En}`, `delta = e - f`, and a vector orthogonal to `delta` has equal
    `e` and `f` coefficients: it is the vector with that coefficient on the `h` line of `T_Co`.  So the
    walls of the three diagrams that meet `T_Co` become vectors of `T_Co`, their classes in `K_I` are
    read by `root_class`, and the `(-2)` ones among them --- the roots of `K_I` in #370's sense --- are
    handed to `root_class_orbits`, which returns each orbit with a transporter checked by
    re-application.

    **No search, and so the same run every time.**  Cusp 3's twelve walls are the hand-read `T_{En}`
    coordinates of `sterks_in_TEn`; cusp 4's eleven are Sterk's own vectors of
    `L_- = H + H(2) + E8(-2)` read off Fig. 10 and 4.3.8, p. 23; cusp 5's fourteen are the printed
    `U + E8(-2)` vectors carried in by `Embeddings.U_E8_2_into_TEn`.  Every cusp vector and every wall
    is the card's row by tag, and `Sterk.cusp_roots_in_TEn` returns the same vectors.  That is what
    cusp 4 did not have before: its span used to be matched inside `K_J` by the lattice embedding Mor,
    one of `O(K_J)`-many maps chosen by the engine, and two runs then gave one and two root classes
    there.

    **What is asserted.**  That the family reaches `K_I` at each cusp, that every class has the square
    of the wall it comes from, that the orbits partition the roots given, and that each transporter is
    a form-preserving isometry of `K_I`.  At cusp 3 it is also asserted, as before, that the action is
    not vacuous: some certified generator moves that one class on `K_I` and is dropped only because
    its image leaves the given family.

    **What is not asserted.**  A count of orbits.  They have no card --- the row that would carry them,
    `029J.cusp_root_orbits.gamma-en-2`, is named in `results/issue370-the-coble-root-orbits.md` for
    filing --- and a **singleton orbit is not a proof of inequivalence**, because
    `generators_are_certified_complete` is `False` at a primitive isotropic line (sage-extensions#312):
    an orbit of more than one class proves those roots `Gamma_{Co,2}`-equivalent, and only a certified
    generating family of `G_v` would let a singleton prove anything.
    """
    enriques = NamedLattices.TEn
    basis = {
        label: enriques.module_generator(label)
        for label in enriques.module_generating_set()
    }
    delta = basis["e"] - basis["f"]
    for number, name in ((3, "Sterk_3"), (4, "Sterk_4"), (5, "Sterk_5")):
        image = _coble_cusp_image(number)
        lattice = image.lattice()
        eta = image.vector()
        reduction = image.reduction()
        cusp_vector, card_walls = _card_cusp(number)
        # The card's T_En vector, read in T_Co, is the cusp vector the image was built at.
        assert _transported_to_coble(cusp_vector, lattice, enriques, eta) == eta
        if number != 4:
            assert cusp_vector == Sterk.selected_isotropic_vectors()[name]
        else:
            assert cusp_vector == Sterk.sterk4_cusp_vector()
            assert cusp_vector != Sterk.selected_isotropic_vectors()[name]
        walls = tuple(Sterk.cusp_roots_in_TEn(name))
        assert set(walls) == set(card_walls)
        inside = [wall for wall in walls if enriques.b(wall, delta) == ZZ.zero()]
        assert cardinal(sum(1 for _ in inside)) > cardinal(0)
        classes = []
        for wall in inside:
            class_ = image.root_class(_transported_to_coble(wall, lattice, enriques, eta))
            assert reduction.q(class_) == enriques.q(wall)
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
        assert cardinal(orbits.cardinality()) > cardinal(0)
        _orbit_partition(orbits, tuple(roots_of_the_boundary), reduction)
        if number == 3:
            # The family is one class, so its orbit is a singleton; the action is not vacuous.
            movers = [
                generator
                for generator in stabilizer
                if generator(eta) == eta
                and image.contains(image.reduction_image(generator), lift=generator)
                and image.reduction_image(generator)(roots_of_the_boundary[0])
                != roots_of_the_boundary[0]
            ]
            assert cardinal(sum(1 for _ in movers)) > cardinal(0)
