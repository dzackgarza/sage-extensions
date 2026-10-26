r"""Real manifolds of one selected differentiability degree."""

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.rings.infinity import Infinity

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.manifolds import TopologicalManifolds
from sage_extensions.categories.rings.ring_foundation import _owned_integers


def _real_ck_degree(degree):
    if degree == Infinity:
        return Infinity
    degree = _owned_integers()(degree)
    if degree < 1:
        raise ValueError(f"a C^k degree must be positive or infinity, not {degree}")
    return degree


class RealCkManifoldMor(CategoricalMor):
    r"""Maps with the selected differentiability degree."""

    class ElementMethods:
        def __init__(self, parent, topological_map, chart_maps):
            Morphism.__init__(self, parent)
            self._topological_map = topological_map
            self._chart_maps = chart_maps

        def underlying_topological_morphism(self):
            return self._topological_map

        def chart_maps(self):
            return self._chart_maps

        def _call_(self, point):
            return self._topological_map(point)

        def weaken_to(self, degree):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, topological_map, chart_maps):
        pass

    @object_level
    def identity(self):
        pass


class RealCkManifoldMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RealCkManifoldMor


class _WeakenDifferentiabilityFunctor(Functor):
    r"""Retain the exact manifold and maps while forgetting higher regularity."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        if self.codomain() is TopologicalManifolds():
            return manifold.underlying_topological_manifold()
        pass

    def _apply_morphism(self, morphism):
        if self.codomain() is TopologicalManifolds():
            return morphism.underlying_topological_morphism()
        pass


class RealCkManifolds(OwnedParameterizedCategory):
    r"""Real manifolds with a compatible ``C^k`` atlas, including ``k=∞``."""

    _MorCategory = RealCkManifoldMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, degree):
        return Category.__classcall__(cls, _real_ck_degree(degree))

    def degree(self):
        return self.parameter()

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"real C^{self.degree()} manifolds"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import ManifoldsOfDimensionAtMost

        return ManifoldsOfDimensionAtMost(self, dimension)

    def PureDimension(self, dimension):
        from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds

        return PureDimensionalManifolds(self, dimension)

    def on(self, topological_manifold, atlas):
        r"""Select a compatible ``C^k`` atlas on the exact topological manifold."""
        pass

    @cached_method
    def forget_to(self, degree):
        degree = _real_ck_degree(degree)
        if degree > self.degree():
            raise ValueError(f"C^{self.degree()} can forget only to C^j with 1 <= j <= {self.degree()}")
        return _WeakenDifferentiabilityFunctor(self, RealCkManifolds(degree))

    @cached_method
    def forget_topology(self):
        return _WeakenDifferentiabilityFunctor(self, TopologicalManifolds())

    class ParentMethods:
        def __init__(self, topological_manifold, atlas, **rest):
            self._topological_manifold = topological_manifold
            self._atlas = atlas
            super().__init__(**rest)

        def underlying_topological_manifold(self):
            return self._topological_manifold

        def atlas(self):
            return self._atlas

        def dimension(self):
            return self.underlying_topological_manifold().dimension()

        def open_submanifold(self, open_inclusion):
            pass

        def open_submanifold_inclusion(self, open_manifold):
            pass

        def weaken_to(self, degree):
            pass
