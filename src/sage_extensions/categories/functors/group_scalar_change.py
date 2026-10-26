r"""Scalar extension and restriction for modules carrying a fixed group action.

For a ring morphism ``f:R -> S`` and a fixed group ``G`` the ordinary
extension/restriction adjunction lifts to representation categories:

``S tensor_R - ⊣ Res_f : R[G]-Mod <-> S[G]-Mod``.

The group action is transported, not recomputed.  Restrict a group module to
its represented ``G``-object, transport that action through the ordinary
module scalar-change functor, then linearize it again.  Objects and arrows use
that same composite, so this file owns no second scalar-change algorithm.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _GroupModuleScalarExtensionFunctor(Functor):
    r"""``S tensor_R - : R[G]-Mod -> S[G]-Mod`` along one scalar map."""

    def __init__(self, ring_map, group, scalar_extension) -> None:
        self._ring_map = ring_map
        self._group = group
        self._source_ring = _owned_ring(ring_map.domain())
        self._target_ring = _owned_ring(ring_map.codomain())
        source = Modules(self._source_ring[group])
        target = Modules(self._target_ring[group])
        self._transport = (
            source.restriction_along_group_inclusion()
            .then(GObjects(group, Modules(self._source_ring)).transport(scalar_extension))
            .then(target.linearization())
        )
        super().__init__(source, target)

    def ring_map(self):
        return self._ring_map

    def group(self):
        return self._group

    def _apply_object(self, group_module):
        r"""Transport the represented action through the ordinary scalar-extension functor."""
        return self._transport(group_module)

    def _apply_morphism(self, morphism):
        return self._transport(morphism)

    def _repr_(self):
        return f"Scalar extension of {self.group()}-modules along {self.ring_map()}"


class _GroupModuleRestrictionOfScalarsFunctor(Functor):
    r"""``Res_f : S[G]-Mod -> R[G]-Mod``."""

    def __init__(self, ring_map, group, restriction) -> None:
        self._ring_map = ring_map
        self._group = group
        self._source_ring = _owned_ring(ring_map.domain())
        self._target_ring = _owned_ring(ring_map.codomain())
        source = Modules(self._target_ring[group])
        target = Modules(self._source_ring[group])
        self._transport = (
            source.restriction_along_group_inclusion()
            .then(GObjects(group, Modules(self._target_ring)).transport(restriction))
            .then(target.linearization())
        )
        super().__init__(source, target)

    def ring_map(self):
        return self._ring_map

    def group(self):
        return self._group

    def _apply_object(self, group_module):
        return self._transport(group_module)

    def _apply_morphism(self, morphism):
        return self._transport(morphism)

    def _repr_(self):
        return f"Restriction of {self.group()}-modules along {self.ring_map()}"


class _GroupModuleBaseChangeAdjunction(Adjunction):
    r"""``S tensor_R - ⊣ Res_f`` on modules carrying a fixed ``G``-action."""

    def __init__(self, ring_map, group) -> None:
        self._ring_map = ring_map
        self._group = group
        self._underlying = Modules(ring_map.domain()).base_change_adjunction(ring_map)
        super().__init__(
            _GroupModuleScalarExtensionFunctor(
                ring_map, group, self._underlying.left_adjoint()
            ),
            _GroupModuleRestrictionOfScalarsFunctor(
                ring_map, group, self._underlying.right_adjoint()
            ),
        )

    def _underlying_adjunction(self):
        return self._underlying

    def _unit_component(self, group_module):
        extended = self.left_adjoint()(group_module)
        restricted = self.right_adjoint()(extended)
        underlying = self._underlying_adjunction()
        source_module = group_module.unformed_module()
        unit = underlying.unit(source_module)
        return group_module.Mor(restricted)._from_equivariant_images(
            unit,
        )

    def _counit_component(self, group_module):
        restricted = self.right_adjoint()(group_module)
        extended = self.left_adjoint()(restricted)
        underlying = self._underlying_adjunction()
        target_module = group_module.unformed_module()
        counit = underlying.counit(target_module)
        return extended.Mor(group_module)._from_equivariant_images(
            counit,
        )

    def _repr_(self):
        return (
            f"Scalar-extension/restriction adjunction for {self._group}-modules "
            f"along {self._ring_map}"
        )


@cached_function
def _group_module_base_change_adjunction(ring_map, group) -> _GroupModuleBaseChangeAdjunction:
    return _GroupModuleBaseChangeAdjunction(ring_map, group)


__all__ = []
