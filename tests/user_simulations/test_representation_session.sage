r"""A session in representation theory of finite groups over several coefficient rings.

Permutation representations, characters and their inner products, isotypic
decompositions, restriction and induction, Frobenius reciprocity, and the
same objects over the integers and over a field of positive characteristic.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


SESSIONS = {
    # name: (group, degree of natural action, number of orbits on pairs, |Hom_G(perm, perm)|-rank)
    "S3": (lambda: Groups.S(3), 3, 2),
    "S4": (lambda: Groups.S(4), 4, 2),
    "A4": (lambda: Groups.A(4), 4, 2),
    "D4": (lambda: Groups.D(4), 4, 3),
}
COEFFICIENTS = {"QQ": lambda: QQ, "ZZ": lambda: ZZ, "GF(2)": lambda: GF(2), "GF(3)": lambda: GF(3)}


def _permutation_module(ring, group, degree):
    points = tuple(range(1, degree + 1))
    module = ring.free_module(degree)

    def act(g, vector):
        return module.Mor(module)({label: module.module_generator(int(g(points[label])) - 1) for label in range(degree)})(vector)

    return Modules(ring[group])(module, act)


@pytest.mark.parametrize("name", sorted(SESSIONS))
@pytest.mark.parametrize("coefficients", sorted(COEFFICIENTS))
def test_a_representation_theory_session(name, coefficients) -> None:
    build, degree, endomorphism_rank = SESSIONS[name]
    ring = COEFFICIENTS[coefficients]()
    group = build()
    rendered(group)

    # The permutation representation and its invariants.
    permutation = _permutation_module(ring, group, degree)
    rendered(permutation)
    assert permutation in Modules(ring[group])
    assert permutation in Modules(ring)
    assert permutation.module_rank() == cardinal(degree)
    assert permutation.group() is group
    generator = group.group_generators()[0]
    assert permutation.action_of(generator) * permutation.action_of(generator.inverse()) == permutation.action_of(group.one())
    invariants = permutation.module_invariants()
    coinvariants = permutation.module_coinvariants()
    rendered(invariants)
    rendered(coinvariants)
    assert invariants.module_rank() == cardinal(1)
    assert coinvariants.module_rank() == cardinal(1)
    total = sum((permutation.module_generator(label) for label in range(degree)), permutation.zero())
    assert permutation.is_invariant(total)
    assert invariants.inclusion().is_in_image(total)

    # Equivariant endomorphisms: their rank counts orbits on pairs.
    endomorphisms = permutation.Mor(permutation)
    rendered(endomorphisms)
    assert endomorphisms.identity()(total) == total
    assert permutation.equivariant_endomorphism_module().module_rank() == cardinal(endomorphism_rank)

    # Characters over the rationals; Brauer characters in positive characteristic.
    if coefficients == "QQ":
        character = permutation.character()
        rendered(character)
        assert character(group.one()) == degree
        assert character(generator) == sum(1 for point in range(1, degree + 1) if generator(point) == point)
        decomposition = permutation.isotypic_decomposition()
        rendered(decomposition)
        assert decomposition.trivial_component().module_rank() == cardinal(1)
        assert decomposition.index() == 1
        assert permutation.isotypic_characters().cardinality() == cardinal(endomorphism_rank)
        components = decomposition.nontrivial_components()
        assert sum(component.module_rank() for component in components) + 1 == degree
    if coefficients.startswith("GF"):
        brauer = permutation.brauer_character()
        rendered(brauer)
        assert brauer(group.one()) == degree

    # Restriction to a cyclic subgroup, induction back, Frobenius reciprocity.
    subgroup = group.subgroup([generator])
    rendered(subgroup)
    restricted = Modules(ZZ[group]).restriction(subgroup)(permutation)
    rendered(restricted)
    assert restricted.group() is subgroup
    assert restricted.module_rank() == cardinal(degree)
    assert restricted.module_invariants().module_rank() >= cardinal(1)
    trivial = Modules(ring).trivial_action(subgroup)(ring.free_module(1))
    induced = Modules(ZZ[subgroup]).induction(group)(trivial)
    coinduced = Modules(ZZ[subgroup]).coinduction(group)(trivial)
    rendered(induced)
    assert induced.module_rank() == cardinal(group.order() // subgroup.order())
    assert coinduced.module_rank() == induced.module_rank()
    assert induced.module_invariants().module_rank() == cardinal(1)
    adjunction = Modules(ZZ[subgroup]).induction_restriction_adjunction(group)
    unit = adjunction.unit(trivial)
    counit = adjunction.counit(permutation)
    rendered(unit)
    assert unit.domain() is trivial
    assert counit.codomain() is permutation
    transposed = adjunction.hom_set_isomorphism_forward(
        counit, adjunction.right_adjoint()(permutation)
    )
    assert adjunction.hom_set_isomorphism_inverse(transposed, permutation) == counit
    if coefficients == "QQ":
        assert induced.character()(group.one()) == induced.module_rank()
        assert induced.isotypic_decomposition().trivial_component().module_rank() == cardinal(1)
