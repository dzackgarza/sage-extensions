r"""Invariants of plane curve singularities at the origin over QQ.

Source: Greuel, Lossen, Shustin, *Introduction to Singularities and Deformations*,
I.2 (Milnor and Tjurina numbers; `\mu = \tau` for quasihomogeneous germs, and
`\mu(x^a + y^b) = (a - 1)(b - 1)`), I.2.4 (the ADE normal forms `A_k: x^2 + y^{k+1}`,
`D_k: x^2 y + y^{k-1}`, `E_6, E_7, E_8` with `\mu = k`) and I.3.4 (`\delta`, branches,
Milnor's formula `\mu = 2\delta - r + 1`).
"""

from sage_extensions.all import *


def _plane():
    plane = QQ.polynomial_ring(("x", "y"))
    return plane, plane.algebra_generator("x"), plane.algebra_generator("y")


def test_the_cusp_has_milnor_and_tjurina_number_two() -> None:
    plane, x, y = _plane()
    cusp = IsolatedHypersurfaceSingularity(plane, y**2 - x**3)

    assert cusp.milnor_number() == 2
    assert cusp.tjurina_number() == 2
    assert cusp.milnor_algebra().dimension() == 2


def test_the_node_has_milnor_and_tjurina_number_one_and_a_two_dimensional_tangent_space() -> None:
    plane, x, y = _plane()
    node = IsolatedHypersurfaceSingularity(plane, x**2 + y**2)

    assert node.milnor_number() == 1
    assert node.tjurina_number() == 1
    assert node.zariski_tangent_space().module_rank() == 2
    assert node.is_singular_at_origin()


def test_the_cusp_has_delta_one_one_branch_and_conductor_the_maximal_ideal() -> None:
    r"""The normalization `\mathbb{Q}[[t^2, t^3]] \subset \mathbb{Q}[[t]]` has
    `\delta = \dim \mathbb{Q}[[t]] / \mathbb{Q}[[t^2, t^3]] = 1` and conductor
    `t^2 \mathbb{Q}[[t]] = (x, y)`; Milnor's formula gives `2 \cdot 1 - 1 + 1 = 2`."""
    plane, x, y = _plane()
    cusp = IsolatedHypersurfaceSingularity(plane, y**2 - x**3)
    conductor = cusp.conductor_ideal_at_origin()
    to_local = conductor.ring().localization_map()

    assert cusp.delta_invariant() == 1
    assert cusp.number_of_branches_at_origin() == 1
    assert to_local(x) in conductor
    assert to_local(y) in conductor
    assert to_local(plane.one()) not in conductor


def test_a1_and_a3_germs_have_milnor_equal_tjurina_equal_one_and_three() -> None:
    for label, milnor in (("A1", 1), ("A3", 3)):
        germ = IsolatedHypersurfaceSingularity.from_ade_type(QQ, label)
        assert germ.milnor_number() == milnor
        assert germ.tjurina_number() == milnor


def test_ade_normal_forms_a4_d5_e6_e7_e8_have_milnor_numbers_four_to_eight() -> None:
    for label, milnor in (("A4", 4), ("D5", 5), ("E6", 6), ("E7", 7), ("E8", 8)):
        germ = IsolatedHypersurfaceSingularity.from_ade_type(QQ, label)
        assert germ.ade_normal_form_type() == (label[0], milnor)
        assert germ.milnor_number() == milnor
