r"""Discrete categories, the functors between them, and the object-set functor.

A discrete category has only identity arrows: $\mathrm{Mor}(p, p)$ has one
element and $\mathrm{Mor}(p, q)$ none for $p \ne q$.  A functor
$\mathrm{Disc}(S) \to \mathrm{Disc}(T)$ is the same as a function
$S \to T$, and it sends identities to identities.  Taking object sets is a
functor $\mathrm{Ob}$ from discrete categories to sets, so it sends the
composite $G \circ F$ to the composite of the object maps.  These are the
definitions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _two_letters():
    return DiscreteCategory(Sets()(("p", "q")))


def _three_letters():
    return DiscreteCategory(Sets()(("a", "b", "c")))


class _UndeclaredSetEndofunctor(Functor):
    r"""An identity action whose faithfulness has deliberately not been declared."""

    def __init__(self):
        super().__init__(Sets(), Sets())

    def _apply_object(self, obj):
        return obj

    def _apply_morphism(self, morphism):
        return morphism


def test_a_functor_with_no_faithfulness_declaration_does_not_claim_nonfaithfulness() -> None:
    undeclared = _UndeclaredSetEndofunctor()
    faithful = Sets().power_set_functor()

    assert undeclared.is_faithful() is Unknown
    assert undeclared.then(faithful).is_faithful() is Unknown
    assert faithful.then(undeclared).is_faithful() is Unknown


def test_a_discrete_category_has_only_identity_arrows() -> None:
    letters = _two_letters()
    identity = letters.identity(letters("p"))

    assert letters in DiscreteCategories()
    assert letters.Mor(letters("p"), letters("p")).cardinality() == cardinal(1)
    assert letters.Mor(letters("p"), letters("q")).cardinality() == cardinal(0)
    assert identity * identity == identity


def test_a_function_of_object_sets_is_a_functor_of_discrete_categories() -> None:
    source = _two_letters()
    target = _three_letters()
    functor = Cat().Mor(source, target).from_object_map(lambda value: "b" if value == "p" else "a")
    on_objects = ObjectSetFunctor()(Cat().arrow(functor))

    assert functor(source("p")) is target("b")
    assert functor(source.identity(source("q"))) == target.identity(target("a"))
    assert on_objects(source.object_set()("p")) == target.object_set()("b")


def test_object_map_does_not_define_a_functor_on_nondiscrete_categories() -> None:
    # In Sets, a functor must additionally act on all set morphisms;
    # an object assignment alone does not define that arrow action.
    for domain, codomain in ((Sets(), Sets()), (_two_letters(), Sets())):
        try:
            Cat().Mor(domain, codomain).from_object_map(lambda value: value)
        except TypeError:
            pass
        else:
            raise AssertionError("a nondiscrete functor was admitted from object-map data alone")


def test_taking_object_sets_preserves_composition() -> None:
    source = _two_letters()
    middle = _three_letters()
    point = DiscreteCategory(Sets()(("x",)))
    first = Cat().Mor(source, middle).from_object_map(lambda value: "b" if value == "p" else "a")
    second = Cat().Mor(middle, point).from_object_map(lambda _value: "x")
    composite = first.then(second)

    assert composite(source("q")) is point("x")
    assert ObjectSetFunctor()(Cat().arrow(composite))(source.object_set()("q")) == point.object_set()("x")
