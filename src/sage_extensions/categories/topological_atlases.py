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
from sage_extensions.logic import AtomicProposition
from sage_extensions.owned_category import _object_of


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
        r"""Select charts, their homeomorphisms and their transitions on the exact space.

        A chart of a topological manifold is a homeomorphism ``phi_s : U_s -> V_s``
        of an open subset ``U_s`` of the space onto an open subset ``V_s`` of
        ``R^n`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  Each
        chart ``s`` has an open submanifold ``U_s`` of ``topological_space``,
        carried into it by ``chart_domain_inclusions[s] : U_s -> X``, and a
        homeomorphism ``charts[s]`` out of ``U_s``.  The transition
        ``tau_{st} = phi_t o phi_s^{-1}`` changes coordinates on the overlap,
        with ``overlap_inclusions[s, t]`` the inclusion of the overlap in the
        chart domains; the pair ``(s, t)`` names its direction, and a family of
        one chart has no pair and so no overlap and no transition.

        The four families of maps are indexed by the charts.  The construction
        retains them and computes nothing from them: whether the transitions are
        homeomorphisms, satisfy the cocycle on triple overlaps and whether the
        chart domains cover the space are decisions the atlas answers
        (:meth:`ParentMethods.transitions_are_homeomorphisms`,
        :meth:`ParentMethods.transition_cocycle_holds`,
        :meth:`ParentMethods.chart_domains_cover`), never conditions a caller is
        charged for at construction (``OWN-22``).
        """
        assert topological_space in TopologicalSpaces(), (
            f"a topological atlas is a family of charts on a topological space, and "
            f"{topological_space} is in {topological_space.category()}"
        )
        return _object_of(
            self,
            topological_space=topological_space,
            chart_domains=chart_domains,
            chart_domain_inclusions=chart_domain_inclusions,
            charts=charts,
            overlap_inclusions=overlap_inclusions,
            transition_maps=transition_maps,
        )

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
            r"""Decide whether the selected chart domains cover the space.

            A chart domain is an open subset of the space, carried into it by
            ``chart_domain_inclusion``, so the domains cover the space exactly
            when every point of the space lies in one of them.  A chart whose
            domain *is* the space covers it, and that is decided here.  Whether
            proper open subsets cover an infinite space is not a question the
            retained maps decide, so the proposition states it.
            """
            space = self.underlying_topological_space()
            match any(
                self._chart_domains[chart] is space for chart in self._charts
            ):
                case True:
                    return True
                case False:
                    return AtomicProposition("chart_domains_cover", self)

        def transitions_are_homeomorphisms(self):
            r"""Decide whether every overlap map is a homeomorphism.

            A coordinate change is read between two charts, so an atlas of one
            chart has no overlap map, and nothing of it could fail to be a
            homeomorphism: it answers ``True``.  From two charts on, the
            recorded maps are arrows of the category of sets, and whether one is
            a homeomorphism is not decided by the arrow, so the proposition
            states it.
            """
            match tuple(self._charts)[1:]:
                case ():
                    return True
                case _:
                    return AtomicProposition("transitions_are_homeomorphisms", self)

        def transition_cocycle_holds(self):
            r"""Decide whether the coordinate changes compose: ``tau_tu o tau_st = tau_su``.

            An atlas of one chart has no coordinate change at all, so the
            cocycle has no instance on it and the atlas answers ``True``.  From
            two charts on the composite and its equality are questions about
            maps the atlas retains but does not compute, so the proposition
            states them.
            """
            match tuple(self._charts)[1:]:
                case ():
                    return True
                case _:
                    return AtomicProposition("transition_cocycle_holds", self)

        def restrict(self, open_inclusion):
            pass

        def restriction_morphism(self, restricted_atlas):
            pass

        def maximal_atlas(self):
            pass

        def topological_manifold(self):
            r"""The manifold these charts present: the space itself, when it is one.

            The charts are homeomorphisms of open subsets of the space, so they
            present it as a topological manifold.  When the space already is one,
            the manifold they present is that space and not a second object
            carrying the same structure (``OWN-15``, ``OWN-19``).  A space that
            is not a manifold is made into one by ``TopologicalManifolds.on``,
            which this tree does not construct, and the refusal names it.
            """
            space = self.underlying_topological_space()
            assert space in TopologicalManifolds(), (
                f"the charts of this atlas present {space} as a topological manifold, and it is "
                f"in {space.category()}: a space that is not one is made into one by "
                f"TopologicalManifolds().on, which this tree does not construct"
            )
            return space

        def _repr_(self):
            r"""An atlas is named by the charts it selects and the space they chart."""
            return (
                f"Topological atlas of the charts {tuple(self._charts)} on "
                f"{self.underlying_topological_space()}"
            )
