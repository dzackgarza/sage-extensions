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
arXiv:0810.1614, §3.1, equation (4)); their image ``\rho(K_v)`` is an output of
the call, and at all five cusps here it is trivial.

The wall counts Sterk publishes for the cusp diagrams (4.3.5--4.3.9) are the
sizes of ``Sterk.sterk_roots()``: twelve, ten, twelve, eleven and fourteen roots
for the five cusps.  What is asserted below is the stronger statement at the
three cusps whose printed roots the library holds in ``T_{\mathrm{En}}``
coordinates: *every* one of those roots' reflections lies in the image, decided
by the discriminant criterion and not by one lift each.  The chamber of that
reflection subgroup -- the wall count itself -- is #297's call.
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


def test_the_kernel_of_the_levi_map_acts_trivially_on_the_discriminant_group() -> None:
    r"""``\rho(K_v)`` is trivial at every cusp, so one lift does decide membership there.

    ``K_v`` contains one Eichler transvection per basis vector of ``v^\perp``,
    eleven of them at each cusp (``v^\perp`` has rank eleven), and each is
    returned only after being checked to fix ``v`` and to act trivially on
    ``N``.  Their discriminant images generate ``\rho(K_v)``
    (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1, equation (4)--(5)), and
    here that image is the trivial group, which is the output the membership
    criterion needs and is not assumed.
    """
    for name, image in _cusp_images().items():
        transvections = image.kernel_transvections()
        assert cardinal(sum(1 for _ in transvections)) == cardinal(11)
        for transvection in transvections:
            assert transvection(image.vector()) == image.vector()
        assert image.kernel_discriminant_image_is_trivial() is True
        assert image.kernel_discriminant_image().cardinality() == cardinal(1)


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

    The wall count is the number ``image.cusp_chamber()`` has to reproduce.  It
    does not return yet (``results/issue312-membership-sift.md`` §3), so this test
    pins the correspondence and the counts, not the chambers.
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
    ``test_every_cusp_chamber_has_the_wall_count_of_its_card_row``, which does
    not return yet.  The controlling vector is Sterk's own, `x = e' + f'`
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


def test_the_fourth_cusps_layers_are_enumerated_in_the_coordinates_of_its_cell() -> None:
    r"""The cusp-4 walk enumerates its layers through the lineality of its cell (#400).

    The controlling vector the call computes at ``Sterk_4`` has a cell with
    lineality: its eight cell normals span rank eight of the nine-dimensional
    ``v_0^\perp`` (#387, ``results/issue387-the-group-of-the-card-chamber.md``
    §4), so the cone of that cell has one lineality direction and the layer
    enumeration of #285, written for cells whose normals are a basis of
    ``v_0^\perp``, does not reach it.  The walk then enumerated every layer by
    the engine's whole-lattice search and gained no wall in thirty minutes
    after its eighth acceptance (probe ``issue387-probe-j2.log``).

    The layers are now enumerated in the coordinates of the cell itself.
    Every vector of ``v_0^\perp`` is, for exactly one coset representative
    ``s`` of the lattice spanned by the normals and the lineality vector
    ``m``, the vector ``s - sum(d_i w_i) + t m``, with the cone coordinates
    ``d`` nonnegative and the lineality coordinate ``t`` an integer bounded
    on both sides by the layer's norm equation — E. B. Vinberg, *On the
    groups of unit elements of certain quadratic forms*, Math. USSR Sb. 16
    (1972), §4.1, the equation (57) with the conditions (58), p. 30 — and
    the engine's whole-lattice search returns exactly the solutions of the
    same layers, restricted to none of them: the two agree on every layer
    both reach (probe ``issue400-probe-b.log``).  What is asserted here is
    the walk's own progress through that enumeration: bounded to twenty
    decompositions past the controlling vector, it accepts more walls than
    the sixteen the stalled walk had reached — its eight cell walls and its
    eight additions, the last at height ``4 sqrt(2)`` — because the layers
    beyond the stall carry walls again, at height ``6 sqrt(2)``.  The wall count of
    the completed
    chamber is the card's row and not this bounded prefix's: Vinberg's
    sequence (38) legitimately contains positive roots, whose halfspaces
    bound the polyhedron without being its walls.
    """
    image = _cusp_images()["Sterk_4"]
    chamber = image.cusp_chamber(max_decompositions=20)
    walls = tuple(chamber.wall_roots())

    assert chamber.is_complete_wall_set() is False
    assert all(image.admits_root(root) for root in walls)
    assert all(root.q() in (ZZ(-2), ZZ(-4)) for root in walls)
    assert cardinal(sum(1 for _ in walls)) > cardinal(16)


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
