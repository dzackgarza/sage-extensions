r"""A cyclic cover retains its affine quotient and invariant-algebra inclusion."""

from sage_extensions.all import *  # noqa: F401,F403


def test_double_cover_affine_quotient_is_base_with_invariant_inclusion() -> None:
    base = QQ["x"]
    x = base.algebra_generator("x")
    cover = CyclicCovers(base, 2)(x**4 - 1)
    inclusion = cover.invariant_algebra_inclusion()

    assert cover.affine_quotient() is cover.base_scheme()
    assert inclusion.domain() is base
    assert inclusion.codomain() is cover.coordinate_algebra()
    assert inclusion(x) == cover.coordinate_algebra()(x)
