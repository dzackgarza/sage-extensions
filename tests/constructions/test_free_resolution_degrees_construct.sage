r"""A one-relation module over (mathbf Z) has free-resolution terms in degrees zero and one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_one_relation_integer_module_resolution_has_degrees_zero_and_one() -> None:
    generators = ZZ.free_module(2)
    relations = ZZ.free_module(1)
    presentation = relations.Mor(generators)(
        {0: 6 * generators.module_generator(0)}
    )
    resolution = presentation.cokernel().free_resolution()
    degrees = resolution.degrees()

    assert degrees.cardinality() == cardinal(2)
    assert 0 in degrees
    assert 1 in degrees
    assert 2 not in degrees
