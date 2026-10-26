r"""Linear Hom objects as modules of represented morphisms.

For the rank-one free module ``M``, ``Hom_ZZ(M,M)`` is a rank-one module.  Its
elements are represented linear maps, evaluation is the ordinary action of a
map on a vector, and conversion to and from the underlying morphism is inverse.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rank_one_endomorphisms():
    module = ZZ.free_module(1)
    homs = module.Mor(module)
    return module, homs


def test_linear_mor_module_retains_source_target_and_base_ring() -> None:
    module, homs = _rank_one_endomorphisms()

    assert homs in LinearMorModules(ZZ)
    assert homs in Modules(ZZ)
    assert homs.base_ring() is ZZ
    assert homs.source_module() is module
    assert homs.target_module() is module


def test_linear_mor_elements_convert_evaluate_and_scale_pointwise() -> None:
    module, homs = _rank_one_endomorphisms()
    generator = module.module_generator(0)
    identity = module.Mor(module).identity()
    element = homs.from_morphism(identity)
    doubled = homs.scalar_multiple(ZZ(2), element)

    assert isinstance(element, homs.ElementType)
    assert homs.as_morphism(element) == identity
    assert homs.evaluation(element, generator) == generator
    assert homs.evaluation(doubled, generator) == 2 * generator


def test_linear_mor_module_morphisms_have_identity() -> None:
    _module, homs = _rank_one_endomorphisms()
    zero = homs.zero()
    identity = Modules(ZZ).Mor(homs, homs).identity()

    assert identity(zero) == zero
    assert identity * identity == identity
