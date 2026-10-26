r"""Cyclic covers of the affine line branched along a section of ``L^n``.

Throughout, ``X = Spec QQ[x]`` is covered by ``U_0 = D(x)`` and ``U_1 = D(1 - x)``,
and ``L`` is the line bundle glued by multiplication by ``x`` from ``U_0`` to
``U_1``.  The section ``s`` of ``L^n`` is ``1`` on ``U_0`` and ``x^n`` on ``U_1``,
which is compatible because ``x^n * 1 = x^n`` on the overlap.  The cyclic cover
algebra is ``A = ⊕_{i<n} L^{-i}`` with ``z^n = s``; on ``U_i`` it is
``O(U_i)[z]/(z^n - s_i)``, free of rank ``n``, and the transition sends
``z ↦ x^{-1} z``, because ``z`` is a local generator of ``L^{-1}``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _cyclic_cover(degree):
    polynomials = QQ["x"]
    x = polynomials.gen()
    line_space = polynomials.affine_spectrum()
    cover = line_space.distinguished_open_cover(x, 1 - x)
    line = QuasiCoherentSheaves(line_space)(cover, {(0, 1): x})
    branch = line.tensor_power(degree).section({0: 1, 1: x**degree})
    return AlgebraSheaves(line_space).cyclic_cover(line, branch, degree), x


def test_double_cover_is_locally_z_squared_equals_the_branch_section() -> None:
    cyclic, x = _cyclic_cover(2)
    on_u0, on_u1 = cyclic.local_algebra(0), cyclic.local_algebra(1)
    z0, z1 = on_u0.algebra_generator("z"), on_u1.algebra_generator("z")

    assert on_u0.module_rank() == 2
    assert on_u1.module_rank() == 2
    assert z0**2 == on_u0.one()
    assert z1**2 == on_u1(x**2)
    assert z1 != on_u1(x)
    transition = cyclic.transition(0, 1)
    assert transition(transition.domain().algebra_generator("z")) == transition.codomain()(x) ** -1 * transition.codomain().algebra_generator("z")


def test_triple_cover_is_locally_free_of_rank_three() -> None:
    cyclic, x = _cyclic_cover(3)
    on_u1 = cyclic.local_algebra(1)
    z1 = on_u1.algebra_generator("z")

    assert cyclic.local_algebra(0).module_rank() == 3
    assert on_u1.module_rank() == 3
    assert z1**3 == on_u1(x**3)
    assert z1**2 != on_u1(x**2)
    transition = cyclic.transition(0, 1)
    assert transition(transition.domain().algebra_generator("z")) == transition.codomain()(x) ** -1 * transition.codomain().algebra_generator("z")


def test_deck_transformation_of_the_double_cover_is_an_involution_over_the_base() -> None:
    r"""The ``μ_2``-action ``z ↦ -z`` gives ``σ`` with ``σ^2 = id`` and ``π σ = π``,
    and ``σ ≠ id`` since ``-z ≠ z`` in characteristic 0."""
    cyclic, _ = _cyclic_cover(2)
    projection = cyclic.relative_spectrum()
    involution = cyclic.constant_deck_transformation()
    double_cover = projection.domain()

    assert involution * involution == double_cover.Mor(double_cover).identity()
    assert involution != double_cover.Mor(double_cover).identity()
    assert projection * involution == projection
