r"""Restriction of scalars retains the original module and scalar map.

Viewing the one-dimensional ``QQ``-vector space as a ``ZZ``-module along the
canonical inclusion changes only its scalar action; its additive group and
underlying elements are unchanged.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rational_line_over_the_integers():
    extension_module = QQ.free_module(1)
    ring_map = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    restricted = extension_module.restrict_scalars(ring_map)
    return extension_module, ring_map, restricted


def test_restricted_scalars_retains_extension_module_ring_map_and_additive_group() -> None:
    extension_module, ring_map, restricted = _rational_line_over_the_integers()

    assert restricted in RestrictedScalarsModules(ZZ)
    assert restricted in Modules(ZZ)
    assert restricted.extension_ring() is QQ
    assert restricted.module_over_extension() is extension_module
    assert restricted.ring_map() is ring_map
    assert restricted.underlying_additive_group() is extension_module.underlying_additive_group()


def test_restricted_scalar_elements_wrap_the_same_underlying_vector() -> None:
    extension_module, _ring_map, restricted = _rational_line_over_the_integers()
    vector = extension_module.module_generator(0)
    wrapped = restricted.wrap(vector)

    assert isinstance(wrapped, restricted.ElementType)
    assert wrapped.underlying_element() == vector
    assert restricted.scalar_multiple(ZZ(2), wrapped).underlying_element() == 2 * vector
    assert restricted.zero().underlying_element() == extension_module.zero()
    assert restricted.an_element() in restricted


def test_restricted_scalars_module_morphisms_have_identity() -> None:
    _extension_module, _ring_map, restricted = _rational_line_over_the_integers()
    identity = restricted.Mor(restricted).identity()

    assert identity(restricted.zero()) == restricted.zero()
    assert identity * identity == identity
