r"""Manifolds with half-space and quadrant local models."""

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
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.manifolds import (
    SmoothManifolds,
    TopologicalManifolds,
)
from sage_extensions.categories.real_ck_manifolds import (
    RealCkManifolds,
    _real_ck_degree,
)
from sage_extensions.categories.topological_spaces import TopologicalSpaces


def _dimension_at_most(category, dimension):
    from sage_extensions.categories.manifold_dimension_strata import ManifoldsOfDimensionAtMost

    return ManifoldsOfDimensionAtMost(category, dimension)


def _pure_dimension(category, dimension):
    from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds

    return PureDimensionalManifolds(category, dimension)


class _StratifiedManifoldMapMethods:
    def __init__(self, parent, continuous_map, interior_map, stratum_maps):
        Morphism.__init__(self, parent)
        self._continuous_map = continuous_map
        self._interior_map = interior_map
        self._stratum_maps = stratum_maps

    def underlying_continuous_map(self):
        return self._continuous_map

    def interior_map(self):
        return self._interior_map

    def stratum_maps(self):
        return self._stratum_maps

    def _call_(self, point):
        return self._continuous_map(point)

    def underlying_topological_stratified_map(self):
        pass

    def __mul__(self, other):
        pass


class _StratifiedManifoldMor(CategoricalMor):
    ElementMethods = _StratifiedManifoldMapMethods

    def _element_constructor_(self, continuous_map, interior_map, stratum_maps):
        pass

    @object_level
    def identity(self):
        pass


class TopologicalBoundaryMor(_StratifiedManifoldMor):
    r"""Continuous maps preserving the specified boundary stratum."""


class SmoothBoundaryMor(_StratifiedManifoldMor):
    r"""Smooth maps preserving the specified boundary stratum."""


class TopologicalCornerMor(_StratifiedManifoldMor):
    r"""Continuous maps preserving the specified corner-depth strata."""


class SmoothCornerMor(_StratifiedManifoldMor):
    r"""Smooth maps preserving the specified corner-depth strata."""


class TopologicalBoundaryMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = TopologicalBoundaryMor


class SmoothBoundaryMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SmoothBoundaryMor


class TopologicalCornerMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = TopologicalCornerMor


class SmoothCornerMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SmoothCornerMor


class _InteriorFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        pass

    def _apply_morphism(self, morphism):
        return morphism.interior_map()


class _UnderlyingTopologicalStrataFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        return manifold.underlying_topological_stratified_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_topological_stratified_map()


class _UnderlyingStratifiedSpaceFunctor(Functor):
    r"""Forget the manifold atlas and strata, on spaces and maps."""

    def __init__(self, source):
        super().__init__(source, TopologicalSpaces())

    def _apply_object(self, manifold):
        return manifold.underlying_topological_space()

    def _apply_morphism(self, morphism):
        return morphism.underlying_continuous_map()


class _SmoothStratifiedCkPresentationFunctor(Functor):
    r"""Place smooth boundary or corner data in its C^infinity category."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        pass

    def _apply_morphism(self, morphism):
        pass


class _StratifiedManifoldMethods:
    def dimension(self):
        pass

    def atlas(self):
        pass

    def interior(self):
        pass

    def interior_inclusion(self):
        pass

    def depth_stratum(self, depth):
        pass

    def underlying_topological_space(self):
        pass


class TopologicalManifoldsWithBoundary(OwnedCategory):
    r"""Manifolds modelled on closed half-spaces, with boundary-preserving maps."""

    _MorCategory = TopologicalBoundaryMorCategoryConstruction

    def super_categories(self):
        return [TopologicalManifoldsWithCorners()]

    @classmethod
    def _repr_object_names(cls):
        return "topological manifolds with boundary"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        return _dimension_at_most(self, dimension)

    def PureDimension(self, dimension):
        return _pure_dimension(self, dimension)

    def on(self, space, atlas, boundary_inclusion):
        pass

    @cached_method
    def interior(self):
        return _InteriorFunctor(self, TopologicalManifolds())

    @cached_method
    def forget(self):
        return _UnderlyingStratifiedSpaceFunctor(self)

    class ParentMethods(_StratifiedManifoldMethods):
        def boundary(self):
            pass

        def boundary_inclusion(self):
            pass


class SmoothManifoldsWithBoundary(OwnedCategory):
    r"""Smooth half-space manifolds with smooth boundary-preserving maps."""

    _MorCategory = SmoothBoundaryMorCategoryConstruction

    def super_categories(self):
        return [SmoothManifoldsWithCorners()]

    @classmethod
    def _repr_object_names(cls):
        return "smooth manifolds with boundary"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        return _dimension_at_most(self, dimension)

    def PureDimension(self, dimension):
        return _pure_dimension(self, dimension)

    def on(self, space, atlas, boundary_inclusion):
        pass

    @cached_method
    def interior(self):
        return _InteriorFunctor(self, SmoothManifolds())

    @cached_method
    def forget_smoothness(self):
        return _UnderlyingTopologicalStrataFunctor(self, TopologicalManifoldsWithBoundary())

    @cached_method
    def as_ck(self):
        return _SmoothStratifiedCkPresentationFunctor(self, RealCkManifoldsWithBoundary(Infinity))

    @cached_method
    def forget_to(self, degree):
        return self.as_ck().then(RealCkManifoldsWithBoundary(Infinity).forget_to(degree))

    @cached_method
    def forget(self):
        return _UnderlyingStratifiedSpaceFunctor(self)

    class ParentMethods(_StratifiedManifoldMethods):
        def boundary(self):
            pass

        def boundary_inclusion(self):
            pass

        def underlying_topological_stratified_manifold(self):
            pass


class TopologicalManifoldsWithCorners(OwnedCategory):
    r"""Manifolds modelled on orthants, with maps preserving corner depth."""

    _MorCategory = TopologicalCornerMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "topological manifolds with corners"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        return _dimension_at_most(self, dimension)

    def PureDimension(self, dimension):
        return _pure_dimension(self, dimension)

    def on(self, space, atlas, depth_strata):
        pass

    @cached_method
    def interior(self):
        return _InteriorFunctor(self, TopologicalManifolds())

    @cached_method
    def forget(self):
        return _UnderlyingStratifiedSpaceFunctor(self)

    class ParentMethods(_StratifiedManifoldMethods):
        def __init__(self, underlying_space, atlas, depth_strata, **rest):
            self._underlying_space = underlying_space
            self._atlas = atlas
            self._depth_strata = depth_strata
            super().__init__(**rest)

        def underlying_topological_space(self):
            return self._underlying_space

        def atlas(self):
            return self._atlas

        def depth_strata(self):
            return self._depth_strata

        def depth_stratum(self, depth):
            return self._depth_strata[depth]


class SmoothManifoldsWithCorners(OwnedCategory):
    r"""Smooth orthant manifolds with smooth maps preserving corner depth."""

    _MorCategory = SmoothCornerMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "smooth manifolds with corners"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        return _dimension_at_most(self, dimension)

    def PureDimension(self, dimension):
        return _pure_dimension(self, dimension)

    def on(self, topological_corner_manifold, atlas):
        pass

    @cached_method
    def interior(self):
        return _InteriorFunctor(self, SmoothManifolds())

    @cached_method
    def forget_smoothness(self):
        return _UnderlyingTopologicalStrataFunctor(self, TopologicalManifoldsWithCorners())

    @cached_method
    def as_ck(self):
        return _SmoothStratifiedCkPresentationFunctor(self, RealCkManifoldsWithCorners(Infinity))

    @cached_method
    def forget_to(self, degree):
        return self.as_ck().then(RealCkManifoldsWithCorners(Infinity).forget_to(degree))

    @cached_method
    def forget(self):
        return _UnderlyingStratifiedSpaceFunctor(self)

    class ParentMethods(_StratifiedManifoldMethods):
        def __init__(self, topological_corner_manifold, atlas, **rest):
            self._topological_corner_manifold = topological_corner_manifold
            self._atlas = atlas
            super().__init__(**rest)

        def underlying_topological_stratified_manifold(self):
            return self._topological_corner_manifold

        def underlying_topological_space(self):
            return self._topological_corner_manifold.underlying_topological_space()

        def atlas(self):
            return self._atlas

        def depth_stratum(self, depth):
            return self._topological_corner_manifold.depth_stratum(depth)


class RealCkStratifiedMor(CategoricalMor):
    r"""Stratum-preserving maps of one selected differentiability degree."""

    class ElementMethods(_StratifiedManifoldMapMethods):
        def underlying_topological_stratified_map(self):
            pass

        def weaken_to(self, degree):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, continuous_map, interior_map, stratum_maps):
        pass

    @object_level
    def identity(self):
        pass


class RealCkBoundaryMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RealCkStratifiedMor


class RealCkCornerMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RealCkStratifiedMor


class _WeakenStratifiedDifferentiabilityFunctor(Functor):
    r"""Forget higher regularity while retaining boundary or corner strata."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        pass

    def _apply_morphism(self, morphism):
        pass


class RealCkManifoldsWithCorners(OwnedParameterizedCategory):
    r"""Corner manifolds with a selected ``C^k`` atlas and maps, including ``k=∞``."""

    _MorCategory = RealCkCornerMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, degree):
        return Category.__classcall__(cls, _real_ck_degree(degree))

    def degree(self):
        return self.parameter()

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"real C^{self.degree()} manifolds with corners"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        return _dimension_at_most(self, dimension)

    def PureDimension(self, dimension):
        return _pure_dimension(self, dimension)

    def on(self, topological_corner_manifold, atlas):
        pass

    @cached_method
    def interior(self):
        return _InteriorFunctor(self, RealCkManifolds(self.degree()))

    @cached_method
    def forget_topology(self):
        return _UnderlyingTopologicalStrataFunctor(self, TopologicalManifoldsWithCorners())

    @cached_method
    def forget(self):
        return _UnderlyingStratifiedSpaceFunctor(self)

    @cached_method
    def forget_to(self, degree):
        degree = _real_ck_degree(degree)
        if degree > self.degree():
            raise ValueError(f"C^{self.degree()} can forget only to C^j with 1 <= j <= {self.degree()}")
        return _WeakenStratifiedDifferentiabilityFunctor(self, RealCkManifoldsWithCorners(degree))

    class ParentMethods(_StratifiedManifoldMethods):
        def __init__(self, topological_corner_manifold, atlas, **rest):
            self._topological_corner_manifold = topological_corner_manifold
            self._atlas = atlas
            super().__init__(**rest)

        def underlying_topological_stratified_manifold(self):
            return self._topological_corner_manifold

        def underlying_topological_space(self):
            return self._topological_corner_manifold.underlying_topological_space()

        def atlas(self):
            return self._atlas

        def depth_stratum(self, depth):
            return self._topological_corner_manifold.depth_stratum(depth)

        def weaken_to(self, degree):
            pass


class RealCkManifoldsWithBoundary(OwnedParameterizedCategory):
    r"""Boundary manifolds with a selected ``C^k`` atlas and maps, including ``k=∞``."""

    _MorCategory = RealCkBoundaryMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, degree):
        return Category.__classcall__(cls, _real_ck_degree(degree))

    def degree(self):
        return self.parameter()

    def super_categories(self):
        return [RealCkManifoldsWithCorners(self.degree())]

    def _repr_object_names(self):
        return f"real C^{self.degree()} manifolds with boundary"

    def an_object(self):
        pass

    def DimensionAtMost(self, dimension):
        return _dimension_at_most(self, dimension)

    def PureDimension(self, dimension):
        return _pure_dimension(self, dimension)

    def on(self, topological_boundary_manifold, atlas):
        pass

    @cached_method
    def interior(self):
        return _InteriorFunctor(self, RealCkManifolds(self.degree()))

    @cached_method
    def forget_topology(self):
        return _UnderlyingTopologicalStrataFunctor(self, TopologicalManifoldsWithBoundary())

    @cached_method
    def forget(self):
        return _UnderlyingStratifiedSpaceFunctor(self)

    @cached_method
    def forget_to(self, degree):
        degree = _real_ck_degree(degree)
        if degree > self.degree():
            raise ValueError(f"C^{self.degree()} can forget only to C^j with 1 <= j <= {self.degree()}")
        return _WeakenStratifiedDifferentiabilityFunctor(self, RealCkManifoldsWithBoundary(degree))

    class ParentMethods(_StratifiedManifoldMethods):
        def underlying_topological_stratified_manifold(self):
            return self._topological_corner_manifold

        def weaken_to(self, degree):
            pass

        def boundary(self):
            pass

        def boundary_inclusion(self):
            pass
