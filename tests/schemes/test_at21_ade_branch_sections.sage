r"""Branch sections of the ADE double covers of Alexeev--Thompson."""

from sage_extensions.all import *


def _vertices(polytope):
    return {tuple(int(coordinate) for coordinate in vertex) for vertex in polytope.vertices()}


def test_the_d4_branch_divisor_is_twice_the_complementary_divisor_and_a_full_section_has_newton_polygon_q() -> None:
    r"""For the \(D_4\) pair, the branch divisor of the double cover is \(B \sim 2C'\), with \(C'\) the
    complementary (non-blue) boundary, and a section with full support has Newton polygon the ADE polygon \(Q\).

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, §4 (the double cover branched in \(B \in |2C'|\)).
    """
    pair = LogPairs(QQ).at21("D", 4)

    assert pair.branch_divisor_class() == 2 * pair.complementary_divisor()
    section = pair.full_newton_branch_section()
    assert _vertices(pair.branch_newton_polygon(section)) == _vertices(pair.polygon())


def test_the_singular_e8_normal_form_has_newton_polygon_with_vertices_22_03_50() -> None:
    r"""The generic \(E_8\) normal-form section has Newton polygon \(Q\); setting its constant to \(0\)
    gives the singular specialization, whose Newton polygon has vertices \((2,2),(0,3),(5,0)\).

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, Table 5 (\(E_8\)).
    """
    pair = LogPairs(QQ).at21("E", 8)
    generic = pair.source_normal_form_section(constant=1)
    singular = pair.source_normal_form_section(constant=0)

    assert _vertices(pair.branch_newton_polygon(generic)) == _vertices(pair.polygon())
    assert _vertices(pair.branch_newton_polygon(singular)) == {(2, 2), (0, 3), (5, 0)}
