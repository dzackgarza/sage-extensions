r"""Selected chart presentations of real manifolds of fixed differentiability degree."""

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

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
from sage_extensions.categories.topological_atlases import TopologicalAtlases
from sage_extensions.categories.real_ck_manifolds import RealCkManifolds, _real_ck_degree
from sage.rings.infinity import Infinity

from sage_extensions.categories.manifolds import DifferentiableManifolds
from sage_extensions.owned_category import _object_of
from sage_extensions.logic import AtomicProposition


class RealCkAtlasMor(CategoricalMor):
    r"""Maps presented by a topological map and compatible chart maps."""

    class ElementMethods:
        def __init__(self, parent, topological_map, chart_maps):
            Morphism.__init__(self, parent)
            self._topological_map = topological_map
            self._chart_maps = chart_maps

        def underlying_topological_morphism(self):
            return self._topological_map

        def chart_maps(self):
            return self._chart_maps

        def real_ck_morphism(self, source, target):
            pass

        def topological_atlas_morphism(self):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, topological_map, chart_maps):
        pass

    @object_level
    def identity(self):
        pass


class RealCkAtlasMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RealCkAtlasMor


class _AtlasUnderlyingTopologicalManifoldFunctor(Functor):
    def __init__(self, degree):
        super().__init__(RealCkAtlases(degree), TopologicalManifolds())

    def _apply_object(self, atlas):
        return atlas.underlying_topological_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_topological_morphism()


class _AtlasRealCkManifoldFunctor(Functor):
    def __init__(self, degree):
        super().__init__(RealCkAtlases(degree), RealCkManifolds(degree))

    def _apply_object(self, atlas):
        pass

    def _apply_morphism(self, morphism):
        pass


class _AtlasUnderlyingTopologicalAtlasFunctor(Functor):
    def __init__(self, degree):
        super().__init__(RealCkAtlases(degree), TopologicalAtlases())

    def _apply_object(self, atlas):
        return atlas.topological_atlas()

    def _apply_morphism(self, morphism):
        return morphism.topological_atlas_morphism()


class _WeakenAtlasDifferentiabilityFunctor(Functor):
    r"""Forget higher atlas regularity on objects and chartwise maps."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, atlas):
        pass

    def _apply_morphism(self, morphism):
        pass


class RealCkAtlases(OwnedParameterizedCategory):
    r"""Compatible ``C^k`` charts on a selected topological manifold."""

    _MorCategory = RealCkAtlasMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, degree):
        return Category.__classcall__(cls, _real_ck_degree(degree))

    def degree(self):
        return self.parameter()

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"real C^{self.degree()} atlas presentations"

    def an_object(self):
        pass

    def on(
        self,
        topological_manifold,
        chart_domains,
        chart_domain_inclusions,
        charts,
        overlap_inclusions,
        transition_maps,
    ):
        r"""Select ``C^k`` charts and their transitions on the exact manifold.

        A ``C^k`` chart is a chart whose transition maps are ``C^k``, so a
        ``C^k`` atlas is a family of charts on one topological manifold
        (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  Each chart
        ``s`` has an open submanifold ``U_s`` of ``topological_manifold``,
        carried into it by ``chart_domain_inclusions[s] : U_s -> X``, and a
        chart ``charts[s]`` out of ``U_s``; the transition
        ``tau_{st} = phi_t o phi_s^{-1}`` changes coordinates on the overlap,
        with ``overlap_inclusions[s, t]`` the inclusion of the overlap in the
        chart domains.  The pair ``(s, t)`` names the direction, and a family of
        one chart has no pair and so no overlap and no transition.

        The four families of maps are indexed by the charts.  The construction
        retains them and computes nothing from them: the differentiability of
        every transition, the cocycle on triple overlaps and whether the chart
        domains cover the manifold are decisions the atlas answers, never
        conditions a caller is charged for at construction (``OWN-22``).
        """
        assert topological_manifold in TopologicalManifolds(), (
            f"a C^{self.degree()} atlas is a family of charts on a topological manifold, and "
            f"{topological_manifold} is in {topological_manifold.category()}"
        )
        return _object_of(
            self,
            topological_manifold=topological_manifold,
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
        return _AtlasUnderlyingTopologicalManifoldFunctor(self.degree())

    @cached_method
    def maximalization(self):
        return _AtlasRealCkManifoldFunctor(self.degree())

    @cached_method
    def forget_differentiability(self):
        return _AtlasUnderlyingTopologicalAtlasFunctor(self.degree())

    @cached_method
    def forget_to(self, degree):
        degree = _real_ck_degree(degree)
        if degree > self.degree():
            raise ValueError(f"C^{self.degree()} can forget only to C^j with j <= {self.degree()}")
        return _WeakenAtlasDifferentiabilityFunctor(self, RealCkAtlases(degree))

    class ParentMethods:
        def __init__(
            self,
            topological_manifold,
            chart_domains,
            chart_domain_inclusions,
            charts,
            overlap_inclusions,
            transition_maps,
            **rest,
        ):
            self._topological_manifold = topological_manifold
            self._chart_domains = chart_domains
            self._chart_domain_inclusions = chart_domain_inclusions
            self._charts = charts
            self._overlap_inclusions = overlap_inclusions
            self._transition_maps = transition_maps
            super().__init__(**rest)

        def underlying_topological_manifold(self):
            return self._topological_manifold

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
            r"""Decide whether the selected chart domains cover the manifold.

            A chart domain is an open submanifold, carried into the manifold by
            ``chart_domain_inclusion``, so the domains cover the manifold exactly
            when every point of it lies in one of them.  A chart whose domain
            *is* the manifold covers it, and that is decided here.  Whether
            proper open submanifolds cover an infinite manifold is not a
            question the retained maps decide, so the proposition states it.
            """
            manifold = self.underlying_topological_manifold()
            match any(
                self._chart_domains[chart] is manifold for chart in self._charts
            ):
                case True:
                    return True
                case False:
                    return AtomicProposition("chart_domains_cover", self)

        def _repr_(self):
            r"""A C^k atlas is named by the charts it selects, their class and the manifold they chart."""
            return (
                f"C^{self.category().degree()} atlas of the charts {tuple(self._charts)} on "
                f"{self.underlying_topological_manifold()}"
            )

        def transitions_are_ck(self):
            r"""Decide whether overlap maps are ``C^k`` diffeomorphisms.

            A coordinate change is read between two charts, so an atlas of one
            chart has no overlap map, and nothing of it could fail to be a
            ``C^k`` diffeomorphism: it answers ``True``.  From two charts on, the
            recorded maps are arrows of the category of sets, and their class is
            not decided by the arrow, so the proposition states it.
            """
            match tuple(self._charts)[1:]:
                case ():
                    return True
                case _:
                    return AtomicProposition("transitions_are_ck", self)

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

        @cached_method
        def real_ck_manifold(self):
            r"""The ``C^k`` manifold these charts present: the manifold itself, when it is one.

            The charts are ``C^k`` charts of the manifold, so they present it as a
            ``C^k`` manifold; when it already is one of at least this class, the
            manifold they present is the manifold itself, not a second object
            carrying the same structure (``OWN-15``, ``OWN-19``).  A manifold
            whose class is lower than the atlas' is not presented by it, and the
            refusal says which degrees are.

            A class of at least ``C^k`` is asked of the manifold's own
            differentiability degree, so a smooth manifold answers every finite
            degree (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).
            """
            manifold = self.underlying_topological_manifold()
            degree = self.category().degree()
            match degree is Infinity:
                case True:
                    assert manifold.is_smooth(), (
                        f"a C^oo atlas presents a smooth manifold, and {manifold} is of class "
                        f"C^{manifold.differentiability_degree()}"
                    )
                case False:
                    assert manifold in DifferentiableManifolds(), (
                        f"a C^{degree} atlas presents a differentiable manifold, and {manifold} "
                        f"is in {manifold.category()}"
                    )
                    assert manifold.is_smooth() or manifold.differentiability_degree() >= degree, (
                        f"a C^{degree} atlas does not present a C^{manifold.differentiability_degree()} "
                        f"manifold: {manifold} is not of class C^{degree} or higher"
                    )
            return manifold

        def topological_atlas(self):
            pass
