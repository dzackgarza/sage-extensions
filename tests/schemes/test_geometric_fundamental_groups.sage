r"""Topological fundamental groups of complex points of two schemes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_fundamental_group_of_pgl2_of_the_complex_numbers_has_order_two() -> None:
    r"""``pi_1(PGL_2(CC), I) = ZZ/2``.

    Derivation: ``PGL_2(CC) = SL_2(CC)/{±1}`` and ``SL_2(CC)`` retracts onto
    ``SU(2) = S^3``, which is simply connected.  ``PGL_2 = D_+(ad - bc) ⊂ P^3``.
    """
    P3 = Schemes(QQ).projective_space(3, names=("a", "b", "c", "d"))
    a = P3.coordinate_ring().algebra_generator("a")
    b = P3.coordinate_ring().algebra_generator("b")
    c = P3.coordinate_ring().algebra_generator("c")
    d = P3.coordinate_ring().algebra_generator("d")
    PGL2 = P3.basic_open(a * d - b * c)
    identity = PGL2.point((1, 0, 0, 1))
    pi1 = PGL2.analytic_fundamental_group(identity)

    assert pi1.cardinality() == 2
    assert pi1.is_abelian()


def test_normalizing_the_nodal_cubic_induces_the_trivial_map_into_infinite_cyclic_pi1() -> None:
    r"""For ``C: y^2 z = x^3 + x^2 z``, ``pi_1(C(CC)) = ZZ`` and ``pi_1(P^1(CC)) = 1``.

    ``C(CC)`` is a sphere with two points identified, homotopy equivalent to
    ``S^2 ∨ S^1`` (Hatcher, *Algebraic Topology*, Example 0.8), and the
    normalization is ``P^1``, simply connected.  The induced map is ``1 -> ZZ``:
    injective, not surjective.  Base point: the smooth point ``[0:1:0]``.
    """
    P2 = Schemes(QQ).projective_space(2, names=("x", "y", "z"))
    x = P2.coordinate_ring().algebra_generator("x")
    y = P2.coordinate_ring().algebra_generator("y")
    z = P2.coordinate_ring().algebra_generator("z")
    C = P2.closed_subscheme(y**2 * z - x**3 - x**2 * z)
    p = C.point((0, 1, 0))
    induced = C.normalization_morphism().induced_map_on_fundamental_groups(p)

    assert induced.domain().cardinality() == 1
    assert induced.codomain().is_abelian()
    assert induced.codomain().abelian_invariants() == (0,)
    assert induced.is_injective()
    assert not induced.is_surjective()
