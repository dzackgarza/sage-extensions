r"""The distinguished open ``D(x)`` of the quadric cone ``xy = z^2``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_open_set_where_x_is_invertible_on_the_quadric_cone_is_smooth() -> None:
    r"""On ``A = QQ[x, y, z]/(xy - z^2)``, inverting ``x`` gives ``y = z^2/x``, so
    ``A_x = QQ[x, 1/x, z]``, a regular domain of dimension 2: the cone is singular
    only at its vertex, which lies outside ``D(x)`` (Hartshorne, I.5, Ex. 5.1)."""
    presentation = QQ["x, y, z"]
    x = presentation.algebra_generator("x")
    y = presentation.algebra_generator("y")
    z = presentation.algebra_generator("z")
    quadric = presentation.quotient_by_relations([x * y - z**2])
    xbar = quadric.algebra_generator("x")
    ybar = quadric.algebra_generator("y")
    zbar = quadric.algebra_generator("z")
    localized = quadric.localization(xbar)
    to_localized = localized.localization_map()

    cone = quadric.affine_spectrum()
    open_set = cone.distinguished_open(xbar)

    assert to_localized(ybar) == to_localized(zbar) ** 2 * to_localized(xbar).inverse_of_unit()
    assert open_set.dimension() == 2
    assert open_set in SmoothSchemes(QQ)
    assert cone not in SmoothSchemes(QQ)
    assert cone.dimension() == 2
