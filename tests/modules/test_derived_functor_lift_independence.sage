r"""Any two chain lifts of one module map are chain homotopic.

This is the comparison theorem (Weibel, *An Introduction to Homological
Algebra*, 2.2.6): a map $M \to N$ lifts to a chain map of projective
resolutions, uniquely up to chain homotopy, so the induced maps on
$\operatorname{Tor}$ and $\operatorname{Ext}$ do not depend on the lift.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_lifts_id_and_three_times_id_of_the_identity_on_z_mod_2_are_chain_homotopic() -> None:
    r"""On $0 \to \mathbb Z \xrightarrow{2} \mathbb Z \to \mathbb Z/2$, $3 - 1 = 2 = d_1 h_0$ with $h_0 = 1$.

    Source: Weibel 2.2.6; the homotopy is computed by hand.
    """
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(2)))
    identity = M.End().one()
    F = M.free_resolution()
    F0, F1 = F.term(0), F.term(1)
    triple = F.Mor(F)({0: 3 * F0.End().one(), 1: 3 * F1.End().one()})
    assert triple.augmented_morphism() == identity

    homotopy = triple.chain_homotopy_to(F.lift_morphism(identity))
    g = F0.module_generator(0)
    assert F.differential(1)(homotopy.component(0)(g)) == 2 * g


def test_tor_and_ext_maps_of_the_identity_do_not_depend_on_the_chain_lift() -> None:
    r"""Both lifts induce the identity on $\operatorname{Tor}_1(\mathbb Z/2, \mathbb Z/2) = \mathbb Z/2$
    and on $\operatorname{Ext}^1(\mathbb Z/2, \mathbb Z/2) = \mathbb Z/2$.

    Source: Weibel 2.2.6 and 3.1 (Tor and Ext of cyclic groups).
    """
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(2)))
    identity = M.End().one()
    F = M.free_resolution()
    triple = F.Mor(F)({0: 3 * F.term(0).End().one(), 1: 3 * F.term(1).End().one()})

    tor = M.tor(M, degree=1)
    ext = M.ext(M, degree=1)
    assert tor.cardinality() == 2
    assert ext.cardinality() == 2

    tor_by_triple = identity.tor_map(M, degree=1, lift=triple)
    ext_by_triple = identity.ext_map(M, degree=1, lift=triple)
    assert tor_by_triple == identity.tor_map(M, degree=1)
    assert ext_by_triple == identity.ext_map(M, degree=1)
    assert tor_by_triple == tor.End().one()
    assert ext_by_triple == ext.End().one()
