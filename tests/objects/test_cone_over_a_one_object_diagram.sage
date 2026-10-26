from sage_extensions.all import *


def three():
    return Sets.Δ[2]


def diagram():
    r"""The diagram $\{*\} \to \mathbf{Set}$ picking out a three-element set $S$."""
    return Cat().Mor(DiscreteCategory(Sets.Δ[0]), Sets()).discrete_diagram(lambda index: three())


def identity_cone():
    r"""$(S, \mathrm{id}_S)$, a limit cone over the one-object diagram at $S$."""
    return diagram().Cones().cone(three(), lambda index: Sets().Mor(three(), three()).identity())


def test_the_cone_is_an_object_of_the_cone_category() -> None:
    assert identity_cone() in diagram().Cones()
    assert diagram().Cones() in Cat()


def test_the_apex_and_the_leg() -> None:
    cone = identity_cone()
    assert cone.apex() is three()
    assert cone.diagram() is diagram()
    assert cone.structure_morphisms().cardinality() == 1


def test_the_identity_cone_is_terminal_among_cones_on_itself() -> None:
    r"""A cone morphism $(S, \mathrm{id}) \to (S, \mathrm{id})$ is an $f$ with $\mathrm{id}\circ f = \mathrm{id}$, so $f = \mathrm{id}$."""
    cone = identity_cone()
    assert diagram().Cones().Mor(cone, cone).cardinality() == 1


def test_the_cone_has_one_endomorphism_category() -> None:
    cone = identity_cone()
    cones = diagram().Cones()
    identity = cones.Mor(cone, cone).identity()
    assert cones.Mor(cone, cone) is cones.Mor(cone, cone)
    assert identity * identity == identity
    assert identity.apex_map() == Sets().Mor(three(), three()).identity()
