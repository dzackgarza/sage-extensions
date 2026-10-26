r"""Quotients of glued lines by ``C_2`` acting on every chart by ``x -> -x``.

Source: SGA 1, Exp. V, Prop. 1.8 and Cor. 1.4: a finite group acting on a scheme with
a stable affine cover has a quotient glued from the affine quotients
``U_i / G = Spec O(U_i)^G``.  Here ``QQ[x]^{C_2} = QQ[x^2]`` (the invariants of
``x -> -x`` are the even polynomials), so ``A^1 / C_2 = Spec QQ[x^2]``, the quotient map
``x -> x^2`` has degree 2, and the origin is fixed, so the action is not free.  On the
line with a doubled origin both origins are fixed; on ``P^1`` glued along ``x -> 1/x`` the
action fixes ``0`` and ``infinity`` and ``P^1 / C_2 = P^1``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _line_punctured_and_negation():
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    return ring, line, line.distinguished_open(x), negation


def _doubled_origin_quotient():
    _ring, line, punctured, negation = _line_punctured_and_negation()
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    doubled = Schemes(QQ).glue_affine_atlas((line, line), (gluing,))
    group = Groups.C(2)
    actions = doubled.gluing_datum().charts().map(lambda chart: negation)
    return line, negation, doubled, doubled.c2_chartwise_invariant_quotient(group, actions)


def test_negation_is_an_involution_of_the_line() -> None:
    r"""``x -> -x`` on ``Spec QQ[x]`` squares to the identity and is not the identity."""
    _ring, line, _punctured, negation = _line_punctured_and_negation()

    assert negation * negation == line.Mor(line).identity()
    assert negation != line.Mor(line).identity()


def test_the_quotient_of_the_doubled_origin_is_glued_from_two_invariant_lines() -> None:
    r"""The quotient is glued from two charts ``Spec QQ[x^2]``; its source is the doubled line."""
    _line, _negation, doubled, quotient = _doubled_origin_quotient()
    chart = quotient.acted_chart(0)
    x = chart.coordinate_algebra().algebra_generator("x")

    assert quotient.source_scheme() is doubled
    assert quotient.chart_index_set().cardinality() == 2
    assert chart.invariant_algebra_inclusion()(chart.invariant_algebra_element(x**2)) == x**2


def test_the_quotient_map_of_the_doubled_origin_is_invariant() -> None:
    r"""``q o g = q`` for the quotient map ``q: X -> X / C_2`` and the generator ``g`` of ``C_2``."""
    _line, _negation, _doubled, quotient = _doubled_origin_quotient()
    generator = quotient.acting_group().an_element()

    assert quotient.quotient_morphism() * quotient.action_of(generator) == quotient.quotient_morphism()


def test_c2_fixes_both_origins_so_it_does_not_act_freely() -> None:
    r"""Both origins are fixed by ``x -> -x``: the fixed locus is nonempty and the action is not free."""
    _line, _negation, _doubled, quotient = _doubled_origin_quotient()
    generator = quotient.acting_group().an_element()

    assert not quotient.fixed_locus_is_empty(generator)
    assert not quotient.action_is_free()


def test_negation_on_the_glued_projective_line_has_quotient_the_projective_line() -> None:
    r"""``[x : y] -> [-x : y]`` preserves both charts of ``P^1``; ``P^1 / C_2 = P^1`` and the action is not free."""
    ring, line, punctured, negation = _line_punctured_and_negation()
    functions = punctured.coordinate_algebra()
    restriction = punctured.inclusion().coordinate_algebra_morphism()
    x = ring.algebra_generator("x")
    reciprocal = functions.induced_morphism(ring.Mor(functions)({"x": restriction(x).inverse_of_unit()}))
    inversion = punctured.Mor(punctured)(reciprocal)
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(inversion, inversion)
    projective = Schemes(QQ).glue_affine_atlas((line, line), (gluing,))
    actions = projective.gluing_datum().charts().map(lambda chart: negation)
    quotient = projective.c2_chartwise_invariant_quotient(Groups.C(2), actions)

    assert not quotient.action_is_free()
    assert quotient.quotient_scheme().is_isomorphic(ProjectiveSpaces(QQ)(1))
