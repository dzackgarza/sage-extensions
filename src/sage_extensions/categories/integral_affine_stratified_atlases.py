r"""Integral-affine chart presentations along boundary and corner strata."""

from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.rings.infinity import Infinity

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.integral_affine_manifolds import (
    IntegralAffineManifoldsWithBoundary,
    IntegralAffineManifoldsWithCorners,
)
from sage_extensions.categories.manifolds_with_boundary import (
    SmoothManifoldsWithBoundary,
    SmoothManifoldsWithCorners,
)
from sage_extensions.categories.stratified_atlases import (
    RealCkBoundaryAtlases,
    RealCkCornerAtlases,
)
from sage_extensions.owned_category_bases import CategoryWithAxiom


for _axiom in ("Oriented", "StrictLatticePointAtlas"):
    if _axiom not in all_axioms:
        all_axioms.add(_axiom)


class IntegralAffineStratifiedAtlasMor(CategoricalMor):
    r"""Stratum-preserving smooth maps with chartwise integral-affine maps."""

    class ElementMethods:
        def __init__(self, parent, smooth_stratified_map, chartwise_affine_maps, stratum_maps):
            Morphism.__init__(self, parent)
            self._smooth_stratified_map = smooth_stratified_map
            self._chartwise_affine_maps = chartwise_affine_maps
            self._stratum_maps = stratum_maps

        def underlying_smooth_stratified_morphism(self):
            return self._smooth_stratified_map

        def chartwise_affine_maps(self):
            return self._chartwise_affine_maps

        def stratum_maps(self):
            return self._stratum_maps

        def integral_affine_manifold_morphism(self):
            pass

        def smooth_atlas_morphism(self):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, smooth_stratified_map, chartwise_affine_maps, stratum_maps):
        pass

    @object_level
    def identity(self):
        pass


class IntegralAffineStratifiedAtlasMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineStratifiedAtlasMor


class _StratifiedAffineAtlasForgetFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, atlas):
        return atlas.underlying_smooth_stratified_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_stratified_morphism()


class _StratifiedAffineAtlasMaximalizationFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, atlas):
        pass

    def _apply_morphism(self, morphism):
        pass


class _StratifiedAffineAtlasSmoothFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, atlas):
        return atlas.smooth_atlas()

    def _apply_morphism(self, morphism):
        return morphism.smooth_atlas_morphism()


class _IntegralAffineStratifiedAtlasMethods:
    def __init__(
        self,
        smooth_stratified_manifold,
        affine_model,
        chart_domains,
        chart_domain_inclusions,
        affine_charts,
        overlap_inclusions,
        transition_maps,
        **rest,
    ):
        self._smooth_stratified_manifold = smooth_stratified_manifold
        self._affine_model = affine_model
        self._chart_domains = chart_domains
        self._chart_domain_inclusions = chart_domain_inclusions
        self._affine_charts = affine_charts
        self._overlap_inclusions = overlap_inclusions
        self._transition_maps = transition_maps
        super().__init__(**rest)

    def underlying_smooth_stratified_manifold(self):
        return self._smooth_stratified_manifold

    def affine_model(self):
        return self._affine_model

    def chart_domains(self):
        return self._chart_domains

    def chart_domain_inclusion(self, chart):
        return self._chart_domain_inclusions[chart]

    def affine_charts(self):
        return self._affine_charts

    def affine_chart(self, chart):
        return self._affine_charts[chart]

    def overlap_inclusion(self, source_chart, target_chart):
        return self._overlap_inclusions[source_chart, target_chart]

    def transition_map(self, source_chart, target_chart):
        return self._transition_maps[source_chart, target_chart]

    def chart_domains_cover(self):
        r"""Decide whether the selected chart domains cover the stratified manifold."""
        pass

    def transitions_are_integral_affine(self):
        r"""Decide whether every overlap map preserves the selected lattice."""
        pass

    def transition_cocycle_holds(self):
        pass

    def restrict(self, open_inclusion):
        pass

    def restriction_morphism(self, restricted_atlas):
        pass

    def maximal_atlas(self):
        pass

    def smooth_atlas(self):
        pass

    def integral_affine_manifold(self):
        pass


class IntegralAffineCornerAtlases(OwnedCategory):
    r"""Integral-affine orthant charts on an exact smooth corner manifold."""

    _MorCategory = IntegralAffineStratifiedAtlasMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine corner atlas presentations"

    def an_object(self):
        pass

    def on(
        self,
        smooth_corner_manifold,
        affine_model,
        chart_domains,
        chart_domain_inclusions,
        affine_charts,
        overlap_inclusions,
        transition_maps,
    ):
        pass

    def transition_is_integral_affine(self, affine_model, transition_map):
        pass

    def refinement(self, finer_atlas, coarser_atlas, chartwise_maps):
        pass

    @cached_method
    def forget(self):
        return _StratifiedAffineAtlasForgetFunctor(self, SmoothManifoldsWithCorners())

    @cached_method
    def maximalization(self):
        return _StratifiedAffineAtlasMaximalizationFunctor(self, IntegralAffineManifoldsWithCorners())

    @cached_method
    def forget_affine_structure(self):
        return _StratifiedAffineAtlasSmoothFunctor(self, RealCkCornerAtlases(Infinity))

    ParentMethods = _IntegralAffineStratifiedAtlasMethods

    class Oriented(CategoryWithAxiom):
        r"""Atlases with determinant-one integral linear changes."""

        @cached_method
        def maximalization(self):
            return _StratifiedAffineAtlasMaximalizationFunctor(
                self, IntegralAffineManifoldsWithCorners().Oriented()
            )

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Atlases whose translations preserve selected lattice points."""

        @cached_method
        def maximalization(self):
            return _StratifiedAffineAtlasMaximalizationFunctor(
                self, IntegralAffineManifoldsWithCorners().StrictLatticePointAtlas()
            )


class IntegralAffineBoundaryAtlases(OwnedCategory):
    r"""Integral-affine half-space charts on an exact smooth boundary manifold."""

    _MorCategory = IntegralAffineStratifiedAtlasMorCategoryConstruction

    def super_categories(self):
        return [IntegralAffineCornerAtlases()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine boundary atlas presentations"

    def an_object(self):
        pass

    def on(
        self,
        smooth_boundary_manifold,
        affine_model,
        chart_domains,
        chart_domain_inclusions,
        affine_charts,
        overlap_inclusions,
        transition_maps,
    ):
        pass

    def transition_is_integral_affine(self, affine_model, transition_map):
        pass

    def refinement(self, finer_atlas, coarser_atlas, chartwise_maps):
        pass

    @cached_method
    def forget(self):
        return _StratifiedAffineAtlasForgetFunctor(self, SmoothManifoldsWithBoundary())

    @cached_method
    def maximalization(self):
        return _StratifiedAffineAtlasMaximalizationFunctor(self, IntegralAffineManifoldsWithBoundary())

    @cached_method
    def forget_affine_structure(self):
        return _StratifiedAffineAtlasSmoothFunctor(self, RealCkBoundaryAtlases(Infinity))

    ParentMethods = _IntegralAffineStratifiedAtlasMethods

    class Oriented(CategoryWithAxiom):
        r"""Atlases with determinant-one integral linear changes."""

        @cached_method
        def maximalization(self):
            return _StratifiedAffineAtlasMaximalizationFunctor(
                self, IntegralAffineManifoldsWithBoundary().Oriented()
            )

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Atlases whose translations preserve selected lattice points."""

        @cached_method
        def maximalization(self):
            return _StratifiedAffineAtlasMaximalizationFunctor(
                self, IntegralAffineManifoldsWithBoundary().StrictLatticePointAtlas()
            )
