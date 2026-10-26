r"""An invertible sheaf on the affine line glued from a transition unit."""

from sage_extensions.all import *  # noqa: F401,F403


def test_line_bundle_glued_by_x_has_tensor_powers_glued_by_powers_of_x_and_is_trivial() -> None:
    r"""Glue ``O`` on ``D(x)`` and ``D(1 - x)`` of ``A^1_Q`` along the unit ``x``.

    ``L^2`` has transition ``x^2``, ``L^dual`` has ``x^{-1}``, and
    ``L (x) L^dual`` has transition 1.  ``x`` is a unit on ``D(x)`` already,
    so the cocycle is a coboundary and ``L = O``: ``Pic(A^1_Q) = 0``.
    """
    ring = QQ['x']
    x = ring('x')
    scheme = ring.affine_spectrum()
    cover = scheme.distinguished_open_cover(x, 1 - x)
    overlap_x = scheme.structure_sheaf().restriction_map(scheme, cover.overlap(0, 1))(x)
    one = overlap_x.parent().one()

    line = QuasiCoherentSheaves(scheme)(cover, {(0, 1): overlap_x})
    square = line.tensor_power(2)
    dual = line.dual_sheaf()

    assert line.is_invertible()
    assert line.transition_unit(0, 1) == overlap_x
    assert line.transition_unit(1, 0) * overlap_x == one
    assert square.transition_unit(0, 1) == overlap_x**2
    assert dual.transition_unit(0, 1) * overlap_x == one
    assert line.tensor_product(dual).transition_unit(0, 1) == one
    assert line.is_isomorphic(scheme.structure_sheaf())
    assert scheme.picard_group().cardinality() == 1
