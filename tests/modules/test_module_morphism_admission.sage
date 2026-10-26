r"""Module-morphism admission keeps laws, derivations, and hypotheses distinct.

These specimens separate actual law decisions from construction-derived maps
and from arbitrary callables whose linearity remains conditional.
"""

import pytest

from sage_extensions.all import *


def _coefficient(module, element, label):
    return module(element).to_vector()(label)


def test_frobenius_on_the_gf4_line_is_additive_but_not_gf4_linear() -> None:
    field = GF(4)
    line = field.free_module(("e",))
    e = line.module_generator("e")
    maps = Modules(field).Mor(line, line)

    def frobenius(element):
        coefficient = _coefficient(line, element, "e")
        return line.scalar_multiple(coefficient * coefficient, e)

    with pytest.raises(ValueError):
        maps.elementwise(frobenius)


def test_module_mor_admits_its_arrow_and_refuses_a_foreign_set_map() -> None:
    r"""A linear arrow is retained; a translation of the underlying set is not linear data."""
    module = ZZ.free_module(Sets.Δ[1])
    first = module.module_generator(0)
    linear = module.End()(lambda label: module.module_generator(label) + first)
    underlying = Modules(ZZ).underlying_set()

    assert module.End()(linear) is linear
    assert underlying(linear).parent() is Sets().Mor(underlying(module), underlying(module))
    assert underlying(linear)(first) == 2 * first

    translation = Sets().Mor(module, module)(lambda vector: vector + first)
    with pytest.raises(TypeError):
        module.End()(translation)
