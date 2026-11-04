r"""``OwnedAbelianGroups`` and ``FinitelyPresentedTorsionModules`` are public names.

``OwnedAbelianGroups = AbelianGroups`` (a function returning the category of
abelian groups) and ``FinitelyPresentedTorsionModules = Modules.FinitelyPresented.Torsion``
(both in ``categories/group/groups.py`` and ``categories/modules/pure/modules.py``)
were exported from their packages and from neither the session module, so a
consumer could not name either: the first is research's stale ``AbelianGroups``
name, and the second was reported as having "no verified constructor" — it is a
category that takes a base ring once it can be reached.
"""

from sage_extensions.all import (
    AbelianGroups,
    FinitelyPresentedTorsionModules,
    Modules,
    OwnedAbelianGroups,
    OwnedFiniteAbelianGroups,
    ZZ,
)


def test_the_abelian_group_category_is_reachable() -> None:
    assert AbelianGroups is OwnedAbelianGroups
    assert repr(OwnedAbelianGroups()) == "Category of abelian groups"
    assert repr(OwnedFiniteAbelianGroups()).startswith("Category of")


def test_finitely_presented_torsion_modules_take_a_base_ring() -> None:
    category = FinitelyPresentedTorsionModules(ZZ)

    assert category is Modules(ZZ).FinitelyPresented().Torsion()
    assert repr(category) == (
        "Category of finitely presented finitely generated torsion modules over Integer Ring"
    )


def test_the_torsion_category_presents_an_object_inside_itself() -> None:
    category = FinitelyPresentedTorsionModules(ZZ)
    example = category.an_object()

    assert example in category
