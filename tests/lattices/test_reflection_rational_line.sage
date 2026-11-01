r"""Reflection is a function of the rational line, not of the chosen vector.

``s_r(x) = x - 2 b(x,r)/b(r,r) r`` is unchanged when ``r`` is scaled by a
nonzero rational, because the scalar cancels: ``s_{lambda r} = s_r``.  The
coefficients ``2 b(x,r)/b(r,r)`` do not cancel, so they are not a property of
the line.  On ``U`` the vector ``e - f`` has square ``-2`` and its reflection
swaps the two isotropic generators; the double ``2(e - f)`` has square ``-8``
and half-integral coefficients against the same integral images.  Both state
the same isometry.

``is_integral_reflection_vector`` tests the coefficients of the representative
it is given, so it answers ``False`` for the double; ``reflection`` reads the
primitive vector of the line, which is the representative the decision belongs
to.
"""

from sage_extensions.all import *

import pytest


def _hyperbolic_plane():
    lattice = Lattices(ZZ)("U")
    return lattice, lattice.basis_vector(0), lattice.basis_vector(1)


def test_the_doubled_root_defines_the_reflection_of_the_root() -> None:
    lattice, e, f = _hyperbolic_plane()
    root = e - f
    doubled = ZZ(2) * root

    assert root.q() == ZZ(-2)
    assert doubled.q() == ZZ(-8)
    assert root.is_integral_reflection_vector()
    assert not doubled.is_integral_reflection_vector()
    assert doubled.primitive_part() == root

    assert lattice.reflection(root)(e) == f
    assert lattice.reflection(doubled)(e) == f
    assert lattice.reflection(doubled)(f) == e
    assert lattice.reflection(doubled) == lattice.reflection(root)


def test_the_doubled_reflection_is_an_involution_of_the_lattice() -> None:
    lattice, e, f = _hyperbolic_plane()
    reflection = lattice.reflection(ZZ(3) * (e - f))

    assert reflection * reflection == lattice.Aut().identity()
    assert reflection in lattice.Aut()
    assert reflection(e + f) == e + f


def test_a_line_with_no_integral_reflection_vector_is_refused() -> None:
    lattice, e, f = _hyperbolic_plane()
    # 2 e + f is primitive, and 2 b(x, 2e + f)/b(2e + f, 2e + f) = 1/2 for x = e.
    vector = ZZ(2) * e + f
    assert vector.content() == ZZ(1)
    assert not vector.is_integral_reflection_vector()

    with pytest.raises(ValueError):
        lattice.reflection(vector)
    with pytest.raises(ValueError):
        lattice.reflection(ZZ(2) * vector)


def test_a_nonprimitive_integral_reflection_vector_still_reflects() -> None:
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 2, 0], [0, 0, -2]])
    first = lattice.module_generator(0)
    doubled = ZZ(2) * first

    # Here the double is itself an integral reflection vector, so no
    # normalization is needed; the answer must be the same either way.
    assert doubled.is_integral_reflection_vector()
    assert not doubled.is_root()
    assert lattice.reflection(doubled) == lattice.reflection(first)
    assert lattice.reflection(doubled)(first) == -first
