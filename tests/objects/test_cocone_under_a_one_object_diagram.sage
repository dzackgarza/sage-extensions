from sage_extensions.all import *


def three():
    return Sets.Δ[2]


def diagram():
    r"""The diagram $\{*\} \to \mathbf{Set}$ picking out a three-element set $S$."""
    return Cat().Mor(DiscreteCategory(Sets.Δ[0]), Sets()).discrete_diagram(lambda index: three())


def identity_cocone():
    r"""$(S, \mathrm{id}_S)$, a colimit cocone under the one-object diagram at $S$."""
    return diagram().Cocones().cocone(three(), lambda index: Sets().Mor(three(), three()).identity())


def test_the_cocone_is_an_object_of_the_cocone_category() -> None:
    assert identity_cocone() in diagram().Cocones()
    assert diagram().Cocones() in Cat()


def test_the_apex_and_the_leg() -> None:
    cocone = identity_cocone()
    assert cocone.apex() is three()
    assert cocone.diagram() is diagram()
    assert cocone.costructure_morphisms().cardinality() == 1


def test_the_identity_cocone_is_initial_among_cocones_on_itself() -> None:
    r"""A cocone morphism $(S, \mathrm{id}) \to (S, \mathrm{id})$ is an $f$ with $f\circ\mathrm{id} = \mathrm{id}$, so $f = \mathrm{id}$."""
    cocone = identity_cocone()
    assert diagram().Cocones().Mor(cocone, cocone).cardinality() == 1


def test_the_cocone_has_one_endomorphism_category() -> None:
    cocone = identity_cocone()
    cocones = diagram().Cocones()
    identity = cocones.Mor(cocone, cocone).identity()
    assert cocones.Mor(cocone, cocone) is cocones.Mor(cocone, cocone)
    assert identity * identity == identity
    assert identity.apex_map() == Sets().Mor(three(), three()).identity()
