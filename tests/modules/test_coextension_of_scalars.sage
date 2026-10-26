r"""Coextension of scalars ``Hom_R(S, -)`` and the ``S``-module constructor from a scalar action.

Specimens: ``S = QQ[x]/(x^2 + 1)`` over ``QQ`` and ``ZZ[S_3]`` over ``ZZ``, both
finitely framed over their scalars.
"""

from sage_extensions.all import *

def _gaussian_rationals():
    r"""``S = QQ[x]/(x^2 + 1)`` with its class ``i`` of ``x`` and its structure map ``QQ -> S``."""
    polynomials = QQ.free_module(["x"]).symmetric_algebra()
    x = next(iter(polynomials.algebra_generators()))
    scalars = (polynomials).quotient_by_relations([x**2 + 1])
    return scalars, scalars(x), scalars.algebra_structure_morphism()


def test_a_module_over_an_algebra_is_constructed_from_its_scalar_action() -> None:
    r"""``QQ^2`` with ``i`` acting by a quarter turn is a ``QQ[i]``-module on which ``i^2 = -1``."""
    scalars, i, _ = _gaussian_rationals()
    plane = QQ.free_module(2)
    endomorphisms = Modules(QQ).End(plane)
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    quarter_turn = endomorphisms({0: e1, 1: -e0})
    identity = endomorphisms.identity()

    labels = scalars.module_generating_set()
    one_label, i_label = labels[0], labels[1]

    def action(scalar):
        coefficients = scalars.framing_morphism().lift(scalar)
        constant = coefficients(one_label)
        imaginary = coefficients(i_label)
        return endomorphisms.scalar_multiple(
            constant,
            identity,
        ) + endomorphisms.scalar_multiple(
            imaginary,
            quarter_turn,
        )

    gaussian_plane = Modules(scalars)(plane, scalars.Mor(endomorphisms)(action))

    assert gaussian_plane in Modules(scalars)
    vector = gaussian_plane(e0 + 2 * e1)
    assert gaussian_plane.scalar_multiple(i, vector) == gaussian_plane(-2 * e0 + e1)
    assert gaussian_plane.scalar_multiple(i, gaussian_plane.scalar_multiple(i, vector)) == -vector
    assert gaussian_plane.scalar_multiple(3 + 2 * i, vector) == gaussian_plane(-e0 + 8 * e1)


def test_coextension_along_a_quadratic_algebra_acts_by_the_right_regular_action() -> None:
    r"""On ``Hom_QQ(S, QQ)`` the action is ``(s . phi)(t) = phi(t s)``, so ``i`` squares to ``-1``."""
    scalars, i, structure_map = _gaussian_rationals()
    line = QQ.free_module(1)
    coextension = Modules(QQ).coextension_of_scalars(structure_map)
    coextended = coextension(line)
    assert coextended in Modules(scalars)

    dual_basis = list(coextended.underlying_set().module_generators())
    phi = coextended(dual_basis[0] + 3 * dual_basis[1])
    acted = coextended.scalar_multiple(i, phi).underlying_element()
    assert acted(scalars.one()) == phi.underlying_element()(i)
    assert acted(i) == -phi.underlying_element()(scalars.one())
    assert coextended.scalar_multiple(i, coextended.scalar_multiple(i, phi)) == -phi


def test_coextension_along_a_group_algebra_is_the_coinduced_module_of_the_trivial_group() -> None:
    r"""``Hom_ZZ(ZZ[G], ZZ)`` is a ``ZZ[G]``-module of rank ``|G|`` whose invariants are the constants."""
    group = Groups.S(3)
    group_algebra = ZZ[group]
    coextension = Modules(ZZ).coextension_of_scalars(
        ZZ.Mor(group_algebra)(lambda integer: integer * group_algebra.one())
    )
    coextended = coextension(ZZ.free_module(1))

    assert coextended in Modules(group_algebra)
    assert coextended.module_rank() == 6
    assert coextended.module_invariants().module_rank() == 1
    assert coextended.module_coinvariants().module_rank() == 1


def test_restriction_is_left_adjoint_to_coextension() -> None:
    r"""The Hom bijection ``Hom_QQ(Res N, M) ~ Hom_S(N, Hom_QQ(S, M))`` round-trips a chosen map."""
    scalars, i, structure_map = _gaussian_rationals()
    free_line = scalars.free_module(1)
    target = QQ.free_module(1)
    adjunction = Modules(scalars).restriction_coextension_adjunction(structure_map)
    restricted = adjunction.left_adjoint()(free_line)
    generator = free_line.module_generator(0)

    unit = adjunction.unit(free_line)
    assert unit(i * generator) == unit.codomain().scalar_multiple(i, unit(generator))

    labels = restricted.module_generating_set()
    weights = restricted.module_category().Mor(restricted, target)(
        {label: (1 + int(labels.ranking_map()(label))) * target.module_generator(0) for label in labels}
    )
    transposed = adjunction.mor_set_isomorphism_forward(weights, free_line)
    assert transposed.domain() is free_line
    recovered = adjunction.mor_set_isomorphism_inverse(transposed, target)
    for label in labels:
        element = restricted.module_generator(label)
        assert recovered(element) == weights(element)


def test_restriction_along_the_structure_map_of_a_group_algebra_forgets_the_action() -> None:
    r"""Along ``ZZ -> ZZ[C2]`` restriction forgets the action and is left adjoint to coextension."""
    group = Groups.C(2)
    group_algebra = ZZ[group]
    structure_map = ZZ.Mor(group_algebra)(lambda integer: integer * group_algebra.one())
    plane = ZZ.free_module(2)
    labels = plane.module_generating_set()
    first, second = labels[0], labels[1]
    e0, e1 = plane.module_generator(first), plane.module_generator(second)

    def swap(group_element, vector):
        if group_element == group.one():
            return vector
        coefficients = vector.to_vector()
        return coefficients(second) * e0 + coefficients(first) * e1

    swapped = Modules(group_algebra)(plane, swap)
    adjunction = Modules(group_algebra).restriction_coextension_adjunction(structure_map)
    forgotten = adjunction.left_adjoint()(swapped)
    assert forgotten in Modules(ZZ)
    assert forgotten.module_rank() == 2

    generator = group.group_generators()[0]
    unit = adjunction.unit(swapped)
    coextended = unit.codomain()
    assert unit(swapped.act(generator, swapped.module_generator(0))) == coextended.act(
        generator, unit(swapped.module_generator(0))
    )

    target = ZZ.free_module(1)
    weights = forgotten.module_category().Mor(forgotten, target)(
        {0: target.module_generator(0), 1: 3 * target.module_generator(0)}
    )
    transposed = adjunction.mor_set_isomorphism_forward(weights, swapped)
    assert transposed.domain() is swapped
    recovered = adjunction.mor_set_isomorphism_inverse(transposed, target)
    for label in forgotten.module_generating_set():
        element = forgotten.module_generator(label)
        assert recovered(element) == weights(element)
