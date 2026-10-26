r"""Descent of an equivariant automorphism of the affine plane to its quotient by the swap.

Source: `\mathbb{Q}[x, y]^{C_2} = \mathbb{Q}[e_1, e_2]` with `e_1 = x + y`,
`e_2 = xy` (fundamental theorem of symmetric polynomials).  The translation
`(x, y) \mapsto (x + 1, y + 1)` commutes with the swap and descends to
`e_1 \mapsto e_1 + 2`, `e_2 \mapsto e_2 + e_1 + 1`.
"""

from sage_extensions.all import *


def test_the_diagonal_translation_descends_to_e1_plus_2_and_e2_plus_e1_plus_1() -> None:
    group = Groups.C(2)
    algebra = QQ.polynomial_ring(("x", "y"))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    plane = algebra.affine_spectrum()
    spec = Algebras(QQ).Associative().Unital().Commutative().spectrum()
    (generator,) = group.group_generators()
    action = group.Mor(plane.automorphism_group())(
        {generator: spec(algebra.Mor(algebra)({"x": y, "y": x}))}
    )
    acted = GObjects(group, Schemes(QQ))(plane, action)
    translation = spec(algebra.Mor(algebra)({"x": x + 1, "y": y + 1}))
    equivariant = GObjects(group, Schemes(QQ)).Mor(acted, acted)(translation)

    descended = GObjects(group, Schemes(QQ)).affine_quotient_functor()(equivariant)
    invariants = acted.quotient_morphism().coordinate_algebra_morphism()
    descended_pullback = descended.coordinate_algebra_morphism()
    e1 = invariants.preimage(x + y)
    e2 = invariants.preimage(x * y)

    assert invariants.domain().algebra_generating_set().cardinality() == 2
    assert descended_pullback(e1) == e1 + 2
    assert descended_pullback(e2) == e2 + e1 + 1
