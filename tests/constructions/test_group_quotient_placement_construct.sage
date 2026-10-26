from sage_extensions.all import *


def test_group_quotient_by_relators_is_asked_at_the_group_owner() -> None:
    group = Groups.S(3)

    assert group not in GroupsWithChosenFinitePresentation()
    group.quotient_by_relators((group.one(),))
