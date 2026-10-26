r"""Groups expose their selected generator labels and finite class functions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_six_selected_group_generating_set_has_one_label() -> None:
    group = Groups.C(6)

    assert group.group_generating_set().cardinality() == cardinal(1)


def test_cyclic_two_constant_class_function_is_constant_on_both_classes() -> None:
    group = Groups.C(2)
    representatives = group.conjugacy_classes_representatives()
    values = tuple(QQ.one() for _representative in representatives)
    function = group.class_function(QQ, values, representatives=representatives)

    assert all(function(representative) == QQ.one() for representative in representatives)
