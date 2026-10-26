r"""Selected chart presentations of finite-dimensional topological manifolds."""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.manifolds import TopologicalManifolds
from sage_extensions.categories.topological_spaces import TopologicalSpaces


class TopologicalAtlasMor(CategoricalMor):
    r"""Continuous maps with compatible maps in selected charts."""

    class ElementMethods:
        def __init__(self, parent, continuous_map, chart_maps):
            Morphism.__init__(self, parent)
            self._continuous_map = continuous_map
            self._chart_maps = chart_maps

        def underlying_continuous_morphism(self):
            return self._continuous_map

        def chart_maps(self):
            return self._chart_maps

        def topological_manifold_morphism(self):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, continuous_map, chart_maps):
        pass

    @object_level
    def identity(self):
        pass


class TopologicalAtlasMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = TopologicalAtlasMor


class _AtlasUnderlyingSpaceFunctor(Functor):
    def __init__(self):
        super().__init__(TopologicalAtlases(), TopologicalSpaces())

    def _apply_object(self, atlas):
        return atlas.underlying_topological_space()

    def _apply_morphism(self, morphism):
        return morphism.underlying_continuous_morphism()


class _AtlasTopologicalManifoldFunctor(Functor):
    def __init__(self):
        super().__init__(TopologicalAtlases(), TopologicalManifolds())

    def _apply_object(self, atlas):
        pass

    def _apply_morphism(self, morphism):
        pass


class TopologicalAtlases(OwnedCategory):
    r"""Compatible homeomorphic charts on one selected topological space."""

    _MorCategory = TopologicalAtlasMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "topological atlas presentations"

    def an_object(self):
        pass

    def on(
        self,
        topological_space,
        chart_domains,
        chart_domain_inclusions,
        charts,
        overlap_inclusions,
        transition_maps,
    ):
        pass

    def refinement(self, finer_atlas, coarser_atlas, chartwise_maps):
        pass

    @cached_method
    def forget(self):
        return _AtlasUnderlyingSpaceFunctor()

    @cached_method
    def maximalization(self):
        return _AtlasTopologicalManifoldFunctor()

    class ParentMethods:
        def __init__(
            self,
            topological_space,
            chart_domains,
            chart_domain_inclusions,
            charts,
            overlap_inclusions,
            transition_maps,
            **rest,
        ):
            self._topological_space = topological_space
            self._chart_domains = chart_domains
            self._chart_domain_inclusions = chart_domain_inclusions
            self._charts = charts
            self._overlap_inclusions = overlap_inclusions
            self._transition_maps = transition_maps
            super().__init__(**rest)

        def underlying_topological_space(self):
            return self._topological_space

        def chart_domains(self):
            return self._chart_domains

        def chart_domain_inclusion(self, chart):
            return self._chart_domain_inclusions[chart]

        def charts(self):
            return self._charts

        def chart(self, chart):
            return self._charts[chart]

        def overlap_inclusion(self, source_chart, target_chart):
            return self._overlap_inclusions[source_chart, target_chart]

        def transition_map(self, source_chart, target_chart):
            return self._transition_maps[source_chart, target_chart]

        def chart_domains_cover(self):
            r"""Decide whether the selected chart domains cover the space."""
            pass

        def transitions_are_homeomorphisms(self):
            r"""Decide whether every overlap map is a homeomorphism."""
            pass

        def transition_cocycle_holds(self):
            pass

        def restrict(self, open_inclusion):
            pass

        def restriction_morphism(self, restricted_atlas):
            pass

        def maximal_atlas(self):
            pass

        def topological_manifold(self):
            pass
