r"""The free-group/underlying-set adjunction ``F ⊣ U``.

The free group on an arbitrary set is an owned group carrying its chosen free
basis.  The corresponding Mor object is supplied by the owned group morphism
layer, so this functor does not choose names, enumerate the source, or pass
through a finite-rank GAP presentation.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.group.groups import (
    Groups,
    OwnedGroups,
)
from sage_extensions.categories.sets.set_categories import Sets


class _FreeGroupFunctor(Functor):
    r"""``F : Set -> Grp``."""

    def __init__(self) -> None:
        super().__init__(Sets(), OwnedGroups())

    def _apply_object(self, set_object):
        return Groups.Free(index_set=set_object)

    def _apply_morphism(self, set_morphism):
        source = self(set_morphism.domain())
        target = self(set_morphism.codomain())
        return source.Mor(target)(
            Sets().Mor(source.free_basis(), target)(
                lambda index: target.free_generator(set_morphism(index)),
            )
        )

    def _repr_(self):
        return "Free-group functor"


class _GroupUnderlyingSetFunctor(Functor):
    r"""``U : Grp -> Set``."""

    _faithful = True

    def __init__(self) -> None:
        super().__init__(OwnedGroups(), Sets())

    def _apply_object(self, group):
        return group

    def _apply_morphism(self, group_morphism):
        r"""``U(f)`` is the function ``f`` computes on points (``CON-17``)."""
        return Sets().Mor(
            group_morphism.domain(),
            group_morphism.codomain(),
        )(lambda element: group_morphism(element))

    def _repr_(self):
        return "Underlying-set functor on groups"


class _FreeGroupUnderlyingSetAdjunction(Adjunction):
    r"""The adjunction ``F : Set <-> Grp : U``."""

    def __init__(self) -> None:
        super().__init__(_FreeGroupFunctor(), _GroupUnderlyingSetFunctor())

    def _unit_component(self, set_object):
        free_group = self.left_adjoint()(set_object)
        return Sets().Mor(set_object, free_group)(free_group.free_generator)

    def _counit_component(self, group):
        free_group = self.left_adjoint()(self.right_adjoint()(group))
        return free_group.Mor(group)(
            Sets().Mor(free_group.free_basis(), group)(
                lambda group_element: group_element,
            )
        )

    def _repr_(self):
        return "Free-group/underlying-set adjunction F ⊣ U"


@cached_function
def _free_group_functor() -> _FreeGroupFunctor:
    return _FreeGroupFunctor()


@cached_function
def _group_underlying_set_functor() -> _GroupUnderlyingSetFunctor:
    return _GroupUnderlyingSetFunctor()


@cached_function
def _free_group_underlying_set_adjunction() -> _FreeGroupUnderlyingSetAdjunction:
    return _FreeGroupUnderlyingSetAdjunction()


__all__ = []
