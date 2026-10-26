r"""Lifting a map of abelian groups to their free resolutions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_reduction_z_mod_6_to_z_mod_3_lifts_to_a_chain_map_of_resolutions() -> None:
    r"""$\mathbb Z/6 \to \mathbb Z/3$ lifts to $0 \to \mathbb Z \xrightarrow{6} \mathbb Z$ over
    $0 \to \mathbb Z \xrightarrow{3} \mathbb Z$ by $1$ in degree $0$ and $\pm 2$ in degree $1$
    ($3 \cdot 2 = 6$), and both squares commute.

    Source: Weibel, An Introduction to Homological Algebra, 2.2.6; by hand.
    """
    source = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))
    target = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(3)))
    reduction = source.Mor(target)({0: target.module_generator(0)})
    P = source.free_resolution()
    Q = target.free_resolution()

    lifted = P.lift_morphism(reduction, Q)

    g = P.term(0).module_generator(0)
    r = P.term(1).module_generator(0)
    s = Q.term(1).module_generator(0)
    assert Q.augmentation()(lifted.component(0)(g)) == reduction(P.augmentation()(g))
    assert Q.differential(1)(lifted.component(1)(r)) == lifted.component(0)(P.differential(1)(r))
    assert lifted.component(1)(r) in (2 * s, -2 * s)
