r"""The group that ``Stab_\Gamma(v)`` induces on ``v^\perp/<v>``, at Sterk's five Enriques cusps.

``T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)`` is the Enriques period lattice
(rank 12, signature ``(2, 10)``, ``|det| = 1024``), and ``\Gamma_{\mathrm{En},2}``
is H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
Math. Z. 207 (1991), 1--36, Proposition 2.7, p. 6 -- the group whose five
``0``-cusps are Proposition 4.2.3 with Remark 4.2.4, p. 16.  Its five cusp
representatives are ``Sterk.selected_isotropic_vectors()``, and at each one
``V. Alexeev, P. Engel, D. Z. Garza, L. Schaffler, *Compact moduli of Enriques
surfaces of degree 2*, Nagoya Math. J. 259 (2025), §3.3, p. 590`` counts five
``0``-cusps of ``F_{En,2}``.

For a primitive isotropic ``v`` the group that the stabilizer induces on
``N = v^\perp/\mathbf Z v`` is the image of ``\Gamma_{\mathrm{En},2} \cap P_v``
under the Levi map ``P_v \to O(N)`` (Dutour Sikirić--Hulek, arXiv:2302.01679v2,
theorem `theorem_isotropic_k_planes`, printed pp. 33--34).  An isometry of ``N`` has
many lifts in ``P_v`` and two differ by an element of the kernel ``K_v``, so
membership is decided on the discriminant image: ``\sigma`` is in the image when
``\rho`` of one lift lies in ``\rho(K_v)\rho(\Gamma)``.  ``K_v`` contains the
Eichler transvections ``t(v, a)``, ``a \perp v`` (Gritsenko--Hulek--Sankaran,
arXiv:0810.1614, §3.1, equation (4)), with a rational parameter when ``v`` has
divisibility two; their image ``\rho(K_v)`` is an output of the call.

The wall counts Sterk publishes for the cusp diagrams (4.3.5--4.3.9) are the
sizes of ``Sterk.sterk_roots()``: twelve, ten, twelve, eleven and fourteen roots
for the five cusps.  What is asserted below is the stronger statement at the
three cusps whose printed roots the library holds in ``T_{\mathrm{En}}``
coordinates: *every* one of those roots' reflections lies in the image, decided
by the discriminant criterion and not by one lift each.  The chamber of that
reflection subgroup is ``cusp_chamber`` (#297), and the tests at the end of this
file compare it with the five printed diagrams, wall by wall and edge by edge.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _gamma_en_2():
    r"""``\Gamma_{En,2}`` on ``T_En``, by the construction of #286 item 2.

    The group is the coinvariant extension subgroup of the degree-two
    polarization of the Enriques involution: Alexeev--Engel--Garza--Schaffler,
    Nagoya Math. J. 259 (2025), Definition 2.6, and Sterk, Proposition 2.7,
    p. 6.  It is built here by that construction and never from a description of
    its image in ``O(A_L)``.
    """
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


_CUSP_IMAGES = {}


def _cusp_images():
    r"""One reduction image per cusp of ``\Gamma_{En,2}``, keyed by Sterk's label.

    Built once per session: the group and its five cusps are the same objects in
    every test of this file, ``\Gamma_{\mathrm{En},2}`` costs half a minute to
    construct, and one discriminant image serves every cusp (it is
    ``\rho(\Gamma_{\mathrm{En},2})``, a property of the group).
    """
    if not _CUSP_IMAGES:
        subgroup = _gamma_en_2()
        _CUSP_IMAGES.update({
            name: subgroup.isotropic_vector_reduction_image(vector)
            for name, vector in Sterk.selected_isotropic_vectors().items()
        })
    return dict(_CUSP_IMAGES)


def test_each_cusp_reduces_to_a_hyperbolic_rank_ten_lattice() -> None:
    r"""``v^\perp/\mathbf Z v`` has rank ``10`` and signature ``(1, 9)``, and is even.

    The determinants separate the first cusp from the other four: ``1024`` for
    ``Sterk_1``, whose vector is the generator ``e`` of the unimodular plane of
    ``T_{\mathrm{En}}``, and ``256`` for the four whose vectors carry a
    divisibility two factor.  Both are read off the lattice, not from a table.
    """
    images = _cusp_images()
    determinants = {
        "Sterk_1": ZZ(-1024),
        "Sterk_2": ZZ(-256),
        "Sterk_3": ZZ(-256),
        "Sterk_4": ZZ(-256),
        "Sterk_5": ZZ(-256),
    }

    assert sorted(images) == ["Sterk_1", "Sterk_2", "Sterk_3", "Sterk_4", "Sterk_5"]
    for name, image in images.items():
        reduction = image.reduction()
        signature = reduction.signature_pair()
        assert reduction.module_rank() == cardinal(10)
        assert (int(signature.first()), int(signature.second())) == (1, 9)
        assert reduction.is_even() is True
        assert reduction.determinant() == determinants[name]
        assert image.lattice().q(image.vector()) == ZZ.zero()
        assert image.vector().is_primitive() is True


def test_two_lifts_of_a_wall_reflection_differ_by_the_kernel_and_get_one_answer() -> None:
    r"""``s_{a+v} s_a`` lies in ``K_v`` and both lifts of a wall reflection are admitted.

    For a printed wall ``a`` of card ``029J``'s row 4.3.8 (Sterk, Math. Z. 207
    (1991), (4.3.8) with Fig. 10, p. 23), ``a`` and ``a + v`` lie in
    ``v^\perp``, both reflections are integral and fix ``v``, and both induce
    the reflection of ``N`` in the class of ``a``; their quotient therefore
    fixes ``v`` and acts trivially on ``N``, which is the kernel ``K_v`` of the
    Levi map.  The quotient is asserted to be an element of ``rho(K_v)``, and
    ``rho(K_v)`` is asserted nontrivial: at this cusp the divisibility of ``v``
    is two, so the kernel is strictly larger than the transvections of lattice
    vectors and a single lift does not decide a class.

    The criterion ``\rho(g) \in \rho(K_v)\rho(\Gamma)`` decides a class of
    ``N``, so it gives the two lifts one answer -- and that answer is *yes* for
    the printed walls, which is what Sterk's figure states: Fig. 10 is "the
    diagram for the reflection subgroup of ``G_v``", so each wall's reflection
    lies in ``G_v``.  Asserting only that the answers agree would hold with both
    lifts refused, which is exactly the failure a kernel computed from lattice
    parameters produces here, so both are asserted admitted.
    """
    image, walls, row = _fourth_chamber()
    lattice = image.lattice()
    vector = image.vector()
    rho = lattice.discriminant_representation()
    kernel_image = image.kernel_discriminant_image()
    kernel_identity = kernel_image.one()
    quotients = []
    for wall in walls:
        first = image.root_reflection(wall)
        second = image.root_reflection(wall + vector)
        quotient = second * first
        assert quotient(vector) == vector
        assert image.line().acts_trivially_on_isotropic_reduction(quotient) is True
        assert rho(quotient) in kernel_image
        assert image.contains_lift(first) is True
        assert image.contains_lift(second) is True
        quotients.append((wall.q(), rho(quotient)))

    assert cardinal(sum(1 for _ in quotients)) == cardinal(row["wall_count"])
    # The kernel's image is not trivial at this cusp, and the (-4) walls are the
    # walls whose quotient is the transvection of the fractional parameter a/2:
    # some printed wall therefore contributes a *nontrivial* class of rho(K_v),
    # which is the class a kernel of lattice parameters would have missed.
    assert image.kernel_discriminant_image_is_trivial() is False
    fractional = tuple(element for square, element in quotients if square == ZZ(-4))
    assert cardinal(sum(1 for _ in fractional)) > cardinal(0)
    assert any(element != kernel_identity for element in fractional)


def test_sterks_published_cusp_roots_are_reflections_of_the_stabilizer_image() -> None:
    r"""Every printed root of the cusps ``1``--``3`` is a reflection in the image.

    Sterk's diagrams 4.3.5--4.3.9 for the five cusps have twelve, ten, twelve,
    eleven and fourteen walls; the library's transcription
    ``Sterk.sterk_roots()`` holds those families, and for the first three cusps
    also in ``T_{\mathrm{En}}`` coordinates (``Sterk.sterks_in_TEn()``).  For
    each of those the reflection of ``T_{\mathrm{En}}`` in the root fixes ``v``,
    so it induces a reflection of ``N``, and the discriminant criterion decides
    that reflection's membership -- exactly, not by exhibiting one lift.
    """
    images = _cusp_images()
    transcribed = Sterk.sterks_in_TEn()
    diagrams = Sterk.sterk_roots()

    assert sorted(transcribed) == ["Sterk_1", "Sterk_2", "Sterk_3"]
    assert cardinal(sum(1 for _ in diagrams["Sterk_1"])) == cardinal(12)
    assert cardinal(sum(1 for _ in diagrams["Sterk_2"])) == cardinal(10)
    assert cardinal(sum(1 for _ in diagrams["Sterk_3"])) == cardinal(12)
    for name, family in transcribed.items():
        roots = tuple(family)
        image = images[name]
        reflections = image.reflection_generators(roots)
        assert cardinal(sum(1 for _ in roots)) == cardinal(sum(1 for _ in diagrams[name]))
        assert tuple(root for root, _ in reflections) == roots
        assert image.generators_are_certified_complete() is False


def test_the_membership_questions_at_the_first_cusp_are_one_sift_per_root() -> None:
    r"""The twelve printed roots at ``Sterk_1``, each decided by one sift of ``\rho(\Gamma)``.

    ``contains_root_reflection`` is the discriminant criterion of #312: the
    reflection of ``T_{\mathrm{En}}`` in a printed root fixes ``v``, so it lies in
    the parabolic, and its class on ``N`` lies in ``G_v`` exactly when
    ``\rho(g) \in \rho(K_v)\rho(\Gamma)``.  At this cusp ``\rho(K_v)`` is trivial
    (the test above), so the whole question is one membership in
    ``\rho(\Gamma_{\mathrm{En},2}) \le O(A_L)``, a group of order ``696729600``,
    and it is answered by sifting one stabilizer chain of that image (A. Seress,
    *Permutation Group Algorithms*, Cambridge University Press 2003, Chapter 4;
    ``discriminant_image_membership``) — never against a list of its elements,
    which is not an option at that order and is not built here.

    Sterk's diagram 4.3.5 (Math. Z. 207 (1991), p. 19) has twelve walls, and the
    twelve roots below are its printed roots in ``T_{\mathrm{En}}`` coordinates.
    """
    image = _cusp_images()["Sterk_1"]
    roots = tuple(Sterk.sterks_in_TEn()["Sterk_1"])
    diagrams = Sterk.sterk_roots()
    decisions = tuple(image.contains_root_reflection(root) for root in roots)

    assert cardinal(sum(1 for _ in decisions)) == cardinal(sum(1 for _ in diagrams["Sterk_1"]))
    assert all(decisions)
    assert image.kernel_discriminant_image_is_trivial() is True



def test_the_lift_criterion_agrees_with_the_levi_route_at_the_first_cusp() -> None:
    r"""``admits_root`` and ``contains_root_reflection`` decide the same twelve roots.

    The chamber of #297 asks about a *class* of ``N``, and ``admits_root`` decides
    it on the lift alone (``contains_lift``); the tests above ask about a vector of
    ``T_{\mathrm{En}}``, and ``contains_root_reflection`` goes through the Levi map
    as well.  Both are the same criterion -- ``\rho(g) \in \rho(K_v)\rho(\Gamma)``
    for a lift of the reflection -- and the descent that lets the chamber skip the
    Levi evaluation is the statement that the reflection of ``L`` in a vector of
    ``v^\perp`` induces the reflection of ``N`` in its class.  Here the two routes
    are required to agree on Sterk's twelve printed roots at ``Sterk_1``
    (diagram 4.3.5, Math. Z. 207 (1991), p. 19), so that the faster route is
    checked against the one that evaluates the Levi map, not assumed.
    """
    image = _cusp_images()["Sterk_1"]
    reduction = HyperbolicLattices(ZZ)(image.reduction())
    walls = tuple(reduction.fundamental_chamber().wall_roots())
    by_the_lift = tuple(image.admits_root(wall) for wall in walls)
    by_the_levi_map = tuple(
        image.contains_root_reflection(image.class_lift(wall)) for wall in walls
    )

    assert cardinal(sum(1 for _ in walls)) > cardinal(1)
    assert by_the_lift == by_the_levi_map
    assert any(by_the_lift)
    assert not all(by_the_lift)


def test_the_five_cusps_are_the_chamber_rows_of_card_029j() -> None:
    r"""Sterk's five cusps are the five ``integral.cusp_chambers`` rows of card ``029J``.

    The rows are the diagrams 4.3.5--4.3.9 of H. Sterk, *Compactifications of the
    period space of Enriques surfaces, Part I*, Math. Z. 207 (1991), §4.3.1 with
    pp. 19, 21, 22, 23 and 24 — 12, 10, 12, 11 and 14 walls, in the paper's order
    and therefore in the order of ``Sterk.selected_isotropic_vectors()`` — and
    each row names its cusp by a primitive isotropic vector in the card's Gram
    coordinates.

    The vectors agree term by term at four of the five: the card's row 4.3.8
    states `(0, 0, 2, 1, -4, ...)` where the library's ``Sterk_4`` is
    `(0, 0, 1, 2, -4, ...)`, two representatives of the same cusp and the one
    place where the two lists differ; the pairing is by the paper's order and the
    count of agreements is what this test pins.

    The wall count is the number ``image.cusp_chamber()`` has to reproduce, which
    ``test_every_cusp_chamber_has_the_wall_count_of_its_card_row`` asserts; this
    test pins the correspondence between the rows and the library's cusps.
    """
    rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
    images = _cusp_images()
    walls = [cardinal(row["walls"]) for row in rows]
    agreements = []
    for row, name in zip(rows, sorted(images)):
        image = images[name]
        assert image.lattice().q(image.vector()) == ZZ.zero()
        assert image.vector().is_primitive() is True
        agreements.append(
            tuple(int(entry) for entry in row["cusp"])
            == tuple(int(entry) for entry in image.vector().to_vector())
        )

    assert cardinal(sum(1 for _ in rows)) == cardinal(sum(1 for _ in images))
    assert cardinal(sum(1 for _ in walls)) == cardinal(sum(1 for _ in rows))
    assert all(count > cardinal(1) for count in walls)
    assert cardinal(sum(1 for _ in set(walls))) > cardinal(1)
    assert cardinal(sum(1 for agreement in agreements if agreement)) == cardinal(4)


def test_every_cusp_chamber_has_the_wall_count_of_its_card_row() -> None:
    r"""The chamber of ``G_v`` at each of Sterk's five cusps, against card ``029J``.

    ``cusp_chamber`` is the fundamental chamber of the reflection subgroup
    ``W' = <s_r : r a root of N, s_r in G_v>`` of ``W = W(N)``.  It is Vinberg's
    algorithm run on the roots whose reflections ``G_v`` admits, and it stops on
    his finite-volume criterion: E. B. Vinberg, *On the groups of unit elements of
    certain quadratic forms*, Math. USSR Sb. 16 (1972), §3.2, Proposition 4
    (p. 28) says the polyhedron cut by the normals the algorithm lists is the
    chamber, and Proposition 5 (p. 29) says the list breaks off once that
    polyhedron has finite volume.  So ``is_complete_wall_set()`` is not an extra
    certificate here: it is the statement that the algorithm reached its own stop,
    and the walls returned are then all of them.

    Sterk computed the five chambers by that algorithm and published the five
    diagrams 4.3.5--4.3.9 (*Compactifications of the period space of Enriques
    surfaces, Part I*, Math. Z. 207 (1991), pp. 19, 21, 22, 23 and 24); their wall
    counts are the ``integral.cusp_chambers`` rows of card ``029J``, which are
    read here by tag and paired with the cusps in the paper's order.  Card row
    4.3.8 states its cusp as ``(0, 0, 2, 1, -4, ...)`` where the library's
    ``Sterk_4`` is ``(0, 0, 1, 2, -4, ...)``: two representatives of one cusp, so
    the pairing is by the paper's order and not by the vectors.

    ``cusp_chamber`` takes no bound here: a bound is not part of the route.
    """
    rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
    images = _cusp_images()
    counted = []
    for row, name in zip(rows, sorted(images)):
        image = images[name]
        chamber = image.cusp_chamber()
        walls = tuple(chamber.wall_roots())
        assert chamber.is_complete_wall_set() is True
        assert all(image.admits_root(root) for root in walls)
        assert all(root.q() in (ZZ(-2), ZZ(-4)) for root in walls)
        counted.append((cardinal(sum(1 for _ in walls)), cardinal(row["walls"])))

    assert cardinal(sum(1 for _ in counted)) == cardinal(sum(1 for _ in rows))
    assert all(measured == expected for measured, expected in counted)


def test_the_first_cusp_writes_down_no_candidate_outside_its_layer() -> None:
    r"""A bounded prefix of the first cusp's walk returns roots and nothing else.

    Every candidate the layer enumeration writes down is a vector of the lattice
    whose square is the layer's own, because conditions (58) of E. B. Vinberg,
    *On the groups of unit elements of certain quadratic forms*, Math. USSR Sb. 16
    (1972), §4.1, p. 30, are applied while the layer is written down and not to a
    finished list.  Before that, the enumeration used the first term of a layer
    as if it were the layer's offset — `a` is a point of the parallelepiped of
    `VinAl`'s decomposition, not a multiple of the controlling vector — so it
    returned vectors of the wrong square at `Sterk_1` and the walk died with
    `ZeroDivisionError` on a candidate of square zero.

    The search is stopped by ``max_decompositions`` here because this test is the
    regression for that error and not the acceptance of the chamber: the wall
    count is asserted, unbounded, by
    ``test_every_cusp_chamber_has_the_wall_count_of_its_card_row``.  The
    controlling vector is Sterk's own, `x = e' + f'`
    (§4.3.5, p. 19), whose cell at the cusp is the nine walls his diagram puts
    through it.
    """
    lattice = NamedLattices.TEn
    labels = {label: lattice.module_generator(label) for label in lattice.module_generating_set()}
    x = labels["ep"] + labels["fp"]
    image = _cusp_images()["Sterk_1"]
    reduction = HyperbolicLattices(ZZ)(image.reduction())
    chamber = image.cusp_chamber(x, max_decompositions=8)
    walls = tuple(chamber.wall_roots())

    assert all(root.q() in (ZZ(-2), ZZ(-4)) for root in walls)
    assert all(image.admits_root(root) for root in walls)
    assert all(reduction.b(root, root) == root.q() for root in walls)


def test_the_fourth_cusps_walk_stops_within_twenty_decompositions_at_the_card_chamber() -> None:
    r"""Bounded to twenty decompositions, the cusp-4 walk reaches its stop with the card's walls.

    The walk enumerates each layer in the coordinates of the cell at its
    controlling vector, the cone coordinates nonnegative and a lineality
    coordinate, where the cell has one, bounded on both sides by the layer's
    norm equation (E. B. Vinberg, *On the groups of unit elements of certain
    quadratic forms*, Math. USSR Sb. 16 (1972), §4.1, the equation (57) with
    the conditions (58), p. 30; #400).  Within twenty decompositions past the
    controlling vector the polyhedron its walls cut out has finite volume,
    which is the algorithm's stop (Proposition 5, p. 29), and its wall count
    is card ``029J``'s row 4.3.8 (H. Sterk, *Compactifications of the period
    space of Enriques surfaces, Part I*, Math. Z. 207 (1991), (4.3.8) with
    Fig. 10, p. 23), read by tag.
    """
    image = _cusp_images()["Sterk_4"]
    row = next(
        row
        for row in card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
        if row["statement"] == "4.3.8"
    )
    chamber = image.cusp_chamber(max_decompositions=20)
    walls = tuple(chamber.wall_roots())

    assert chamber.is_complete_wall_set() is True
    assert all(image.admits_root(root) for root in walls)
    assert all(root.q() in (ZZ(-2), ZZ(-4)) for root in walls)
    assert cardinal(sum(1 for _ in walls)) == cardinal(row["walls"])


def test_each_of_the_fourth_cusps_first_layers_agrees_with_the_whole_lattice_in_the_cell() -> None:
    r"""The cell enumeration of a layer is exactly that layer's whole-lattice solutions in the cell.

    The walk at the fourth cusp enumerates its layers in the coordinates of
    the cell at the controlling vector (#400): the cone coordinates
    nonnegative, the lineality coordinate an integer bounded on both sides
    by the layer's norm equation.  Its candidates are then exactly the
    solutions of the layer's equation (57) that lie in the cell — E. B.
    Vinberg, *On the groups of unit elements of certain quadratic forms*,
    Math. USSR Sb. 16 (1972), §4.1, the equation (57) with the conditions
    (58), p. 30 — the vectors whose coordinates in the cell normals are
    nonpositive, which is to pair nonpositively with every adjugate dual
    normal of the cell.  The engine's whole-lattice enumeration returns
    every solution of the same equation with no restriction, so the two
    sets agree on each layer both searches reach; the first four are
    compared here, layer by layer, with the layer named on failure — the
    probe ``issue400-probe-b.log`` compared the first thirteen the same way
    before the whole-lattice search itself runs out of memory at the
    fourteenth.

    The dual normals are verified before use: each pairs zero with every
    normal but its own, and positively with its own, so each is a positive
    multiple of the dual basis vector of the cell normals, and pairing
    nonpositively with every dual is the nonpositive orthant of the normal
    coordinates and not some other cone.
    """
    image = _cusp_images()["Sterk_4"]
    reduction = image.reduction()

    def coordinates_of(candidate):
        return tuple(int(entry) for entry in candidate.to_vector())

    for layer in image.cusp_layer_enumerations(layers=4):
        normals = layer.cell_normals()
        duals = layer.cell_dual_normals()
        for i, normal in enumerate(normals):
            for j, dual in enumerate(duals):
                pairing = reduction.b(normal, dual)
                if i == j:
                    assert pairing > 0
                else:
                    assert pairing == 0
        in_the_cell = [
            candidate
            for candidate in layer.whole_lattice_candidates()
            if all(reduction.b(candidate, dual) <= 0 for dual in duals)
        ]
        assert {coordinates_of(candidate) for candidate in layer.cell_candidates()} == {
            coordinates_of(candidate) for candidate in in_the_cell
        }, (
            f"layer {layer.layer_number()} of square {layer.square()} at offset "
            f"{layer.offset()} disagrees with its whole-lattice solutions in the cell"
        )


_FOURTH_CHAMBER = {}


def _fourth_chamber():
    r"""Card ``029J``'s row 4.3.8 as ``(reduction image at its cusp, its walls, the row)``.

    The row stores the cusp vector of H. Sterk, *Compactifications of the period
    space of Enriques surfaces, Part I*, Math. Z. 207 (1991), (4.3.8), p. 23,
    and the eleven walls of Fig. 10 in the card's Gram coordinates, which are
    those of ``T_{\mathrm{En}}``; both are read here by tag, and the image is
    built once per session.
    """
    if not _FOURTH_CHAMBER:
        row = next(
            row
            for row in card("cusp_diagrams", "029J")["rows"]["gamma-en-2"]
            if row["statement"] == "4.3.8"
        )
        subgroup = _gamma_en_2()
        lattice = subgroup.supergroup().domain()
        image = subgroup.isotropic_vector_reduction_image(
            lattice([int(entry) for entry in row["cusp"]])
        )
        walls = tuple(
            image.lattice()([int(entry) for entry in wall]) for wall in row["wall_vectors"]
        )
        _FOURTH_CHAMBER.update(image=image, walls=walls, row=row)
    return _FOURTH_CHAMBER["image"], _FOURTH_CHAMBER["walls"], _FOURTH_CHAMBER["row"]


def test_every_wall_of_the_fourth_cusp_chamber_is_a_reflection_of_the_stabilizer_image() -> None:
    r"""Each of Fig. 10's eleven walls is admitted, whichever lift of its class is reflected.

    Sterk (4.3.8), p. 23, prints Fig. 10 as "the diagram for the reflection
    subgroup of ``G_v``", ``G_v`` the image of ``\Gamma_v`` in
    ``O(v^\perp/\mathbf Z v)`` (the definition after Lemma 4.3.4), so the reflection in each of
    its walls lies in ``G_v``.  Each printed wall is a vector of ``v^\perp``,
    and its reflection in ``T_{\mathrm{En}}`` fixes ``v`` and induces the
    reflection of ``N`` in the wall's class.  Membership of that class in
    ``G_v`` is a property of the class: ``admits_root``, which reflects in
    the frame's lift of the class, and ``contains_lift`` of the reflection in
    the printed vector, which is another lift of the same reflection of ``N``,
    must both say yes.
    """
    image, walls, row = _fourth_chamber()
    reduction = image.reduction()
    perpendicular = reduction.orthogonal_complement()
    classes = tuple(
        reduction.projection()(perpendicular.inclusion().lift(wall)) for wall in walls
    )
    printed = tuple(image.contains_lift(image.root_reflection(wall)) for wall in walls)
    by_class = tuple(image.admits_root(wall_class) for wall_class in classes)

    assert cardinal(sum(1 for _ in walls)) == cardinal(row["wall_count"])
    assert all(printed)
    assert all(by_class)


_CARD_CHAMBERS = {}


def _card_cusp_rows():
    r"""Card ``029J``'s five cusp diagrams, keyed by the statement of Sterk's paper they transcribe.

    H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
    Math. Z. 207 (1991), §4.3.1 with the diagrams (4.3.5)--(4.3.9), printed on
    pp. 19, 21, 22, 23 and 24: at each of the five ``0``-cusps of
    ``\Gamma_{\mathrm{En},2}`` the walls of the chamber of \(G_v\) and the diagram they
    form.  Read here by tag from card ``029J``'s ``integral.cusp_chambers`` rows.
    """
    return {
        row["statement"]: row
        for row in card("cusp_diagrams", "029J")["rows"]["gamma-en-2"]
    }


def _normalized(vector):
    r"""Return the class of ``vector`` up to sign.

    A root and its negative span one line and define one reflection, so a printed wall
    and a returned wall are the same wall when their vectors agree up to sign: this is
    the key that comparison uses.
    """
    coordinates = [int(entry) for entry in vector.to_vector()]
    for entry in coordinates:
        if entry:
            return tuple(coordinates if entry > 0 else [-value for value in coordinates])
    return tuple(coordinates)


def _wall_correspondence(reduction, printed, returned):
    r"""Match Sterk's printed walls to the returned ones by their pairings, or ``{}``.

    The two families are chambers of one reflection subgroup, so they are the same
    diagram exactly when some bijection carries every pairing to its image: the square
    of a wall to the square of its image and the pairing of two walls to the pairing of
    their images.  That bijection is what this search returns, and it is found by
    backtracking over the walls in decreasing order of how many walls they meet, with
    the square and every pairing taken so far as the pruning conditions.  The search is
    over ``11`` to ``14`` walls of a tree, so it is small.

    A match is the statement that the two families of roots have the same Gram matrix,
    which is the statement that their Coxeter matrices coincide; it is not a statement
    that the wall vectors coincide, and at these cusps they do not (see
    ``test_the_chamber_at_each_cusp_has_sterks_printed_gram_and_diagram``).
    """
    positions = tuple(position for position, _wall in enumerate(printed))
    images = tuple(position for position, _wall in enumerate(returned))
    squares = {
        position: reduction.b(printed[position], printed[position]) for position in positions
    }
    degrees = {
        position: sum(
            1
            for other in positions
            if other != position and reduction.b(printed[position], printed[other]) != ZZ.zero()
        )
        for position in positions
    }
    returned_degrees = {
        index: sum(
            1
            for other in images
            if other != index and reduction.b(returned[index], returned[other]) != ZZ.zero()
        )
        for index in images
    }
    order = tuple(sorted(positions, key=lambda position: -degrees[position]))
    assignment = {}

    def compatible(left, right):
        if squares[left] != reduction.b(returned[right], returned[right]):
            return False
        return all(
            reduction.b(printed[left], printed[other])
            == reduction.b(returned[right], returned[image])
            for other, image in assignment.items()
        )

    def search(remaining):
        if not remaining:
            return True
        left, rest = remaining[0], remaining[1:]
        for right in images:
            if right in assignment.values():
                continue
            if returned_degrees[right] != degrees[left] or not compatible(left, right):
                continue
            assignment[left] = right
            if search(rest):
                return True
            del assignment[left]
        return False

    if not search(order):
        return {}
    return dict(assignment)


def _card_chamber(statement):
    r"""The call's chamber at a card cusp, Sterk's printed chamber, and their correspondence.

    ``statement`` names a row of card ``029J``'s ``cusp_diagrams``, and the image is
    built at that row's own cusp vector -- for (4.3.8), p. 23, that is
    `2e' + f' + \bar\alpha_1`, the vector Fig. 10 is drawn at, not (4.2.3)'s other
    representative of the same cusp.

    The returned chamber is the cell of the reflection subgroup \(W'\le G_v\) at the
    controlling vector the call computes for itself (Vinberg 1972, §3.2, after
    Proposition 3, p. 27), so it is a chamber of \(W'\) and Sterk's printed chamber is
    another; the two are compared through their pairings by
    :func:`_wall_correspondence`, which is what the recorded diagram is.

    Every printed wall's reflection is asserted to lie in \(G_v\): Sterk draws each
    diagram as "the diagram for the reflection subgroup of \(G_v\)", and
    :meth:`admits_root` decides that, wall by wall, on the discriminant group.

    Built once per session: the five chambers cost minutes, and three tests below read
    them.
    """
    if statement not in _CARD_CHAMBERS:
        row = _card_cusp_rows()[statement]
        subgroup = _gamma_en_2()
        lattice = subgroup.supergroup().domain()
        image = subgroup.isotropic_vector_reduction_image(
            lattice([int(entry) for entry in row["cusp"]])
        )
        reduction = image.reduction()
        walls = tuple(
            lattice([int(entry) for entry in wall]) for wall in row["wall_vectors"]
        )
        printed = tuple(image.root_class(wall) for wall in walls)
        assert all(image.admits_root(wall) for wall in printed), (
            f"Sterk's diagram {statement} is the diagram for the reflection subgroup of G_v, so the "
            "reflection in each printed wall lies in G_v"
        )
        chamber = image.cusp_chamber()
        returned = tuple(chamber.wall_roots())
        _CARD_CHAMBERS[statement] = {
            "image": image,
            "chamber": chamber,
            "row": row,
            "walls": walls,
            "printed": printed,
            "returned": returned,
            "match": _wall_correspondence(reduction, printed, returned),
        }
    return _CARD_CHAMBERS[statement]


def test_the_chamber_at_each_cusp_has_sterks_printed_gram_and_diagram() -> None:
    r"""The chamber the call returns carries Sterk's recorded Gram and his recorded diagram.

    H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
    Math. Z. 207 (1991), (4.3.5)--(4.3.9) with Figs. 4, 6, 8, 10 and 12, pp. 19, 21,
    22, 23 and 24, prints at each of the five ``0``-cusps of ``\Gamma_{\mathrm{En},2}``
    the walls of the chamber of \(G_v\), and card ``029J``'s rows store those walls as
    vectors of ``T_{\mathrm{En}}`` together with the diagram's edges.  ``cusp_chamber``
    returns a chamber of the reflection subgroup of \(G_v\), and the two chambers are
    matched wall by wall on their pairings: the whole Gram matrix of the printed walls
    is asserted to be the Gram matrix of the returned ones under that match, and the
    returned diagram, with the card's own names \(\alpha_i\) on the walls the match
    puts them on, is asserted to have the card's bonds -- order \(\infty\)
    included.

    **What is and is not the same vector list.**  The returned chamber is the cell at
    the controlling vector the call computes for itself, so it need not be Sterk's
    list of wall vectors: the two chambers share nine of their twelve walls at
    (4.3.5) and six of ten at (4.3.6), the remaining walls being other walls of the
    same reflection subgroup, and their Gram matrices coincide.  So the two are
    congruent root families with one diagram, and the diagram is compared as a
    labelled graph -- the card's \(\alpha_i\) on the matched walls -- rather than by
    the wall vectors.  At the first cusp the transporting element is exhibited and
    certified in \(G_v\) by
    ``test_the_first_cusps_chamber_is_sterks_under_one_admitted_reflection``; at the
    other four it is not exhibited, so what is asserted there is the recorded Gram,
    the recorded diagram, and that every printed wall is an admitted reflection of
    \(G_v\).
    """
    rows = _card_cusp_rows()
    assert cardinal(sum(1 for _ in rows)) == cardinal(5)
    for statement in sorted(rows):
        data = _card_chamber(statement)
        row = data["row"]
        printed = data["printed"]
        returned = data["returned"]
        match = data["match"]
        names = tuple(row["vertices"])
        assert data["chamber"].is_complete_wall_set() is True
        assert cardinal(sum(1 for _ in returned)) == cardinal(row["wall_count"])
        reduction = data["image"].reduction()
        assert cardinal(sum(1 for _ in match)) == cardinal(row["wall_count"]), statement
        assert all(position in match for position, _name in enumerate(names))
        positions = tuple(position for position, _wall in enumerate(printed))
        for left in positions:
            for right in positions:
                assert reduction.b(printed[left], printed[right]) == reduction.b(
                    returned[match[left]], returned[match[right]]
                ), statement
        diagram = CoxeterDiagrams()(
            tuple(returned[match[position]] for position, _name in enumerate(names))
        )
        recorded = {
            (edge["left"], edge["right"]): edge["order"] for edge in row["edges"]
        }
        for position, left in enumerate(names):
            for other_position, right in enumerate(names):
                if position == other_position:
                    continue
                recorded_order = recorded.get((left, right), recorded.get((right, left), 2))
                bond = diagram.coxeter_entry(position, other_position)
                if recorded_order is None:
                    assert bond == Infinity, statement
                else:
                    assert bond == recorded_order, statement


def test_every_cusp_chambers_walls_are_roots_that_pair_nonnegatively() -> None:
    r"""The returned walls are roots of ``N``, and they pair nonnegatively.

    Each wall is a root -- square ``-2`` or ``-4``, primitive -- and the roots pair
    nonnegatively, which is Vinberg's condition on the normals he lists: his
    \(e\) satisfy \((e,e)>0\) and \((e,e_i)\le 0\) for every earlier term (E. B.
    Vinberg, *On the groups of unit elements of certain quadratic forms*, Math. USSR
    Sb. 16 (1972), §3.2, the conditions (40), pp. 27--28), and the roots of a negative
    definite form with the form negated are those normals, so the pairing of two roots
    is the negative of a pairing of normals.  In the chamber's own terms this says the
    dihedral angles are at most a right angle, which is what makes the polyhedron
    acute-angled and Vinberg's finite-volume criterion applicable.
    """
    rows = _card_cusp_rows()
    for statement in sorted(rows):
        data = _card_chamber(statement)
        reduction = data["image"].reduction()
        returned = data["returned"]
        assert all(reduction.q(wall) in (ZZ(-2), ZZ(-4)) for wall in returned)
        assert all(wall.is_primitive() is True for wall in returned)
        assert all(
            reduction.b(left, right) >= ZZ.zero()
            for position, left in enumerate(returned)
            for right in returned[position + 1:]
        )
        assert cardinal(sum(1 for _ in returned)) == cardinal(data["row"]["wall_count"])


def test_the_first_cusps_reduction_is_the_lattice_sterks_lemma_records() -> None:
    r"""``e^\perp/\mathbf Z e \cong H(2) \oplus E_8(-2)``, and `H \oplus E_8(-2)` at another cusp.

    H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
    Math. Z. 207 (1991), Lemma 4.3.4, p. 17: for one of the five vectors of (4.2.3),
    \(v^\perp/\mathbf Z v \cong \mathbf H \oplus E_8(-2)\) unless \(v = e\), and
    \(e^\perp/\mathbf Z e \cong \mathbf H(2) \oplus E_8(-2)\).  Both are read off the
    call's own reduction at the cusp vector it is given -- the first cusp's ``e`` and
    the second's ``e'`` -- and not off a lattice built for the occasion.
    """
    images = _cusp_images()
    first = images["Sterk_1"]
    second = images["Sterk_2"]
    rows = _card_cusp_rows()
    assert tuple(int(entry) for entry in first.vector().to_vector()) == tuple(
        int(entry) for entry in rows["4.3.5"]["cusp"]
    )
    assert tuple(int(entry) for entry in second.vector().to_vector()) == tuple(
        int(entry) for entry in rows["4.3.6"]["cusp"]
    )
    assert first.reduction().is_isometric_to(NamedLattices.U.twist(2) + NamedLattices.E8_2) is True
    assert second.reduction().is_isometric_to(NamedLattices.U_E8_2) is True


def test_the_stabilizer_image_returns_the_chambers_reflections_and_decides_membership() -> None:
    r"""The generators the call returns at a cusp, and the membership decision certifying them.

    At a primitive isotropic *line* the parabolic's own constructed generator family is
    not available -- ``parabolic_stabilizer_generators`` is stated for a plane and
    refuses rank one, which is what ``generation_obstruction`` says -- so the family the
    call returns is the reflection part of \(G_v\): the images of the reflections in the
    roots it admits (#312).  At the first cusp those are Sterk's twelve printed walls,
    and ``reflection_generators`` returns one isometry of \(N\) per wall.

    Membership is decided for an isometry of \(N\) by :meth:`contains`, on the
    discriminant group, and never by a list of the group's elements: the criterion is
    \(\rho(g) \in \rho(K_v)\rho(\Gamma)\) for one lift \(g\), and both answers are
    asserted here.  The walls Sterk prints are admitted.  Not every wall of the *full*
    chamber of \(N\) is: at the first cusp some of those reflections lie outside
    \(G_v\), which is why Sterk's diagram there is the subgroup's and not \(O(N)\)'s.
    """
    data = _card_chamber("4.3.5")
    image = data["image"]
    row = data["row"]
    reduction = image.reduction()
    walls = data["walls"]
    pairs = image.reflection_generators(walls)
    assert cardinal(sum(1 for _ in pairs)) == cardinal(row["wall_count"])
    reflections = tuple(reflection for _root, reflection in pairs)
    assert all(reflection.parent() is reduction.Aut() for reflection in reflections)
    lifted = tuple(image.root_reflection(wall) for wall in walls)
    assert all(
        image.contains(image.reduction_image(isometry), lift=isometry) for isometry in lifted
    )
    full = tuple(HyperbolicLattices(ZZ)(reduction).fundamental_chamber().wall_roots())
    dropped = tuple(wall for wall in full if not image.admits_root(wall))
    assert cardinal(sum(1 for _ in dropped)) > cardinal(0)
    outside = tuple(image.root_reflection(image.class_lift(wall)) for wall in dropped)
    assert not any(
        image.contains(image.reduction_image(isometry), lift=isometry) for isometry in outside
    )


def test_the_first_cusps_chamber_is_sterks_under_one_admitted_reflection() -> None:
    r"""Sterk's first chamber is the returned one moved by one reflection of ``N``, and it lies in ``G_v``.

    At (4.3.5), p. 19, the returned chamber and the printed one share nine of their
    twelve walls; those nine span a hyperplane of \(N\), and an isometry of \(N\) that
    carries one chamber onto the other and fixes that hyperplane pointwise is the
    reflection in it.  Here that reflection is exhibited: its axis is the primitive
    lattice vector along the difference of the one printed wall from the returned wall
    it is matched to, the reflection of the three remaining walls is asserted to be
    Sterk's three, and the nine shared walls are asserted to be fixed.

    It is a reflection of the *lattice* \(N\) -- the axis has square `4` and the
    coefficients \(2b(x,u)/q(u)\) are integral -- and
    :meth:`contains` then decides whether it lies in \(G_v\): it does, so at this cusp
    the returned chamber is Sterk's up to an element of the cusp group, which is what
    #285's acceptance asks for.  That decision is the discriminant criterion of #312,
    one sift of ``\rho(\Gamma_{\mathrm{En},2})`` in \(O(A_L)\), and not a list of the
    group's elements.
    """
    data = _card_chamber("4.3.5")
    image = data["image"]
    reduction = image.reduction()
    printed = data["printed"]
    returned = data["returned"]
    match = data["match"]
    positions = tuple(position for position, _wall in enumerate(printed))
    shared = tuple(
        position for position in positions if printed[position] == returned[match[position]]
    )
    moved = tuple(
        position for position in positions if printed[position] != returned[match[position]]
    )
    assert cardinal(sum(1 for _ in shared)) == cardinal(9)
    assert cardinal(sum(1 for _ in moved)) == cardinal(3)
    assert reduction.sublattice_from(
        tuple(returned[match[position]] for position in shared)
    ).module_rank() == cardinal(9)
    difference = printed[moved[0]] - returned[match[moved[0]]]
    coordinates = [int(value) for value in difference.to_vector()]
    divisor = abs(int(gcd(coordinates)))
    axis = reduction([value // divisor for value in coordinates])
    reflection = reduction.reflection(axis)
    assert all(
        reflection(returned[match[position]]) == printed[position] for position in moved
    )
    assert all(
        reflection(returned[match[position]]) == returned[match[position]] for position in shared
    )
    assert image.contains(reflection) is True
