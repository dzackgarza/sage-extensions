r"""A cyclic discriminant module keeps the inverse of its own normalizations.

``<-2>``, ``<2>``, ``<-4>`` and ``<-8>`` have a cyclic discriminant group, so
their discriminant module is presented on one generator.  ``torsion_submodule``
goes through the invariant-factor normalization of that module and of its form;
both are isomorphisms, and an isomorphism retains the inverse it was built with
rather than dropping it at construction.  ``diag(-2,-1)`` is the two-generator
control that already took the other branch.
"""

from sage_extensions.all import *


def test_a_module_automorphism_retains_the_inverse_it_was_built_with() -> None:
    r"""An automorphism is an isomorphism: its inverse is computed, not dropped."""
    module = ZZ.free_module(2)
    labels = tuple(module.module_generating_set())
    first = module.module_generator(labels[0])
    second = module.module_generator(labels[1])
    swap = module.Aut()((second, first))
    assert (~swap)(swap(first)) == first
    assert swap((~swap)(second)) == second
    assert (~swap)(second) == first


def test_a_cyclic_discriminant_module_has_its_torsion_submodule() -> None:
    cases = ((([[-2]]), 2), (([[2]]), 2), (([[-4]]), 4), (([[-8]]), 8))
    for matrix, expected in cases:
        lattice = Lattices(ZZ)(matrix)
        module = lattice.discriminant_module()
        assert module.cardinality() == expected
        torsion = module.torsion_submodule()
        assert torsion.cardinality() == expected
        inclusion = torsion.inclusion()
        assert inclusion.domain() is torsion
        assert inclusion.codomain() is module
        assert inclusion.is_injective()
    # The two-generator control, whose discriminant is cyclic of order two.
    control = Lattices(ZZ)([[-2, 0], [0, -1]]).discriminant_module()
    assert control.torsion_submodule().cardinality() == 2


def test_the_discriminant_form_normalization_retains_its_inverse() -> None:
    for matrix in ([[-2]], [[2]], [[-4]]):
        module = Lattices(ZZ)(matrix).discriminant_module()
        normalized = module.invariant_factor_form()
        forward = normalized.forward()
        inverse = normalized.inverse()
        for label in module.module_generating_set():
            generator = module.module_generator(label)
            assert inverse(forward(generator)) == generator, (matrix, label)
