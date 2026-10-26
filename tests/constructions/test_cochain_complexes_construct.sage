r"""Cochain complexes expose their differential, cycles, boundaries, and cohomology.

For the two-term complex ``ZZ -> ZZ^2`` sending ``1`` to the first basis vector,
``H^0=0`` and ``H^1`` is the second coordinate line.  The differential on the
degree-zero generator is exactly the chosen inclusion vector.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coordinate_inclusion_complex():
    source = ZZ.free_module(1)
    target = ZZ.free_module(2)
    differential = source.Mor(target)({0: target.module_generator(0)})
    complex_ = CochainComplexes(ZZ)({0: source, 1: target}, {0: differential})
    return source, target, differential, complex_


def test_cochain_complex_retains_and_applies_its_differential() -> None:
    source, target, differential, complex_ = _coordinate_inclusion_complex()
    generator = source.module_generator(0)

    assert complex_ in CochainComplexes(ZZ)
    assert complex_.differential().degree_shift() == 1
    assert complex_.d(generator) == target.module_generator(0)
    assert isinstance(complex_.zero(), complex_.ElementType)
    assert differential(generator) == target.module_generator(0)


def test_coordinate_inclusion_complex_has_expected_cycles_boundaries_and_cohomology() -> None:
    _source, _target, _differential, complex_ = _coordinate_inclusion_complex()

    assert complex_.cycles(0).cardinality() == 1
    assert complex_.boundaries(1).module_rank() == 1
    assert complex_.cohomology(0).cardinality() == 1
    assert complex_.cohomology(1).module_rank() == 1


def test_cochain_complex_morphisms_have_identity() -> None:
    _source, _target, _differential, complex_ = _coordinate_inclusion_complex()
    identity = complex_.Mor(complex_).identity()

    assert identity.domain() is complex_
    assert identity.codomain() is complex_
    assert identity * identity == identity
