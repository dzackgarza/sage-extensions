r"""Transporters of ``O(U_QQ)`` between commensurable lattices in ``U tensor QQ``."""

from sage_extensions.all import *


def test_diagonal_rescaling_of_the_hyperbolic_basis_is_a_rational_isometry() -> None:
    r"""``ZZe + ZZf`` and ``ZZ(2e) + ZZ(f/2)`` lie in one ``O(U_QQ)``-orbit.

    With ``b(e,f) = 1`` and ``e, f`` isotropic, ``diag(2, 1/2)`` preserves the
    form and carries the first lattice onto the second.
    """
    plane = Lattices(QQ)("U")
    e, f = plane.module_generators()
    source = plane.span([e, f], ZZ)
    target = plane.span([2 * e, f / 2], ZZ)

    transporter = plane.O().transporter(source, target)
    assert not transporter.is_empty()
    g = transporter.an_element()
    assert plane.b(g(e), g(f)) == 1
    assert plane.b(g(e), g(e)) == 0
    assert all(g(v) in target for v in source.module_generators())
    assert all((~g)(w) in source for w in target.module_generators())


def test_commensurable_lattices_of_different_determinant_share_no_orbit() -> None:
    r"""``ZZe + ZZf`` (determinant ``-1``) and ``ZZ(2e) + ZZf`` (determinant ``-4``)
    are not isometric, so no element of ``O(U_QQ)`` carries one onto the other.
    """
    plane = Lattices(QQ)("U")
    e, f = plane.module_generators()
    source = plane.span([e, f], ZZ)
    target = plane.span([2 * e, f], ZZ)

    assert source.determinant() == -1
    assert target.determinant() == -4
    assert plane.O().transporter(source, target).is_empty()
