r"""Cohomology modules retain their degree, complex, and cycle quotient.

For ``ZZ --2--> ZZ`` in degrees zero and one, ``H^1`` is ``ZZ/2``.  The
class of the degree-one generator is nonzero and every selected cycle
representative maps back to the same cohomology class.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _h1_of_doubling():
    source = ZZ.free_module(1)
    target = ZZ.free_module(1)
    differential = source.Mor(target)({0: 2 * target.module_generator(0)})
    complex_ = CochainComplexes(ZZ)({0: source, 1: target}, {0: differential})
    return target, complex_, complex_.cohomology(1)


def test_cohomology_module_retains_complex_degree_and_cycle_classes() -> None:
    target, complex_, cohomology = _h1_of_doubling()
    cycle = target.module_generator(0)
    cohomology_class = cohomology.class_of_cycle(cycle)
    representative = cohomology.cycle_representative(cohomology_class)

    assert cohomology in CohomologyModules(ZZ)
    assert cohomology.cochain_complex() is complex_
    assert cohomology.cohomological_degree() == 1
    assert cohomology.degree() == 1
    assert cohomology_class != cohomology.zero()
    assert cohomology.class_of_cycle(representative) == cohomology_class
    assert isinstance(cohomology_class, cohomology.ElementType)


def test_cohomology_module_morphisms_have_identity() -> None:
    _target, _complex, cohomology = _h1_of_doubling()
    identity = cohomology.Mor(cohomology).identity()

    assert identity(cohomology.zero()) == cohomology.zero()
    assert identity * identity == identity
