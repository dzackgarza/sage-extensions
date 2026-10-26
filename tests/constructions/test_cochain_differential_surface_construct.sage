r"""A cochain differential retains its complex and degreewise components."""

from sage_extensions.all import *  # noqa: F401,F403


def _coordinate_inclusion_complex():
    source = ZZ.free_module(1)
    target = ZZ.free_module(2)
    differential = source.Mor(target)({0: target.module_generator(0)})
    complex_ = CochainComplexes(ZZ)({0: source, 1: target}, {0: differential})
    return source, target, differential, complex_


def test_cochain_differential_retains_its_complex_and_shift() -> None:
    _source, _target, _chosen, complex_ = _coordinate_inclusion_complex()
    differential = complex_.differential()

    assert differential.complex() is complex_
    assert differential.degree_shift() == 1


def test_cochain_differential_component_is_the_selected_degree_zero_map() -> None:
    source, target, chosen, complex_ = _coordinate_inclusion_complex()
    differential = complex_.differential()
    component = differential.component(0)
    generator = source.module_generator(0)

    assert component.domain() is source
    assert component.codomain() is target
    assert component(generator) == chosen(generator)
