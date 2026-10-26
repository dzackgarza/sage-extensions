r"""General modules retain their underlying set, additive group, and scalar action.

The Lebesgue convolution algebra is a real module whose elements are represented
functions rather than coordinate vectors.  It therefore supplies a non-free
specimen of the general module construction.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_lebesgue_convolution_algebra_is_a_general_real_module() -> None:
    module = LebesgueConvolutionAlgebra
    zero = module.zero()
    action = module.scalar_action_input()

    assert module in GeneralModules(RR)
    assert module.underlying_set() in Sets()
    assert module.underlying_additive_group() in AdditiveGroups()
    assert module.module_laws_decision() is True
    assert action.domain() is RR
    assert action.codomain() is module.underlying_additive_group().End()
    assert module.cardinality().is_finite() is False
    assert module.is_finite() is False
    assert isinstance(zero, module.ElementType)
    assert zero.value() == zero.underlying_element()
