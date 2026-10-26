r"""Modules over varying commutative base rings.

The Grothendieck category of modules contains every ordinary ``R``-module while
retaining its scalar ring.  On a fixed fibre its identity arrow is the usual
module identity, and its elements are the same owned module elements.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_fixed_fibre_module_is_an_object_over_commutative_rings() -> None:
    module = ZZ.free_module(2)
    element = module.module_generator(0)
    category = ModulesOverCommutativeRings()

    assert module in category
    assert module.base_ring() is ZZ
    assert isinstance(element, category.ElementType)


def test_fibered_module_identity_is_the_fixed_fibre_identity() -> None:
    module = ZZ.free_module(2)
    category = ModulesOverCommutativeRings()
    identity = category.Mor(module, module).identity()

    assert identity(module.module_generator(0)) == module.module_generator(0)
    assert identity * identity == identity
