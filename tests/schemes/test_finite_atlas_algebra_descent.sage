r"""Gluing affine lines along the punctured line.

Two copies of ``A^1 = Spec QQ[x]`` and ``A^1 = Spec QQ[y]``, glued along
``D(x) ≅ D(y)``, give the line with a doubled origin when the transition is
``y -> x`` and the projective line when it is ``y -> 1/x`` (Hartshorne II
Examples 2.3.5 and 2.3.6).  Global functions tell them apart: ``QQ[x]`` in the
first case, ``QQ`` in the second.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _two_lines_glued_by(image_of_y):
    L = QQ['x']
    x = L.gen()
    M = QQ['y']
    y = M.gen()
    U = L.affine_spectrum()
    V = M.affine_spectrum()
    Ux = U.basic_open(x)
    Vy = V.basic_open(y)
    transition = Ux.Mor(Vy)({y: image_of_y(Ux.coordinate_ring()(x))})
    return Schemes(QQ).glue((U, V), {(0, 1): transition}), x


def test_the_line_with_doubled_origin_has_global_functions_qq_x_and_is_not_separated() -> None:
    r"""Gluing along ``y -> x`` gives ``Gamma = QQ[x]``, one-dimensional, non-separated (Hartshorne II Examples 2.3.5 and 4.0.1)."""
    X, x = _two_lines_glued_by(lambda u: u)

    assert X.dimension() == 1
    assert not X.is_separated()
    assert not X.is_affine()
    assert X.global_sections().krull_dimension() == 1
    assert X.global_sections().is_isomorphic(QQ['x'])


def test_the_projective_line_glued_along_y_equals_one_over_x_has_only_constant_functions() -> None:
    r"""Gluing along ``y -> 1/x`` gives ``P^1`` with ``Gamma(P^1, O) = QQ`` (Hartshorne II Ex. 2.3.6)."""
    X, x = _two_lines_glued_by(lambda u: u**-1)

    assert X.dimension() == 1
    assert X.is_separated()
    assert X.is_proper()
    assert X.global_sections().krull_dimension() == 0
    assert X.global_sections().is_isomorphic(QQ)
    assert X.is_isomorphic(Schemes(QQ).projective_space(1))
