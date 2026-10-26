r"""Sheaves as presheaves equipped with descent data for a coverage.

On the trivial coverage every presheaf satisfies descent canonically.  A
constant two-point presheaf on the one-object discrete site therefore gives the
smallest sheaf specimen while retaining the same presheaf functor and its
canonical descent datum.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _constant_sheaf_on_one_object_site():
    site = DiscreteCategory(Sets.Δ[0])
    presheaves = site.presheaves()
    presheaf = presheaves.constant_functor(Sets.Δ[1])
    descent = DescentData.trivial(presheaf)
    sheaves = Sheaves(descent.coverage(), Sets())
    sheaf = sheaves(presheaf, descent)
    return site, presheaf, descent, sheaves, sheaf


def test_trivial_descent_constructs_a_sheaf_and_retains_its_descent_data() -> None:
    site, presheaf, descent, sheaves, sheaf = _constant_sheaf_on_one_object_site()

    assert sheaves in Cat()
    assert sheaf in sheaves
    assert sheaf in site.presheaves()
    assert sheaf.descent_data() is descent
    assert descent.presheaf() is presheaf
    assert descent.coverage() is TrivialCoveringFamilies(site)
    assert descent.value_category() is Sets()


def test_trivial_sheaf_has_the_same_two_point_value_on_the_site_object() -> None:
    site, _presheaf, _descent, _sheaves, sheaf = _constant_sheaf_on_one_object_site()
    obj = site(0)

    assert sheaf(obj).cardinality() == cardinal(2)


def test_sheaf_morphisms_have_identity() -> None:
    _site, _presheaf, _descent, sheaves, sheaf = _constant_sheaf_on_one_object_site()
    identity = sheaves.Mor(sheaf, sheaf).identity()

    assert identity.domain() is sheaf
    assert identity.codomain() is sheaf
    assert identity * identity == identity
