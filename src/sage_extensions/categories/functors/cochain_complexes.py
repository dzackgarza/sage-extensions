r"""Forgetful functor from represented cochain complexes to graded modules."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.modules.cochain_complexes import CochainComplexes
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _CochainUnderlyingGradedModuleFunctor(Functor):
    r"""Forget the differential while retaining the same graded module."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(CochainComplexes(self._base_ring), GradedModules(self._base_ring))

    def _apply_object(self, complex_):
        return complex_

    def _apply_morphism(self, morphism):
        return morphism

    def _repr_(self):
        return f"Underlying graded module of cochain complexes over {self._base_ring}"


@cached_function
def _cochain_underlying_graded_module_functor(base_ring):
    return _CochainUnderlyingGradedModuleFunctor(base_ring)


__all__ = []
