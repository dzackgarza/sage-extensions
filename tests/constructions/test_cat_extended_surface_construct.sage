r"""Cat exposes functor Mors, meets and joins of categories, and presheaf transport."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cat_functor_mor_contains_the_identity_functor() -> None:
    identity = Sets().identity_functor()
    arrow = Cat().functor_mor(Sets(), Sets())(identity)

    assert arrow.functor() is identity
    assert arrow.domain() is Sets()
    assert arrow.codomain() is Sets()


def test_cat_meet_and_join_follow_category_inclusion_order() -> None:
    finite_modules = Cat().meet((Modules(ZZ), FiniteSets()))
    ambient = Cat().join((Modules(ZZ), FiniteSets()))
    cyclic_two = Modules(ZZ)(Zmod(2))

    assert cyclic_two in finite_modules
    assert finite_modules.is_subcategory(Modules(ZZ))
    assert finite_modules.is_subcategory(FiniteSets())
    assert ambient == Sets()


def test_cat_presheaf_transport_has_expected_endpoints_for_identity_site_map() -> None:
    site = DiscreteCategory(Sets()(("*",)))
    transport = Cat().presheaf_transport(
        IdentityFunctor(site),
        Sets().power_set_functor(),
    )

    assert transport.domain() == site.presheaves(Sets())
    assert transport.codomain() == site.presheaves(Sets())
