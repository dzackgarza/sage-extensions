r"""The structure morphism of a glued invariant quotient factors through the quotient."""

from sage_extensions.all import *  # noqa: F401,F403


def _doubled_origin_quotient():
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(x)
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    doubled = Schemes(QQ).glue_affine_charts(line, line, gluing)
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    group = Groups.C(2)
    actions = doubled.gluing_datum().charts().map(lambda _chart: negation)
    return doubled.c2_chartwise_invariant_quotient(group, actions)


def test_structure_morphism_factors_through_the_glued_invariant_quotient() -> None:
    quotient = _doubled_origin_quotient()
    structure = quotient.source_scheme().structure_morphism()
    factor = quotient.factor_invariant_affine_morphism(structure)

    assert factor.domain() is quotient.quotient_scheme()
    assert factor.codomain() is structure.codomain()
    assert factor * quotient.quotient_morphism() == structure
