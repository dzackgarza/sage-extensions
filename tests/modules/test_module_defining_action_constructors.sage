r"""Finitely presented abelian groups: presentations, maps between them, and derived constructions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_map_z_plus_z6_to_z_plus_z3_lifts_to_a_map_of_presentations() -> None:
    r"""$x \mapsto u$, $y \mapsto v$ is well defined $\mathbb Z \oplus \mathbb Z/6 \to \mathbb Z \oplus \mathbb Z/3$
    since $6v = 0$; it lifts to a map of free presentations whose square commutes and whose projection
    recovers the map (comparison theorem in degree 0).

    Source: Weibel, An Introduction to Homological Algebra, 2.2.6.
    """
    F = ZZ**2
    x, y = F.module_generator(0), F.module_generator(1)
    source = F / F.submodule([6 * y])
    G = ZZ**2
    u, v = G.module_generator(0), G.module_generator(1)
    target = G / G.submodule([3 * v])

    morphism = source.Mor(target)({0: target(u), 1: target(v)})
    assert morphism.kernel().cardinality() == 2
    assert morphism.is_surjective()

    square = morphism.selected_presentation_morphism()
    assert square.right() * source.presentation() == target.presentation() * square.left()
    for i in (0, 1):
        lifted = square.right()(source.presentation().codomain().module_generator(i))
        assert target.presentation_projection()(lifted) == morphism(source.module_generator(i))


def test_three_constructions_of_z_mod_6_are_isomorphic() -> None:
    r"""$\mathbb Z/(6)$, $\mathbb Z^2/(6x, c)$ and the ring $\mathbb Z/6$ regarded as a $\mathbb Z$-module agree.

    Source: by hand (the relation c kills a free summand).
    """
    F = ZZ**1
    presented = F / F.submodule([6 * F.module_generator(0)])
    G = ZZ**2
    stabilized = G / G.submodule([6 * G.module_generator(0), G.module_generator(1)])
    ring_as_module = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))

    assert presented.is_isomorphic(ring_as_module)
    assert stabilized.is_isomorphic(presented)
    assert stabilized.cardinality() == 6
    assert not presented.is_isomorphic(Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(3))))


def test_tensor_hom_and_exterior_square_of_z_mod_6() -> None:
    r"""$\mathbb Z/6 \otimes \mathbb Z = \mathbb Z/6$, $\operatorname{End}(\mathbb Z/6) = \mathbb Z/6$,
    $(\mathbb Z/6)^{\otimes 2} = \operatorname{Sym}^2(\mathbb Z/6) = \mathbb Z/6$, $\Lambda^2(\mathbb Z/6) = 0$
    (a cyclic module has vanishing exterior square), and $\operatorname{Hom}(\mathbb Z/6, \mathbb Z) = 0$.

    Source: Lang, Algebra, XVI.1 and XIX.1; by hand.
    """
    M = Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(6)))
    assert M.tensor_product(ZZ**1).cardinality() == 6
    assert M.End().cardinality() == 6
    assert M.tensor_power(2).cardinality() == 6
    assert M.symmetric_power(2).cardinality() == 6
    assert M.exterior_power(2).is_zero()
    assert M.dual_module().is_zero()
