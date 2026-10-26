r"""Relative ``Proj`` of the symmetric algebra of a free module: ``P(O^{n+1}) = P^n_X``.

Source: Hartshorne, *Algebraic Geometry*, II.7 (``P(E) = Proj Sym E``; for
``E = O_X^{n+1}`` it is ``P^n_X``) and Proposition II.7.11(b) (the natural surjection
``pi^* E -> O(1)``).  For a free module of rank 1, ``Sym O = O[T]`` and
``Proj A[T] = Spec (A[T]_T)_0 = Spec A``, so ``P(O_X) -> X`` is an isomorphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_projectivization_of_a_rank_two_space_over_a_point_is_the_projective_line() -> None:
    r"""``P(QQ^2) = Proj QQ[s, t] = P^1_QQ``, one-dimensional over ``Spec QQ``."""
    point = QQ.affine_spectrum()
    projection = point.associated_module_sheaf(QQ.free_module(("s", "t"))).projectivization()

    assert projection.codomain() is point
    assert projection.domain().is_isomorphic(ProjectiveSpaces(QQ)(1))
    assert projection.domain().dimension() == 1


def test_projectivization_of_the_trivial_rank_two_bundle_on_the_line_is_p1_times_the_line() -> None:
    r"""``P(O^2)`` over ``A^1 = Spec QQ[x]`` is ``P^1 x A^1``, with every rational fibre ``P^1``."""
    ring = QQ.polynomial_ring("x")
    line = ring.affine_spectrum()
    projection = line.associated_module_sheaf(ring.free_module(("u", "v"))).projectivization()
    total = projection.domain()

    assert projection.codomain() is line
    assert total.dimension() == 2
    assert total.is_isomorphic(Schemes(QQ).product((ProjectiveSpaces(QQ)(1), line)))
    assert projection.fiber(line.point((3,))).is_isomorphic(ProjectiveSpaces(QQ)(1))


def test_the_universal_quotient_of_the_trivial_rank_two_bundle_is_surjective() -> None:
    r"""Proposition II.7.11(b): ``pi^* O^2 -> O(1)`` is surjective on ``P(O^2)``."""
    ring = QQ.polynomial_ring("x")
    line = ring.affine_spectrum()
    total = line.associated_module_sheaf(ring.free_module(("u", "v"))).projectivization().domain()

    assert total.universal_quotient().is_surjective()
    assert total.tautological_line_bundle().rank() == 1


def test_projectivization_of_the_structure_sheaf_is_the_base() -> None:
    r"""``P(O_X) = Proj O_X[T] = X``: the projection is an isomorphism."""
    line = QQ.polynomial_ring("x").affine_spectrum()

    assert line.structure_sheaf().projectivization().is_isomorphism()


def test_projectivization_commutes_with_extending_scalars_to_a_quadratic_field() -> None:
    r"""``Sym`` commutes with base change, so ``P(QQ^2) x_QQ K = P(K^2) = P^1_K`` for ``K = QQ(sqrt 2)``."""
    field = QuadraticField(2, "s")
    point = QQ.affine_spectrum()
    projection = point.associated_module_sheaf(QQ.free_module(("s", "t"))).projectivization()
    comparison = projection.domain().projectivization_base_change(QQ.Mor(field)(lambda element: field(element)))

    assert comparison.changed_projectivization().domain().is_isomorphic(ProjectiveSpaces(field)(1))
