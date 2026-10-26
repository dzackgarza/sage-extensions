r"""The algebra QQ[x,y]/(x^2-y^3) realizes the pushout of t↦x² and t↦y³."""

from sage_extensions.all import *  # noqa: F401,F403


def _cuspidal_pushout():
    category = Algebras(QQ).Associative().Unital().Commutative()
    parameter = QQ.polynomial_ring("t")
    first = QQ.polynomial_ring("x")
    second = QQ.polynomial_ring("y")
    t = parameter.algebra_generator("t")
    x = first.algebra_generator("x")
    y = second.algebra_generator("y")
    square = parameter.Mor(first)({"t": x**2})
    cube = parameter.Mor(second)({"t": y**3})
    return category.pushout(square, cube), square, cube


def test_cuspidal_pushout_retains_its_span_and_commuting_maps() -> None:
    pushout, square, cube = _cuspidal_pushout()
    maps = pushout.pushout_maps()
    span = pushout.pushout_span()

    assert pushout in CommutativeAlgebraPushouts(QQ)
    assert span[0] == square
    assert span[1] == cube
    assert maps[0] == pushout.left_pushout_map()
    assert maps[1] == pushout.right_pushout_map()
    assert pushout.left_pushout_map() * square == pushout.right_pushout_map() * cube
    assert isinstance(pushout.one(), pushout.ElementType)


def test_cuspidal_pushout_factorizes_a_compatible_cocone() -> None:
    pushout, _, _ = _cuspidal_pushout()
    first = pushout.left_pushout_map().domain()
    second = pushout.right_pushout_map().domain()
    target = QQ.polynomial_ring("z")
    z = target.algebra_generator("z")
    left = first.Mor(target)({"x": z**3})
    right = second.Mor(target)({"y": z**2})
    induced = pushout.from_pushout_cocone(left, right)

    assert induced * pushout.left_pushout_map() == left
    assert induced * pushout.right_pushout_map() == right

