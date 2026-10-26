r"""Relative spectra of quasi-coherent algebras glued on a Zariski cover of the line.

Source: Hartshorne, *Algebraic Geometry*, Exercise II.5.17(c)--(d): for a
quasi-coherent ``O_Y``-algebra ``A`` there is a unique ``f: Spec A -> Y`` with
``f^{-1}(V) = Spec A(V)`` for every open affine ``V``, and ``f`` is affine.  Taking
``V = Y`` for affine ``Y = Spec QQ[x]`` gives ``Spec A = Spec A(Y)``.  The algebra
``QQ[x][z]/(z^2 - x)`` is free of rank 2 over ``QQ[x]`` on ``1, z``, so its relative
spectrum is finite of degree 2; ``Spec_Y O_Y = Y`` by the same uniqueness.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _line_and_cover():
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    return ring, x, line, line.distinguished_open_cover(x, x - ring.one())


def _square_root_of_x_algebra(algebra):
    polynomial = algebra.polynomial_ring("z")
    z = polynomial.algebra_generator("z")
    return polynomial.quotient_ring(polynomial.ideal(z**2 - polynomial(algebra.algebra_generator("x"))))


def test_relative_spec_over_an_affine_line_is_spec_of_the_global_algebra() -> None:
    r"""``Spec_Y(A~) = Spec A`` for ``Y = Spec QQ[x]`` and ``A = QQ[x, z]/(z^2 - x)``, finite of degree 2."""
    ring = QQ.polynomial_ring("x")
    line = ring.affine_spectrum()
    plane = QQ.polynomial_ring(("x", "z"))
    x, z = plane.algebra_generator("x"), plane.algebra_generator("z")
    algebra = plane.quotient_ring(plane.ideal(z**2 - x))
    structure = ring.Mor(algebra)({"x": algebra(x)})

    relative = line.relative_spectrum(structure)

    assert relative.arrow().codomain() is line
    assert relative.arrow().domain().is_isomorphic(algebra.affine_spectrum())
    assert relative.arrow().is_finite()
    assert relative.arrow().degree() == 2


def test_relative_spec_of_the_glued_square_root_of_x_is_a_double_cover_of_the_line() -> None:
    r"""``O[z]/(z^2 - x)`` glued on ``D(x) cup D(x - 1)``: its relative spectrum is finite of degree 2 over ``A^1``."""
    _ring, _x, line, cover = _line_and_cover()
    local_algebras = tuple(_square_root_of_x_algebra(open_.coordinate_ring()) for open_ in cover.opens())
    left = cover.restrict_algebra(local_algebras[0], 0, 1)
    right = cover.restrict_algebra(local_algebras[1], 1, 0)
    transition = left.Mor(right)({"z": right.algebra_generator("z")})

    relative = cover.glue_algebras(local_algebras, {(0, 1): transition}).relative_spectrum()

    assert relative.arrow().codomain() is line
    assert relative.arrow().is_finite()
    assert relative.arrow().degree() == 2


def test_relative_spec_of_the_structure_sheaf_is_the_base() -> None:
    r"""``Spec_Y O_Y -> Y`` is an isomorphism: glue the chart rings by the identity."""
    _ring, _x, line, cover = _line_and_cover()
    local_algebras = tuple(open_.coordinate_ring() for open_ in cover.opens())
    left = cover.restrict_algebra(local_algebras[0], 0, 1)
    right = cover.restrict_algebra(local_algebras[1], 1, 0)
    transition = left.Mor(right).identity()

    relative = cover.glue_algebras(local_algebras, {(0, 1): transition}).relative_spectrum()

    assert relative.arrow().codomain() is line
    assert relative.arrow().is_isomorphism()
