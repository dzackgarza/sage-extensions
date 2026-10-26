r"""Adjunctions for the represented finite category of ``G``-sets.

For a finitely generated group acting on finite represented sets this module
implements

``(-)/G ⊣ Triv_G ⊣ (-)^G``.

When ``G`` itself is finite, the represented finite category is also closed
under the standard free and cofree constructions, giving

``G × - ⊣ U ⊣ Map(G,-)``.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.group.g_sets import (
    FiniteGSets,
    _fixed_point_set,
)
from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.group.groups import _owned_group
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import (
    FiniteSets,
    Sets,
)


class TrivialGSetFunctor(Functor):
    r"""``Triv_G : FinSet -> FinGSet_G``."""

    def __init__(self, group) -> None:
        self._group = _owned_group(group)
        super().__init__(FiniteSets(), FiniteGSets(self._group))

    def group(self):
        return self._group

    def _apply_object(self, set_object):
        return FiniteGSets(self.group()).trivial(set_object)

    def _apply_morphism(self, set_morphism):
        source = self(set_morphism.domain())
        target = self(set_morphism.codomain())
        return source.Mor(target)(set_morphism)

    def _repr_(self):
        return f"Trivial {self.group()}-action on finite sets"


class GSetOrbitsFunctor(Functor):
    r"""``(-)/G : FinGSet_G -> FinSet``."""

    def __init__(self, group) -> None:
        self._group = _owned_group(group)
        super().__init__(FiniteGSets(self._group), FiniteSets())

    def group(self):
        return self._group

    def _apply_object(self, g_set):
        return g_set.orbits()

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return Sets().Mor(source, target)(
            lambda orbit: target.orbit_of(morphism(orbit.representative()))
        )

    def _repr_(self):
        return f"{self.group()}-orbit functor on finite G-sets"


class GSetFixedPointsFunctor(Functor):
    r"""``(-)^G : FinGSet_G -> FinSet``."""

    def __init__(self, group) -> None:
        self._group = _owned_group(group)
        super().__init__(FiniteGSets(self._group), FiniteSets())

    def group(self):
        return self._group

    def _apply_object(self, g_set):
        return _fixed_point_set(g_set)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        # ``f^G`` is the function ``f`` computes on fixed points (``CON-17``).
        return Sets().Mor(source, target)(lambda point: morphism(point))

    def _repr_(self):
        return f"{self.group()}-fixed-point functor on finite G-sets"


class GSetOrbitsTrivialAdjunction(Adjunction):
    r"""``(-)/G ⊣ Triv_G`` on represented finite ``G``-sets."""

    def __init__(self, group) -> None:
        group = _owned_group(group)
        super().__init__(GSetOrbitsFunctor(group), TrivialGSetFunctor(group))

    def _repr_(self):
        return f"Orbit/trivial-action adjunction (-)/G ⊣ Triv_G for {self.right_adjoint().group()}"

    def _unit_component(self, g_set):
        orbit_set = self.left_adjoint()(g_set)
        trivial_orbits = self.right_adjoint()(orbit_set)
        return g_set.Mor(trivial_orbits)(orbit_set.orbit_of)

    def _counit_component(self, set_object):
        trivial = self.right_adjoint()(set_object)
        orbit_set = self.left_adjoint()(trivial)
        return Sets().Mor(orbit_set, set_object)(lambda orbit: orbit.representative())



class GSetTrivialFixedAdjunction(Adjunction):
    r"""``Triv_G ⊣ (-)^G`` on represented finite ``G``-sets."""

    def __init__(self, group) -> None:
        group = _owned_group(group)
        super().__init__(TrivialGSetFunctor(group), GSetFixedPointsFunctor(group))

    def _repr_(self):
        return f"Trivial-action/fixed-point adjunction Triv_G ⊣ (-)^G for {self.left_adjoint().group()}"

    def _unit_component(self, set_object):
        trivial = self.left_adjoint()(set_object)
        fixed = self.right_adjoint()(trivial)
        return Sets().Mor(set_object, fixed)(lambda point: point)

    def _counit_component(self, g_set):
        fixed = self.right_adjoint()(g_set)
        trivial_fixed = self.left_adjoint()(fixed)
        return trivial_fixed.Mor(g_set)(lambda point: point)



class FreeGSetFunctor(Functor):
    r"""``G × - : FinSet -> FinGSet_G`` with left translation on ``G``."""

    def __init__(self, group) -> None:
        self._group = _owned_group(group)
        assert self._group.is_finite() is True, (
            f"G x S is a finite G-set for every finite set S only when G is finite, but {self._group} is not "
            "known to be finite"
        )
        super().__init__(FiniteSets(), FiniteGSets(self._group))

    def group(self):
        return self._group

    def _apply_object(self, set_object):
        group_points = finite_ordered_set(self.group())
        point_set = Sets().product(
            indexed_family(
                Sets.Δ[1],
                lambda index: group_points if int(index) == 0 else set_object,
            )
        )

        def action(group_element, point):
            return point_set(
                lambda index: (
                    group_element * point.component(0)
                    if int(index) == 0
                    else point.component(1)
                )
            )

        return FiniteGSets(self.group())(point_set, action)

    def free_point(self, free_g_set, group_element, point):
        return free_g_set.point_set()(
            lambda index: group_element if int(index) == 0 else point
        )

    def _apply_morphism(self, set_morphism):
        source = self(set_morphism.domain())
        target = self(set_morphism.codomain())
        return source.Mor(target)(
            lambda point: self.free_point(
                target,
                point.component(0),
                set_morphism(point.component(1)),
            )
        )

    def _repr_(self):
        return f"Free finite {self.group()}-set functor"


class UnderlyingFiniteGSetFunctor(Functor):
    r"""``U : FinGSet_G -> FinSet``."""

    _faithful = True

    def __init__(self, group) -> None:
        self._group = _owned_group(group)
        self._generic_forgetful = GObjects(self._group, Sets()).forgetful_functor()
        super().__init__(FiniteGSets(self._group), FiniteSets())

    def group(self):
        return self._group

    def _apply_object(self, g_set):
        return self._generic_forgetful(g_set)

    def _apply_morphism(self, morphism):
        return self._generic_forgetful(morphism)

    def _repr_(self):
        return f"Underlying finite-set functor on {self.group()}-sets"


class CofreeGSetFunctor(Functor):
    r"""``Map(G,-) : FinSet -> FinGSet_G`` with ``(a f)(h)=f(h a)``."""

    def __init__(self, group) -> None:
        self._group = _owned_group(group)
        assert self._group.is_finite() is True, (
            f"Map(G, S) is a finite G-set for every finite set S only when G is finite, but {self._group} is "
            "not known to be finite"
        )
        self._group_points = finite_ordered_set(self._group)
        super().__init__(FiniteSets(), FiniteGSets(self._group))

    def group(self):
        return self._group

    def group_points(self):
        return self._group_points

    def _function_value_in_point_set(self, function_point, group_element):
        return function_point.component(self.group_points()(group_element))

    def _function_point_in_point_set(self, point_set, function):
        return point_set(function)

    def _apply_object(self, set_object):
        point_set = Sets().product(indexed_family(self.group_points(), lambda _group_element: set_object))

        def action(group_element, function_point):
            return self._function_point_in_point_set(
                point_set,
                lambda argument: self._function_value_in_point_set(
                    function_point, argument * group_element
                ),
            )

        return FiniteGSets(self.group())(point_set, action)

    def function_value(self, cofree_g_set, function_point, group_element):
        if function_point not in cofree_g_set:
            raise TypeError(f"{function_point} is not a point of the cofree G-set {cofree_g_set}")
        return self._function_value_in_point_set(function_point, group_element)

    def function_point(self, cofree_g_set, function):
        return self._function_point_in_point_set(cofree_g_set.point_set(), function)

    def _apply_morphism(self, set_morphism):
        source = self(set_morphism.domain())
        target = self(set_morphism.codomain())
        return source.Mor(target)(
            lambda function_point: self.function_point(
                target,
                lambda group_element: set_morphism(
                    self.function_value(source, function_point, group_element)
                ),
            )
        )

    def _repr_(self):
        return f"Cofree finite {self.group()}-set functor"


class FreeGSetUnderlyingAdjunction(Adjunction):
    r"""``G × - ⊣ U`` on finite sets and represented finite ``G``-sets."""

    def __init__(self, group) -> None:
        group = _owned_group(group)
        super().__init__(FreeGSetFunctor(group), FiniteGSets(group).forgetful_functor())

    def _repr_(self):
        return f"Free/underlying adjunction G x - ⊣ U for {self.left_adjoint().group()}"

    def _unit_component(self, set_object):
        free = self.left_adjoint()(set_object)
        return Sets().Mor(set_object, free)(
            lambda point: self.left_adjoint().free_point(
                free, self.left_adjoint().group().one(), point
            )
        )

    def _counit_component(self, g_set):
        free = self.left_adjoint()(self.right_adjoint()(g_set))
        return free.Mor(g_set)(
            lambda point: g_set.act(point[0], point[1])
        )



class UnderlyingCofreeGSetAdjunction(Adjunction):
    r"""``U ⊣ Map(G,-)`` on represented finite ``G``-sets."""

    def __init__(self, group) -> None:
        group = _owned_group(group)
        super().__init__(FiniteGSets(group).forgetful_functor(), CofreeGSetFunctor(group))

    def _repr_(self):
        return f"Underlying/cofree adjunction U ⊣ Map(G, -) for {self.right_adjoint().group()}"

    def _unit_component(self, g_set):
        cofree = self.right_adjoint()(self.left_adjoint()(g_set))
        return g_set.Mor(cofree)(
            lambda point: self.right_adjoint().function_point(
                cofree,
                lambda group_element: g_set.act(group_element, point),
            )
        )

    def _counit_component(self, set_object):
        cofree = self.right_adjoint()(set_object)
        return Sets().Mor(cofree, set_object)(
            lambda function_point: self.right_adjoint().function_value(
                cofree,
                function_point,
                self.right_adjoint().group().one(),
            )
        )



@cached_function
def _g_set_orbits_trivial_adjunction(group) -> GSetOrbitsTrivialAdjunction:
    return GSetOrbitsTrivialAdjunction(group)


@cached_function
def _g_set_trivial_fixed_adjunction(group) -> GSetTrivialFixedAdjunction:
    return GSetTrivialFixedAdjunction(group)


@cached_function
def _free_g_set_underlying_adjunction(group) -> FreeGSetUnderlyingAdjunction:
    return FreeGSetUnderlyingAdjunction(group)


@cached_function
def _underlying_cofree_g_set_adjunction(group) -> UnderlyingCofreeGSetAdjunction:
    return UnderlyingCofreeGSetAdjunction(group)


__all__ = [
    "CofreeGSetFunctor",
    "FreeGSetFunctor",
    "FreeGSetUnderlyingAdjunction",
    "GSetFixedPointsFunctor",
    "GSetOrbitsFunctor",
    "GSetOrbitsTrivialAdjunction",
    "GSetTrivialFixedAdjunction",
    "TrivialGSetFunctor",
    "UnderlyingCofreeGSetAdjunction",
    "UnderlyingFiniteGSetFunctor",
]
