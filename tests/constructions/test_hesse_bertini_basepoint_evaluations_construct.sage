r"""The Hesse pencil exposes value and first-jet evaluation at its basepoint."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hesse_basepoint_value_evaluation_is_the_order_one_jet_map() -> None:
    hesse = HesseBertiniFamily()
    evaluation = hesse.basepoint_value_evaluation()

    assert evaluation.domain() is hesse.linear_system().selected_section_space()
    assert evaluation.codomain().jet_point() is hesse.basepoint()
    assert evaluation.codomain().jet_order() == 1


def test_hesse_basepoint_first_jet_evaluation_is_the_order_two_jet_map() -> None:
    hesse = HesseBertiniFamily()
    evaluation = hesse.basepoint_first_jet_evaluation()

    assert evaluation.domain() is hesse.linear_system().selected_section_space()
    assert evaluation.codomain().jet_point() is hesse.basepoint()
    assert evaluation.codomain().jet_order() == 2
