r"""Isotypic decompositions of integral representations of cyclic groups."""

from sage_extensions.all import *


def test_the_swap_on_ZZ2_has_isotypic_components_ZZ_1_1_and_ZZ_1_minus_1_of_index_two() -> None:
    r"""``ZZ(1,1) + ZZ(1,-1)`` has determinant ``-2``, so index 2 in ``ZZ^2``."""
    group = Groups.C(2)
    module = ZZ.free_module(2)
    x, y = module.module_generators()
    swap = module.Mor(module)({0: y, 1: x})

    def action(group_element, vector):
        return vector if group_element == group.one() else swap(vector)

    acted = Modules(ZZ[group])(module, action)
    decomposition = acted.isotypic_decomposition()
    plus = decomposition.trivial_component()
    minus = decomposition.nontrivial_components()[0]

    assert decomposition.isotypic_characters().cardinality() == 2
    assert plus.module_rank() == 1
    assert minus.module_rank() == 1
    assert plus.inclusion().is_in_image(acted(x + y))
    assert minus.inclusion().is_in_image(acted(x - y))
    assert decomposition.index() == 2


def test_the_permutation_module_of_C3_splits_rationally_into_degrees_one_and_two_with_index_three() -> None:
    r"""``ZZ^3 = ZZ(1,1,1) + {sum = 0}`` up to index ``det[(1,1,1),(1,-1,0),(0,1,-1)] = 3``."""
    group = Groups.C(3)
    generator = next(iter(group.group_generators()))
    module = ZZ.free_module(3)
    x, y, z = module.module_generators()
    cycle = module.Mor(module)({0: y, 1: z, 2: x})

    def action(group_element, vector):
        exponent = next(k for k in range(3) if group_element == generator**k)
        for _ in range(exponent):
            vector = cycle(vector)
        return vector

    acted = Modules(ZZ[group])(module, action)
    characters = acted.isotypic_characters()
    decomposition = acted.isotypic_decomposition()

    assert characters.cardinality() == 2
    assert Set(character.degree() for character in characters) == Set((ZZ(1), ZZ(2)))
    assert decomposition.trivial_component().module_rank() == 1
    assert decomposition.nontrivial_components()[0].module_rank() == 2
    assert decomposition.index() == 3


def test_group_lattice_invariants_and_formed_coinvariants_keep_the_form() -> None:
    group = Groups.C(2)
    lattice = Lattices(ZZ)("U")
    labels = lattice.module_generating_set()
    x, y = lattice.module_generators()
    swap = lattice.Aut()({labels[0]: y, labels[1]: x})

    def action(group_element, vector):
        return vector if group_element == group.one() else swap(vector)

    acted = Lattices(ZZ[group])(lattice, action)
    decomposition = acted.isotypic_decomposition()
    invariants = acted.invariant_lattice()
    formed_coinvariants = acted.formed_coinvariants()
    module_coinvariants = acted.module_coinvariants()

    assert decomposition.trivial_component().gram_tensor() == invariants.gram_tensor()
    assert decomposition.nontrivial_components()[0].gram_tensor() == formed_coinvariants.gram_tensor()
    assert decomposition.trivial_component().inclusion() == invariants.inclusion()
    assert decomposition.nontrivial_components()[0].inclusion() == formed_coinvariants.inclusion()
    assert invariants.gram_tensor() == tensor(ZZ, (), (1, 1), [[2]])
    assert formed_coinvariants.gram_tensor() == tensor(ZZ, (), (1, 1), [[-2]])
    assert module_coinvariants.module_rank() == 1
    assert module_coinvariants in Modules(ZZ)
    assert module_coinvariants not in FormModules(ZZ)
    assert formed_coinvariants in FormModules(ZZ)
