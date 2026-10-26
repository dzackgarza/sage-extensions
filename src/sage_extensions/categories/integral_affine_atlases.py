r"""Selected presentations of integral-affine atlases on smooth manifolds."""

from sage.misc.cachefunc import cached_method
from sage.categories.morphism import Morphism
from sage.rings.infinity import Infinity

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.integral_affine_manifolds import IntegralAffineManifolds
from sage_extensions.categories.manifolds import SmoothManifolds
from sage_extensions.categories.real_ck_atlases import RealCkAtlases
from sage_extensions.owned_category_bases import CategoryWithAxiom


class IntegralAffineAtlasMor(CategoricalMor):
    r"""Smooth maps with compatible chartwise integral-affine maps."""

    class ElementMethods:
        def __init__(self, parent, smooth_map, chartwise_affine_maps):
            Morphism.__init__(self, parent)
            self._smooth_map = smooth_map
            self._chartwise_affine_maps = chartwise_affine_maps

        def underlying_smooth_morphism(self):
            return self._smooth_map

        def chartwise_affine_maps(self):
            return self._chartwise_affine_maps

        def _call_(self, point):
            return self._smooth_map(point)

        def integral_affine_morphism(self, source, target):
            pass

        def smooth_atlas_morphism(self):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, smooth_map, chartwise_affine_maps):
        pass

    @object_level
    def identity(self):
        pass


class IntegralAffineAtlasMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineAtlasMor


class _AtlasUnderlyingManifoldFunctor(Functor):
    r"""Forget the atlas presentation on objects and maps."""

    def __init__(self, source):
        super().__init__(source, SmoothManifolds())

    def _apply_object(self, atlas):
        return atlas.underlying_smooth_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_morphism()


class _AtlasMaximalizationFunctor(Functor):
    r"""Pass from a compatible atlas to its selected maximal structure."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, atlas):
        pass

    def _apply_morphism(self, morphism):
        pass


class _UnderlyingSmoothAtlasFunctor(Functor):
    def __init__(self, source):
        super().__init__(source, RealCkAtlases(Infinity))

    def _apply_object(self, atlas):
        return atlas.smooth_atlas()

    def _apply_morphism(self, morphism):
        return morphism.smooth_atlas_morphism()


class IntegralAffineAtlases(OwnedCategory):
    r"""Compatible charts into one selected real affine lattice model."""

    _MorCategory = IntegralAffineAtlasMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine atlas presentations"

    def an_object(self):
        pass

    def on(
        self,
        smooth_manifold,
        affine_model,
        chart_domains,
        chart_domain_inclusions,
        affine_charts,
        overlap_inclusions,
        transition_maps,
    ):
        r"""Select charts and affine transitions on the exact smooth manifold."""
        pass

    def transition_is_integral_affine(self, affine_model, transition_map):
        r"""Decide whether the transition preserves the model's selected lattice."""
        pass

    def refinement(self, finer_atlas, coarser_atlas, chartwise_maps):
        pass

    @cached_method
    def forget(self):
        return _AtlasUnderlyingManifoldFunctor(self)

    @cached_method
    def maximalization(self):
        return _AtlasMaximalizationFunctor(self, IntegralAffineManifolds())

    @cached_method
    def forget_affine_structure(self):
        return _UnderlyingSmoothAtlasFunctor(self)

    class ParentMethods:
        def __init__(
            self,
            smooth_manifold,
            affine_model,
            chart_domains,
            chart_domain_inclusions,
            affine_charts,
            overlap_inclusions,
            transition_maps,
            **rest,
        ):
            self._smooth_manifold = smooth_manifold
            self._affine_model = affine_model
            self._chart_domains = chart_domains
            self._chart_domain_inclusions = chart_domain_inclusions
            self._affine_charts = affine_charts
            self._overlap_inclusions = overlap_inclusions
            self._transition_maps = transition_maps
            super().__init__(**rest)

        def underlying_smooth_manifold(self):
            return self._smooth_manifold

        def affine_model(self):
            return self._affine_model

        def affine_group_action(self):
            return self.affine_model().integral_affine_group_action()

        def chart_domains(self):
            return self._chart_domains

        def chart_domain_inclusion(self, chart):
            r"""Return the selected open inclusion of a chart domain."""
            return self._chart_domain_inclusions[chart]

        def affine_charts(self):
            return self._affine_charts

        def affine_chart(self, chart):
            r"""Return the affine map from its exact open domain to the model."""
            return self._affine_charts[chart]

        def transition_maps(self):
            return self._transition_maps

        def overlap_inclusion(self, source_chart, target_chart):
            r"""Return the overlap's inclusion into the source chart domain."""
            return self._overlap_inclusions[source_chart, target_chart]

        def transition_map(self, source_chart, target_chart):
            r"""Return the integral-affine map on the specified overlap."""
            return self._transition_maps[source_chart, target_chart]

        def transition_linear_part(self, source_chart, target_chart):
            r"""Return the transition's induced map of the selected lattice."""
            return self.transition_map(source_chart, target_chart).linear_part()

        def chart_domains_cover(self):
            r"""Decide whether the selected chart domains cover the manifold."""
            pass

        def transitions_are_integral_affine(self):
            r"""Decide whether every overlap map preserves the selected lattice."""
            pass

        def transition_cocycle_holds(self):
            r"""Decide the affine cocycle condition on each triple overlap."""
            pass

        def restrict(self, open_inclusion):
            pass

        def restriction_morphism(self, restricted_atlas):
            pass

        def maximal_atlas(self):
            pass

        def smooth_atlas(self):
            pass

        @cached_method
        def integral_affine_manifold(self):
            pass

    class Oriented(CategoryWithAxiom):
        r"""Atlases with determinant-one integral linear transitions."""

        @cached_method
        def maximalization(self):
            return _AtlasMaximalizationFunctor(self, IntegralAffineManifolds().Oriented())

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Atlases whose transitions preserve selected lattice points."""

        @cached_method
        def maximalization(self):
            return _AtlasMaximalizationFunctor(
                self, IntegralAffineManifolds().StrictLatticePointAtlas()
            )
