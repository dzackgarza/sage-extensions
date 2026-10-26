r"""Linear Hom objects form additive groups under pointwise addition."""

from sage_extensions.all import *  # noqa: F401,F403


def test_endomorphisms_of_a_rational_line_have_pointwise_zero_and_addition() -> None:
    line = QQ.free_module(1)
    endomorphisms = line.Mor(line)
    e = line.module_generator(0)
    identity = endomorphisms.identity()
    zero = endomorphisms.zero()

    assert zero(e) == line.zero()
    assert (identity + zero)(e) == e
    assert (identity + identity)(e) == 2 * e

