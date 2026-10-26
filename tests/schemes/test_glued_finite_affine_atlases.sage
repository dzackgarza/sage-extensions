r"""Schemes glued from finite affine atlases, and their global functions.

Source: Stacks Project, Tag 01JA (gluing schemes from a finite family of charts
``U_i``, opens ``U_ij`` and isomorphisms ``phi_ij`` satisfying the cocycle condition on
triple overlaps) and Tag 01MM (the standard affine charts of ``P^n``).  Global functions
are the compatible families of chart functions (the sheaf condition), so gluing
``Spec QQ[x]`` to itself along ``D(x)`` by the identity gives ``Gamma(X, O) = QQ[x]``, and
by ``x -> 1/x`` gives ``Gamma(P^1, O) = QQ[x] cap QQ[1/x] = QQ`` (Hartshorne III.5.1).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _line_and_punctured_line():
    ring = QQ.polynomial_ring("x")
    line = ring.affine_spectrum()
    return ring, line, line.distinguished_open(ring.algebra_generator("x"))


def _identity_gluing(punctured):
    identity = punctured.Mor(punctured).identity()
    return Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)


def _reciprocal_gluing(ring, punctured):
    functions = punctured.coordinate_algebra()
    restriction = punctured.inclusion().coordinate_algebra_morphism()
    x = ring.algebra_generator("x")
    reciprocal = functions.induced_morphism(ring.Mor(functions)({"x": restriction(x).inverse_of_unit()}))
    inversion = punctured.Mor(punctured)(reciprocal)
    return Schemes(QQ).Core().Mor(punctured, punctured)(inversion, inversion)


def test_the_line_with_a_tripled_origin_satisfies_the_cocycle_condition() -> None:
    r"""Three lines glued pairwise by the identity of ``D(x)``: the cocycle holds on ``D(x)``.

    The triple overlap ``U_01 cap U_02`` is ``D(x)`` and ``phi_12 o phi_01 = phi_02`` there.
    The three open immersions are pairwise distinct, and the identity on every chart
    glues to a fold onto the line.
    """
    _ring, line, punctured = _line_and_punctured_line()
    gluing = _identity_gluing(punctured)
    tripled = Schemes(QQ).glue_affine_atlas((line, line, line), (gluing, gluing, gluing))
    atlas = tripled.gluing_datum()
    identity = line.Mor(line).identity()
    fold = tripled.Mor(line)((identity, identity, identity))

    assert atlas.triple_overlap(0, 1, 2) is punctured
    assert atlas.chart_embedding(0) != atlas.chart_embedding(2)
    assert fold * atlas.chart_embedding(2) == identity


def test_an_atlas_of_two_lines_glued_by_the_identity_has_one_transition() -> None:
    r"""Two charts have exactly one unordered pair, hence one chart change."""
    _ring, line, punctured = _line_and_punctured_line()
    doubled = Schemes(QQ).glue_affine_atlas((line, line), (_identity_gluing(punctured),))

    assert doubled.gluing_datum().transition_index_set().cardinality() == 1


def test_the_fold_of_an_atlas_of_two_lines_restricts_to_the_identity_on_each_chart() -> None:
    r"""The chart change from chart 1 back to chart 0 lives on ``D(x)``, and the fold is the identity on chart 1."""
    _ring, line, punctured = _line_and_punctured_line()
    doubled = Schemes(QQ).glue_affine_atlas((line, line), (_identity_gluing(punctured),))
    atlas = doubled.gluing_datum()
    identity = line.Mor(line).identity()
    fold = doubled.Mor(line)((identity, identity))

    assert atlas.overlap(1, 0) is punctured
    assert fold * atlas.chart_embedding(1) == identity


def test_global_functions_on_the_line_with_doubled_origin_are_the_polynomials() -> None:
    r"""``Gamma(X, O) = {(f, g) in QQ[x]^2 : f = g in QQ[x, 1/x]} = QQ[x]``: restriction to a chart is bijective."""
    _ring, line, punctured = _line_and_punctured_line()
    doubled = Schemes(QQ).glue_affine_atlas((line, line), (_identity_gluing(punctured),))
    atlas = doubled.finite_affine_atlas()

    assert atlas.global_function_restriction(0).is_bijective()
    assert atlas.global_function_restriction(1).is_bijective()


def test_global_functions_on_the_glued_projective_line_are_the_constants() -> None:
    r"""``Gamma(P^1, O) = QQ[x] cap QQ[1/x] = QQ``, of rank one over ``QQ``."""
    ring, line, punctured = _line_and_punctured_line()
    projective = Schemes(QQ).glue_affine_atlas((line, line), (_reciprocal_gluing(ring, punctured),))

    assert projective.finite_affine_atlas().global_function_algebra().module_rank() == 1


def test_the_projective_plane_is_glued_from_its_three_standard_charts() -> None:
    r"""``P^2 = U_0 cup U_1 cup U_2`` with ``U_i = D_+(x_i)``: three charts, and the gluing is ``P^2``."""
    plane = ProjectiveSpaces(QQ)(2)
    glued = plane.glued_from_standard_charts()

    assert glued.gluing_datum().transition_index_set().cardinality() == 3
    assert glued.is_isomorphic(plane)
