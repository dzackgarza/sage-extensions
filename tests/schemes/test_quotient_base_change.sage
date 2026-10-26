r"""Invariant maps factor through the quotient of the affine plane by the coordinate swap."""

from sage_extensions.all import *


def test_the_swap_invariant_map_x_plus_y_factors_through_the_quotient() -> None:
    r"""`(x, y) \mapsto x + y` is invariant under `x \leftrightarrow y`, so it factors
    uniquely through `\mathbb{A}^2 \to \mathbb{A}^2 / C_2 = \operatorname{Spec}
    \mathbb{Q}[x, y]^{C_2}`; the map `(x, y) \mapsto x` is not invariant and does not."""
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
    target_ring = QQ.polynomial_ring("t")
    target = target_ring.affine_spectrum()
    quotient = acted.quotient_morphism()

    trace = spec(target_ring.Mor(algebra)({"t": x + y}))
    first = spec(target_ring.Mor(algebra)({"t": x}))
    descended = acted.descend_invariant_family(trace)

    assert descended.codomain() is target
    assert descended * quotient == trace
    assert not acted.is_invariant_family(first)
