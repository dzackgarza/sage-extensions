from sage_extensions.all import *


def test_the_simple_reflection_s1_of_A2_negates_a1_and_sends_a2_to_a1_plus_a2() -> None:
    r"""\(s_1(x) = x - 2\frac{b(x, a_1)}{b(a_1, a_1)} a_1\) with \(b(a_1, a_1) = -2\) and
    \(b(a_1, a_2) = 1\) gives \(s_1(a_1) = -a_1\), \(s_1(a_2) = a_1 + a_2\)."""
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.simple_roots()
    reflection = lattice.reflection(first)

    assert reflection(first) == -first
    assert reflection(second) == first + second
    assert reflection(second).q() == second.q()
    assert reflection * reflection == lattice.Aut().one()
    assert reflection != lattice.Aut().one()
