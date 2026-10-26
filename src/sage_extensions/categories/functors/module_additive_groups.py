r"""The forgetful functor from left modules to abelian groups."""

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.magmas import AdditiveGroups


class UnderlyingAdditiveGroupFunctor(Functor):
    r"""Forget the scalar action and retain the chosen underlying additive group."""

    _faithful = True

    def __init__(self, modules) -> None:
        super().__init__(modules, AdditiveGroups().AdditiveCommutative())

    def _apply_object(self, module):
        return module.underlying_additive_group()

    def _apply_morphism(self, morphism):
        source = morphism.domain()
        target = morphism.codomain()
        mor = self.codomain().Mor(self(source), self(target))
        return mor.elementwise(
            lambda element: target._underlying_additive_element(morphism(source(element)))
        )

    def _repr_(self):
        return "Underlying additive group functor"
